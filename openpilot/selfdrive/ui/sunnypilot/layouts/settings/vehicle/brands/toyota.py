"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from opendbc.car.toyota.values import ToyotaFlags
from opendbc.sunnypilot.car.toyota.values import ToyotaFlagsSP
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.base import BrandSettings
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr, tr_noop
from openpilot.system.ui.widgets import DialogResult
from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp


ONROAD_ONLY_DESCRIPTION = tr_noop("Start the vehicle to check vehicle compatibility.")
SNG_HACK_UNAVAILABLE = tr_noop("sunnypilot Longitudinal Control must be available and enabled for your vehicle to use this feature.")
BSM_UNAVAILABLE = tr_noop("Enhanced Blind Spot Monitoring requires a TSS2 Toyota/Lexus without SecOC.")
BSM_STOCK_LONG_UNAVAILABLE = tr_noop("Enhanced Blind Spot Monitoring is not available while Enforce Factory Longitudinal Control is enabled.")
BSM_REQUIRED = tr_noop("This vehicle does not report blind spot status over the standard CAN signals. " +
                        "Enhanced Blind Spot Monitoring is required for blind spot detection.")

DESCRIPTIONS = {
  'enforce_stock_longitudinal': tr_noop(
    'sunnypilot will not take over control of gas and brakes. Factory Toyota longitudinal control will be used.'
  ),
  'stop_and_go_hack': tr_noop(
    'sunnypilot will allow some Toyota/Lexus cars to auto resume during stop and go traffic. ' +
    'This feature is only applicable to certain models that are able to use longitudinal control. This is an alpha feature. Use at your own risk.'
  ),
  'enhanced_bsm': tr_noop(
    'sunnypilot will poll the blind spot monitor diagnostics directly from the radar. Use this on vehicles whose blind spot monitors ' +
    'do not report blind spot status over the standard CAN signals. This is an alpha feature. Use at your own risk.'
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

    self.enhanced_bsm = toggle_item_sp(
      lambda: tr("Enhanced Blind Spot Monitoring (Alpha)"),
      description=lambda: tr(DESCRIPTIONS["enhanced_bsm"]),
      initial_state=ui_state.params.get_bool("ToyotaEnhancedBsm"),
      callback=self._on_enable_enhanced_bsm,
      enabled=lambda: not ui_state.engaged,
    )

    self.items = [
      self.enforce_stock_longitudinal,
      self.stop_and_go_hack,
      self.enhanced_bsm,
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

  def _on_enable_enhanced_bsm(self, state: bool):
    if state:
      def confirm_callback(result: int):
        if result == DialogResult.CONFIRM:
          ui_state.params.put_bool("ToyotaEnhancedBsm", True)
          ui_state.params.put_bool("OnroadCycleRequested", True)
        else:
          self.enhanced_bsm.action_item.set_state(False)

      content = (f"<h1>{self.enhanced_bsm.title}</h1><br>" +
                 f"<p>{self.enhanced_bsm.description}</p>")

      dlg = ConfirmDialog(content, tr("Enable"), rich=True, callback=confirm_callback)
      gui_app.push_widget(dlg)

    else:
      ui_state.params.put_bool("ToyotaEnhancedBsm", False)
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

      # Enhanced BSM needs the radar diagnostic address, which is only in the TX allowlist for
      # TSS2 cars without SecOC that are not enforcing factory longitudinal control
      bsm_supported = bool(ui_state.CP.flags & ToyotaFlags.TSS2) and not bool(ui_state.CP.flags & ToyotaFlags.SECOC)
      bsm_available = bsm_supported and not enforce_stock
      self.enhanced_bsm.action_item.set_enabled(bsm_available and not ui_state.engaged)

      bsm_desc = tr(DESCRIPTIONS["enhanced_bsm"])
      if not bsm_supported:
        self.enhanced_bsm.action_item.set_state(False)
        bsm_desc = "<b>" + tr(BSM_UNAVAILABLE) + "</b>\n\n" + bsm_desc
      elif enforce_stock:
        self.enhanced_bsm.action_item.set_state(False)
        bsm_desc = "<b>" + tr(BSM_STOCK_LONG_UNAVAILABLE) + "</b>\n\n" + bsm_desc
      elif ui_state.CP_SP is not None and ui_state.CP_SP.flags & ToyotaFlagsSP.SP_NEED_DEBUG_BSM:
        bsm_desc = "<b>" + tr(BSM_REQUIRED) + "</b>\n\n" + bsm_desc

      if self.enhanced_bsm.description != bsm_desc:
        self.enhanced_bsm.set_description(bsm_desc)
        if not bsm_available:
          self.enhanced_bsm.show_description(True)
    else:
      self.stop_and_go_hack.action_item.set_enabled(False)
      new_desc = "<b>" + tr(ONROAD_ONLY_DESCRIPTION) + "</b>\n\n" + tr(DESCRIPTIONS["stop_and_go_hack"])
      if self.stop_and_go_hack.description != new_desc:
        self.stop_and_go_hack.set_description(new_desc)
        self.stop_and_go_hack.show_description(True)

      self.enhanced_bsm.action_item.set_enabled(False)
      bsm_desc = "<b>" + tr(ONROAD_ONLY_DESCRIPTION) + "</b>\n\n" + tr(DESCRIPTIONS["enhanced_bsm"])
      if self.enhanced_bsm.description != bsm_desc:
        self.enhanced_bsm.set_description(bsm_desc)
        self.enhanced_bsm.show_description(True)
