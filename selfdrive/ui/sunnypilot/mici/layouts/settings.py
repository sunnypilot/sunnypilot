"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.mici.layouts.settings import settings as OP
from openpilot.selfdrive.ui.mici.layouts.settings.settings import SettingsBigButton
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.cruise import CruiseLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.display import DisplayLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.models import ModelsLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.steering import SteeringLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.sunnylink import SunnylinkLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.trips import TripsLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.visuals import VisualsLayoutMici
from openpilot.system.ui.lib.application import gui_app

ICON_SIZE = 70


class SettingsLayoutSP(OP.SettingsLayout):
  def __init__(self):
    OP.SettingsLayout.__init__(self)

    sunnylink_panel = SunnylinkLayoutMici()
    sunnylink_btn = SettingsBigButton("sunnylink", "", "icons_mici/settings/developer/ssh.png")
    sunnylink_btn.set_click_callback(lambda: gui_app.push_widget(sunnylink_panel))

    models_panel = ModelsLayoutMici()
    models_btn = SettingsBigButton("models", "", "../../sunnypilot/selfdrive/assets/offroad/icon_models.png")
    models_btn.set_click_callback(lambda: gui_app.push_widget(models_panel))

    cruise_panel = CruiseLayoutMici()
    cruise_btn = SettingsBigButton("cruise", "", "../../sunnypilot/selfdrive/assets/offroad/icon_vehicle.png")
    cruise_btn.set_click_callback(lambda: gui_app.push_widget(cruise_panel))

    steering_panel = SteeringLayoutMici()
    steering_btn = SettingsBigButton("steering", "", "../../sunnypilot/selfdrive/assets/offroad/icon_lateral.png")
    steering_btn.set_click_callback(lambda: gui_app.push_widget(steering_panel))

    display_panel = DisplayLayoutMici()
    display_btn = SettingsBigButton("display", "", "../../sunnypilot/selfdrive/assets/offroad/icon_display.png")
    display_btn.set_click_callback(lambda: gui_app.push_widget(display_panel))

    visuals_panel = VisualsLayoutMici()
    visuals_btn = SettingsBigButton("visuals", "", "../../sunnypilot/selfdrive/assets/offroad/icon_visuals.png")
    visuals_btn.set_click_callback(lambda: gui_app.push_widget(visuals_panel))

    trips_panel = TripsLayoutMici()
    trips_btn = SettingsBigButton("trips", "", "../../sunnypilot/selfdrive/assets/offroad/icon_trips.png")
    trips_btn.set_click_callback(lambda: gui_app.push_widget(trips_panel))

    items = self._scroller._items.copy()

    items.insert(1, sunnylink_btn)
    items.insert(2, models_btn)
    items.insert(3, cruise_btn)
    items.insert(4, steering_btn)
    items.insert(5, display_btn)
    items.insert(6, visuals_btn)
    items.insert(7, trips_btn)
    self._scroller._items.clear()
    for item in items:
      self._scroller.add_widget(item)
