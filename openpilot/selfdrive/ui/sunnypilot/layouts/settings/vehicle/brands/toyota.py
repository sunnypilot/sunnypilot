"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.base import BrandSettings
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr, tr_noop
from openpilot.system.ui.widgets import DialogResult
from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp


ONROAD_ONLY_DESCRIPTION = tr_noop("Start the vehicle to check vehicle compatibility.")
SNG_HACK_UNAVAILABLE = tr_noop("sunnypilot Longitudinal Control must be available and enabled for your vehicle to use this feature.")

DESCRIPTIONS = {
  'enforce_stock_longitudinal': tr_noop(
    'sunnypilot will not take over control of gas and brakes. Factory Toyota longitudinal control will be used.'
  ),
  'stop_and_go_hack': tr_noop(
    'sunnypilot will allow some Toyota/Lexus cars to auto resume during stop and go traffic. ' +
    'This feature is only applicable to certain models that are able to use longitudinal control. This is an alpha feature. Use at your own risk.'
  )
}


class ToyotaSettings(BrandSettings):
  def __init__(self):
    super().__init__()

    self.enforce_stock_longitudinal = toggle_item_sp(
      lambda: tr("Enforce Factory Longitudinal Control"),
      description=lambda: tr(DESCRIPTIONS["enforce_stock_longitudinal"]),
      initial_state=ui_state.params.get_bool("ToyotaEnforceStockLongitudinal"),
      callback=self._on_enable_enforce_stock_longitudinal,
      enabled=lambda: not ui_state.engaged,
    )

    self.stop_and_go_hack = toggle_item_sp(
      lambda: tr("Stop and Go Hack (Alpha)"),
      description=lambda: tr(DESCRIPTIONS["stop_and_go_hack"]),
      initial_state=ui_state.params.get_bool("ToyotaStopAndGoHack"),
      callback=self._on_enable_stop_and_go_hack,
      enabled=lambda: not ui_state.engaged,
    )

    self.items = [
      self.enforce_stock_longitudinal,
      self.stop_and_go_hack,
    ]

  def _on_enable_enforce_stock_longitudinal(self, state: bool):
    if state:
      def confirm_callback(result: int):
        if result == DialogResult.CONFIRM:
          ui_state.params.put_bool("ToyotaEnforceStockLongitudinal", True)
          if ui_state.params.get_bool("AlphaLongitudinalEnabled"):
            ui_state.params.put_bool("AlphaLongitudinalEnabled", False)
          ui_state.params.put_bool("ToyotaStopAndGoHack", False)
          self.stop_and_go_hack.action_item.set_state(False)
          ui_state.params.put_bool("OnroadCycleRequested", True)
        else:
          self.enforce_stock_longitudinal.action_item.set_state(False)

      content = (f"<h1>{self.enforce_stock_longitudinal.title}</h1><br>" +
                 f"<p>{self.enforce_stock_longitudinal.description}</p>")

      dlg = ConfirmDialog(content, tr("Enable"), rich=True, callback=confirm_callback)
      gui_app.push_widget(dlg)

    else:
      ui_state.params.put_bool("ToyotaEnforceStockLongitudinal", False)
      ui_state.params.put_bool("OnroadCycleRequested", True)

  def _on_enable_stop_and_go_hack(self, state: bool):
    if state:
      def confirm_callback(result: int):
        if result == DialogResult.CONFIRM:
          ui_state.params.put_bool("ToyotaStopAndGoHack", True)
          ui_state.params.put_bool("OnroadCycleRequested", True)
        else:
          self.stop_and_go_hack.action_item.set_state(False)

      content = (f"<h1>{self.stop_and_go_hack.title}</h1><br>" +
                 f"<p>{self.stop_and_go_hack.description}</p>")

      dlg = ConfirmDialog(content, tr("Enable"), rich=True, callback=confirm_callback)
      gui_app.push_widget(dlg)

    else:
      ui_state.params.put_bool("ToyotaStopAndGoHack", False)
      ui_state.params.put_bool("OnroadCycleRequested", True)

  def update_settings(self):
    if ui_state.CP is not None:
      longitudinal = ui_state.CP.openpilotLongitudinalControl
      enforce_stock = self.enforce_stock_longitudinal.action_item.get_state()

      if longitudinal and not enforce_stock:
        self.stop_and_go_hack.action_item.set_enabled(not ui_state.engaged)
        new_desc = tr(DESCRIPTIONS["stop_and_go_hack"])
        show_desc = False
      else:
        self.stop_and_go_hack.action_item.set_enabled(False)
        self.stop_and_go_hack.action_item.set_state(False)
        new_desc = "<b>" + tr(SNG_HACK_UNAVAILABLE) + "</b>\n\n" + tr(DESCRIPTIONS["stop_and_go_hack"])
        show_desc = True

      if self.stop_and_go_hack.description != new_desc:
        self.stop_and_go_hack.set_description(new_desc)
        if show_desc:
          self.stop_and_go_hack.show_description(True)
    else:
      self.stop_and_go_hack.action_item.set_enabled(False)
      new_desc = "<b>" + tr(ONROAD_ONLY_DESCRIPTION) + "</b>\n\n" + tr(DESCRIPTIONS["stop_and_go_hack"])
      if self.stop_and_go_hack.description != new_desc:
        self.stop_and_go_hack.set_description(new_desc)
        self.stop_and_go_hack.show_description(True)
