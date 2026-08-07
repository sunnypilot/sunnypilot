"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from openpilot.cereal import messaging, custom
from opendbc.car import structs
from openpilot.common.constants import CV
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.car.cruise import V_CRUISE_MAX, V_CRUISE_UNSET
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.accel_controller import AccelController, AccelControllerState
from openpilot.sunnypilot.selfdrive.controls.lib.dec.dec import DynamicExperimentalController
from openpilot.sunnypilot.selfdrive.controls.lib.e2e_alerts_helper import E2EAlertsHelper
from openpilot.sunnypilot.selfdrive.controls.lib.smart_cruise_control.smart_cruise_control import SmartCruiseControl
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.speed_limit_assist import SpeedLimitAssist
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.speed_limit_resolver import SpeedLimitResolver
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP
from openpilot.sunnypilot.models.helpers import get_active_bundle

DecState = custom.LongitudinalPlanSP.DynamicExperimentalControl.DynamicExperimentalControlState
LongitudinalPlanSource = custom.LongitudinalPlanSP.LongitudinalPlanSource


class LongitudinalPlannerSP:
  def __init__(self, CP: structs.CarParams, CP_SP: structs.CarParamsSP, mpc, dt: float = DT_MDL):
    self.mpc = mpc
    self.accel_controller = AccelController(CP, dt=dt)
    self.events_sp = EventsSP()
    self.dec = DynamicExperimentalController(CP, mpc)
    self.scc = SmartCruiseControl()
    self.resolver = SpeedLimitResolver()
    self.sla = SpeedLimitAssist(CP, CP_SP)
    self.generation = int(model_bundle.generation) if (model_bundle := get_active_bundle()) else None
    self.source = LongitudinalPlanSource.cruise
    self.e2e_alerts_helper = E2EAlertsHelper()
    self._radar_log_mono_time = None
    self._radar_fresh_this_cycle = True

    self.output_v_target = 0.
    self.output_a_target = 0.

  def is_e2e(self, sm: messaging.SubMaster) -> bool:
    experimental_mode = sm['selfdriveState'].experimentalMode
    if not self.dec.active():
      return experimental_mode

    return experimental_mode and self.dec.mode() == "blended"

  def update_accel_controller(self, sm: messaging.SubMaster, v_cruise: float, prev_accel_constraint: bool,
                              stock_accel_max: float, reset_state: bool) -> tuple[bool, float]:
    is_e2e = self.is_e2e(sm)
    force_decel = sm['controlsState'].forceDecel
    previous_mpc_failed = self.mpc.last_solution_status != 0

    self.accel_controller.update(
      sm['radarState'], base_speed=self.output_v_target, v_ego=sm['carState'].vEgo, a_ego=sm['carState'].aEgo,
      follow_personality=sm['selfdriveState'].personality, acc_selected=not is_e2e,
      engaged=not reset_state and not force_decel, cruise_initialized=sm['carState'].vCruise != V_CRUISE_UNSET,
      stock_accel_max=stock_accel_max if self.allow_throttle else 0.0, previous_should_stop=self.output_should_stop,
      radar_fresh=self._radar_fresh_this_cycle, previous_mpc_source=self.mpc.source, planner_speed=self.v_desired_filter.x,
      planner_accel=self.a_desired,
    )
    controller = self.accel_controller
    actuating = controller.is_active and not is_e2e and not force_decel and not previous_mpc_failed
    valid_lead_stop_hold = actuating and controller.state == AccelControllerState.stopHold and controller.selected_lead >= 0
    controller_v_cruise = v_cruise if valid_lead_stop_hold else min(v_cruise, controller.output_v_target) if actuating else v_cruise
    accel_max = controller.mpc_accel_max if actuating else None
    cruise_accel_max = controller.cruise_accel_max if actuating else None
    jerk_cost_multiplier = controller.get_jerk_cost_multiplier(
      actuating, prev_accel_constraint, v_cruise - controller_v_cruise, previous_mpc_failed,
    )
    self.mpc.set_accel_controller_params(accel_max, jerk_cost_multiplier, cruise_accel_max)
    return is_e2e, controller_v_cruise

  def update_should_stop(self, should_stop: bool) -> bool:
    return self.accel_controller.update_should_stop(should_stop)

  def update_targets(self, sm: messaging.SubMaster, v_ego: float, a_ego: float, v_cruise: float) -> tuple[float, float]:
    CS = sm['carState']
    v_cruise_cluster_kph = min(CS.vCruiseCluster, V_CRUISE_MAX)
    v_cruise_cluster = v_cruise_cluster_kph * CV.KPH_TO_MS

    long_enabled = sm['carControl'].enabled
    long_override = sm['carControl'].cruiseControl.override

    # Smart Cruise Control
    self.scc.update(sm, long_enabled, long_override, v_ego, a_ego, v_cruise)

    # Speed Limit Resolver
    self.resolver.update(v_ego, sm)

    # Speed Limit Assist
    has_speed_limit = self.resolver.speed_limit_valid or self.resolver.speed_limit_last_valid
    self.sla.update(long_enabled, long_override, v_ego, a_ego, v_cruise_cluster, self.resolver.speed_limit,
                    self.resolver.speed_limit_final_last, has_speed_limit, self.resolver.distance, self.events_sp)

    targets = {
      LongitudinalPlanSource.cruise: (v_cruise, a_ego),
      LongitudinalPlanSource.sccVision: (self.scc.vision.output_v_target, self.scc.vision.output_a_target),
      LongitudinalPlanSource.sccMap: (self.scc.map.output_v_target, self.scc.map.output_a_target),
      LongitudinalPlanSource.speedLimitAssist: (self.sla.output_v_target, self.sla.output_a_target),
    }

    self.source = min(targets, key=lambda k: targets[k][0])
    self.output_v_target, self.output_a_target = targets[self.source]
    return self.output_v_target, self.output_a_target

  def _update_radar_freshness(self, sm: messaging.SubMaster) -> bool:
    radar_log_mono_time = sm.logMonoTime['radarState']
    radar_healthy = sm.valid['radarState'] and sm.alive['radarState']
    radar_advanced = self._radar_log_mono_time is None or radar_log_mono_time > self._radar_log_mono_time
    if radar_advanced:
      self._radar_log_mono_time = radar_log_mono_time
    return radar_healthy and radar_advanced

  def update(self, sm: messaging.SubMaster) -> None:
    self._radar_fresh_this_cycle = self._update_radar_freshness(sm)
    self.accel_controller.update_params()
    self.events_sp.clear()
    self.dec.update(sm, radar_fresh=self._radar_fresh_this_cycle, planner_accel=self.output_a_target)
    self.e2e_alerts_helper.update(sm, self.events_sp)

  def publish_longitudinal_plan_sp(self, sm: messaging.SubMaster, pm: messaging.PubMaster) -> None:
    plan_sp_send = messaging.new_message('longitudinalPlanSP')

    plan_sp_send.valid = sm.all_checks(service_list=['carState', 'controlsState'])

    longitudinalPlanSP = plan_sp_send.longitudinalPlanSP
    longitudinalPlanSP.longitudinalPlanSource = self.source
    longitudinalPlanSP.vTarget = float(self.output_v_target)
    longitudinalPlanSP.aTarget = float(self.output_a_target)
    longitudinalPlanSP.events = self.events_sp.to_msg()

    # Dynamic Experimental Control
    dec = longitudinalPlanSP.dec
    dec.state = DecState.blended if self.dec.mode() == 'blended' else DecState.acc
    dec.enabled = self.dec.enabled()
    dec.active = self.dec.active()

    accelController = longitudinalPlanSP.accelController
    accelController.enabled = self.accel_controller.is_enabled
    accelController.active = self.accel_controller.is_active
    accelController.profile = self.accel_controller.profile
    accelController.state = self.accel_controller.state

    # Smart Cruise Control
    smartCruiseControl = longitudinalPlanSP.smartCruiseControl
    # Vision Control
    sccVision = smartCruiseControl.vision
    sccVision.state = self.scc.vision.state
    sccVision.vTarget = float(self.scc.vision.output_v_target)
    sccVision.aTarget = float(self.scc.vision.output_a_target)
    sccVision.currentLateralAccel = float(self.scc.vision.current_lat_acc)
    sccVision.maxPredictedLateralAccel = float(self.scc.vision.max_pred_lat_acc)
    sccVision.enabled = self.scc.vision.is_enabled
    sccVision.active = self.scc.vision.is_active
    # Map Control
    sccMap = smartCruiseControl.map
    sccMap.state = self.scc.map.state
    sccMap.vTarget = float(self.scc.map.output_v_target)
    sccMap.aTarget = float(self.scc.map.output_a_target)
    sccMap.enabled = self.scc.map.is_enabled
    sccMap.active = self.scc.map.is_active

    # Speed Limit
    speedLimit = longitudinalPlanSP.speedLimit
    resolver = speedLimit.resolver
    resolver.speedLimit = float(self.resolver.speed_limit)
    resolver.speedLimitLast = float(self.resolver.speed_limit_last)
    resolver.speedLimitFinal = float(self.resolver.speed_limit_final)
    resolver.speedLimitFinalLast = float(self.resolver.speed_limit_final_last)
    resolver.speedLimitValid = self.resolver.speed_limit_valid
    resolver.speedLimitLastValid = self.resolver.speed_limit_last_valid
    resolver.speedLimitOffset = float(self.resolver.speed_limit_offset)
    resolver.distToSpeedLimit = float(self.resolver.distance)
    resolver.source = self.resolver.source
    assist = speedLimit.assist
    assist.state = self.sla.state
    assist.enabled = self.sla.is_enabled
    assist.active = self.sla.is_active
    assist.vTarget = float(self.sla.output_v_target)
    assist.aTarget = float(self.sla.output_a_target)

    # E2E Alerts
    e2eAlerts = longitudinalPlanSP.e2eAlerts
    e2eAlerts.greenLightAlert = self.e2e_alerts_helper.green_light_alert
    e2eAlerts.leadDepartAlert = self.e2e_alerts_helper.lead_depart_alert

    pm.send('longitudinalPlanSP', plan_sp_send)
