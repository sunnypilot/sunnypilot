"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import messaging, custom
from opendbc.car import structs
from openpilot.sunnypilot.selfdrive.controls.lib.dec.dec import DynamicExperimentalController
from openpilot.sunnypilot.selfdrive.controls.lib.e2e_alerts_helper import E2EAlertsHelper
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP
from openpilot.sunnypilot.models.helpers import get_active_bundle

from openpilot.sunnypilot.selfdrive.controls.lib.accel_personality.accel_controller import AccelPersonalityController
from openpilot.sunnypilot.selfdrive.controls.lib.dynamic_personality.dynamic_follow import FollowDistanceController
from opendbc.car.interfaces import ACCEL_MIN

DecState = custom.LongitudinalPlanSP.DynamicExperimentalControl.DynamicExperimentalControlState
LongitudinalPlanSource = custom.LongitudinalPlanSP.LongitudinalPlanSource


class LongitudinalPlannerSP:
  def __init__(self, CP: structs.CarParams, CP_SP: structs.CarParamsSP, mpc):
    self.events_sp = EventsSP()
    self.dec = DynamicExperimentalController(CP, mpc)
    self.accel_controller = AccelPersonalityController()
    self.dynamic_follow = FollowDistanceController()
    self.generation = int(model_bundle.generation) if (model_bundle := get_active_bundle()) else None
    self.source = LongitudinalPlanSource.cruise
    self.e2e_alerts_helper = E2EAlertsHelper()

    self.output_v_target = 0.0
    self.output_a_target = 0.0

  @property
  def mlsim(self) -> bool:
    # If we don't have a generation set, we assume it's default model. Which as of today are mlsim.
    return bool(self.generation is None or self.generation >= 11)

  def get_mpc_mode(self) -> str | None:
    if not self.dec.active():
      return None

    return self.dec.mode()

  def get_accel_clip(self, v_ego: float, mode: str) -> list[float] | None:
    if mode == 'acc' and self.accel_controller.is_enabled():
      return [ACCEL_MIN, self.accel_controller.get_max_accel(v_ego)]
    return None

  def get_cruise_min_accel(self, v_ego: float) -> float | None:
    if self.accel_controller.is_enabled():
      return self.accel_controller.get_min_accel(v_ego)
    return None

  def get_t_follow(self, v_ego: float) -> float | None:
    if self.dynamic_follow.is_enabled():
      return self.dynamic_follow.get_follow_distance_multiplier(v_ego)
    return None

  def update_targets(self, sm: messaging.SubMaster, v_ego: float, a_ego: float, v_cruise: float) -> tuple[float, float]:
    self.source = LongitudinalPlanSource.cruise
    self.output_v_target = v_cruise
    self.output_a_target = a_ego

    if sm.valid['mapdOut']:
      suggested_speed = sm['mapdOut'].suggestedSpeed
      if suggested_speed > 0 and suggested_speed < self.output_v_target:
        self.output_v_target = suggested_speed
        self.source = LongitudinalPlanSource.mapd

    return self.output_v_target, self.output_a_target

  def update(self, sm: messaging.SubMaster) -> None:
    self.events_sp.clear()
    self.dec.update(sm)
    self.e2e_alerts_helper.update(sm, self.events_sp)
    self.accel_controller.update(sm)

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

    longitudinalPlanSP.accelPersonality = int(self.accel_controller.get_accel_personality())

    # E2E Alerts
    e2eAlerts = longitudinalPlanSP.e2eAlerts
    e2eAlerts.greenLightAlert = self.e2e_alerts_helper.green_light_alert
    e2eAlerts.leadDepartAlert = self.e2e_alerts_helper.lead_depart_alert

    pm.send('longitudinalPlanSP', plan_sp_send)
