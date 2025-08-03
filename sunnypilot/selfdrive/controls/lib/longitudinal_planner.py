"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import messaging, custom
from opendbc.car import structs
from openpilot.selfdrive.car.cruise import V_CRUISE_UNSET
from openpilot.sunnypilot.selfdrive.controls.lib.dec.dec import DynamicExperimentalController
from openpilot.sunnypilot.selfdrive.controls.lib.vision_turn_controller import VisionTurnController
from openpilot.sunnypilot.models.helpers import get_active_bundle

from openpilot.sunnypilot.selfdrive.controls.lib.vibe_personality.vibe_personality import VibePersonalityController
DecState = custom.LongitudinalPlanSP.DynamicExperimentalControl.DynamicExperimentalControlState


class LongitudinalPlannerSP:
  def __init__(self, CP: structs.CarParams, mpc):
    self.dec = DynamicExperimentalController(CP, mpc)
    self.v_tsc = VisionTurnController(CP)
    self.vibe_controller = VibePersonalityController()
    self.generation = int(model_bundle.generation) if (model_bundle := get_active_bundle()) else None

  @property
  def mlsim(self) -> bool:
    # If we don't have a generation set, we assume it's default model. Which as of today are mlsim.
    return bool(self.generation is None or self.generation >= 11)

  def get_mpc_mode(self) -> str | None:
    if not self.dec.active():
      return None

    return self.dec.mode()

  def update_v_cruise(self, sm: messaging.SubMaster, v_ego: float, a_ego: float, v_cruise: float) -> float:
    self.v_tsc.update(sm, sm['carControl'].enabled, v_ego, a_ego, v_cruise)

    v_cruise_v_tsc = self.v_tsc.v_turn if self.v_tsc.is_active else V_CRUISE_UNSET

    return min(v_cruise, v_cruise_v_tsc)

  def update(self, sm: messaging.SubMaster) -> None:
    self.dec.update(sm)
    self.vibe_controller.update()

  def publish_longitudinal_plan_sp(self, sm: messaging.SubMaster, pm: messaging.PubMaster) -> None:
    plan_sp_send = messaging.new_message('longitudinalPlanSP')

    plan_sp_send.valid = sm.all_checks(service_list=['carState', 'controlsState'])

    longitudinalPlanSP = plan_sp_send.longitudinalPlanSP

    # Dynamic Experimental Control
    dec = longitudinalPlanSP.dec
    dec.state = DecState.blended if self.dec.mode() == 'blended' else DecState.acc
    dec.enabled = self.dec.enabled()
    dec.active = self.dec.active()

    # Vision Turn Speed Control
    visionTurnSpeedControl = longitudinalPlanSP.visionTurnSpeedControl
    visionTurnSpeedControl.state = self.v_tsc.state
    visionTurnSpeedControl.velocity = float(self.v_tsc.v_turn)
    visionTurnSpeedControl.currentLateralAccel = float(self.v_tsc.current_lat_acc)
    visionTurnSpeedControl.maxPredictedLateralAccel = float(self.v_tsc.max_pred_lat_acc)

    pm.send('longitudinalPlanSP', plan_sp_send)
