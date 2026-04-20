"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.vehicle_sub_layouts.brands.base import BrandSettingsMici
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.selfdrive.ui.mici.widgets.button import BigMultiParamToggle
from opendbc.sunnypilot.car.chrysler.values_ext import JEEPS


class ChryslerSettingsMici(BrandSettingsMici):
  def __init__(self):
    super().__init__()
    self.is_supported_jeep = False

    self.brake_hold_toggle = BigMultiParamToggle(
      tr("Jeep Brake Hold (Beta)"),
      "JeepBrakeHold",
      [tr("Disabled"), tr("+2 Offset"), tr("+3 Offset")],
      select_callback=self._on_toggle_changed,
    )

    self.items = [self.brake_hold_toggle]

  def _on_toggle_changed(self, option: str):
    self.update_settings()

  def update_settings(self):
    bundle = ui_state.params.get("CarPlatformBundle")
    if bundle:
      platform = bundle.get("platform")
      self.is_supported_jeep = platform in {j.name for j in JEEPS}
    elif ui_state.CP is not None:
      self.is_supported_jeep = ui_state.CP.carFingerprint in {j.name for j in JEEPS}

    self.brake_hold_toggle.set_enabled(self.is_supported_jeep and ui_state.is_offroad())
