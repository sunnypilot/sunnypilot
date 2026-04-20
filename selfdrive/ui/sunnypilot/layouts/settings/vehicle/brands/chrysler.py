"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.base import BrandSettings
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp
from opendbc.sunnypilot.car.chrysler.values_ext import JEEPS


class ChryslerSettings(BrandSettings):
  def __init__(self):
    super().__init__()
    self.is_supported_jeep = False

    from openpilot.system.ui.sunnypilot.widgets.list_view import multiple_button_item_sp
    self.brake_hold_toggle = multiple_button_item_sp(
      tr("Jeep Brake Hold (Beta)"),
      "",
      [tr("Disabled"), tr("+2 Offset"), tr("+3 Offset")],
      param="JeepBrakeHold",
      callback=self._on_toggle_changed,
    )

    self.items = [self.brake_hold_toggle]

  def _on_toggle_changed(self, index):
    ui_state.params.put("JeepBrakeHold", str(index))
    self.update_settings()

  def _disabled_msg(self):
    if not self.is_supported_jeep:
      return tr("This feature is only available on Jeep Grand Cherokee 2016-21.")
    if not ui_state.is_offroad():
      return tr("Enable \"Always Offroad\" in Device panel, or turn vehicle off to toggle.")
    return ""

  def update_settings(self):
    # Match Subaru's pattern: prefer offroad CarPlatformBundle for platform detection,
    # fall back to live CP when onroad.
    bundle = ui_state.params.get("CarPlatformBundle")
    if bundle:
      platform = bundle.get("platform")
      self.is_supported_jeep = platform in {j.name for j in JEEPS}
    elif ui_state.CP is not None:
      self.is_supported_jeep = ui_state.CP.carFingerprint in {j.name for j in JEEPS}

    disabled_msg = self._disabled_msg()
    desc = tr("Holds the brakes after ACC auto-cancels at standstill (Jeep's ~3s SNG timeout). "
              "Automatically resumes ACC when the lead vehicle departs. "
              "Releases on any driver input (gas/brake/cancel/gear change).")

    self.brake_hold_toggle.action_item.set_enabled(self.is_supported_jeep and ui_state.is_offroad())
    self.brake_hold_toggle.set_description(f"<b>{disabled_msg}</b><br><br>{desc}" if disabled_msg else desc)
    self.brake_hold_toggle.action_item.set_selected_button(int(ui_state.params.get("JeepBrakeHold") or "0"))
