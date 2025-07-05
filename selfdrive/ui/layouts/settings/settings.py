import pyray as rl
from dataclasses import dataclass
from enum import IntEnum
from collections.abc import Callable
from openpilot.selfdrive.ui.layouts.settings.developer import DeveloperLayout
from openpilot.selfdrive.ui.layouts.settings.device import DeviceLayout
from openpilot.selfdrive.ui.layouts.settings.firehose import FirehoseLayout
from openpilot.selfdrive.ui.layouts.settings.software import SoftwareLayout
from openpilot.selfdrive.ui.layouts.settings.toggles import TogglesLayout
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.scroller import Scroller
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.selfdrive.ui.layouts.network import NetworkLayout
from openpilot.system.ui.lib.widget import Widget
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.models import ModelsLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.sunnylink import SunnylinkLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.osm import OSMLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.trips import TripsLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle import VehicleLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.steering import SteeringLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.cruise import CruiseLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.visuals import VisualsLayout

# Import individual panels

SETTINGS_CLOSE_TEXT = "X"
# Constants
SIDEBAR_WIDTH = 500
CLOSE_BTN_SIZE = 200
NAV_BTN_HEIGHT = 110
PANEL_MARGIN = 50
ICON_SIZE = 80

# Colors
SIDEBAR_COLOR = rl.BLACK
PANEL_COLOR = rl.BLACK
CLOSE_BTN_COLOR = rl.Color(41, 41, 41, 255)
CLOSE_BTN_PRESSED = rl.Color(59, 59, 59, 255)
TEXT_NORMAL = rl.Color(128, 128, 128, 255)
TEXT_SELECTED = rl.Color(255, 255, 255, 255)


class PanelType(IntEnum):
  DEVICE = 0
  NETWORK = 1
  TOGGLES = 2
  SOFTWARE = 3
  FIREHOSE = 4
  DEVELOPER = 5
  SUNNYLINK = 6
  MODELS = 7
  STEERING = 8
  CRUISE = 9
  VISUALS = 10
  OSM = 11
  TRIPS = 12
  VEHICLE = 13


@dataclass
class PanelInfo:
  name: str
  instance: object
  button_rect: rl.Rectangle = rl.Rectangle(0, 0, 0, 0)
  icon: str = ""


