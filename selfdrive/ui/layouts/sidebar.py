import pyray as rl
import time
from dataclasses import dataclass
from collections.abc import Callable
from cereal import log
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight, MousePos, FONT_SCALE
from openpilot.system.ui.lib.multilang import tr, tr_noop
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget

SIDEBAR_WIDTH = 300
METRIC_HEIGHT = 126
METRIC_WIDTH = 240
METRIC_MARGIN = 30
FONT_SIZE = 35

MAX_CPU_TEMP = 107
MAX_GPU_TEMP = 107

ThermalStatus = log.DeviceState.ThermalStatus
NetworkType = log.DeviceState.NetworkType
PandaState = log.PandaState
PandaType = PandaState.PandaType

# Thermal colors per severity
THERMAL_COLORS = {
  ThermalStatus.green: rl.Color(0xA0, 0xF0, 0xB0, 0xFF),
  ThermalStatus.yellow: rl.Color(0xF0, 0xE6, 0xA0, 0xFF),
  ThermalStatus.red: rl.Color(0xF8, 0xB0, 0xB0, 0xFF),
  ThermalStatus.danger: rl.Color(0xF8, 0xB0, 0xB0, 0xFF),
  ThermalStatus.offroad: rl.Color(0xCC, 0xCC, 0xCC, 0xFF),
}

# Minimal-ish network type labels
NETWORK_TYPES = {
  NetworkType.none: tr_noop("No Network"),
  NetworkType.wifi: tr_noop("Wi-Fi"),
  NetworkType.cell2G: tr_noop("2G"),
  NetworkType.cell3G: tr_noop("3G"),
  NetworkType.cell4G: tr_noop("4G"),
  NetworkType.cell5G: tr_noop("5G"),
  NetworkType.cellUnknown: tr_noop("Cell"),
}

# Small helper data structures for card metrics
@dataclass
class Metric:
  label: str
  value: str
  icon_name: str | None = None
  color: rl.Color | None = None


@dataclass
class Colors:
  BG = rl.Color(0x05, 0x0A, 0x0F, 0xFF)  # Deep, subtle navy / charcoal
  TEXT_PRIMARY = rl.Color(0xF5, 0xF5, 0xF7, 0xFF)  # Off-white
  TEXT_MUTED = rl.Color(0x90, 0x95, 0x9A, 0xFF)
  TEXT_ACCENT = rl.Color(0xA0, 0xF0, 0xB0, 0xFF)   # Mint accent
  DIVIDER = rl.Color(0x22, 0x25, 0x2A, 0xFF)

  STATUS_CARD_BG = rl.Color(0x11, 0x16, 0x1C, 0xEE)
  STATUS_CARD_BORDER = rl.Color(0x2A, 0x30, 0x3A, 0xFF)

  METRIC_BG = rl.Color(0x0D, 0x13, 0x1A, 0xEE)
  METRIC_BORDER = rl.Color(0x1F, 0x26, 0x30, 0xFF)

  BADGE_BG = rl.Color(0x18, 0x21, 0x2A, 0xFF)
  BADGE_GREEN = rl.Color(0x9B, 0xE7, 0xB0, 0xFF)
  BADGE_YELLOW = rl.Color(0xF5, 0xE0, 0xA0, 0xFF)
  BADGE_RED = rl.Color(0xF7, 0xB0, 0xB8, 0xFF)

  WIFI_GOOD = rl.Color(0x9B, 0xE7, 0xB0, 0xFF)
  WIFI_OK = rl.Color(0xF5, 0xE0, 0xA0, 0xFF)
  WIFI_BAD = rl.Color(0xF7, 0xB0, 0xB8, 0xFF)

  TEMP_COOL = rl.Color(0x9B, 0xE7, 0xB0, 0xFF)
  TEMP_WARM = rl.Color(0xF5, 0xE0, 0xA0, 0xFF)
  TEMP_HOT = rl.Color(0xF7, 0xB0, 0xB8, 0xFF)

  PANDA_CONNECTED = rl.Color(0x9B, 0xE7, 0xB0, 0xFF)
  PANDA_DISCONNECTED = rl.Color(0xF7, 0xB0, 0xB8, 0xFF)


