"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.base import BrandSettings
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp


class FordSettings(BrandSettings):
  def __init__(self):
    super().__init__()
    self.coherent_path_toggle = toggle_item_sp(
      tr("Coherent Ford Path (Experimental)"),
      tr("Solve the fast path offset and angle at one shared lookahead. Disable to use the previous Ford path controller."),
      param="FordCoherentPath",
    )
    self.items = [self.coherent_path_toggle]

  def update_settings(self):
    self.coherent_path_toggle.action_item.set_enabled(ui_state.is_offroad())
