"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.selfdrive.ui.onroad.hud_renderer import HudRenderer
from openpilot.selfdrive.ui.sunnypilot.onroad.developer_ui import DeveloperUiRenderer
from openpilot.selfdrive.ui.sunnypilot.onroad.road_name import RoadNameRenderer
from openpilot.selfdrive.ui.sunnypilot.onroad.rocket_fuel import RocketFuel
from openpilot.selfdrive.ui.sunnypilot.onroad.turn_signal import TurnSignalController


class HudRendererSP(HudRenderer):
  def __init__(self):
    super().__init__()
    self.developer_ui = DeveloperUiRenderer()
    self.road_name_renderer = RoadNameRenderer()
    self.rocket_fuel = RocketFuel()
    self.turn_signal_controller = TurnSignalController()

  def _update_state(self) -> None:
    super()._update_state()
    self.road_name_renderer.update()
    self.turn_signal_controller.update()

  def _render(self, rect: rl.Rectangle) -> None:
    super()._render(rect)
    self.developer_ui.render(rect)

    self.road_name_renderer.render(rect)
    self.turn_signal_controller.render(rect)

    if ui_state.rocket_fuel:
      self.rocket_fuel.render(rect, ui_state.sm)
