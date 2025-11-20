import json
from functools import partial

from openpilot.common.params import Params
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import DialogResult, Widget
from openpilot.system.ui.widgets.confirm_dialog import alert_dialog
from openpilot.system.ui.widgets.list_view import button_item
from openpilot.system.ui.widgets.option_dialog import MultiOptionDialog
from openpilot.system.ui.widgets.scroller import Scroller

from openpilot.sunnypilot.navd.navigationd import Navigationd
from openpilot.system.ui.sunnypilot.widgets.input_dialog import InputDialogSP
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, multiple_button_item_sp


class NavigationLayout(Widget):
  def __init__(self):
    super().__init__()
    self.navd = Navigationd()
    self._params = Params()
    self._initialize_items()
    self._scroller = Scroller(self.items, line_separator=True, spacing=0)

  def _initialize_items(self):
    self.items = [
      button_item("Mapbox token", "Edit", "Enter your mapbox public token", partial(self._show_param_input_dialog, "MapboxToken", "Enter Mapbox Token")),
      button_item("Mapbox route", "Edit", "", partial(self._show_param_input_dialog, "MapboxRoute", "Enter Mapbox Route")),
      button_item("Clear current route", "Clear", "", self.clear_route),
      multiple_button_item_sp("Favorites", "Select favorite route", ["Home", "Work", "Favorites"], 0, callback=self._favorites_callback),
      button_item("Set Home", "Set", "", partial(self._open_favorite_dialog, "home", "Set Home Route")),
      button_item("Set Work", "Set", "", partial(self._open_favorite_dialog, "work", "Set Work Route")),
      button_item("Add Favorite", "Add", "Add a new favorite", self._add_fav),
      button_item("Remove Favorite", "Remove", "Remove a favorite", self._remove_fav),
      toggle_item_sp("Allow navigation", "Enable navigation service", callback=self.update_navigation_visibility, param="AllowNavigation"),
      toggle_item_sp("Mapbox recompute", "Enable automatic route recomputation", param="MapboxRecompute"),
      toggle_item_sp("Navigation allowed", "Allow navigation to automatically take turns", param="NavDesiresAllowed"),
    ]
    (self.mapbox_token_item, self.mapbox_route_item, _, _, self.set_home_item, self.set_work_item, self.add_fav_item, self.remove_fav_item,
     self.allow_navigation_toggle, self.mapbox_recompute_toggle, self.nav_allowed_toggle) = self.items

  def _show_param_input_dialog(self, param_name, title):
    current_text = self._params.get(param_name, return_default=True) or ""
    InputDialogSP(title, current_text=current_text, param=param_name).show()

  def clear_route(self):
    self.navd.route = None
    self._params.remove("MapboxRoute")

  def _favorite_input_callback(self, fav_key, result, text):
    if result == DialogResult.CONFIRM and text:
      self._update_favorite_from_text(text, fav_key)

  def _open_favorite_dialog(self, fav_key, title):
    InputDialogSP(title, current_text=self._get_favorites().get(fav_key, ""), callback=partial(self._favorite_input_callback, fav_key)).show()

  def _add_fav(self):
    InputDialogSP("Favorite Name", "", callback=self._handle_favorite_name_input, min_text_size=1).show()

  def _handle_favorite_name_input(self, result, name):
    if result == DialogResult.CONFIRM and name:
      InputDialogSP(f"Set Route for {name}", "",
                    callback=lambda res, text: self._update_favorite_from_text(text, name, is_fav=True) if res == DialogResult.CONFIRM and text else None,
                    min_text_size=1).show()

  def _update_favorite_from_text(self, text, key, is_fav=False):
    if not text:
      return
    obj = self._get_favorites()
    if is_fav:
      obj.setdefault("favorites", {})[key] = text
    else:
      obj[key] = text
    self._params.put("MapboxFavorites", json.dumps(obj))

  def _get_favorites(self):
    favs_str = self._params.get("MapboxFavorites", "{}")
    try:
      return json.loads(favs_str)
    except Exception:
      return {}

  def _handle_select_favorite(self, result):
    if result == DialogResult.CONFIRM and self._select_dialog.selection:
      route = self._get_favorites().get("favorites", {}).get(self._select_dialog.selection, "")
      if route:
        self._params.put("MapboxRoute", route)
    gui_app.set_modal_overlay(None)

  def _favorites_callback(self, index):
    favs = self._get_favorites()
    if index in (0, 1):
      route = favs.get("home" if index == 0 else "work", "")
      if route:
        self._params.put("MapboxRoute", route)
      return

    favorites_obj = favs.get("favorites", {})
    if not favorites_obj:
      gui_app.set_modal_overlay(alert_dialog(tr("No custom favorites set")))
      return
    self._select_dialog = MultiOptionDialog(tr("Select Favorite"), list(favorites_obj.keys()))
    gui_app.set_modal_overlay(self._select_dialog, callback=self._handle_select_favorite)
    return

  def _handle_remove_favorite(self, result):
    if result == DialogResult.CONFIRM and self._remove_dialog.selection:
      favs = self._get_favorites()
      favorites_obj = favs.get("favorites", {})
      if favorites_obj.pop(self._remove_dialog.selection, None) is not None:
        favs["favorites"] = favorites_obj
        self._params.put("MapboxFavorites", json.dumps(favs))
    gui_app.set_modal_overlay(None)

  def _remove_fav(self):
    favorites_obj = self._get_favorites().get("favorites", {})
    if not favorites_obj:
      gui_app.set_modal_overlay(alert_dialog(tr("No custom favorites to remove")))
      return
    self._remove_dialog = MultiOptionDialog(tr("Remove Favorite"), list(favorites_obj.keys()))
    gui_app.set_modal_overlay(self._remove_dialog, callback=self._handle_remove_favorite)

  def update_navigation_visibility(self, state):
    for item in (self.mapbox_recompute_toggle, self.nav_allowed_toggle, self.set_home_item, self.set_work_item, self.add_fav_item, self.remove_fav_item):
      item.set_visible(state)

  def _update_state(self):
    super()._update_state()
    self.mapbox_token_item.action_item.set_value(self._params.get("MapboxToken", "") or "Mapbox token not set")
    self.mapbox_route_item.action_item.set_value(self._params.get("MapboxRoute", "") or "Destination not set")
    self.update_navigation_visibility(self._params.get_bool("AllowNavigation"))

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
