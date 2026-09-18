"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from openpilot.cereal import messaging, custom
from opendbc.car import structs
from openpilot.common.constants import CV
from openpilot.selfdrive.car.cruise import V_CRUISE_MAX
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import get_T_FOLLOW
from openpilot.sunnypilot.selfdrive.controls.lib.e2e_alerts_helper import E2EAlertsHelper
from openpilot.sunnypilot.selfdrive.controls.lib.smart_cruise_control.smart_cruise_control import SmartCruiseControl
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.speed_limit_assist import SpeedLimitAssist
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.speed_limit_resolver import SpeedLimitResolver
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP
from openpilot.sunnypilot.models.helpers import get_active_bundle

LongitudinalPlanSource = custom.LongitudinalPlanSP.LongitudinalPlanSource

SPEED_LIMIT_APPROACH_SHAPE = 1.5
# Coasting behind a lead becomes eligible just inside the personality's own
# steady-state gap, so a lead at normal following distance still qualifies.
LEAD_COAST_FOLLOW_FACTOR = 0.95


def lead_coast_min_distance(v_ego: float, personality) -> float:
  return max(6., LEAD_COAST_FOLLOW_FACTOR * get_T_FOLLOW(personality) * max(v_ego, 0.))


class SpeedLimitApproach:
  """Release once per target; speed noise must never re-arm the override."""
  def __init__(self):
    self.target = 0.
    self.released = False

  def update(self, active: bool, target: float, v_ego: float, release_gap: float, cancel: bool = False) -> bool:
    if not active or target <= 0.:
      self.target = 0.
      self.released = False
      return False
    if abs(target - self.target) > 0.1 * CV.KPH_TO_MS:
      self.target = target
      self.released = False
    self.released |= cancel or v_ego <= target + release_gap
    return not self.released


def speed_limit_no_brake_active(enabled: bool, lower_lookahead_active: bool, has_lead: bool) -> bool:
  return enabled and lower_lookahead_active and not has_lead


def limit_speed_limit_decel_target(a_target: float, speed_limit_source_active: bool, has_lead: bool, max_decel: float) -> float:
  if speed_limit_source_active and not has_lead:
    return max(a_target, max_decel)
  return a_target


def speed_limit_idle_active(v_ego: float, speed_limit_target: float, release_gap: float, mode: str) -> bool:
  return mode == "idle" and speed_limit_target > 0. and v_ego > speed_limit_target + release_gap


def no_lead_normal_decel_idle_active(mode: str, intentional_decel: bool, cruise_source_active: bool,
                                     a_target: float, min_idle_decel: float, has_lead: bool, should_stop: bool,
                                     lead_coast_allowed: bool = False) -> bool:
  return (mode == "idle" and intentional_decel and cruise_source_active and a_target <= min_idle_decel and
          (not has_lead or lead_coast_allowed) and not should_stop)


def speed_limit_current_limit_decel_needed(speed_limit_source_active: bool, lower_lookahead_active: bool,
                                           v_ego: float, speed_limit_target: float, overspeed_margin: float = 0.) -> bool:
  return speed_limit_source_active and not lower_lookahead_active and speed_limit_target > 0. and \
    v_ego > speed_limit_target + overspeed_margin


def speed_limit_approach_accel(v_ego: float, v_target: float, distance: float, lookahead_speed_factor: float,
                               accel_coast: float, min_accel: float, max_accel: float = 0.0) -> float:
  coast_accel = max(min(accel_coast, max_accel), min_accel)
  if v_target <= 0. or distance <= 0. or v_ego <= v_target:
    return coast_accel

  required_accel = (v_target ** 2 - v_ego ** 2) / max(2.0 * distance, 1.0)
  if required_accel >= coast_accel:
    return coast_accel
  if required_accel <= min_accel:
    return min_accel

  lookahead_distance = max(v_ego, v_target) * CV.MS_TO_KPH * lookahead_speed_factor
  progress = 1.0 - distance / max(lookahead_distance, distance, 1.0)
  urgency = max(min(progress, 1.0), 0.0) ** SPEED_LIMIT_APPROACH_SHAPE
  target_accel = min(required_accel, coast_accel + urgency * (min_accel - coast_accel))
  return max(min(target_accel, coast_accel), min_accel)


def speed_limit_no_brake_accel_target(v_ego: float, speed_limit_target: float, release_gap: float, no_brake_accel: float,
                                      mode: str = "fixed", distance: float = 0., lookahead_speed_factor: float = 0.,
                                      accel_coast: float | None = None, min_accel: float = -1.2) -> float:
  if speed_limit_target > 0. and v_ego <= speed_limit_target + release_gap:
    return 0.
  if mode == "idle":
    return 0.
  if mode == "dynamic":
    approach_accel = speed_limit_approach_accel(v_ego, speed_limit_target, distance, lookahead_speed_factor,
                                                accel_coast if accel_coast is not None else no_brake_accel, min_accel)
    return approach_accel
  return no_brake_accel


class LongitudinalPlannerSP:
  def __init__(self, CP: structs.CarParams, CP_SP: structs.CarParamsSP, mpc):
    self.events_sp = EventsSP()
    self.resolver = SpeedLimitResolver()
    self.scc = SmartCruiseControl()
    self.resolver = SpeedLimitResolver()
    self.sla = SpeedLimitAssist(CP, CP_SP)
    self.generation = int(model_bundle.generation) if (model_bundle := get_active_bundle()) else None
    self.source = LongitudinalPlanSource.cruise
    self.e2e_alerts_helper = E2EAlertsHelper()

    self.output_v_target = 0.
    self.output_a_target = 0.

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
    self.events_sp.clear()
    self.e2e_alerts_helper.update(sm, self.events_sp)

  def publish_longitudinal_plan_sp(self, sm: messaging.SubMaster, pm: messaging.PubMaster) -> None:
    plan_sp_send = messaging.new_message('longitudinalPlanSP')

    plan_sp_send.valid = sm.all_checks(service_list=['carState', 'controlsState'])

    longitudinalPlanSP = plan_sp_send.longitudinalPlanSP
    longitudinalPlanSP.longitudinalPlanSource = self.source
    longitudinalPlanSP.vTarget = float(self.output_v_target)
    longitudinalPlanSP.aTarget = float(self.output_a_target)
    longitudinalPlanSP.events = self.events_sp.to_msg()

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
    assist.longitudinalIdle = bool(getattr(self, "longitudinal_idle", False))

    # E2E Alerts
    e2eAlerts = longitudinalPlanSP.e2eAlerts
    e2eAlerts.greenLightAlert = self.e2e_alerts_helper.green_light_alert
    e2eAlerts.leadDepartAlert = self.e2e_alerts_helper.lead_depart_alert

    pm.send('longitudinalPlanSP', plan_sp_send)
