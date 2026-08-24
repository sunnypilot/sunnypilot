"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import math

from openpilot.cereal import messaging, custom, log
from opendbc.car import structs
from openpilot.common.constants import CV
from openpilot.selfdrive.car.cruise import V_CRUISE_MAX
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.accel_controller import AccelController
from openpilot.sunnypilot.selfdrive.controls.lib.dec.dec import DynamicExperimentalController
from openpilot.sunnypilot.selfdrive.controls.lib.e2e_alerts_helper import E2EAlertsHelper
from openpilot.sunnypilot.selfdrive.controls.lib.smart_cruise_control.smart_cruise_control import SmartCruiseControl
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.speed_limit_assist import SpeedLimitAssist
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.speed_limit_resolver import SpeedLimitResolver
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP
from openpilot.sunnypilot.models.helpers import get_active_bundle

DecState = custom.LongitudinalPlanSP.DynamicExperimentalControl.DynamicExperimentalControlState
LongitudinalPlanSource = custom.LongitudinalPlanSP.LongitudinalPlanSource
MpcPlanSource = log.LongitudinalPlan.LongitudinalPlanSource

E2E_BRAKE_HOLD_ACCEL = -0.2  # m/s^2


class LongitudinalPlannerSP:
  def __init__(self, CP: structs.CarParams, CP_SP: structs.CarParamsSP, mpc):
    self.accel_controller = AccelController()
    self.accel_controller_active = False
    self.events_sp = EventsSP()
    self.dec = DynamicExperimentalController(CP, mpc)
    self.scc = SmartCruiseControl()
    self.resolver = SpeedLimitResolver()
    self.sla = SpeedLimitAssist(CP, CP_SP)
    self.generation = int(model_bundle.generation) if (model_bundle := get_active_bundle()) else None
    self.source = LongitudinalPlanSource.cruise
    self.e2e_alerts_helper = E2EAlertsHelper()
    self.a_cruise = 0.  # re-assigned by the subclass; declared here because get_max_accel_override clamps it

    self.output_v_target = 0.
    self.output_a_target = 0.

  def is_e2e(self, sm: messaging.SubMaster) -> bool:
    experimental_mode = sm['selfdriveState'].experimentalMode
    if not experimental_mode:
      return False

    if not self.dec.active() or self.dec.mode() == "blended":
      return True

    # hold a brake the model already owns rather than release it mid-brake; min() means this can only ever
    # add deceleration, and never one that was not already the selected source
    if self.mpc.source == MpcPlanSource.e2e and sm['modelV2'].action.desiredAcceleration < E2E_BRAKE_HOLD_ACCEL:
      return True

    return False

  def get_max_accel_override(self, v_ego: float, _v_target: float, e2e: bool) -> float | None:
    """Pure speed-scheduled authority. The arrival taper is the comfort law's job, not the ceiling's."""
    self.accel_controller_active = bool(self.accel_controller.is_enabled() and (e2e or self.allow_throttle))
    if not self.accel_controller_active:
      return None

    ceiling = self.accel_controller.get_max_accel(v_ego)

    # get_cruise_accel jerk-limits AFTER clipping to max_accel, so a carried value above the ceiling ratchets
    # the command back over it. upper side only: never make braking less negative
    if math.isfinite(self.a_cruise):
      self.a_cruise = min(self.a_cruise, ceiling)

    return ceiling

  def _has_valid_selected_lead(self, sm: messaging.SubMaster, source: MpcPlanSource) -> bool:
    radar_valid = sm.valid.get('radarState', False) and getattr(sm, 'alive', {}).get('radarState', False)
    return radar_valid and ((source == MpcPlanSource.lead0 and sm['radarState'].leadOne.present) or
                            (source == MpcPlanSource.lead1 and sm['radarState'].leadTwo.present))

  def arbitrate_cruise_candidate(self, sm: messaging.SubMaster, gated: float, ungated: float,
                                 mpc_accel: float, mpc_source: MpcPlanSource, *, allow_throttle: bool,
                                 e2e: bool, force_decel: bool) -> float:
    finite = all(math.isfinite(value) for value in (gated, ungated, mpc_accel))
    coast_gate_changed_source = gated < mpc_accel <= ungated
    if (finite and not allow_throttle and not e2e and not force_decel
        and self._has_valid_selected_lead(sm, mpc_source) and coast_gate_changed_source):
      return ungated

    return gated

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

  def update(self, sm: messaging.SubMaster) -> None:
    self.accel_controller.update()
    self.events_sp.clear()
    self.e2e_alerts_helper.update(sm, self.events_sp)

  def update_dec(self, sm: messaging.SubMaster) -> None:
    self.dec.update(sm)

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
    dec.decelIntent = float(self.dec.signals.decel_intent)
    dec.curveDetected = bool(self.dec.signals.curve_detected)
    dec.wantBlended = bool(self.dec.want_blended)
    dec.leadVeto = bool(self.dec.lead_veto)

    accel_controller = longitudinalPlanSP.accelController
    accel_controller.enabled = bool(self.accel_controller.is_enabled())
    accel_controller.active = bool(self.accel_controller_active)
    accel_controller.profile = int(self.accel_controller.profile)

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
