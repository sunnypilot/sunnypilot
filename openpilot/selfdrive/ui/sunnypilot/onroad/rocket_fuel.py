"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl

from openpilot.cereal import custom
from opendbc.car.structs import car
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached

MADSState = custom.ModularAssistiveDrivingSystem.ModularAssistiveDrivingSystemState
LongCtrlState = car.CarControl.Actuators.LongControlState
IDLE_DISPLAY_ACCEL_DEADBAND = 0.05


class RocketFuel:
  def __init__(self):
    self.vc_accel = 0.0

  @staticmethod
  def service_alive(sm, service: str) -> bool:
    try:
      return bool(sm.alive[service])
    except (AttributeError, KeyError):
      return False

  @staticmethod
  def longitudinal_idle_active(sm) -> bool:
    try:
      # The UI samples 100 Hz controls messages at its rendering rate. Fresh,
      # valid requests may fail frequency checks on a slower UI (e.g. 20 FPS).
      services = ['carControlSP', 'carControl']
      if not sm.all_alive(services) or not sm.all_valid(services):
        return False
      # Display the accepted controls request, not a planner request that may
      # have been rejected before reaching car control.
      return bool(sm['carControlSP'].longitudinalIdle and sm['carControl'].longActive)
    except (AttributeError, KeyError):
      return False

  @staticmethod
  def paused_without_pedals(sm) -> bool:
    try:
      if not RocketFuel.service_alive(sm, 'carState') or not RocketFuel.service_alive(sm, 'selfdriveStateSP'):
        return False
      CS = sm['carState']
      mads = sm['selfdriveStateSP'].mads
      return bool(mads.state == MADSState.paused and not CS.gasPressed and not CS.brakePressed)
    except (AttributeError, KeyError):
      return False

  @staticmethod
  def long_paused_without_accel(sm) -> bool:
    try:
      if not (RocketFuel.service_alive(sm, 'carState') and RocketFuel.service_alive(sm, 'controlsState') and
              RocketFuel.service_alive(sm, 'longitudinalPlan')):
        return False
      CS = sm['carState']
      controls_state = sm['controlsState']
      a_target = sm['longitudinalPlan'].aTarget
      return bool(controls_state.longControlState == LongCtrlState.off and
                  abs(a_target) <= IDLE_DISPLAY_ACCEL_DEADBAND and
                  not CS.gasPressed and not CS.brakePressed)
    except (AttributeError, KeyError):
      return False

  def render(self, rect: rl.Rectangle, sm) -> None:
    if not ui_state.rocket_fuel:
      return

    vc_accel0 = sm['carState'].aEgo
    longitudinal_idle = (self.longitudinal_idle_active(sm) or
                         self.paused_without_pedals(sm) or
                         self.long_paused_without_accel(sm))

    # Smooth the acceleration
    self.vc_accel = self.vc_accel + (vc_accel0 - self.vc_accel) / 5.0

    hha = 0.0
    color = rl.Color(0, 0, 0, 0)  # Transparent by default

    if self.vc_accel > 0:
      hha = 0.85 - 0.1 / self.vc_accel  # only extend up to 85%
      color = rl.Color(0, 245, 0, 200)
    elif self.vc_accel < 0:
      hha = 0.85 + 0.1 / self.vc_accel  # only extend up to 85%
      color = rl.Color(245, 0, 0, 200)

    if hha < 0:
      hha = 0.0

    hha = hha * rect.height
    wp = 28.0

    # Draw
    rect_h = rect.height

    if self.vc_accel > 0:
      ra_y = rect_h / 2.0 - hha / 2.0
    else:
      ra_y = rect_h / 2.0

    if hha > 0:
      rl.draw_rectangle(int(rect.x), int(rect.y + ra_y), int(wp), int(hha / 2.0), color)

    if longitudinal_idle:
      marker_w = int(wp * 2.0)
      marker_h = 68
      font_size = 48
      marker_y = int(rect.y + rect.height / 2.0 - marker_h / 2.0)
      rl.draw_rectangle(int(rect.x), marker_y, marker_w, marker_h, rl.Color(245, 180, 0, 220))
      font = gui_app.font(FontWeight.BOLD)
      text_size = measure_text_cached(font, "N", font_size)
      text_pos = rl.Vector2(rect.x + (marker_w - text_size.x) / 2, marker_y + (marker_h - text_size.y) / 2)
      rl.draw_text_ex(font, "N", text_pos, font_size, 0, rl.WHITE)
