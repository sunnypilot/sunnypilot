"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from dataclasses import dataclass
from enum import IntEnum

import pyray as rl
from openpilot.selfdrive.ui.layouts.settings import settings as OP
from openpilot.selfdrive.ui.layouts.settings.developer import DeveloperLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.device import DeviceLayoutSP
from openpilot.selfdrive.ui.layouts.settings.firehose import FirehoseLayout
from openpilot.selfdrive.ui.layouts.settings.software import SoftwareLayout
from openpilot.selfdrive.ui.layouts.settings.toggles import TogglesLayout
from openpilot.system.ui.lib.application import gui_app, MousePos
from openpilot.system.ui.lib.multilang import tr_noop
from openpilot.system.ui.sunnypilot.lib.styles import style
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets.network import NetworkUI
from openpilot.system.ui.lib.wifi_manager import WifiManager
from openpilot.system.ui.widgets import Widget
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.models import ModelsLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.sunnylink import SunnylinkLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.osm import OSMLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.trips import TripsLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle import VehicleLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.steering import SteeringLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.cruise import CruiseLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.visuals import VisualsLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.display import DisplayLayout

# from openpilot.selfdrive.ui.sunnypilot.layouts.settings.navigation import NavigationLayout

OP.PANEL_COLOR = rl.Color(10, 10, 10, 255)
ICON_SIZE = 70

OP.PanelType = IntEnum(  # type: ignore
  "PanelType",
  [es.name for es in OP.PanelType] + [
    "SUNNYLINK",
    "MODELS",
    "STEERING",
    "CRUISE",
    "VISUALS",
    "DISPLAY",
    "OSM",
    "NAVIGATION",
    "TRIPS",
    "VEHICLE",
  ],
  start=0,
)


@dataclass
class PanelInfo(OP.PanelInfo):
  icon: str = ""


class NavButton(Widget):
  def __init__(self, parent, p_type, p_info):
    super().__init__()
    self.parent = parent
    self.panel_type = p_type
    self.panel_info = p_info

  def _render(self, rect):
    is_selected = self.panel_type == self.parent._current_panel
    text_color = OP.TEXT_SELECTED if is_selected else OP.TEXT_NORMAL
    content_x = rect.x + 90
    text_size = measure_text_cached(self.parent._font_medium, self.panel_info.name, 65)

    # Draw background if selected
    if is_selected:
      self.container_rect = rl.Rectangle(
        content_x - 50, rect.y, OP.SIDEBAR_WIDTH - 50, OP.NAV_BTN_HEIGHT
      )
      rl.draw_rectangle_rounded(self.container_rect, 0.2, 5, OP.CLOSE_BTN_COLOR)

    if self.panel_info.icon:
      icon_texture = gui_app.texture(self.panel_info.icon, ICON_SIZE, ICON_SIZE, keep_aspect_ratio=True)
      rl.draw_texture(icon_texture, int(content_x), int(rect.y + (OP.NAV_BTN_HEIGHT - icon_texture.height) / 2),
                      rl.WHITE)
      content_x += ICON_SIZE + 20

    # Draw button text (right-aligned)
    text_pos = rl.Vector2(
      content_x,
      rect.y + (OP.NAV_BTN_HEIGHT - text_size.y) / 2
    )
    rl.draw_text_ex(self.parent._font_medium, self.panel_info.name, text_pos, 55, 0, text_color)

    # Store button rect for click detection
    self.panel_info.button_rect = rect


class SettingsLayoutSP(OP.SettingsLayout):
  def __init__(self):
    OP.SettingsLayout.__init__(self)
    self._nav_items: list[Widget] = []

    # Create sidebar scroller
    self._sidebar_scroller = Scroller([], spacing=0, line_separator=False, pad_end=False)

    # Panel configuration
    wifi_manager = WifiManager()
    wifi_manager.set_active(False)

    self._panels = {
      OP.PanelType.DEVICE: PanelInfo(tr_noop("Device"), DeviceLayoutSP(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_home.png"),
      OP.PanelType.NETWORK: PanelInfo(tr_noop("Network"), NetworkUI(wifi_manager), icon="icons/network.png"),
      OP.PanelType.SUNNYLINK: PanelInfo(tr_noop("sunnylink"), SunnylinkLayout(), icon="icons/shell.png"),
      OP.PanelType.TOGGLES: PanelInfo(tr_noop("Toggles"), TogglesLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_toggle.png"),
      OP.PanelType.SOFTWARE: PanelInfo(tr_noop("Software"), SoftwareLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_software.png"),
      OP.PanelType.MODELS: PanelInfo(tr_noop("Models"), ModelsLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_models.png"),
      OP.PanelType.STEERING: PanelInfo(tr_noop("Steering"), SteeringLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_lateral.png"),
      OP.PanelType.CRUISE: PanelInfo(tr_noop("Cruise"), CruiseLayout(), icon="icons/speed_limit.png"),
      OP.PanelType.VISUALS: PanelInfo(tr_noop("Visuals"), VisualsLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_visuals.png"),
      OP.PanelType.DISPLAY: PanelInfo(tr_noop("Display"), DisplayLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_display.png"),
      OP.PanelType.OSM: PanelInfo(tr_noop("OSM"), OSMLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_map.png"),
      # OP.PanelType.NAVIGATION: PanelInfo(tr_noop("Navigation"), NavigationLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_map.png"),
      OP.PanelType.TRIPS: PanelInfo(tr_noop("Trips"), TripsLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_trips.png"),
      OP.PanelType.VEHICLE: PanelInfo(tr_noop("Vehicle"), VehicleLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_vehicle.png"),
      OP.PanelType.DEVELOPER: PanelInfo(tr_noop("Developer"), DeveloperLayout(), icon="icons/shell.png"),
    }

  def _draw_sidebar(self, rect: rl.Rectangle):
    rl.draw_rectangle_rec(rect, OP.SIDEBAR_COLOR)

    # NOTE: close button removed — settings toggled via the sidebar settings button.
    # Adjust top padding so nav items sit higher now that the close button is gone.
    self._close_btn_rect = rl.Rectangle(rect.x, rect.y, 0, 0)

    # Navigation buttons with scroller
    if not self._nav_items:
      for panel_type, panel_info in self._panels.items():
        nav_button = NavButton(self, panel_type, panel_info)
        nav_button.rect.width = rect.width - 100  # Full width minus padding
        nav_button.rect.height = OP.NAV_BTN_HEIGHT
        self._nav_items.append(nav_button)
        self._sidebar_scroller.add_widget(nav_button)

    # Draw navigation section with scroller
    nav_rect = rl.Rectangle(
      rect.x,
      rect.y + style.ITEM_PADDING * 2,  # Start higher since no close button
      rect.width,
      rect.height - style.ITEM_PADDING * 4
    )

    if self._nav_items:
      self._sidebar_scroller.render(nav_rect)
      return

  def _handle_mouse_release(self, mouse_pos: MousePos) -> bool:
    # Close button removed: settings closed via sidebar settings toggle

    # Check navigation buttons
    for panel_type, panel_info in self._panels.items():
      if rl.check_collision_point_rec(mouse_pos, panel_info.button_rect) and self._sidebar_scroller.scroll_panel.is_touch_valid():
        self.set_current_panel(panel_type)
        return True

    return False

  def show_event(self):
    super().show_event()
    self._panels[self._current_panel].instance.show_event()
    self._sidebar_scroller.show_event()
