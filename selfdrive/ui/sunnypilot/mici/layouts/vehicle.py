"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json
import os
import pyray as rl
from collections.abc import Callable
from functools import partial

from openpilot.common.basedir import BASEDIR
from openpilot.selfdrive.ui.mici.widgets.button import BigButton
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import DialogResult
from openpilot.selfdrive.ui.mici.widgets.dialog import BigConfirmationDialog
from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog
from openpilot.system.ui.sunnypilot.widgets.tree_dialog import TreeNode, TreeFolder
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.widgets.scroller import NavScroller
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.selfdrive.ui.mici.layouts.settings.settings import SettingsBigButton

from openpilot.selfdrive.ui.sunnypilot.mici.layouts.vehicle_sub_layouts.brands.factory import BrandSettingsFactoryMici

CAR_LIST_JSON_OUT = os.path.join(BASEDIR, "sunnypilot", "selfdrive", "car", "car_list.json")
SP_ICON = "../../sunnypilot/selfdrive/assets/offroad"


class VehicleModelSelectLayoutMici(NavScroller):
  def __init__(self, make_name, nodes, on_platform_selected, back_callback: Callable[[], None] | None = None):
    super().__init__()
    if back_callback is not None:
      self.set_back_callback(back_callback)

    self._make_name = make_name
    self._nodes = nodes
    self._on_platform_selected = on_platform_selected
    
    for node in nodes:
      item = SettingsBigButton(node.data.get('display_name', node.ref), scroll=True)
      item.set_click_callback(partial(self._on_model_selected, node.ref))
      self._scroller.add_widget(item)

  def _on_model_selected(self, ref):
    if self._on_platform_selected:
      self._on_platform_selected(ref, DialogResult.CONFIRM)


class VehicleMakeSelectLayoutMici(NavScroller):
  def __init__(self, folders, on_platform_selected, back_callback: Callable[[], None] | None = None):
    super().__init__()
    if back_callback is not None:
      self.set_back_callback(back_callback)

    self._folders = folders
    self._on_platform_selected = on_platform_selected
    
    for folder in folders:
      item = SettingsBigButton(folder.folder, scroll=True)
      item.set_click_callback(partial(self._on_make_selected, folder))
      self._scroller.add_widget(item)

  def _on_make_selected(self, folder):
    def back_to_makes():
      gui_app.pop_widget()
    
    model_layout = VehicleModelSelectLayoutMici(folder.folder, folder.nodes, self._on_platform_selected, back_to_makes)
    gui_app.push_widget(model_layout)


class PlatformSelectorMici(BigButton):
  def __init__(self, on_platform_change: Callable[[], None] | None = None):
    super().__init__(tr("Vehicle"), "", scroll=True)
    with open(CAR_LIST_JSON_OUT) as car_list_json:
      self._platforms = json.load(car_list_json)

    self._on_platform_change = on_platform_change
    self.set_icon(gui_app.texture(f"{SP_ICON}/icon_vehicle.png", 64, 64))
    self.set_click_callback(self._on_clicked)
    self.refresh()

  def _on_clicked(self):
    if ui_state.params.get("CarPlatformBundle"):
      ui_state.params.remove("CarPlatformBundle")
      self.refresh()
      if self._on_platform_change:
        self._on_platform_change()
    else:
      self._show_platform_dialog()

  def _set_platform(self, platform_name):
    if data := self._platforms.get(platform_name):
      ui_state.params.put("CarPlatformBundle", {**data, "name": platform_name})
      self.refresh()
      if self._on_platform_change:
        self._on_platform_change()

  def _on_platform_selected(self, platform_ref, res):
    if res == DialogResult.CONFIRM and platform_ref:
      offroad_msg = tr("This setting will take effect immediately.") if ui_state.is_offroad() else \
                    tr("This setting will take effect once the device enters offroad state.")

      callback = partial(self._confirm_platform, platform_ref)
      icon = gui_app.texture(f"{SP_ICON}/icon_vehicle.png", 64, 64)
      confirm_dialog = BigConfirmationDialog(offroad_msg, icon, confirm_callback=callback)
      gui_app.push_widget(confirm_dialog)

  def _confirm_platform(self, platform_name):
    # BigConfirmationDialog handles its own dismissal via exit_on_confirm=True (default)
    self._set_platform(platform_name)
    gui_app.pop_widget()
    gui_app.pop_widget()

  def _show_platform_dialog(self):
    platforms = sorted(self._platforms.keys())
    makes = sorted({self._platforms[p].get('make') for p in platforms})
    folders = [TreeFolder(make, [TreeNode(p, {
      'display_name': p,
      'search_tags': f"{p} {self._platforms[p].get('make')} {' '.join(map(str, self._platforms[p].get('year', [])))} {self._platforms[p].get('model', p)}"
    }) for p in platforms if self._platforms[p].get('make') == make]) for make in makes]
    
    def on_make_back():
      gui_app.pop_widget()
      
    make_layout = VehicleMakeSelectLayoutMici(folders, self._on_platform_selected, back_callback=on_make_back)
    gui_app.push_widget(make_layout)

  def refresh(self):
    self._platform = tr("Unrecognized Vehicle")
    self.set_value(tr("None"))

    if bundle := ui_state.params.get("CarPlatformBundle"):
      self._platform = bundle.get("name", "")
      self.set_value(self._platform)
    elif ui_state.CP is not None and ui_state.CP.carFingerprint != "MOCK":
      self._platform = ui_state.CP.carFingerprint
      self.set_value(self._platform)
    self.set_enabled(True)


class VehicleLayoutMici(NavScroller):
  def __init__(self, back_callback: Callable[[], None] | None = None):
    super().__init__()
    if back_callback is not None:
      self.set_back_callback(back_callback)

    self._brand = object()
    self._brand_settings = None

    self._platform_selector = PlatformSelectorMici(self._update_brand_settings)

    self._update_brand_settings()

  def _update_brand_settings(self):
    platform_name = None
    if ui_state.CP is not None and ui_state.CP.carFingerprint != "MOCK":
      platform_name = ui_state.CP.carFingerprint

    if bundle := ui_state.params.get("CarPlatformBundle"):
        platform_name = bundle.get("name")

    brand = None
    if platform_name and platform_name in self._platform_selector._platforms:
      brand = self._platform_selector._platforms.get(platform_name).get("make")

    if brand != self._brand:
      self._brand = brand
      self._scroller._items.clear()

      if self._brand:
        self._brand_settings = BrandSettingsFactoryMici.create_brand_settings(self._brand)
        if self._brand_settings:
          for item in self._brand_settings.items:
            self._scroller.add_widget(item)
      else:
        self._brand_settings = None

      self._scroller.add_widget(self._platform_selector)

  def _update_state(self):
    super()._update_state()
    self._platform_selector.refresh()
    if self._brand_settings:
      self._brand_settings.update_settings()
