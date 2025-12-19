"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json
from functools import partial

from openpilot.common.params import Params
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import DialogResult, Widget
from openpilot.system.ui.widgets.confirm_dialog import alert_dialog
from openpilot.system.ui.widgets.list_view import button_item
from openpilot.system.ui.widgets.option_dialog import MultiOptionDialog
from openpilot.system.ui.widgets.scroller_tici import Scroller

from openpilot.sunnypilot.navd.navigationd import Navigationd
from openpilot.system.ui.sunnypilot.widgets.input_dialog import InputDialogSP
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.nav_text_autofill import AutofillInputDialogSP
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, multiple_button_item_sp


class NavigationLayout(Widget):
  def __init__(self):
    super().__init__()
    self._navd = Navigationd()
    self._params = Params()

    self._mapbox_token_item = button_item("Mapbox token", "Edit", "Enter your mapbox public token",
                                         partial(self._show_param_input, "MapboxToken", "Enter Mapbox Token"))
    self._mapbox_route_item = button_item("Mapbox route", "Edit", "",
                                         partial(self._show_param_input, "MapboxRoute", "Enter Mapbox Route"))

    self._vis_items = [
      button_item("Set Home", "Set", "", partial(self._open_fav_dialog, "home", "Set Home Route")),
      button_item("Set Work", "Set", "", partial(self._open_fav_dialog, "work", "Set Work Route")),
      button_item("Add Favorite", "Add", "Add a new favorite", self._add_fav),
      button_item("Remove Favorite", "Remove", "Remove a favorite", self._remove_fav),
      toggle_item_sp("Mapbox recompute", "Enable automatic route recomputation", param="MapboxRecompute"),
      toggle_item_sp("Navigation allowed", "Allow navigation to automatically take turns", param="NavDesiresAllowed"),
    ]

    self.items = [
      self._mapbox_token_item, self._mapbox_route_item,
      button_item("Clear current route", "Clear", "", self._clear_route),
      multiple_button_item_sp("Favorites", "Select favorite route", ["Home", "Work", "Favorites"], 0, callback=self._favorites_callback),
      *self._vis_items[:4],
      toggle_item_sp("Allow navigation", "Enable navigation service", callback=self._update_navigation_visibility, param="AllowNavigation"),
      *self._vis_items[4:],
    ]
    self._scroller = Scroller(self.items, line_separator=True, spacing=0)

  @property
  def _favs(self):
    try:
      return json.loads(self._params.get("MapboxFavorites") or "{}")
    except Exception:
      return {}

  def _show_param_input(self, param, title):
    if param == "MapboxRoute":
      AutofillInputDialogSP(title, current_text=self._params.get(param, return_default=True) or "", param=param).show()
    else:
      InputDialogSP(title, current_text=self._params.get(param, return_default=True) or "", param=param).show()

  def _clear_route(self):
    self._navd.route = None
    self._params.remove("MapboxRoute")

  def _handle_save_fav(self, key, is_fav, res, text):
    if res == DialogResult.CONFIRM and text:
      favs = self._favs
      (favs.setdefault("favorites", {}) if is_fav else favs)[key] = text
      self._params.put("MapboxFavorites", json.dumps(favs))

  def _open_fav_dialog(self, key, title):
    InputDialogSP(title, current_text=self._favs.get(key, ""), callback=partial(self._handle_save_fav, key, False)).show()

  def _add_fav_name_cb(self, res, name):
    if res == DialogResult.CONFIRM and name:
      InputDialogSP(f"Set Route for {name}", "", callback=partial(self._handle_save_fav, name, True), min_text_size=1).show()

  def _add_fav(self):
    InputDialogSP("Favorite Name", "", callback=self._add_fav_name_cb, min_text_size=1).show()

  def _set_mapbox_route_cb(self, favorites, selection):
    self._params.put("MapboxRoute", favorites[selection])

  def _favorites_callback(self, index):
    favs = self._favs
    if index < 2:
      if route := favs.get(["home", "work"][index]):
        self._params.put("MapboxRoute", route)
    elif favorites := favs.get("favorites"):
      self._show_list_dialog(tr("Select Favorite"), list(favorites.keys()), partial(self._set_mapbox_route_cb, favorites))
    else:
      gui_app.set_modal_overlay(alert_dialog(tr("No custom favorites set")))

  def _remove_fav_cb(self, selection):
    favs = self._favs
    if favs.get("favorites", {}).pop(selection, None):
      self._params.put("MapboxFavorites", json.dumps(favs))

  def _remove_fav(self):
    if favorites := self._favs.get("favorites"):
      self._show_list_dialog(tr("Remove Favorite"), list(favorites.keys()), self._remove_fav_cb)
    else:
      gui_app.set_modal_overlay(alert_dialog(tr("No custom favorites to remove")))

  def _list_dialog_cb(self, callback, res):
    if res == DialogResult.CONFIRM and self._dialog.selection:
      callback(self._dialog.selection)
    gui_app.set_modal_overlay(None)

  def _show_list_dialog(self, title, items, callback):
    self._dialog = MultiOptionDialog(title, items)
    gui_app.set_modal_overlay(self._dialog, callback=partial(self._list_dialog_cb, callback))

  def _update_navigation_visibility(self, state):
    for item in self._vis_items:
      item.set_visible(state)

  def _update_state(self):
    self._mapbox_token_item.action_item.set_value(self._params.get("MapboxToken") or "Mapbox token not set")
    self._mapbox_route_item.action_item.set_value(self._params.get("MapboxRoute") or "Destination not set")
    self._update_navigation_visibility(self._params.get_bool("AllowNavigation"))

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
