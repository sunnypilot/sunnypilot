"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import messaging, custom
from opendbc.car import structs
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.sunnypilot.selfdrive.controls.lib.dec.dec import DynamicExperimentalController
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller.common import Policy
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller.speed_limit_controller import SpeedLimitController
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller.speed_limit_resolver import SpeedLimitResolver
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP
from openpilot.sunnypilot.models.helpers import get_active_bundle

DecState = custom.LongitudinalPlanSP.DynamicExperimentalControl.DynamicExperimentalControlState


class LongitudinalPlannerSP:
  def __init__(self, CP: structs.CarParams, mpc):
    self.events_sp = EventsSP()
    self.params = Params()
    self.frame = -1

    self.policy = self.params.get("SpeedLimitControlPolicy", return_default=True)
    self.resolver = SpeedLimitResolver(self.policy)

    self.dec = DynamicExperimentalController(CP, mpc)
    self.generation = int(model_bundle.generation) if (model_bundle := get_active_bundle()) else None
    self.slc = SpeedLimitController(CP)

  @property
  def mlsim(self) -> bool:
    # If we don't have a generation set, we assume it's default model. Which as of today are mlsim.
    return bool(self.generation is None or self.generation >= 11)

  def update_params(self):
    if self.frame % int(3. / DT_MDL) == 0:
      self.policy = Policy(self.params.get("SpeedLimitControlPolicy", return_default=True))
      self.resolver.change_policy(self.policy)

  def get_mpc_mode(self) -> str | None:
    if not self.dec.active():
      return None

    return self.dec.mode()

  def update_v_cruise(self, sm: messaging.SubMaster, v_ego: float, a_ego: float, v_cruise: float) -> float:
    self.events_sp.clear()

    # Speed Limit Control
    _speed_limit, _distance, _source = self.resolver.resolve(v_ego, sm)
    v_cruise_slc = self.slc.update(sm, v_ego, a_ego, v_cruise, _speed_limit, _distance, _source, self.events_sp)

    v_cruise_final = min(v_cruise, v_cruise_slc)

    return v_cruise_final

  def update(self, sm: messaging.SubMaster) -> None:
    self.dec.update(sm)

    self.frame += 1

  def publish_longitudinal_plan_sp(self, sm: messaging.SubMaster, pm: messaging.PubMaster) -> None:
    plan_sp_send = messaging.new_message('longitudinalPlanSP')

    plan_sp_send.valid = sm.all_checks(service_list=['carState', 'controlsState'])

    longitudinalPlanSP = plan_sp_send.longitudinalPlanSP
    longitudinalPlanSP.events = self.events_sp.to_msg()

    # Dynamic Experimental Control
    dec = longitudinalPlanSP.dec
    dec.state = DecState.blended if self.dec.mode() == 'blended' else DecState.acc
    dec.enabled = self.dec.enabled()
    dec.active = self.dec.active()

    # Speed Limit Control
    slc = longitudinalPlanSP.slc
    slc.state = self.slc.state
    slc.enabled = self.slc.is_enabled
    slc.active = self.slc.is_active
    slc.speedLimit = float(self.slc.speed_limit)
    slc.speedLimitOffset = float(self.slc.speed_limit_offset)
    slc.distToSpeedLimit = float(self.slc.distance)

    pm.send('longitudinalPlanSP', plan_sp_send)