class SettingsLayout(Widget):
  def __init__(self):
    super().__init__()
    self._current_panel = PanelType.DEVICE
    self._nav_items: list[Widget] = []

    # Create sidebar scroller
    self._sidebar_scroller = Scroller([], spacing=0, line_separator = False, pad_end=False)


    # Panel configuration
    self._panels = {
      PanelType.DEVICE: PanelInfo("Device", DeviceLayout(), icon="icons/shell.png"),
      PanelType.NETWORK: PanelInfo("Network", NetworkLayout(), icon="icons/network.png"),
      PanelType.SUNNYLINK: PanelInfo("sunnylink", SunnylinkLayout(), icon="icons/shell.png"),
      PanelType.TOGGLES: PanelInfo("Toggles", TogglesLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_toggle.png"),
      PanelType.SOFTWARE: PanelInfo("Software", SoftwareLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_software.png"),
      PanelType.MODELS: PanelInfo("Models", ModelsLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_models.png"),
      PanelType.STEERING: PanelInfo("Steering", SteeringLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_lateral.png"),
      PanelType.CRUISE: PanelInfo("Cruise", CruiseLayout(), icon="icons/speed_limit.png"),
      PanelType.VISUALS: PanelInfo("Visuals", VisualsLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_visuals.png"),
      PanelType.OSM: PanelInfo("OSM", OSMLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_map.png"),
      PanelType.TRIPS: PanelInfo("Trips", TripsLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_trips.png"),
      PanelType.VEHICLE: PanelInfo("Vehicle", VehicleLayout(), icon="../../sunnypilot/selfdrive/assets/offroad/icon_vehicle.png"),
      PanelType.FIREHOSE: PanelInfo("Firehose", FirehoseLayout(), icon="icons/shell.png"),
      PanelType.DEVELOPER: PanelInfo("Developer", DeveloperLayout(), icon="icons/shell.png"),
    }

    self._font_medium = gui_app.font(FontWeight.MEDIUM)
    self._font_bold = gui_app.font(FontWeight.SEMI_BOLD)

    # Callbacks
    self._close_callback: Callable | None = None

  def set_callbacks(self, on_close: Callable):
    self._close_callback = on_close

  def _render(self, rect: rl.Rectangle):
    # Calculate layout
    sidebar_rect = rl.Rectangle(rect.x, rect.y, SIDEBAR_WIDTH, rect.height)
    panel_rect = rl.Rectangle(rect.x + SIDEBAR_WIDTH, rect.y, rect.width - SIDEBAR_WIDTH, rect.height)

    # Draw components
    self._draw_sidebar(sidebar_rect)
    self._draw_current_panel(panel_rect)

  def _create_nav_button(self, panel_type: PanelType, panel_info: PanelInfo) -> Widget:
    class NavButton(Widget):
      def __init__(self, parent, p_type, p_info):
        super().__init__()
        self.parent = parent
        self.panel_type = p_type
        self.panel_info = p_info

      def _render(self, rect):
        is_selected = self.panel_type == self.parent._current_panel
        text_color = TEXT_SELECTED if is_selected else TEXT_NORMAL
        content_x = rect.x + 90
        text_size = measure_text_cached(self.parent._font_medium, self.panel_info.name, 65)

        if self.panel_info.icon:
          icon_texture = gui_app.texture(self.panel_info.icon, ICON_SIZE, ICON_SIZE)
          rl.draw_texture(icon_texture, int(content_x), int(rect.y + (NAV_BTN_HEIGHT - text_size.y) / 2), rl.WHITE)
          content_x += ICON_SIZE + 20

        # Draw button text (right-aligned)
        text_pos = rl.Vector2(
          content_x,
          rect.y + (NAV_BTN_HEIGHT - text_size.y) / 2
        )
        rl.draw_text_ex(self.parent._font_medium, self.panel_info.name, text_pos, 65, 0, text_color)

        # Store button rect for click detection
        self.panel_info.button_rect = rect

    return NavButton(self, panel_type, panel_info)

  def _draw_sidebar(self, rect: rl.Rectangle):
    rl.draw_rectangle_rec(rect, SIDEBAR_COLOR)

    # Close button
    close_btn_rect = rl.Rectangle(
      rect.x + (rect.width - CLOSE_BTN_SIZE) / 2, rect.y + 45, CLOSE_BTN_SIZE, CLOSE_BTN_SIZE
    )

    pressed = (rl.is_mouse_button_down(rl.MouseButton.MOUSE_BUTTON_LEFT) and
               rl.check_collision_point_rec(rl.get_mouse_position(), close_btn_rect))
    close_color = CLOSE_BTN_PRESSED if pressed else CLOSE_BTN_COLOR
    rl.draw_rectangle_rounded(close_btn_rect, 1.0, 20, close_color)

    close_text_size = measure_text_cached(self._font_bold, SETTINGS_CLOSE_TEXT, 140)
    close_text_pos = rl.Vector2(
      close_btn_rect.x + (close_btn_rect.width - close_text_size.x) / 2,
      close_btn_rect.y + (close_btn_rect.height - close_text_size.y) / 2,
    )
    rl.draw_text_ex(self._font_bold, SETTINGS_CLOSE_TEXT, close_text_pos, 140, 0, TEXT_SELECTED)

    # Store close button rect for click detection
    self._close_btn_rect = close_btn_rect

    # Navigation buttons with scroller
    if not self._nav_items:
      for panel_type, panel_info in self._panels.items():
        nav_button = self._create_nav_button(panel_type, panel_info)
        nav_button.rect.width = rect.width - 100  # Full width minus padding
        nav_button.rect.height = NAV_BTN_HEIGHT
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

    # Navigation buttons
    y = rect.y + 300
    for panel_type, panel_info in self._panels.items():
      button_rect = rl.Rectangle(rect.x + 50, y, rect.width - 150, NAV_BTN_HEIGHT)

      # Button styling
      is_selected = panel_type == self._current_panel
      text_color = TEXT_SELECTED if is_selected else TEXT_NORMAL
      # Draw button text (right-aligned)
      text_size = measure_text_cached(self._font_medium, panel_info.name, 65)
      text_pos = rl.Vector2(
        button_rect.x + button_rect.width - text_size.x, button_rect.y + (button_rect.height - text_size.y) / 2
      )
      rl.draw_text_ex(self._font_medium, panel_info.name, text_pos, 65, 0, text_color)

      # Store button rect for click detection
      panel_info.button_rect = button_rect

      y += NAV_BTN_HEIGHT

  def _draw_current_panel(self, rect: rl.Rectangle):
    rl.draw_rectangle_rounded(
      rl.Rectangle(rect.x + 10, rect.y + 10, rect.width - 20, rect.height - 20), 0.04, 30, PANEL_COLOR
    )
    content_rect = rl.Rectangle(rect.x + PANEL_MARGIN, rect.y + 25, rect.width - (PANEL_MARGIN * 2), rect.height - 50)
    # rl.draw_rectangle_rounded(content_rect, 0.03, 30, PANEL_COLOR)
    panel = self._panels[self._current_panel]
    if panel.instance:
      panel.instance.render(content_rect)

  def _handle_mouse_release(self, mouse_pos: rl.Vector2) -> bool:
    # Check close button
    if rl.check_collision_point_rec(mouse_pos, self._close_btn_rect):
      if self._close_callback:
        self._close_callback()
      return True

    # Check navigation buttons
    for panel_type, panel_info in self._panels.items():
      if rl.check_collision_point_rec(mouse_pos, panel_info.button_rect):
        self.set_current_panel(panel_type)
        return True

    return False

  def set_current_panel(self, panel_type: PanelType):
    if panel_type != self._current_panel:
      self._current_panel = panel_type

  def close_settings(self):
    if self._close_callback:
      self._close_callback()
