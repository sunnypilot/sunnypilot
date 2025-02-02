"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import messaging, custom
from opendbc.car import structs
from openpilot.sunnypilot.selfdrive.controls.lib.dec.dec import DynamicExperimentalController
from openpilot.sunnypilot.selfdrive.controls.lib.accel_personality.accel_controller import AccelController

DecState = custom.LongitudinalPlanSP.DynamicExperimentalControl.DynamicExperimentalControlState


class LongitudinalPlannerSP:
  def __init__(self, CP: structs.CarParams, mpc):
    self.dec = DynamicExperimentalController(CP, mpc)
    self.accel_controller = AccelController()

  def get_mpc_mode(self) -> str | None:
    """ Returns the current MPC mode if DEC is active. """
    return self.dec.mode() if self.dec.active() else None

  def compute_accel_limits(self, v_ego: float, sm, CP) -> tuple[list[float], list[float]]:
    """ Delegates acceleration limit computation to AccelController. """
    return self.accel_controller.compute_accel_limits(v_ego, sm, CP)

  def update(self, sm: messaging.SubMaster) -> None:
    """ Updates DEC and AccelController states. """
    self.dec.update(sm)
    self.accel_controller.update()

  def publish_longitudinal_plan_sp(self, sm: messaging.SubMaster, pm: messaging.PubMaster) -> None:
    """ Publishes the longitudinal plan state to messaging. """
    plan_sp_send = messaging.new_message('longitudinalPlanSP')
    plan_sp_send.valid = sm.all_checks(service_list=['carState', 'controlsState'])

    longitudinalPlanSP = plan_sp_send.longitudinalPlanSP

    # Dynamic Experimental Control
    dec = longitudinalPlanSP.dec
    dec.state = DecState.blended if self.dec.mode() == 'blended' else DecState.acc
    dec.enabled = self.dec.enabled()
    dec.active = self.dec.active()

    pm.send('longitudinalPlanSP', plan_sp_send)
