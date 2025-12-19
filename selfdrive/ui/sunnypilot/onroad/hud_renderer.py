"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl

from openpilot.selfdrive.ui.onroad.hud_renderer import HudRenderer
from openpilot.selfdrive.ui.sunnypilot.onroad.developer_ui import DeveloperUiRenderer
from openpilot.selfdrive.ui.sunnypilot.onroad.navigation_hud import NavigationHudRenderer


class HudRendererSP(HudRenderer):
  def __init__(self):
    super().__init__()
    self.developer_ui = DeveloperUiRenderer()
    self.navigation_hud = NavigationHudRenderer()

  def _render(self, rect: rl.Rectangle) -> None:
    self.navigation_hud.render(rect)
    super()._render(rect)
    self.developer_ui.render(rect)