class Sidebar(Widget):
  def __init__(self):
    super().__init__()
    self._rect = rl.Rectangle(0, 0, SIDEBAR_WIDTH, 0)

    self._font_regular: rl.Font = gui_app.font(FontWeight.NORMAL)
    self._font_medium: rl.Font = gui_app.font(FontWeight.MEDIUM)
    self._font_semibold: rl.Font = gui_app.font(FontWeight.SEMI_BOLD)
    self._font_bold: rl.Font = gui_app.font(FontWeight.BOLD)

    # Textures
    self._logo = gui_app.texture("icons/sidebar/konik_logo.png", 96, 96)
    self._settings_icon = gui_app.texture("icons/sidebar/settings.png", 44, 44)
    self._wifi_icon = gui_app.texture("icons/sidebar/wifi.png", 28, 28)
    self._wifi_off_icon = gui_app.texture("icons/sidebar/wifi_off.png", 28, 28)
    self._temp_icon = gui_app.texture("icons/sidebar/temp.png", 32, 32)
    self._car_icon = gui_app.texture("icons/sidebar/car.png", 32, 32)
    self._panda_icon = gui_app.texture("icons/sidebar/panda.png", 32, 32)
    self._record_icon = gui_app.texture("icons/sidebar/mic.png", 26, 26)

    # State
    self._recording_audio = False
    self._net_type: str = tr("No Network")
    self._net_strength: int = 0  # 0-5
    self._thermal_status: ThermalStatus = ThermalStatus.offroad
    self._cpu_temp: float = 0.0
    self._gpu_temp: float = 0.0
    self._panda_type: PandaType | None = None
    self._panda_state: PandaState | None = None
    self._panda_present: bool = False
    self._vehicle_info_line: str = tr("No Vehicle")

    self._settings_button_action: Callable[[], None] | None = None

    # Smooth hover feedback for settings
    self._settings_hover_t = 0.0

    self.set_visible(lambda: True)

  def set_rect(self, rect: rl.Rectangle) -> None:
    self._rect = rl.Rectangle(rect.x, rect.y, SIDEBAR_WIDTH, rect.height)

  def set_settings_action(self, cb: Callable[[], None]):
    self._settings_button_action = cb

  # Public API: if the onroad layout wants vehicle status text
  def update_vehicle_info(self, text: str):
    self._vehicle_info_line = text

  def _update_state(self) -> None:
    sm = ui_state.sm
    if not sm.updated['deviceState']:
      return

    device_state = sm['deviceState']

    self._recording_audio = ui_state.recording_audio
    self._update_network_status(device_state)
    self._update_temperature_status(device_state)
    self._update_connection_status(device_state)
    self._update_panda_status()

  def _update_network_status(self, device_state):
    self._net_type = NETWORK_TYPES.get(device_state.networkType.raw, tr_noop("Unknown"))
    strength = device_state.networkStrength
    self._net_strength = max(0, min(5, strength.raw + 1)) if strength.raw > 0 else 0

  def _update_temperature_status(self, device_state):
    self._thermal_status = device_state.thermalStatus
    self._cpu_temp = max(0.0, float(device_state.cpuTempC[0] if device_state.cpuTempC else 0.0))
    self._gpu_temp = max(0.0, float(device_state.gpuTempC[0] if device_state.gpuTempC else 0.0))

  def _update_connection_status(self, device_state):
    # Nothing super detailed for now; we just rely on network type & strength
    pass

  def _update_panda_status(self):
    sm = ui_state.sm
    self._panda_present = sm.valid['pandaStates'] and len(sm['pandaStates']) > 0
    if self._panda_present:
      panda = sm['pandaStates'][0]
      self._panda_state = panda
      self._panda_type = panda.pandaType
    else:
      self._panda_state = None
      self._panda_type = None

  # Input handling: click on settings button
  def _handle_mouse_release(self, mouse: MousePos) -> None:
    if self._settings_button_action is None:
      return

    _, settings_rect = self._layout_header(self._rect)
    if self._point_in_rect(mouse.x, mouse.y, settings_rect):
      self._settings_button_action()

  @staticmethod
  def _point_in_rect(x: float, y: float, rect: rl.Rectangle) -> bool:
    return rect.x <= x <= rect.x + rect.width and rect.y <= y <= rect.y + rect.height

  # Layout helpers
  def _layout_header(self, rect: rl.Rectangle):
    padding = 22
    content_width = rect.width - padding * 2

    logo_size = 72
    y = rect.y + 26

    logo_rect = rl.Rectangle(
      rect.x + padding,
      y,
      logo_size,
      logo_size,
    )

    # Right side: Konik + state + settings icon
    settings_size = 42
    settings_rect = rl.Rectangle(
      rect.x + rect.width - padding - settings_size,
      y + (logo_size - settings_size) / 2,
      settings_size,
      settings_size,
    )

    return (logo_rect, settings_rect)

  def _render(self, rect: rl.Rectangle) -> None:
    r = self._rect

    # Sidebar background
    rl.draw_rectangle_rec(r, Colors.BG)

    # Header
    logo_rect, settings_rect = self._layout_header(r)
    self._draw_header(r, logo_rect, settings_rect)

    # Cards region
    card_top = logo_rect.y + logo_rect.height + 30
    card_left = r.x + 16
    card_right = r.x + r.width - 16
    card_width = card_right - card_left

    # Status card (Konik / vehicle / recording)
    status_card_rect = rl.Rectangle(card_left, card_top, card_width, 112)
    self._draw_status_card(status_card_rect)

    # Metric cards grid
    metrics_top = status_card_rect.y + status_card_rect.height + 20
    self._draw_metric_cards_grid(card_left, metrics_top, card_width)

  def _draw_header(self, rect: rl.Rectangle, logo_rect: rl.Rectangle, settings_rect: rl.Rectangle):
    # Logo
    rl.draw_texture_pro(
      self._logo,
      rl.Rectangle(0, 0, self._logo.width, self._logo.height),
      logo_rect,
      rl.Vector2(0, 0),
      0.0,
      rl.WHITE,
    )

    # Konik Stable text + mini status below
    text_x = logo_rect.x + logo_rect.width + 14
    text_y = logo_rect.y + 8

    title = "Konik Stable"
    title_size = measure_text_cached(self._font_semibold, title, 26)
    rl.draw_text_ex(
      self._font_semibold,
      title,
      rl.Vector2(text_x, text_y),
      26,
      0,
      Colors.TEXT_PRIMARY,
    )

    # Subtle "UI" or mode description
    mode_text = tr("Onroad UI")
    mode_size = measure_text_cached(self._font_regular, mode_text, 20)
    rl.draw_text_ex(
      self._font_regular,
      mode_text,
      rl.Vector2(text_x, text_y + title_size.y + 4),
      20,
      0,
      Colors.TEXT_MUTED,
    )

    # Settings icon hover state
    mx, my = rl.get_mouse_position()
    hovering = self._point_in_rect(mx, my, settings_rect)
    target = 1.0 if hovering else 0.0
    self._settings_hover_t += (target - self._settings_hover_t) * 0.15

    # Draw settings button with hover halo
    if self._settings_hover_t > 0.01:
      halo_radius = settings_rect.width / 2 + 10 * self._settings_hover_t
      rl.draw_circle(
        int(settings_rect.x + settings_rect.width / 2),
        int(settings_rect.y + settings_rect.height / 2),
        halo_radius,
        rl.Color(255, 255, 255, int(20 * self._settings_hover_t)),
      )

    rl.draw_texture_pro(
      self._settings_icon,
      rl.Rectangle(0, 0, self._settings_icon.width, self._settings_icon.height),
      settings_rect,
      rl.Vector2(0, 0),
      0.0,
      rl.Color(255, 255, 255, 230),
    )

  def _draw_status_card(self, rect: rl.Rectangle):
    # Background card with border
    card_roundness = 0.4
    rl.draw_rectangle_rounded(rect, card_roundness, 8, Colors.STATUS_CARD_BG)
    rl.draw_rectangle_rounded_lines_ex(rect, card_roundness, 8, 2, Colors.STATUS_CARD_BORDER)

    padding = 16
    inner_x = rect.x + padding
    inner_y = rect.y + padding
    inner_w = rect.width - padding * 2

    # Left: small dot + "System" label and state
    # Right: audio recording + short timestamp maybe

    # System state
    system_label = tr("System")
    system_state = tr("Ready") if ui_state.started else tr("Idle")

    # Dot to indicate overall health: based on thermal + panda
    ok = (self._thermal_status in (ThermalStatus.green, ThermalStatus.offroad)) and self._panda_present
    warn = (self._thermal_status == ThermalStatus.yellow) or not self._panda_present
    dot_color = Colors.BADGE_GREEN if ok else Colors.BADGE_YELLOW if warn else Colors.BADGE_RED

    # Dot
    dot_radius = 6
    rl.draw_circle(int(inner_x + dot_radius), int(inner_y + dot_radius + 2), dot_radius, dot_color)

    # Label & state
    label_x = inner_x + dot_radius * 2 + 8
    rl.draw_text_ex(
      self._font_medium,
      system_label,
      rl.Vector2(label_x, inner_y),
      22,
      0,
      Colors.TEXT_MUTED,
    )

    rl.draw_text_ex(
      self._font_semibold,
      system_state,
      rl.Vector2(label_x, inner_y + 24),
      24,
      0,
      Colors.TEXT_PRIMARY,
    )

    # Vehicle line below
    vehicle_label = self._vehicle_info_line
    vehicle_y = inner_y + 24 + 26 + 6
    vehicle_color = Colors.TEXT_MUTED
    rl.draw_text_ex(
      self._font_regular,
      vehicle_label,
      rl.Vector2(inner_x, vehicle_y),
      20,
      0,
      vehicle_color,
    )

    # Right side: recording badge if active
    if self._recording_audio:
      badge_text = tr("Recording")
      badge_padding_x = 10
      badge_padding_y = 6
      text_size = measure_text_cached(self._font_medium, badge_text, 18)
      badge_w = text_size.x + self._record_icon.width + badge_padding_x * 3
      badge_h = text_size.y + badge_padding_y * 2

      badge_rect = rl.Rectangle(
        rect.x + rect.width - badge_w - 16,
        rect.y + rect.height - badge_h - 12,
        badge_w,
        badge_h,
      )

      rl.draw_rectangle_rounded(badge_rect, 0.6, 8, Colors.BADGE_BG)
      rl.draw_rectangle_rounded_lines_ex(badge_rect, 0.6, 8, 1.5, Colors.BADGE_RED)

      icon_x = badge_rect.x + badge_padding_x
      icon_y = badge_rect.y + (badge_rect.height - self._record_icon.height) / 2
      rl.draw_texture(
        self._record_icon,
        int(icon_x),
        int(icon_y),
        Colors.BADGE_RED,
      )

      text_x = icon_x + self._record_icon.width + badge_padding_x
      text_y = badge_rect.y + (badge_rect.height - text_size.y) / 2
      rl.draw_text_ex(
        self._font_medium,
        badge_text,
        rl.Vector2(text_x, text_y),
        18,
        0,
        Colors.TEXT_PRIMARY,
      )

  def _draw_metric_cards_grid(self, left: float, top: float, width: float):
    # We'll do a simple vertical stack of compact cards for:
    # 1. Connectivity (Wi-Fi / network)
    # 2. Thermal (CPU/GPU temp)
    # 3. Panda / peripherals
    card_height = 74
    gap = 14

    # Connectivity card
    conn_rect = rl.Rectangle(left, top, width, card_height)
    self._draw_connectivity_card(conn_rect)

    # Thermal card
    therm_rect = rl.Rectangle(left, conn_rect.y + card_height + gap, width, card_height)
    self._draw_thermal_card(therm_rect)

    # Panda / car interface card
    panda_rect = rl.Rectangle(left, therm_rect.y + card_height + gap, width, card_height)
    self._draw_panda_card(panda_rect)

  def _draw_metric_card(self, rect: rl.Rectangle, title: str, subtitle: str, icon: rl.Texture, color: rl.Color):
    # Generic medium-round card
    roundness = 0.4
    rl.draw_rectangle_rounded(rect, roundness, 8, Colors.METRIC_BG)
    rl.draw_rectangle_rounded_lines_ex(rect, roundness, 8, 2, Colors.METRIC_BORDER)

    padding = 14
    inner_x = rect.x + padding
    inner_y = rect.y + padding

    # Icon area
    icon_box = rl.Rectangle(
      inner_x,
      inner_y,
      32,
      32,
    )

    rl.draw_texture_pro(
      icon,
      rl.Rectangle(0, 0, icon.width, icon.height),
      icon_box,
      rl.Vector2(0, 0),
      0.0,
      color,
    )

    # Text content
    text_x = icon_box.x + icon_box.width + 10
    title_size = measure_text_cached(self._font_medium, title, 20)
    rl.draw_text_ex(
      self._font_medium,
      title,
      rl.Vector2(text_x, inner_y + 1),
      20,
      0,
      Colors.TEXT_PRIMARY,
    )

    rl.draw_text_ex(
      self._font_regular,
      subtitle,
      rl.Vector2(text_x, inner_y + title_size.y + 4),
      18,
      0,
      Colors.TEXT_MUTED,
    )

  def _draw_connectivity_card(self, rect: rl.Rectangle):
    # Determine Wi-Fi or "No Network"
    net_type_text = tr(self._net_type)
    if self._net_strength <= 0 or net_type_text == tr("No Network"):
      icon = self._wifi_off_icon
      bars_color = Colors.WIFI_BAD
      subtitle = tr("Offline")
    else:
      icon = self._wifi_icon
      if self._net_strength >= 4:
        bars_color = Colors.WIFI_GOOD
      elif self._net_strength >= 2:
        bars_color = Colors.WIFI_OK
      else:
        bars_color = Colors.WIFI_BAD

      subtitle = f"{net_type_text} · {self._net_strength}/5"

    self._draw_metric_card(rect, tr("Connectivity"), subtitle, icon, bars_color)

  def _draw_thermal_card(self, rect: rl.Rectangle):
    # Decide color / status
    t = max(self._cpu_temp, self._gpu_temp)
    if t <= 65:
      color = Colors.TEMP_COOL
      status = tr("Cool")
    elif t <= 80:
      color = Colors.TEMP_WARM
      status = tr("Warm")
    else:
      color = Colors.TEMP_HOT
      status = tr("Hot")

    subtitle = f"{int(self._cpu_temp)}° / {int(self._gpu_temp)}°  ·  {status}"
    self._draw_metric_card(rect, tr("Thermals"), subtitle, self._temp_icon, color)

  def _draw_panda_card(self, rect: rl.Rectangle):
    if not self._panda_present:
      color = Colors.PANDA_DISCONNECTED
      subtitle = tr("No Panda Detected")
    else:
      color = Colors.PANDA_CONNECTED
      if self._panda_type is not None:
        type_name = PandaType.toString(self._panda_type)
      else:
        type_name = "Unknown"

      subtitle = tr(f"{type_name} Connected")

    self._draw_metric_card(rect, tr("Vehicle Interface"), subtitle, self._panda_icon, color)