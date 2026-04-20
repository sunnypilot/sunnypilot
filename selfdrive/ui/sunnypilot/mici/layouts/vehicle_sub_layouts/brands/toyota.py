"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.vehicle_sub_layouts.brands.base import BrandSettingsMici
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.selfdrive.ui.mici.widgets.button import BigToggle
from openpilot.selfdrive.ui.mici.widgets.dialog import BigConfirmationDialog


class ToyotaSettingsMici(BrandSettingsMici):
  def __init__(self):
    super().__init__()

    self.enforce_stock_longitudinal = BigToggle(
      tr("Enforce Factory Longitudinal Control"),
      initial_state=ui_state.params.get_bool("ToyotaEnforceStockLongitudinal"),
      toggle_callback=self._on_enable_enforce_stock_longitudinal,
    )

    self.stop_and_go_hack = BigToggle(
      tr("Stop and Go Hack (Alpha)"),
      initial_state=ui_state.params.get_bool("ToyotaStopAndGoHack"),
      toggle_callback=self._on_enable_stop_and_go_hack,
    )

    self.items = [
      self.enforce_stock_longitudinal,
      self.stop_and_go_hack,
    ]

  def _on_enable_enforce_stock_longitudinal(self, state: bool):
    if state:
      def confirm_callback():
        ui_state.params.put_bool("ToyotaEnforceStockLongitudinal", True)
        if ui_state.params.get_bool("AlphaLongitudinalEnabled"):
          ui_state.params.put_bool("AlphaLongitudinalEnabled", False)
        ui_state.params.put_bool("ToyotaStopAndGoHack", False)
        self.stop_and_go_hack.set_checked(False)
        ui_state.params.put_bool("OnroadCycleRequested", True)

      dlg = BigConfirmationDialog(
        tr("Enable Enforce Factory Longitudinal Control?"),
        None,
        confirm_callback=confirm_callback,
        cancel_callback=lambda: self.enforce_stock_longitudinal.set_checked(False)
      )
      gui_app.push_widget(dlg)
    else:
      ui_state.params.put_bool("ToyotaEnforceStockLongitudinal", False)
      ui_state.params.put_bool("OnroadCycleRequested", True)

  def _on_enable_stop_and_go_hack(self, state: bool):
    if state:
      def confirm_callback():
        ui_state.params.put_bool("ToyotaStopAndGoHack", True)
        ui_state.params.put_bool("OnroadCycleRequested", True)

      dlg = BigConfirmationDialog(
        tr("Enable Stop and Go Hack?"),
        None,
        confirm_callback=confirm_callback,
        cancel_callback=lambda: self.stop_and_go_hack.set_checked(False)
      )
      gui_app.push_widget(dlg)
    else:
      ui_state.params.put_bool("ToyotaStopAndGoHack", False)
      ui_state.params.put_bool("OnroadCycleRequested", True)

  def update_settings(self):
    if ui_state.CP is not None:
      longitudinal = ui_state.CP.openpilotLongitudinalControl
      enforce_stock = ui_state.params.get_bool("ToyotaEnforceStockLongitudinal")

      if longitudinal and not enforce_stock:
        self.stop_and_go_hack.set_enabled(not ui_state.engaged)
      else:
        self.stop_and_go_hack.set_enabled(False)
        self.stop_and_go_hack.set_checked(False)

      self.enforce_stock_longitudinal.set_enabled(not ui_state.engaged)
    else:
      self.stop_and_go_hack.set_enabled(False)
      self.enforce_stock_longitudinal.set_enabled(not ui_state.engaged)
