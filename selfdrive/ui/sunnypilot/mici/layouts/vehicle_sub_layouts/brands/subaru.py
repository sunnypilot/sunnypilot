"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.vehicle_sub_layouts.brands.base import BrandSettingsMici
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.selfdrive.ui.mici.widgets.button import BigToggle
from opendbc.car.subaru.values import CAR, SubaruFlags


class SubaruSettingsMici(BrandSettingsMici):
  def __init__(self):
    super().__init__()
    self.has_stop_and_go = False

    self.stop_and_go_toggle = BigToggle(
      tr("Stop and Go (Beta)"),
      initial_state=ui_state.params.get_bool("SubaruStopAndGo"),
      toggle_callback=self._on_sng_toggle_changed,
    )

    self.stop_and_go_manual_parking_brake_toggle = BigToggle(
      tr("Stop and Go for Manual Parking Brake (Beta)"),
      initial_state=ui_state.params.get_bool("SubaruStopAndGoManualParkingBrake"),
      toggle_callback=self._on_sng_mpb_toggle_changed,
    )

    self.items = [self.stop_and_go_toggle, self.stop_and_go_manual_parking_brake_toggle]

  def _on_sng_toggle_changed(self, state: bool):
    ui_state.params.put_bool("SubaruStopAndGo", state)
    self.update_settings()

  def _on_sng_mpb_toggle_changed(self, state: bool):
    ui_state.params.put_bool("SubaruStopAndGoManualParkingBrake", state)
    self.update_settings()

  def update_settings(self):
    bundle = ui_state.params.get("CarPlatformBundle")
    if bundle:
      platform = bundle.get("platform")
      config = CAR[platform].config
      self.has_stop_and_go = not (config.flags & (SubaruFlags.GLOBAL_GEN2 | SubaruFlags.HYBRID))
    elif ui_state.CP is not None:
      self.has_stop_and_go = not (ui_state.CP.flags & (SubaruFlags.GLOBAL_GEN2 | SubaruFlags.HYBRID))

    for toggle in [self.stop_and_go_toggle, self.stop_and_go_manual_parking_brake_toggle]:
      toggle.set_enabled(self.has_stop_and_go and ui_state.is_offroad())
