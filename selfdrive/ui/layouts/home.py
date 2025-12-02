import time
import datetime
import pyray as rl
from enum import IntEnum
from cereal import log
from openpilot.common.params import Params
from openpilot.selfdrive.ui.layouts.settings.settings import PanelType
from openpilot.selfdrive.ui.layouts.offroad_alerts import OffroadAlertsLayout
from openpilot.system.ui.lib.animation import ease_out_cubic, LinearAnimation
from openpilot.system.ui.lib.application import gui_app, FontWeight, MousePos, MouseEvent
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.widgets import Widget

REFRESH_INTERVAL = 10.0
BASE_WIDTH = 2560
BASE_HEIGHT = 1080
BRAND_FONT = 200
VERSION_FONT = 72
META_FONT = 56
PADDING = 48
ICON_MARGIN = 60
SWIPE_THRESHOLD = 120
SWIPE_EDGE = 80
WIFI_Y_OFFSET = -15
MODE_Y_OFFSET = 10
MODE_SCALE_FACTOR = 0.9
ALERT_ANIM_DURATION = 0.25
SWIPE_RIGHT_EDGE = 80
ALERT_OVERLAY_BASE = rl.Color(0, 0, 0, 255)
NetworkType = log.DeviceState.NetworkType


class HomeLayoutState(IntEnum):
  HOME = 0
  ALERTS = 1


