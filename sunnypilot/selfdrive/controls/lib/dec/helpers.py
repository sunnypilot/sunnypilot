"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import messaging, custom
from opendbc.car import structs
from openpilot.sunnypilot.selfdrive.controls.lib.dec.dec import DynamicExperimentalController

DecState = custom.LongitudinalPlanSP.DynamicExperimentalControl.DynamicExperimentalControlState


class DecPlanner:
  def __init__(self, CP: structs.CarParams, mpc):
    self.CP = CP
    self.mpc = mpc
    self.dynamic_experimental_controller = DynamicExperimentalController()

  def get_mpc_mode(self) -> str | None:
    if not self.dynamic_experimental_controller.active():
      return None

    return self.dynamic_experimental_controller.mode()

  def update(self, sm: messaging.SubMaster) -> None:
    self.dynamic_experimental_controller.set_mpc_fcw_crash_cnt(self.mpc.crash_cnt)
    self.dynamic_experimental_controller.update(self.CP.radarUnavailable, sm)

  def publish_longitudinal_plan_sp(self, sm: messaging.SubMaster, pm: messaging.PubMaster) -> None:
    plan_sp_send = messaging.new_message('longitudinalPlanSP')

    plan_sp_send.valid = sm.all_checks(service_list=['carState', 'controlsState'])

    longitudinalPlanSP = plan_sp_send.longitudinalPlanSP

    # DEC
    dec = longitudinalPlanSP.dec
    dec.state = DecState.blended if self.dynamic_experimental_controller.mode() == 'blended' else DecState.acc
    dec.enabled = self.dynamic_experimental_controller.enabled()
    dec.active = self.dynamic_experimental_controller.active()

    pm.send('longitudinalPlanSP', plan_sp_send)
