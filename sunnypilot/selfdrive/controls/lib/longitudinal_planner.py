"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np
from cereal import messaging, custom
from opendbc.car import structs
from openpilot.selfdrive.controls.lib.drive_helpers import get_accel_from_plan
from openpilot.sunnypilot.models.helpers import get_active_model_runner
from openpilot.sunnypilot.selfdrive.controls.lib.dec.dec import DynamicExperimentalController

DecState = custom.LongitudinalPlanSP.DynamicExperimentalControl.DynamicExperimentalControlState


class LongitudinalPlannerSP:
  def __init__(self, CP: structs.CarParams, mpc):
    self.dec = DynamicExperimentalController(CP, mpc)

  def get_mpc_mode(self) -> str | None:
    if not self.dec.active():
      return None

    return self.dec.mode()

  def update(self, sm: messaging.SubMaster) -> None:
    self.dec.update(sm)

  def publish_longitudinal_plan_sp(self, sm: messaging.SubMaster, pm: messaging.PubMaster) -> None:
    plan_sp_send = messaging.new_message('longitudinalPlanSP')

    plan_sp_send.valid = sm.all_checks(service_list=['carState', 'controlsState'])

    longitudinalPlanSP = plan_sp_send.longitudinalPlanSP

    # Dynamic Experimental Control
    dec = longitudinalPlanSP.dec
    dec.state = DecState.blended if self.dec.mode() == 'blended' else DecState.acc
    dec.enabled = self.dec.enabled()
    dec.active = self.dec.active()

    pm.send('longitudinalPlanSP', plan_sp_send)

  @staticmethod
  def override_accel_for_snpe_models(output_a_target: float, output_should_stop: bool, speeds: np.ndarray,
                                     accels: np.ndarray, t_idxs: np.ndarray, action_t: float, vEgoStopping: float) -> tuple[float, bool]:
    """ Overrides the calculated acceleration target only if the active model is SNPE/thneed.
        Otherwise, it returns the provided targets unchanged. """
    is_snpe = get_active_model_runner() == custom.ModelManagerSP.Runner.snpe

    if is_snpe: # SNPE models use only the get_accel_from_plan calculation
      return get_accel_from_plan(speeds, accels, t_idxs, action_t, vEgoStopping)
    else: # For non-SNPE models, return the already calculated values from the main planner
      return output_a_target, output_should_stop
