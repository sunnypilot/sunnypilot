#!/usr/bin/env python3
import math
import numpy as np
from openpilot.common.numpy_fast import clip, interp
from openpilot.common.params import Params
from cereal import car

import cereal.messaging as messaging
from openpilot.common.conversions import Conversions as CV
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.selfdrive.controls.lib.sunnypilot.common import Source
from openpilot.selfdrive.controls.lib.sunnypilot.speed_limit_controller import SpeedLimitController
from openpilot.selfdrive.car.interfaces import ACCEL_MIN, ACCEL_MAX
from openpilot.selfdrive.controls.lib.longcontrol import LongCtrlState
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import LongitudinalMpc
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import T_IDXS as T_IDXS_MPC
from openpilot.selfdrive.controls.lib.drive_helpers import V_CRUISE_MAX, CONTROL_N, get_speed_error
from openpilot.selfdrive.controls.lib.vision_turn_controller import VisionTurnController
from openpilot.selfdrive.controls.lib.turn_speed_controller import TurnSpeedController
from openpilot.selfdrive.controls.lib.sunnypilot.accel_controller import AccelController
from openpilot.selfdrive.controls.lib.sunnypilot.dynamic_experimental_controller import DynamicExperimentalController
from openpilot.selfdrive.controls.lib.events import Events
from openpilot.common.swaglog import cloudlog

LON_MPC_STEP = 0.2  # first step is 0.2s
A_CRUISE_MIN = -1.2
A_CRUISE_MAX_VALS = [1.6, 1.2, 0.8, 0.6]
A_CRUISE_MAX_BP = [0., 10.0, 25., 40.]
CONTROL_N_T_IDX = ModelConstants.T_IDXS[:CONTROL_N]

# Lookup table for turns
_A_TOTAL_MAX_V = [1.7, 3.2]
_A_TOTAL_MAX_BP = [20., 40.]


EventName = car.CarEvent.EventName


def get_max_accel(v_ego):
  return interp(v_ego, A_CRUISE_MAX_BP, A_CRUISE_MAX_VALS)


def limit_accel_in_turns(v_ego, angle_steers, a_target, CP):
  """
  This function returns a limited long acceleration allowed, depending on the existing lateral acceleration
  this should avoid accelerating when losing the target in turns
  """
  # FIXME: This function to calculate lateral accel is incorrect and should use the VehicleModel
  # The lookup table for turns should also be updated if we do this
  a_total_max = interp(v_ego, _A_TOTAL_MAX_BP, _A_TOTAL_MAX_V)
  a_y = v_ego ** 2 * angle_steers * CV.DEG_TO_RAD / (CP.steerRatio * CP.wheelbase)
  a_x_allowed = math.sqrt(max(a_total_max ** 2 - a_y ** 2, 0.))

  return [a_target[0], min(a_target[1], a_x_allowed)]


def get_accel_from_plan(CP, speeds, accels):
    if len(speeds) == CONTROL_N:
      v_target_now = interp(DT_MDL, CONTROL_N_T_IDX, speeds)
      a_target_now = interp(DT_MDL, CONTROL_N_T_IDX, accels)

      v_target = interp(CP.longitudinalActuatorDelay + DT_MDL, CONTROL_N_T_IDX, speeds)
      a_target = 2 * (v_target - v_target_now) / CP.longitudinalActuatorDelay - a_target_now

      v_target_1sec = interp(CP.longitudinalActuatorDelay + DT_MDL + 1.0, CONTROL_N_T_IDX, speeds)
    else:
      v_target = 0.0
      v_target_now = 0.0
      v_target_1sec = 0.0
      a_target = 0.0
    should_stop = (v_target < CP.vEgoStopping and
                    v_target_1sec < CP.vEgoStopping)
    return a_target, should_stop


