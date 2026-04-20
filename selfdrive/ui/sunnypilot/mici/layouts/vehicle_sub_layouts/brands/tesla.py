"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.vehicle_sub_layouts.brands.base import BrandSettingsMici
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.selfdrive.ui.mici.widgets.button import BigParamControl


class TeslaSettingsMici(BrandSettingsMici):
  def __init__(self):
    super().__init__()
    self.coop_steering_toggle = BigParamControl(
      tr("Cooperative Steering (Beta)"),
      "TeslaCoopSteering"
    )
    self.items = [self.coop_steering_toggle]

  def update_settings(self):
    self.coop_steering_toggle.set_enabled(ui_state.is_offroad())
