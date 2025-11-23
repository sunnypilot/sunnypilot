"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json
import pyray as rl
from collections.abc import Callable
from functools import partial

from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import DialogResult, Widget
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog
from openpilot.system.ui.widgets.option_dialog import MultiOptionDialog

from opendbc.sunnypilot.car.platform_list import CAR_LIST_JSON_OUT
from openpilot.system.ui.sunnypilot.lib.styles import style
from openpilot.system.ui.sunnypilot.widgets.helpers.fuzzy_search import search_from_list
from openpilot.system.ui.sunnypilot.widgets.input_dialog import InputDialogSP
from openpilot.selfdrive.ui.sunnypilot.ui_state import ui_state_sp


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

    self._offroad = False
    self._on_platform_change = on_platform_change
    self.refresh(False)

  @property
  def text(self):
    return self._label._text

  def set_parent_rect(self, parent_rect):
    super().set_parent_rect(parent_rect)
    self._rect.width = parent_rect.width

  def _on_clicked(self):
    if ui_state_sp.params.get("CarPlatformBundle"):
      ui_state_sp.params.remove("CarPlatformBundle")
      self.refresh(self._offroad)
      if self._on_platform_change:
        self._on_platform_change()
    else:
      InputDialogSP(tr("Please type in your vehicle's name"), callback=self._on_search_input).show()

  def _set_platform(self, platform_name):
    if data := self._platforms.get(platform_name):
      ui_state_sp.params.put("CarPlatformBundle", {**data, "name": platform_name})
      self.refresh(self._offroad)
      if self._on_platform_change:
        self._on_platform_change()

  def _on_platform_selected(self, dialog, res):
    if res == DialogResult.CONFIRM and dialog.selection:
      self._set_platform(dialog.selection)

  def _search_platforms(self, query):
    results = search_from_list(query, sorted(self._platforms.keys()))
    if not results:
      gui_app.set_modal_overlay(ConfirmDialog(tr(f"No vehicles found for query: {query}"), tr("OK"), cancel_text=""))
      return

    dialog = MultiOptionDialog(tr("Select a vehicle"), results)
    gui_app.set_modal_overlay(dialog, partial(self._on_platform_selected, dialog))


  def _on_search_input(self, res, text):
    if res == DialogResult.CONFIRM and text:
      self._search_platforms(text)
      self.refresh(self._offroad)

  def refresh(self, offroad):
    self._offroad = offroad
    self.brand = ""
    self.color = style.YELLOW,
    self._platform = tr("Unrecognized Vehicle")
    self.set_text(tr("No vehicle selected"))

    if bundle := ui_state_sp.params.get("CarPlatformBundle"):
      self._platform = bundle.get("name", "")
      self.brand = bundle.get("brand", "")
      self.set_text(self._platform)
      self.color = style.BLUE
    elif ui_state_sp.CP and ui_state_sp.CP.carFingerprint != "MOCK":
      self._platform = ui_state_sp.CP.carFingerprint
      self.brand = ui_state_sp.CP.brand
      self.set_text(self._platform)
      self.color = style.GREEN
    self.set_enabled(True)
