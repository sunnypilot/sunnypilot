"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.base import BrandSettings
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp
from opendbc.car.subaru.values import CAR, SubaruFlags


class SubaruSettings(BrandSettings):
  def __init__(self):
    super().__init__()
    self.has_stop_and_go = False
    self.has_brake_hold = False

    self.stop_and_go_toggle = toggle_item_sp(tr("Stop and Go (Beta)"), "", param="SubaruStopAndGo", callback=self._on_toggle_changed)

    self.stop_and_go_manual_parking_brake_toggle = toggle_item_sp(tr("Stop and Go for Manual Parking Brake (Beta)"), "",
                                                                  param="SubaruStopAndGoManualParkingBrake", callback=self._on_toggle_changed)

    self.avh_toggle = toggle_item_sp(tr("Automatic Vehicle Hold (AVH) (Beta)"), "",
                                     param="SubaruAutoVehicleHold", callback=self._on_toggle_changed)

    self.items = [self.stop_and_go_toggle, self.stop_and_go_manual_parking_brake_toggle, self.avh_toggle]

  def _on_toggle_changed(self, _):
    self.update_settings()

  def stop_and_go_disabled_msg(self):
    if not self.has_stop_and_go:
      return tr("This feature is currently not available on this platform.")
    elif not ui_state.is_offroad():
      return tr("Enable \"Always Offroad\" in Device panel, or turn vehicle off to toggle.")
    return ""

  def avh_disabled_msg(self):
    if not self.has_brake_hold:
      return tr("This feature is currently not available on this platform.")
    elif not ui_state.is_offroad():
      return tr("Enable \"Always Offroad\" in Device panel, or turn vehicle off to toggle.")
    return ""

  def update_settings(self):
    brake_hold_mask = SubaruFlags.GLOBAL_GEN2 | SubaruFlags.PREGLOBAL | SubaruFlags.LKAS_ANGLE | SubaruFlags.HYBRID
    bundle = ui_state.params.get("CarPlatformBundle")
    if bundle:
      platform = bundle.get("platform")
      config = CAR[platform].config
      self.has_stop_and_go = not (config.flags & (SubaruFlags.GLOBAL_GEN2 | SubaruFlags.HYBRID))
      self.has_brake_hold = not (config.flags & brake_hold_mask)
    elif ui_state.CP is not None:
      self.has_stop_and_go = not (ui_state.CP.flags & (SubaruFlags.GLOBAL_GEN2 | SubaruFlags.HYBRID))
      self.has_brake_hold = not (ui_state.CP.flags & brake_hold_mask)

    disabled_msg = self.stop_and_go_disabled_msg()
    descriptions = [
      tr("Experimental feature to enable auto-resume during stop-and-go for certain supported Subaru platforms."),
      tr("Experimental feature to enable stop and go for Subaru Global models with manual handbrake. " +
         "Models with electric parking brake should keep this disabled. Thanks to martinl for this implementation!")
    ]

    for toggle, desc in zip([self.stop_and_go_toggle, self.stop_and_go_manual_parking_brake_toggle], descriptions, strict=True):
      toggle.action_item.set_enabled(self.has_stop_and_go and ui_state.is_offroad())
      toggle.set_description(f"<b>{disabled_msg}</b><br><br>{desc}" if disabled_msg else desc)

    avh_disabled_msg = self.avh_disabled_msg()
    avh_desc = tr("Holds the brakes at a complete stop while MADS is engaged, and releases when you press the accelerator. " +
                  "Subaru Global (non-Gen2, non-hybrid) only.")
    self.avh_toggle.action_item.set_enabled(self.has_brake_hold and ui_state.is_offroad())
    self.avh_toggle.set_description(f"<b>{avh_disabled_msg}</b><br><br>{avh_desc}" if avh_disabled_msg else avh_desc)
