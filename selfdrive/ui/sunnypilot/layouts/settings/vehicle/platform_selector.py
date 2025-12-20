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
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import DialogResult, Widget
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog

from openpilot.system.ui.sunnypilot.lib.styles import style
from openpilot.system.ui.sunnypilot.widgets.tree_dialog import TreeOptionDialog, TreeNode, TreeFolder
from openpilot.selfdrive.ui.ui_state import ui_state

CAR_LIST_JSON_OUT = os.path.join(BASEDIR, "sunnypilot", "selfdrive", "car", "car_list.json")


class LegendWidget(Widget):
  def __init__(self, platform_selector):
    super().__init__()
    self.set_rect(rl.Rectangle(0, 0, 0, 350))
    self._platform_selector = platform_selector
    self._font = gui_app.font(FontWeight.NORMAL)
    self._bold_font = gui_app.font(FontWeight.BOLD)

  def _render(self, rect):
    x = rect.x + 20
    y = rect.y + 20
    rl.draw_text_ex(self._font, tr("Select vehicle to force fingerprint manually."), rl.Vector2(x, y), 40, 0, style.ITEM_DESC_TEXT_COLOR)
    y += 80
    rl.draw_text_ex(self._font, tr("Colors represent vehicle fingerprint status:"), rl.Vector2(x, y), 40, 0, style.ITEM_DESC_TEXT_COLOR)
    y += 80

    items = [
      (style.GREEN, tr("Fingerprinted automatically")),
      (style.BLUE, tr("Manually selected fingerprint")),
      (style.YELLOW, tr("Not fingerprinted or manually selected")),
    ]
    for color, text in items:
      p_color = self._platform_selector.color
      is_active = p_color.r == color.r and p_color.g == color.g and p_color.b == color.b and p_color.a == color.a
      rl.draw_rectangle(int(x), int(y + 5), 30, 30, color)
      font = self._bold_font if is_active else self._font
      text_color = rl.WHITE if is_active else style.ITEM_DESC_TEXT_COLOR
      rl.draw_text_ex(font, f"- {text}", rl.Vector2(x + 50, y - 7), 40, 0, text_color)
      y += 50


class PlatformSelector(Button):
  def __init__(self, on_platform_change: Callable[[], None] | None = None):
    super().__init__(tr("Vehicle"), self._on_clicked, button_style=ButtonStyle.NORMAL)
    self.set_rect(rl.Rectangle(0, 0, 0, 120))

    with open(CAR_LIST_JSON_OUT) as car_list_json:
      self._platforms = json.load(car_list_json)

    self._on_platform_change = on_platform_change
    self.refresh()

  @property
  def text(self):
    return self._label._text

  def set_parent_rect(self, parent_rect):
    super().set_parent_rect(parent_rect)
    self._rect.width = parent_rect.width

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

  def _on_platform_selected(self, dialog, res):
    if res == DialogResult.CONFIRM and dialog.selection_ref:
      offroad_msg = tr("This setting will take effect immediately.") if ui_state.is_offroad else \
                    tr("This setting will take effect once the device enters offroad state.")

      confirm_dialog = ConfirmDialog(offroad_msg, tr("Confirm"))

      callback = partial(self._confirm_platform, dialog.selection_ref)
      gui_app.set_modal_overlay(confirm_dialog, callback=callback)

  def _confirm_platform(self, platform_name, res):
    if res == DialogResult.CONFIRM:
      self._set_platform(platform_name)

  def _show_platform_dialog(self):
    platforms = sorted(self._platforms.keys())
    makes = sorted({self._platforms[p].get('make') for p in platforms})
    folders = [TreeFolder(make, [TreeNode(p, {
      'display_name': p,
      'search_tags': f"{p} {self._platforms[p].get('make')} {' '.join(map(str, self._platforms[p].get('year', [])))} {self._platforms[p].get('model', p)}"
    }) for p in platforms if self._platforms[p].get('make') == make]) for make in makes]
    dialog = TreeOptionDialog(
      tr("Select a vehicle"),
      folders,
      search_title=tr("Search your vehicle"),
      search_subtitle=tr("Enter model year (e.g., 2021) and model (Toyota Corolla):"),
      search_funcs=[lambda node: node.data.get('display_name', ''), lambda node: node.data.get('search_tags', '')]
    )
    callback = partial(self._on_platform_selected, dialog)
    dialog.on_exit = callback
    gui_app.set_modal_overlay(dialog, callback=callback)

  def refresh(self):
    self.color = style.YELLOW
    self._platform = tr("Unrecognized Vehicle")
    self.set_text(tr("No vehicle selected"))

    if bundle := ui_state.params.get("CarPlatformBundle"):
      self._platform = bundle.get("name", "")
      self.set_text(self._platform)
      self.color = style.BLUE
    elif ui_state.CP and ui_state.CP.carFingerprint != "MOCK":
      self._platform = ui_state.CP.carFingerprint
      self.set_text(self._platform)
      self.color = style.GREEN
    self.set_enabled(True)
