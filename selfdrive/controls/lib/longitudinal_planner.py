#!/usr/bin/env python3
import math
import numpy as np
from openpilot.common.params import Params
import cereal.messaging as messaging
from opendbc.car.interfaces import ACCEL_MIN, ACCEL_MAX
from openpilot.common.conversions import Conversions as CV
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.realtime import DT_MDL

from openpilot.common.params import Params, UnknownKeyName
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.selfdrive.controls.lib.longcontrol import LongCtrlState
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import LongitudinalMpc
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import T_IDXS as T_IDXS_MPC
from openpilot.selfdrive.controls.lib.drive_helpers import CONTROL_N, get_speed_error, get_accel_from_plan
from openpilot.selfdrive.car.cruise import V_CRUISE_MAX, V_CRUISE_UNSET
from openpilot.common.swaglog import cloudlog

from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlannerSP

# Dynamic Acceleration Boost helper
# DAB and ALC imports
from openpilot.sunnypilot.selfdrive.controls.lib.dab.dab import (
  DynamicAccelerationBoost,
  LEAD_HEADWAY_TIME,
  LEAD_DISTANCE_MIN,
  CurvatureData,
  DabInputs,
  DabOutputs,
  LeadData,
)
from openpilot.sunnypilot.selfdrive.controls.lib.auto_lane_change import AutoLaneChangeController, AutoLaneChangeMode

# --- Turn-signal acceleration assist ---------------------------------------
SIGNAL_NUDGE_ACCEL = 0.3     # extra m/s^2 when signal on
SIGNAL_NUDGE_DURATION = 1.0  # duration in seconds

LON_MPC_STEP = 0.2  # first step is 0.2s
A_CRUISE_MAX_VALS = [1.6, 1.2, 0.8, 0.6]
A_CRUISE_MAX_BP = [0., 10.0, 25., 40.]
CONTROL_N_T_IDX = ModelConstants.T_IDXS[:CONTROL_N]
ALLOW_THROTTLE_THRESHOLD = 0.5
MIN_ALLOW_THROTTLE_SPEED = 2.5

# User-toggle parameter stored in Params for enabling Dynamic-τ helper.
DYNAMIC_HELPER_PARAM = "DynamicAcceleration"

# Above this speed, ignore E2E slowdowns when no radar lead is detected to
# prevent phantom braking on clear highway
PHANTOM_BRAKE_SPEED = 22.0  # m/s (~50 mph)
# Maximum difference between MPC and E2E target decel to still treat as
# phantom braking when no radar lead is present.
PHANTOM_BRAKE_THRESHOLD = 0.3  # m/s^2
PHANTOM_BRAKE_TIME = 0.5  # s duration before applying mild model braking

# Lookup table for turns
_A_TOTAL_MAX_V = [1.7, 3.2]
_A_TOTAL_MAX_BP = [20., 40.]

# Accel clip smoothing: speed breakpoints (m/s) and smoothing per cycle (m/s^2)
ACCEL_CLIP_SMOOTH_BP = [0.0, 20.0, 40.0]
ACCEL_CLIP_SMOOTH_VALS = [0.3, 0.1, 0.05]

# Maximum change in deceleration allowed per cycle [m/s^2].
DECEL_RATE_LIMIT = 0.3


def get_max_accel(v_ego):
  return np.interp(v_ego, A_CRUISE_MAX_BP, A_CRUISE_MAX_VALS)

def get_coast_accel(pitch):
  return np.sin(pitch) * -5.65 - 0.3  # fitted from data using xx/projects/allow_throttle/compute_coast_accel.py