class HomeLayout(Widget):
  def __init__(self):
    super().__init__()
    self.params = Params()

    self.current_state = HomeLayoutState.HOME
    self.last_refresh = 0.0

    self.settings_callback = None
    self.open_panel_callback = None

    self._version_text: tuple[str, str, str, str, str] | None = None
    self._experimental_mode = False

    self._scale = 1.0
    self._swipe_start: MousePos | None = None
    self._swipe_active = False
    self._swipe_side: str | None = None  # 'left' or 'right'
    self._alerts_anim = LinearAnimation(ALERT_ANIM_DURATION)

    self._net_type = NetworkType.none
    self._net_strength = 0

    self._settings_icon = gui_app.texture("icons_mici/settings.png", 180, 180)
    self._wifi_icons = {
      "slash": gui_app.texture("icons_mici/settings/network/wifi_strength_slash.png", 210, 180),
      "none": gui_app.texture("icons_mici/settings/network/wifi_strength_none.png", 210, 180),
      "low": gui_app.texture("icons_mici/settings/network/wifi_strength_low.png", 210, 180),
      "medium": gui_app.texture("icons_mici/settings/network/wifi_strength_medium.png", 210, 180),
      "full": gui_app.texture("icons_mici/settings/network/wifi_strength_full.png", 210, 180),
    }
    self._cell_icons = {
      "none": gui_app.texture("icons_mici/settings/network/cell_strength_none.png", 200, 160),
      "low": gui_app.texture("icons_mici/settings/network/cell_strength_low.png", 200, 160),
      "medium": gui_app.texture("icons_mici/settings/network/cell_strength_medium.png", 200, 160),
      "high": gui_app.texture("icons_mici/settings/network/cell_strength_high.png", 200, 160),
      "full": gui_app.texture("icons_mici/settings/network/cell_strength_full.png", 200, 160),
    }
    self._mode_icons = {
      "exp": gui_app.texture("icons_mici/experimental_mode.png", 200, 200),
      "wheel": gui_app.texture("icons_mici/wheel.png", 200, 200),
    }

    self._font_brand = gui_app.font(FontWeight.SEMI_BOLD)
    self._font_version = gui_app.font(FontWeight.MEDIUM)
    self._font_meta = gui_app.font(FontWeight.MEDIUM)

    self._alerts_layout = OffroadAlertsLayout()

  def show_event(self):
    self.last_refresh = time.monotonic()
    self._alerts_layout.show_event()
    self._refresh()

  def hide_event(self):
    self._alerts_layout.hide_event()

  def set_settings_callback(self, callback):
    self.settings_callback = callback

  def set_panel_callback(self, callback):
    self.open_panel_callback = callback

  def _set_state(self, state: HomeLayoutState):
    if state != self.current_state:
      if state == HomeLayoutState.ALERTS:
        self._alerts_layout.show_event()
      else:
        self._alerts_layout.hide_event()
      self.current_state = state

  def _render(self, rect: rl.Rectangle):
    current_time = time.monotonic()
    if current_time - self.last_refresh >= REFRESH_INTERVAL:
      self._refresh()
      self.last_refresh = current_time

    self._render_cluster()

    if self.current_state == HomeLayoutState.ALERTS:
      self._render_alert_overlay()
    elif self._alerts_anim.active:
      self._render_alert_overlay()

  def _update_state(self):
    if ui_state.sm.updated['deviceState']:
      device_state = ui_state.sm['deviceState']
      self._net_type = device_state.networkType
      strength = device_state.networkStrength
      self._net_strength = max(0, min(5, strength.raw + 1)) if strength.raw > 0 else 0

  def _handle_mouse_event(self, mouse_event: MouseEvent):
    super()._handle_mouse_event(mouse_event)

    # Open: swipe starting from left edge
    if mouse_event.left_pressed and mouse_event.pos.x <= SWIPE_EDGE:
      self._swipe_start = mouse_event.pos
      self._swipe_active = True
      self._swipe_side = 'left'
    # when alerts are open, allow close swipe starting near right edge
    if self.current_state == HomeLayoutState.ALERTS and mouse_event.left_pressed and mouse_event.pos.x >= self._rect.x + self._rect.width - SWIPE_RIGHT_EDGE:
      self._swipe_start = mouse_event.pos
      self._swipe_active = True
      self._swipe_side = 'right'

    if self._swipe_active and mouse_event.left_released and self._swipe_start is not None:
      dx = mouse_event.pos.x - self._swipe_start.x
      dy = mouse_event.pos.y - self._swipe_start.y
      if self._swipe_side == 'left' and dx > SWIPE_THRESHOLD and self.current_state != HomeLayoutState.ALERTS:
        self._start_alert_anim('in')
      elif self._swipe_side == 'right' and dx < -SWIPE_THRESHOLD and self.current_state == HomeLayoutState.ALERTS:
        self._start_alert_anim('out')
      self._swipe_active = False
      self._swipe_start = None
      self._swipe_side = None

    if mouse_event.left_released and self._swipe_start:
      self._swipe_active = False
      self._swipe_start = None
      self._swipe_side = None
      return

    # Block clicks to underlying UI while alerts overlay is showing/animating
    if self.current_state == HomeLayoutState.ALERTS or self._alerts_anim.active:
      return

  def _content_panel_rect(self) -> rl.Rectangle:
    return rl.Rectangle(self._rect.x, self._rect.y, self._rect.width, self._rect.height)

  def _render_cluster(self):
    self._scale = min(self._rect.width / BASE_WIDTH, self._rect.height / BASE_HEIGHT)

    brand_pos = rl.Vector2(self._rect.x + PADDING * self._scale, self._rect.y + PADDING * self._scale)
    brand_size = BRAND_FONT * self._scale
    rl.draw_text_ex(self._font_brand, "hoofpilot", brand_pos, brand_size, 0, rl.WHITE)

    if self._version_text is None:
      version_line = ""
      meta_line = ""
    else:
      _, version, branch, commit, date_display = self._version_text
      version_line = version
      meta_parts = [p for p in [branch, commit, date_display] if p]
      meta_line = " / ".join(meta_parts)

    version_y = brand_pos.y + brand_size + 24 * self._scale
    version_pos = rl.Vector2(brand_pos.x, version_y)
    if version_line:
      rl.draw_text_ex(self._font_version, version_line, version_pos, VERSION_FONT * self._scale, 0, rl.Color(255, 255, 255, 230))

    meta_y = version_y + VERSION_FONT * self._scale + 8 * self._scale
    if meta_line:
      meta_pos = rl.Vector2(brand_pos.x, meta_y)
      rl.draw_text_ex(self._font_meta, meta_line, meta_pos, META_FONT * self._scale, 0, rl.Color(200, 200, 200, 220))

    self._render_icons()

  def _render_icons(self):
    # Block interaction when alerts overlay is active/animating
    alerts_blocking = self.current_state == HomeLayoutState.ALERTS or self._alerts_anim.active

    icon_scale = max(0.9, min(1.4, self._scale * 1.05))
    gear_w = self._settings_icon.width * icon_scale
    gear_h = self._settings_icon.height * icon_scale
    hit_pad = 24 * self._scale  # enlarge tap area

    base_x = self._rect.x + ICON_MARGIN * self._scale
    base_y = self._rect.y + self._rect.height - gear_h - ICON_MARGIN * self._scale

    rl.draw_texture_ex(self._settings_icon, (int(base_x), int(base_y)), 0, icon_scale, rl.WHITE)

    if not alerts_blocking and rl.is_mouse_button_released(rl.MouseButton.MOUSE_BUTTON_LEFT):
      mouse_pos = rl.get_mouse_position()
      rect = rl.Rectangle(base_x - hit_pad, base_y - hit_pad, gear_w + hit_pad * 2, gear_h + hit_pad * 2)
      if rl.check_collision_point_rec(mouse_pos, rect):
        if self.open_panel_callback:
          self.open_panel_callback(PanelType.DEVICE)
        elif self.settings_callback:
          self.settings_callback()

    conn_x = base_x + gear_w + 50 * self._scale
    conn_w = 0
    conn_texture = self._select_connectivity_icon()
    if conn_texture:
      conn_w = conn_texture.width * icon_scale
      conn_h = conn_texture.height * icon_scale
      conn_y = self._rect.y + self._rect.height - conn_h - ICON_MARGIN * self._scale + (gear_h - conn_h) / 2 + WIFI_Y_OFFSET * self._scale
      rl.draw_texture_ex(conn_texture, (int(conn_x), int(conn_y)), 0, icon_scale, rl.WHITE)

      if not alerts_blocking and rl.is_mouse_button_released(rl.MouseButton.MOUSE_BUTTON_LEFT):
        mouse_pos = rl.get_mouse_position()
        rect = rl.Rectangle(conn_x - hit_pad, conn_y - hit_pad, conn_w + hit_pad * 2, conn_h + hit_pad * 2)
        if rl.check_collision_point_rec(mouse_pos, rect) and self.open_panel_callback:
          self.open_panel_callback(PanelType.NETWORK)

    mode_icon = self._mode_icons["exp"] if self._experimental_mode else self._mode_icons["wheel"]
    mode_scale = icon_scale * MODE_SCALE_FACTOR
    mode_w = mode_icon.width * mode_scale
    mode_h = mode_icon.height * mode_scale
    mode_x = conn_x + (conn_w if conn_texture else 0) + 50 * self._scale
    mode_y = self._rect.y + self._rect.height - mode_h - ICON_MARGIN * self._scale + (gear_h - mode_h) / 2 + MODE_Y_OFFSET * self._scale
    rl.draw_texture_ex(mode_icon, (int(mode_x), int(mode_y)), 0, mode_scale, rl.WHITE)

    if not alerts_blocking and rl.is_mouse_button_released(rl.MouseButton.MOUSE_BUTTON_LEFT):
      mouse_pos = rl.get_mouse_position()
      rect = rl.Rectangle(mode_x - hit_pad, mode_y - hit_pad, mode_w + hit_pad * 2, mode_h + hit_pad * 2)
      if rl.check_collision_point_rec(mouse_pos, rect) and self.open_panel_callback:
        self.open_panel_callback(PanelType.TOGGLES)

  def _select_connectivity_icon(self):
    if self._net_type == NetworkType.wifi:
      level = min(max(self._net_strength, 0), 5)
      if level <= 1:
        return self._wifi_icons["none"]
      if level == 2:
        return self._wifi_icons["low"]
      if level in (3, 4):
        return self._wifi_icons["medium"]
      return self._wifi_icons["full"]

    if self._net_type in (NetworkType.cell2G, NetworkType.cell3G, NetworkType.cell4G, NetworkType.cell5G):
      level = min(max(self._net_strength, 0), 5)
      if level <= 1:
        return self._cell_icons["none"]
      if level == 2:
        return self._cell_icons["low"]
      if level == 3:
        return self._cell_icons["medium"]
      if level == 4:
        return self._cell_icons["high"]
      return self._cell_icons["full"]

    return self._wifi_icons["slash"]

  def _refresh(self):
    self._version_text = self._get_version_text()
    self._experimental_mode = ui_state.params.get_bool("ExperimentalMode")
    self._alerts_layout.refresh()

  def _get_version_text(self) -> tuple[str, str, str, str, str] | None:
    description = self.params.get("UpdaterCurrentDescription") or ""
    if isinstance(description, bytes):
      description = description.decode("utf-8", "replace")

    if description:
      parts = [p.strip() for p in description.split(" / ")]
      version = parts[0] if len(parts) > 0 else ""
      branch = parts[1] if len(parts) > 1 else ""
      commit = parts[2] if len(parts) > 2 else ""
      raw_date = parts[3] if len(parts) > 3 else ""
      date_display = self._format_date(raw_date)
      return "hoofpilot", version, branch, commit, date_display

    return None

  def _format_date(self, raw_date: str) -> str:
    try:
      parsed = datetime.date.fromisoformat(raw_date.split(" ")[0])
      return parsed.strftime("%b %d")
    except Exception:
      return raw_date

  # Alerts overlay rendering/animation
  def _start_alert_anim(self, direction: str):
    self._alerts_anim.start(direction)
    if direction == 'in':
      self._alerts_layout.show_event()
    else:
      self._alerts_layout.hide_event()

  def _draw_alerts_backdrop(self, rect: rl.Rectangle, alpha: float):
    alpha = max(0.0, min(1.0, alpha))
    if alpha <= 0.0:
      return

    base = rl.Color(ALERT_OVERLAY_BASE.r, ALERT_OVERLAY_BASE.g, ALERT_OVERLAY_BASE.b, int(ALERT_OVERLAY_BASE.a * alpha))
    # Solid, uniform blackout over the home view (no gradients/lines)
    rl.draw_rectangle_rec(rect, base)

  def _render_alert_overlay(self):
    full_rect = self._content_panel_rect()
    progress = 1.0 if self.current_state == HomeLayoutState.ALERTS else 0.0
    direction = 1.0 if self.current_state == HomeLayoutState.ALERTS else -1.0

    if self._alerts_anim.active:
      progress = self._alerts_anim.step()
      direction = self._alerts_anim.direction

    eased = ease_out_cubic(progress)
    fade = eased
    x = full_rect.x - full_rect.width * (1 - eased)

    overlay_rect = rl.Rectangle(x, full_rect.y, full_rect.width, full_rect.height)
    self._draw_alerts_backdrop(overlay_rect, fade)
    self._alerts_layout.render(overlay_rect)

    if not self._alerts_anim.active:
      if direction > 0 and progress >= 1.0:
        self._set_state(HomeLayoutState.ALERTS)
      elif direction < 0 and progress <= 0.0:
        self._set_state(HomeLayoutState.HOME)
