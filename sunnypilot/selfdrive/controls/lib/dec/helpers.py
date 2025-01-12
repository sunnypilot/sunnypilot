"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import messaging, custom
from openpilot.sunnypilot.selfdrive.controls.lib.dec.dec import DynamicExperimentalController

MpcSource = custom.LongitudinalPlanSP.MpcSource


class DecPlanner:
  def __init__(self, CP, mpc):
    self.CP = CP
    self.mpc = mpc

    self.is_enabled = False

    self.dynamic_experimental_controller = DynamicExperimentalController()

  def get_mpc_mode(self, sm):
    if not self.is_enabled or not sm['selfdriveState'].experimentalMode:
      return None

    return self.dynamic_experimental_controller.get_mpc_mode()

  def update(self, sm):
    self.dynamic_experimental_controller.set_mpc_fcw_crash_cnt(self.mpc.crash_cnt)
    self.dynamic_experimental_controller.update(self.CP.radarUnavailable, sm)

  def publish_longitudinal_plan_sp(self, sm, pm):
    plan_sp_send = messaging.new_message('longitudinalPlanSP')

    plan_sp_send.valid = sm.all_checks(service_list=['carState', 'controlsState'])

    longitudinalPlanSP = plan_sp_send.longitudinalPlanSP

    # DEC
    longitudinalPlanSP.mpcSource = MpcSource.blended if self.mpc.mode == 'blended' else MpcSource.acc

    longitudinalPlanSP.dynamicExperimentalControl = self.dynamic_experimental_controller.is_enabled()

    pm.send('longitudinalPlanSP', plan_sp_send)