def limit_accel_in_turns(v_ego, angle_steers, a_target, CP):
  """
  This function returns a limited long acceleration allowed, depending on the existing lateral acceleration
  this should avoid accelerating when losing the target in turns
  """
  # FIXME: This function to calculate lateral accel is incorrect and should use the VehicleModel
  # The lookup table for turns should also be updated if we do this
  a_total_max = np.interp(v_ego, _A_TOTAL_MAX_BP, _A_TOTAL_MAX_V)
  a_y = v_ego ** 2 * angle_steers * CV.DEG_TO_RAD / (CP.steerRatio * CP.wheelbase)
  a_x_allowed = math.sqrt(max(a_total_max ** 2 - a_y ** 2, 0.))

  return [a_target[0], min(a_target[1], a_x_allowed)]


class LongitudinalPlanner(LongitudinalPlannerSP):
  def __init__(self, CP, init_v=0.0, init_a=0.0, dt=DT_MDL):
    self.CP = CP
    self.mpc = LongitudinalMpc(dt=dt)
    self.mpc.mode = 'acc'
    LongitudinalPlannerSP.__init__(self, self.CP, self.mpc)
    self.fcw = False
    self.dt = dt
    self.allow_throttle = True

    # Params interface for user toggle
    self._params = Params()

    self.a_desired = init_a
    self.v_desired_filter = FirstOrderFilter(init_v, 2.0, self.dt)
    self.prev_accel_clip = [ACCEL_MIN, ACCEL_MAX]
    self.v_model_error = 0.0
    self.output_a_target = 0.0
    self.output_should_stop = False

    # Debug / helper state
    self.helper_clear_road = 0.0
    self.helper_accel_boost = 0.0
    self.helper_weight = 0.0
    self.helper_curviness = 0.0
    self.helper_lead_car_gate = 0.0
    self.helper_tts_gate = 0.0
    self.helper_curv_gate = 0.0
    self.helper_phantom_brake_gate = 0.0
    self.helper_slow_radar_gate = 0.0
    self.helper_helper_accel = 0.0
    self._helper_a_lpf = 0.0  # low-pass filtered helper accel command
    self._clear_road_lpf = 0.0  # smoothed clear-road metric

    # Dynamic acceleration boost helper instance
    self._dyn_helper = DynamicAccelerationBoost()
    self._phantom_timer = 0.0
    # Auto lane change controller (55 mph+ auto-overtake)
    self._auto_lc = AutoLaneChangeController()


    self.v_desired_trajectory = np.zeros(CONTROL_N)
    self.a_desired_trajectory = np.zeros(CONTROL_N)
    self.j_desired_trajectory = np.zeros(CONTROL_N)
    self.solverExecutionTime = 0.0

    self.params = Params()
    self.param_read_counter = 0
    self.read_param()

    # turn-signal nudge state
    self.signal_nudge_timer = SIGNAL_NUDGE_DURATION
    self.prev_blink = False

    # Track previous accel target for decel rate limiting
    self.prev_output_a_target = init_a

    self.dynamic_personality = False


  def read_param(self):
    try:
      self.dynamic_personality = self.params.get_bool("DynamicPersonality")
    except AttributeError:
      pass


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
    if len(model_msg.meta.disengagePredictions.gasPressProbs) > 1:
      throttle_prob = model_msg.meta.disengagePredictions.gasPressProbs[1]
    else:
      throttle_prob = 1.0
    return x, v, a, j, throttle_prob

  def update(self, sm):
    self.mode = 'blended' if sm['selfdriveState'].experimentalMode else 'acc'
    LongitudinalPlannerSP.update(self, sm)
    if dec_mpc_mode := self.get_mpc_mode():
      self.mode = dec_mpc_mode

    if len(sm['carControl'].orientationNED) == 3:
      accel_coast = get_coast_accel(sm['carControl'].orientationNED[1])
    else:
      accel_coast = ACCEL_MAX

    v_ego = sm['carState'].vEgo
    v_cruise_kph = min(sm['carState'].vCruise, V_CRUISE_MAX)
    v_cruise = v_cruise_kph * CV.KPH_TO_MS
    v_cruise_initialized = sm['carState'].vCruise != V_CRUISE_UNSET

    long_control_off = sm['controlsState'].longControlState == LongCtrlState.off
    force_slow_decel = sm['controlsState'].forceDecel

    # Reset current state when not engaged, or user is controlling the speed
    reset_state = long_control_off if self.CP.openpilotLongitudinalControl else not sm['selfdriveState'].enabled
    # PCM cruise speed may be updated a few cycles later, check if initialized
    reset_state = reset_state or not v_cruise_initialized

    # No change cost when user is controlling the speed, or when standstill
    prev_accel_constraint = not (reset_state or sm['carState'].standstill)

    if self.mode == 'acc':
      accel_clip = [ACCEL_MIN, get_max_accel(v_ego)]
      steer_angle_without_offset = sm['carState'].steeringAngleDeg - sm['liveParameters'].angleOffsetDeg
      accel_clip = limit_accel_in_turns(v_ego, steer_angle_without_offset, accel_clip, self.CP)
    else:
      accel_clip = [ACCEL_MIN, ACCEL_MAX]

    if reset_state:
      self.v_desired_filter.x = v_ego
      # Clip aEgo to cruise limits to prevent large accelerations when becoming active
      self.a_desired = np.clip(sm['carState'].aEgo, accel_clip[0], accel_clip[1])

    # Prevent divergence, smooth in current v_ego
    self.v_desired_filter.x = max(0.0, self.v_desired_filter.update(v_ego))
    # Compute model v_ego error
    self.v_model_error = get_speed_error(sm['modelV2'], v_ego)
    x, v, a, j, throttle_prob = self.parse_model(sm['modelV2'], self.v_model_error)
    # Don't clip at low speeds since throttle_prob doesn't account for creep
    self.allow_throttle = throttle_prob > ALLOW_THROTTLE_THRESHOLD or v_ego <= MIN_ALLOW_THROTTLE_SPEED

    if not self.allow_throttle:
      clipped_accel_coast = max(accel_coast, accel_clip[0])
      clipped_accel_coast_interp = np.interp(v_ego, [MIN_ALLOW_THROTTLE_SPEED, MIN_ALLOW_THROTTLE_SPEED*2], [accel_clip[1], clipped_accel_coast])
      accel_clip[1] = min(accel_clip[1], clipped_accel_coast_interp)

    if force_slow_decel:
      v_cruise = 0.0

    self.mpc.set_weights(prev_accel_constraint, personality=sm['selfdriveState'].personality)
    self.mpc.set_cur_state(self.v_desired_filter.x, self.a_desired)
    self.mpc.update(sm['radarState'], v_cruise, x, v, a, j, personality=sm['selfdriveState'].personality, dynamic_personality = self.dynamic_personality)

    self.v_desired_trajectory = np.interp(CONTROL_N_T_IDX, T_IDXS_MPC, self.mpc.v_solution)
    self.a_desired_trajectory = np.interp(CONTROL_N_T_IDX, T_IDXS_MPC, self.mpc.a_solution)
    self.j_desired_trajectory = np.interp(CONTROL_N_T_IDX, T_IDXS_MPC[:-1], self.mpc.j_solution)

    # TODO counter is only needed because radar is glitchy, remove once radar is gone
    self.fcw = self.mpc.crash_cnt > 2 and not sm['carState'].standstill
    if self.fcw:
      cloudlog.info("FCW triggered")

    # Interpolate 0.05 seconds and save as starting point for next iteration
    a_prev = self.a_desired
    self.a_desired = float(np.interp(self.dt, CONTROL_N_T_IDX, self.a_desired_trajectory))
    self.v_desired_filter.x = self.v_desired_filter.x + self.dt * (self.a_desired + a_prev) / 2.0

    action_t =  self.CP.longitudinalActuatorDelay + DT_MDL
    output_a_target_mpc, output_should_stop_mpc = get_accel_from_plan(self.v_desired_trajectory, self.a_desired_trajectory, CONTROL_N_T_IDX,
                                                                        action_t=action_t, vEgoStopping=self.CP.vEgoStopping)
    output_a_target_e2e = sm['modelV2'].action.desiredAcceleration
    output_should_stop_e2e = sm['modelV2'].action.shouldStop


    # ---------------------------------------------------------------------
    # Select base acceleration target from ACC (MPC) and/or E2E planner
    # ---------------------------------------------------------------------

    if self.mode == 'acc':
      output_a_target = output_a_target_mpc
      self.output_should_stop = output_should_stop_mpc
    else:
      output_a_target = min(output_a_target_mpc, output_a_target_e2e)
      self.output_should_stop = output_should_stop_e2e or output_should_stop_mpc

    # ---------------------------------------------------------------------
    # Dynamic Acceleration Boost (DAB)
    # ---------------------------------------------------------------------
    # Optionally blend in a dynamic helper acceleration when the road ahead
    # is clear.  This behaviour can be toggled at runtime via the persistent
    # Param stored under *DYNAMIC_HELPER_PARAM* ("DynamicAcceleration").
    #
    # The helper returns a convex combination between the planner target and
    # an aggressive helper acceleration so we simply replace *output_a_target*
    # with the final blended value.  All safety clipping and smoothing below
    # remains unchanged.

    # Feature is enabled by default. Users can disable it by setting the
    # persisted param *DynamicAcceleration* to "0" (false).
    dyn_helper_enabled = True
    try:
      # get_bool() returns False if the key is present and explicitly set to
      # "0", otherwise True when "1" or when the key doesn't exist. This makes
      # the helper opt-out rather than opt-in which matches historical SP
      # behaviour.
      dyn_helper_enabled = self._params.get_bool(DYNAMIC_HELPER_PARAM) if self._params.get(DYNAMIC_HELPER_PARAM, encoding="utf-8") is not None else True
    except Exception:
      # Params not available in some unit tests – keep default.
      pass

    try:
      mdl = sm['modelV2'].leadsV3[0]
      model_lead = LeadData(
        status=True,
        dRel=float(mdl.x[0]),
        vRel=float(mdl.v[0] - v_ego),
        vLead=float(mdl.v[0]),
      )
    except Exception:
      model_lead = LeadData(False)

    try:
      curvature = CurvatureData(
        desired=float(sm['modelV2'].action.desiredCurvature),
        x=list(sm['modelV2'].position.x),
        y=list(sm['modelV2'].position.y),
        yaw_rate=list(sm['modelV2'].orientationRate.z),
        speeds=list(sm['modelV2'].velocity.x),
      )
    except Exception:
      curvature = CurvatureData(0.0, [], [], [], [])

    inputs = DabInputs(
      v_ego=v_ego,
      a_ego=sm['carState'].aEgo,
      v_set=v_cruise if v_cruise_initialized else self.v_desired_filter.x,
      output_a_target=output_a_target,
      output_a_mpc=output_a_target_mpc,
      output_a_e2e=output_a_target_e2e,
      v_desired=self.v_desired_trajectory,
      allow_throttle=self.allow_throttle,
      radar_lead=LeadData(
        status=bool(sm['radarState'].leadOne.status),
        dRel=float(sm['radarState'].leadOne.dRel),
        vRel=float(sm['radarState'].leadOne.vRel),
        vLead=float(sm['radarState'].leadOne.vLead),
      ),
      model_lead=model_lead,
      curvature=curvature,
      personality=sm['selfdriveState'].personality,
    )

    if dyn_helper_enabled:
      out = self._compute_dynamic_helper(sm, inputs)

      # Expose debug values (used by on-road UI or loggers)
      self.helper_clear_road = out.clear_road
      self.helper_accel_boost = out.a_helper
      self.helper_weight = out.weight
      self.helper_lead_car_gate = out.lead_car_gate
      self.helper_tts_gate = out.tts_gate
      self.helper_curv_gate = out.curv_gate
      self.helper_phantom_brake_gate = out.phantom_brake_gate
      self.helper_slow_radar_gate = out.slow_radar_gate
      self.helper_helper_accel = out.a_final
      try:
        self.helper_curviness = self._dyn_helper.curviness
      except Exception:
        self.helper_curviness = 0.0

      # Replace planner target with helper-blended value
      output_a_target = out.a_final
    else:
      output_a_target = self._dyn_helper._phantom_brake_gate(inputs)

    # -------------------------------------------------------------------
    # Turn-signal acceleration nudge
    # -------------------------------------------------------------------
    blink = sm['carState'].leftBlinker != sm['carState'].rightBlinker
    if blink and not self.prev_blink:
      self.signal_nudge_timer = 0.0

    if blink:
      self.signal_nudge_timer = min(self.signal_nudge_timer + self.dt, SIGNAL_NUDGE_DURATION)
    else:
      self.signal_nudge_timer = SIGNAL_NUDGE_DURATION

    self.prev_blink = blink

    nudge_active = blink and self.signal_nudge_timer <= SIGNAL_NUDGE_DURATION
    lead = sm['radarState'].leadOne
    headway = lead.dRel / max(v_ego, 0.1) if lead.status else float('inf')
    lead_close = bool(lead.status) and (headway < LEAD_HEADWAY_TIME or lead.dRel < LEAD_DISTANCE_MIN)

    if nudge_active and not lead_close and output_a_target_mpc >= 0.0 and not self.output_should_stop:
      output_a_target += SIGNAL_NUDGE_ACCEL

    # Limit how quickly decel can increase to smooth phantom braking
    if output_a_target < self.prev_output_a_target:
      output_a_target = max(output_a_target, self.prev_output_a_target - DECEL_RATE_LIMIT)
    self.prev_output_a_target = output_a_target

    # Compute smoothing value based on v_ego and ACCEL_CLIP_SMOOTH_BP/VALS
    smoothing = float(np.interp(v_ego, ACCEL_CLIP_SMOOTH_BP, ACCEL_CLIP_SMOOTH_VALS))

    for idx in range(2):
      accel_clip[idx] = np.clip(
        accel_clip[idx],
        self.prev_accel_clip[idx] - smoothing,
        self.prev_accel_clip[idx] + smoothing
      )
    self.output_a_target = np.clip(output_a_target, accel_clip[0], accel_clip[1])
    self.prev_accel_clip = accel_clip

  # ---------------------------------------------------------------------------
  # Dynamic τ acceleration helper implementation
  # ---------------------------------------------------------------------------

  def _compute_dynamic_helper(self, sm, inputs: DabInputs) -> DabOutputs:
    """Return dynamic helper result."""
    print(f"[LP] _compute_dynamic_helper called. v_ego: {inputs.v_ego:.2f}, output_a_target: {inputs.output_a_target:.2f}")

    # Delegates implementation to the standalone DynamicAccelerationBoost
    # helper maintained in openpilot.sunnypilot.selfdrive.controls.lib.dab.
    out = self._dyn_helper.compute(sm, inputs)
    print(f"[LP] _compute_dynamic_helper output. a_final: {out.a_final:.2f}, clear_road: {out.clear_road:.2f}, weight: {out.weight:.2f}")
    return out


  def publish(self, sm, pm):
    plan_send = messaging.new_message('longitudinalPlan')
    print(f"[LP] publish called. output_a_target: {self.output_a_target:.2f}, should_stop: {self.output_should_stop}")

    plan_send.valid = sm.all_checks(service_list=['carState', 'controlsState', 'selfdriveState'])

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

    longitudinalPlan.aTarget = float(self.output_a_target)
    longitudinalPlan.shouldStop = bool(self.output_should_stop)
    longitudinalPlan.allowBrake = True
    longitudinalPlan.allowThrottle = bool(self.allow_throttle)

    pm.send('longitudinalPlan', plan_send)

    self.publish_longitudinal_plan_sp(sm, pm)
