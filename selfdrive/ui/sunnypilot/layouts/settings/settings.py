import pyray as rl
from dataclasses import dataclass
from enum import IntEnum
from openpilot.selfdrive.ui.layouts.settings import settings as OP
from openpilot.selfdrive.ui.layouts.settings.developer import DeveloperLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.device import DeviceLayoutSP
from openpilot.selfdrive.ui.layouts.settings.firehose import FirehoseLayout
from openpilot.selfdrive.ui.layouts.settings.software import SoftwareLayout
from openpilot.selfdrive.ui.layouts.settings.toggles import TogglesLayout
from openpilot.system.ui.lib.application import gui_app,MousePos
from openpilot.system.ui.widgets.scroller import Scroller
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets.network import WifiManagerUI
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
from selfdrive.ui.sunnypilot.layouts.settings.display import DisplayLayout

OP.PANEL_COLOR = rl.Color(10, 10, 10, 255)
ICON_SIZE = 70

OP.PanelType = IntEnum( # type: ignore
  "PanelType",
  [es.name for es in OP.PanelType] + [
    "SUNNYLINK",
    "MODELS",
    "STEERING",
    "CRUISE",
    "VISUALS",
    "DISPLAY",
    "OSM",
    "TRIPS",
    "VEHICLE",
  ],
  start=0,
  )

@dataclass
class PanelInfo(OP.PanelInfo):
  icon: str = ""


class SettingsLayoutSP(OP.SettingsLayout):
  def __init__(self):
    OP.SettingsLayout.__init__(self)
    self._nav_items: list[Widget] = []

    # Create sidebar scroller
    self._sidebar_scroller = Scroller([], spacing=0, line_separator = False, pad_end=False)

    # Panel configuration
    wifi_manager = WifiManager()
    wifi_manager.set_active(False)

    self._panels = {
      OP.PanelType.DEVICE: PanelInfo("Device", DeviceLayoutSP(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_home.png"),
      OP.PanelType.NETWORK: PanelInfo("Network", WifiManagerUI(wifi_manager), icon="icons/network.png"),
      OP.PanelType.SUNNYLINK: PanelInfo("sunnylink", SunnylinkLayout(), icon="icons/shell.png"),
      OP.PanelType.TOGGLES: PanelInfo("Toggles", TogglesLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_toggle.png"),
      OP.PanelType.SOFTWARE: PanelInfo("Software", SoftwareLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_software.png"),
      OP.PanelType.MODELS: PanelInfo("Models", ModelsLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_models.png"),
      OP.PanelType.STEERING: PanelInfo("Steering", SteeringLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_lateral.png"),
      OP.PanelType.CRUISE: PanelInfo("Cruise", CruiseLayout(), icon="icons/speed_limit.png"),
      OP.PanelType.VISUALS: PanelInfo("Visuals", VisualsLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_visuals.png"),
      OP.PanelType.DISPLAY: PanelInfo("Display", DisplayLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_display.png"),
      OP.PanelType.OSM: PanelInfo("OSM", OSMLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_map.png"),
      OP.PanelType.TRIPS: PanelInfo("Trips", TripsLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_trips.png"),
      OP.PanelType.VEHICLE: PanelInfo("Vehicle", VehicleLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_vehicle.png"),
      OP.PanelType.FIREHOSE: PanelInfo("Firehose", FirehoseLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_firehose.png"),
      OP.PanelType.DEVELOPER: PanelInfo("Developer", DeveloperLayout(), icon="icons/shell.png"),
    }

  def _create_nav_button(self, panel_type: OP.PanelType, panel_info: PanelInfo) -> Widget:
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
            content_x - 20, rect.y, OP.SIDEBAR_WIDTH - 70, OP.NAV_BTN_HEIGHT
          )
          rl.draw_rectangle_rounded(self.container_rect, 0.2, 5, OP.CLOSE_BTN_COLOR)

        if self.panel_info.icon:
          icon_texture = gui_app.texture(self.panel_info.icon, ICON_SIZE, ICON_SIZE, keep_aspect_ratio=True)
          rl.draw_texture(icon_texture, int(content_x), int(rect.y + (OP.NAV_BTN_HEIGHT - icon_texture.height) / 2), rl.WHITE)
          content_x += ICON_SIZE + 20

        # Draw button text (right-aligned)
        text_pos = rl.Vector2(
          content_x,
          rect.y + (OP.NAV_BTN_HEIGHT - text_size.y) / 2
        )
        rl.draw_text_ex(self.parent._font_medium, self.panel_info.name, text_pos, 65, 0, text_color)

        # Store button rect for click detection
        self.panel_info.button_rect = rect

    return NavButton(self, panel_type, panel_info)

  def _draw_sidebar(self, rect: rl.Rectangle):
    rl.draw_rectangle_rec(rect, OP.SIDEBAR_COLOR)

    # Close button
    close_btn_rect = rl.Rectangle(
      rect.x + (rect.width - OP.CLOSE_BTN_SIZE) / 2, rect.y + 45, OP.CLOSE_BTN_SIZE, OP.CLOSE_BTN_SIZE
    )

    pressed = (rl.is_mouse_button_down(rl.MouseButton.MOUSE_BUTTON_LEFT) and
               rl.check_collision_point_rec(rl.get_mouse_position(), close_btn_rect))
    close_color = OP.CLOSE_BTN_PRESSED if pressed else OP.CLOSE_BTN_COLOR
    rl.draw_rectangle_rounded(close_btn_rect, 1.0, 20, close_color)

    close_text_size = measure_text_cached(self._font_medium, OP.SETTINGS_CLOSE_TEXT, 140)
    close_text_pos = rl.Vector2(
      close_btn_rect.x + (close_btn_rect.width - close_text_size.x) / 2,
      close_btn_rect.y + (close_btn_rect.height - close_text_size.y) / 2,
      )
    rl.draw_text_ex(self._font_medium, OP.SETTINGS_CLOSE_TEXT, close_text_pos, 140, 0, OP.TEXT_SELECTED)

    # Store close button rect for click detection
    self._close_btn_rect = close_btn_rect

    # Navigation buttons with scroller
    if not self._nav_items:
      for panel_type, panel_info in self._panels.items():
        nav_button = self._create_nav_button(panel_type, panel_info)
        nav_button.rect.width = rect.width - 100  # Full width minus padding
        nav_button.rect.height = OP.NAV_BTN_HEIGHT
        self._nav_items.append(nav_button)
        self._sidebar_scroller.add_widget(nav_button)

    # Draw navigation section with scroller
    nav_rect = rl.Rectangle(
      rect.x,
      rect.y + 300,  # Starting Y position for nav items
      rect.width,
      rect.height - 300  # Remaining height after close button
    )

    if self._nav_items:
      self._sidebar_scroller.render(nav_rect)
      return


  def _handle_mouse_release(self, mouse_pos: MousePos) -> bool:
    # Check close button
    if rl.check_collision_point_rec(mouse_pos, self._close_btn_rect):
      if self._close_callback:
        self._close_callback()
      return True

    # Check navigation buttons
    for panel_type, panel_info in self._panels.items():
      if rl.check_collision_point_rec(mouse_pos, panel_info.button_rect) and self._sidebar_scroller.scroll_panel.is_touch_valid():
        self.set_current_panel(panel_type)
        return True

    return False