class LongitudinalPlanner:
  def __init__(self, CP, init_v=0.0, init_a=0.0, dt=DT_MDL):
    self.CP = CP
    self.mpc = LongitudinalMpc(dt=dt)
    self.fcw = False
    self.dt = dt

    self.a_desired = init_a
    self.v_desired_filter = FirstOrderFilter(init_v, 2.0, self.dt)
    self.v_model_error = 0.0

    self.v_desired_trajectory = np.zeros(CONTROL_N)
    self.a_desired_trajectory = np.zeros(CONTROL_N)
    self.j_desired_trajectory = np.zeros(CONTROL_N)
    self.solverExecutionTime = 0.0
    self.params = Params()
    self.param_read_counter = 0
    self.read_param()

    self.cruise_source = 'cruise'
    self.vision_turn_controller = VisionTurnController(CP)
    self.speed_limit_controller = SpeedLimitController(CP)
    self.events = Events()
    self.turn_speed_controller = TurnSpeedController()
    self.dynamic_experimental_controller = DynamicExperimentalController()
    self.accel_controller = AccelController()

  def read_param(self):
    try:
      self.dynamic_experimental_controller.set_enabled(self.params.get_bool("DynamicExperimentalControl"))
    except AttributeError:
      self.dynamic_experimental_controller = DynamicExperimentalController()
      self.accel_controller = AccelController()

  @staticmethod
  def parse_model(model_msg, model_error):
    if (len(model_msg.position.x) == ModelConstants.IDX_N and
       len(model_msg.velocity.x) == ModelConstants.IDX_N and
       len(model_msg.acceleration.x) == ModelConstants.IDX_N):
      x = np.interp(T_IDXS_MPC, ModelConstants.T_IDXS, model_msg.position.x) - model_error * T_IDXS_MPC
      v = np.interp(T_IDXS_MPC, ModelConstants.T_IDXS, model_msg.velocity.x) - model_error
      a = np.interp(T_IDXS_MPC, ModelConstants.T_IDXS, model_msg.acceleration.x)
      j = np.zeros(len(T_IDXS_MPC))
    else:
      x = np.zeros(len(T_IDXS_MPC))
      v = np.zeros(len(T_IDXS_MPC))
      a = np.zeros(len(T_IDXS_MPC))
      j = np.zeros(len(T_IDXS_MPC))
    return x, v, a, j

  def update(self, sm):
    if self.param_read_counter % 50 == 0:
      self.read_param()
    self.param_read_counter += 1
    if self.dynamic_experimental_controller.is_enabled() and sm['controlsState'].experimentalMode:
      self.mpc.mode = self.dynamic_experimental_controller.get_mpc_mode(self.CP.radarUnavailable, sm['carState'], sm['radarState'].leadOne, sm['modelV2'], sm['controlsState'], sm['navInstruction'].maneuverDistance)
    else:
      self.mpc.mode = 'blended' if sm['controlsState'].experimentalMode else 'acc'

    v_ego = sm['carState'].vEgo
    v_cruise_kph = min(sm['controlsState'].vCruise, V_CRUISE_MAX)
    v_cruise = v_cruise_kph * CV.KPH_TO_MS

    long_control_off = sm['controlsState'].longControlState == LongCtrlState.off
    force_slow_decel = sm['controlsState'].forceDecel

    # Reset current state when not engaged, or user is controlling the speed
    reset_state = long_control_off if self.CP.openpilotLongitudinalControl else not sm['carControl'].hudControl.speedVisible

    # No change cost when user is controlling the speed, or when standstill
    prev_accel_constraint = not (reset_state or sm['carState'].standstill)

    if self.mpc.mode == 'acc':
      accel_limits = [A_CRUISE_MIN, get_max_accel(v_ego)]
      accel_limits_turns = limit_accel_in_turns(v_ego, sm['carState'].steeringAngleDeg, accel_limits, self.CP)
    else:
      accel_limits = [ACCEL_MIN, ACCEL_MAX]
      accel_limits_turns = [ACCEL_MIN, ACCEL_MAX]

    # override accel using Accel Controller
    if self.accel_controller.is_enabled(accel_personality=sm['controlsStateSP'].accelPersonality):
      # get min, max from accel controller
      min_limit, max_limit = self.accel_controller.get_accel_limits(v_ego, accel_limits)
      if self.mpc.mode == 'acc':
        # VOACC car, just give it max min (-1.2) so I can brake harder
        accel_limits = [A_CRUISE_MIN, max_limit] if self.CP.radarUnavailable else [min_limit, max_limit]
        # recalculate limit turn according to the new min, max
        accel_limits_turns = limit_accel_in_turns(v_ego, sm['carState'].steeringAngleDeg, accel_limits, self.CP)
      else:
        # blended, just give it max min (-3.5) and max from accel controller
        accel_limits = [ACCEL_MIN, ACCEL_MAX]
        accel_limits_turns = [ACCEL_MIN, ACCEL_MAX]

    if reset_state:
      self.v_desired_filter.x = v_ego
      # Clip aEgo to cruise limits to prevent large accelerations when becoming active
      self.a_desired = clip(sm['carState'].aEgo, accel_limits[0], accel_limits[1])

    # Prevent divergence, smooth in current v_ego
    self.v_desired_filter.x = max(0.0, self.v_desired_filter.update(v_ego))
    # Compute model v_ego error
    self.v_model_error = get_speed_error(sm['modelV2'], v_ego)

    if force_slow_decel:
      v_cruise = 0.0

    # Get active solutions for custom long mpc.
    v_cruise = self.cruise_solutions(
      not reset_state and (self.CP.openpilotLongitudinalControl or not self.CP.pcmCruiseSpeed),
      self.v_desired_filter.x, self.a_desired, v_cruise, sm)

    # clip limits, cannot init MPC outside of bounds
    accel_limits_turns[0] = min(accel_limits_turns[0], self.a_desired + 0.05)
    accel_limits_turns[1] = max(accel_limits_turns[1], self.a_desired - 0.05)

    self.mpc.set_weights(prev_accel_constraint, personality=sm['controlsStateSP'].personality)
    self.mpc.set_accel_limits(accel_limits_turns[0], accel_limits_turns[1])
    self.mpc.set_cur_state(self.v_desired_filter.x, self.a_desired)
    x, v, a, j = self.parse_model(sm['modelV2'], self.v_model_error)
    self.mpc.update(sm['radarState'], v_cruise, x, v, a, j, personality=sm['controlsStateSP'].personality, dynamic_personality=sm['controlsStateSP'].dynamicPersonality)

    self.v_desired_trajectory = np.interp(CONTROL_N_T_IDX, T_IDXS_MPC, self.mpc.v_solution)
    self.a_desired_trajectory = np.interp(CONTROL_N_T_IDX, T_IDXS_MPC, self.mpc.a_solution)
    self.j_desired_trajectory = np.interp(CONTROL_N_T_IDX, T_IDXS_MPC[:-1], self.mpc.j_solution)

    # TODO counter is only needed because radar is glitchy, remove once radar is gone
    self.fcw = self.mpc.crash_cnt > 2 and not sm['carState'].standstill
    if self.fcw:
      cloudlog.info("FCW triggered")

    # Interpolate 0.05 seconds and save as starting point for next iteration
    a_prev = self.a_desired
    self.a_desired = float(interp(self.dt, CONTROL_N_T_IDX, self.a_desired_trajectory))
    self.v_desired_filter.x = self.v_desired_filter.x + self.dt * (self.a_desired + a_prev) / 2.0

    self.e2e_events(sm)

  def publish(self, sm, pm):
    plan_send = messaging.new_message('longitudinalPlan')

    plan_send.valid = sm.all_checks(service_list=['carState', 'controlsState'])

    longitudinalPlan = plan_send.longitudinalPlan
    longitudinalPlan.modelMonoTime = sm.logMonoTime['modelV2']
    longitudinalPlan.processingDelay = (plan_send.logMonoTime / 1e9) - sm.logMonoTime['modelV2']
    longitudinalPlan.solverExecutionTime = self.mpc.solve_time

    longitudinalPlan.speeds = self.v_desired_trajectory.tolist()
    longitudinalPlan.accels = self.a_desired_trajectory.tolist()
    longitudinalPlan.jerks = self.j_desired_trajectory.tolist()

    longitudinalPlan.hasLead = sm['radarState'].leadOne.status
    longitudinalPlan.longitudinalPlanSource = self.mpc.source
    longitudinalPlan.fcw = self.fcw

    a_target, should_stop = get_accel_from_plan(self.CP, longitudinalPlan.speeds, longitudinalPlan.accels)
    longitudinalPlan.aTarget = a_target
    longitudinalPlan.shouldStop = should_stop
    longitudinalPlan.allowBrake = True
    longitudinalPlan.allowThrottle = True

    pm.send('longitudinalPlan', plan_send)

    plan_sp_send = messaging.new_message('longitudinalPlanSP')

    plan_sp_send.valid = sm.all_checks(service_list=['carState', 'controlsState'])

    longitudinalPlanSP = plan_sp_send.longitudinalPlanSP

    longitudinalPlanSP.longitudinalPlanSource = self.mpc.source if self.mpc.source != 'cruise' else self.cruise_source

    longitudinalPlanSP.e2eX = self.mpc.e2e_x.tolist()

    longitudinalPlanSP.visionTurnControllerState = self.vision_turn_controller.state
    longitudinalPlanSP.visionTurnSpeed = float(self.vision_turn_controller.v_target)
    longitudinalPlanSP.visionCurrentLatAcc = float(self.vision_turn_controller.current_lat_acc)
    longitudinalPlanSP.visionMaxPredLatAcc = float(self.vision_turn_controller.max_pred_lat_acc)

    longitudinalPlanSP.speedLimitControlState = self.speed_limit_controller.state
    longitudinalPlanSP.speedLimit = float(self.speed_limit_controller.speed_limit)
    longitudinalPlanSP.speedLimitOffset = float(self.speed_limit_controller.speed_limit_offset)
    longitudinalPlanSP.distToSpeedLimit = float(self.speed_limit_controller.distance)
    longitudinalPlanSP.isMapSpeedLimit = bool(self.speed_limit_controller.source not in (Source.none, Source.nav))
    longitudinalPlanSP.events = self.events.to_msg()

    longitudinalPlanSP.turnSpeedControlState = self.turn_speed_controller.state
    longitudinalPlanSP.turnSpeed = float(self.turn_speed_controller.v_target)

    longitudinalPlanSP.e2eBlended = self.mpc.mode

    pm.send('longitudinalPlanSP', plan_sp_send)

  def cruise_solutions(self, enabled, v_ego, a_ego, v_cruise, sm):
    # Update controllers
    self.vision_turn_controller.update(enabled, v_ego, v_cruise, sm)
    self.events = Events()
    self.speed_limit_controller.update(enabled, v_ego, a_ego, sm, v_cruise, self.events)
    self.turn_speed_controller.update(enabled, v_ego, sm, v_cruise)

    v_tsc_target = self.vision_turn_controller.v_target if self.vision_turn_controller.is_active else 255
    slc_target = self.speed_limit_controller.speed_limit_offseted if self.speed_limit_controller.is_active else 255
    m_tsc_target = self.turn_speed_controller.v_target if self.turn_speed_controller.is_active else 255

    # Pick solution with the lowest velocity target.
    v_solutions = min(v_cruise, v_tsc_target, slc_target, m_tsc_target)

    return v_solutions

  def e2e_events(self, sm):
    e2e_long_status = sm['e2eLongStateSP'].status

    if e2e_long_status in (1, 2):
      self.events.add(EventName.e2eLongStart)
