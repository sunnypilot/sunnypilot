import datetime
import time

from cereal import log
import pyray as rl
from collections.abc import Callable
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.layouts import HBoxLayout
from openpilot.system.ui.widgets.icon_widget import IconWidget
from openpilot.system.ui.widgets.label import UnifiedLabel, gui_label, TextEffect
from openpilot.system.ui.lib.application import gui_app, FontWeight, MousePos
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.version import RELEASE_BRANCHES

HEAD_BUTTON_FONT_SIZE = 40
HOME_PADDING = 8
SETTINGS_ZONE_WIDTH = 280
ALERTS_ZONE_WIDTH = 180

NetworkType = log.DeviceState.NetworkType

NETWORK_TYPES = {
  NetworkType.none: "Offline",
  NetworkType.wifi: "WiFi",
  NetworkType.cell2G: "2G",
  NetworkType.cell3G: "3G",
  NetworkType.cell4G: "LTE",
  NetworkType.cell5G: "5G",
  NetworkType.ethernet: "Ethernet",
}


class AlertsPill(Widget):
  ICON_OFFSET = 12
  COUNT_OFFSET = 40

  def __init__(self):
    super().__init__()
    self.set_rect(rl.Rectangle(0, 0, 104, 52))

    self._pill_bg_txt = gui_app.texture("icons_mici/alerts_pill.png", 104, 52)
    self._warning_txt = gui_app.texture("icons_mici/offroad_alerts/red_warning.png", 36, 36)
    self._alert_count_callback: Callable[[], int] | None = None

  def set_alert_count_callback(self, callback: Callable[[], int] | None):
    self._alert_count_callback = callback

  def _render(self, _):
    alert_count = self._alert_count_callback() if self._alert_count_callback else 0
    if alert_count > 0:
      pill_w, pill_h = self._pill_bg_txt.width, self._pill_bg_txt.height
      rl.draw_texture_ex(self._pill_bg_txt, rl.Vector2(self.rect.x, self.rect.y), 0.0, 1.0, rl.WHITE)

      warn_x = self.rect.x + self.ICON_OFFSET
      warn_y = self.rect.y + (pill_h - self._warning_txt.height) / 2
      rl.draw_texture_ex(self._warning_txt, rl.Vector2(warn_x, warn_y), 0.0, 1.0, rl.WHITE)

      count_rect = rl.Rectangle(self.rect.x + self.COUNT_OFFSET, self.rect.y, pill_w - self.COUNT_OFFSET, pill_h)
      gui_label(count_rect, str(alert_count), font_size=36,
                alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER,
                alignment_vertical=rl.GuiTextAlignmentVertical.TEXT_ALIGN_MIDDLE)


class WifiIcon(Widget):
  def __init__(self):
    super().__init__()
    self.set_rect(rl.Rectangle(0, 0, 54, 44))  # max size of all icons
    self._net_type = NetworkType.none
    self._net_strength = 0

    self._wifi_slash_txt = gui_app.texture("icons_mici/settings/network/wifi_strength_slash.png", 50, 44)
    self._wifi_none_txt = gui_app.texture("icons_mici/settings/network/wifi_strength_none.png", 50, 37)
    self._wifi_low_txt = gui_app.texture("icons_mici/settings/network/wifi_strength_low.png", 50, 37)
    self._wifi_medium_txt = gui_app.texture("icons_mici/settings/network/wifi_strength_medium.png", 50, 37)
    self._wifi_full_txt = gui_app.texture("icons_mici/settings/network/wifi_strength_full.png", 50, 37)

  def _update_state(self):
    device_state = ui_state.sm['deviceState']
    self._net_type = device_state.networkType
    strength = device_state.networkStrength
    self._net_strength = max(0, min(5, strength.raw + 1)) if strength.raw > 0 else 0

  def _render(self, _):
    if self._net_type == NetworkType.wifi:
      # There is no 1
      draw_net_txt = {0: self._wifi_none_txt,
                      2: self._wifi_low_txt,
                      3: self._wifi_medium_txt,
                      4: self._wifi_full_txt,
                      5: self._wifi_full_txt}.get(self._net_strength, self._wifi_low_txt)
    else:
      draw_net_txt = self._wifi_slash_txt

    draw_x = self._rect.x + (self._rect.width - draw_net_txt.width) / 2
    draw_y = self._rect.y + (self._rect.height - draw_net_txt.height) / 2

    if draw_net_txt == self._wifi_slash_txt:
      # Offset by difference in height between slashless and slash icons to make center align match
      draw_y -= (self._wifi_slash_txt.height - self._wifi_none_txt.height) / 2

    rl.draw_texture_ex(draw_net_txt, rl.Vector2(draw_x, draw_y), 0.0, 1.0, rl.Color(255, 255, 255, int(255 * 0.9)))


class CellularIcon(Widget):
  def __init__(self):
    super().__init__()
    self.set_rect(rl.Rectangle(0, 0, 54, 44))  # max size of all icons
    self._net_strength = 0

    self._cell_none_txt = gui_app.texture("icons_mici/settings/network/cell_strength_none.png", 54, 36)
    self._cell_low_txt = gui_app.texture("icons_mici/settings/network/cell_strength_low.png", 54, 36)
    self._cell_medium_txt = gui_app.texture("icons_mici/settings/network/cell_strength_medium.png", 54, 36)
    self._cell_high_txt = gui_app.texture("icons_mici/settings/network/cell_strength_high.png", 54, 36)
    self._cell_full_txt = gui_app.texture("icons_mici/settings/network/cell_strength_full.png", 54, 36)

  def _update_state(self):
    val = ui_state.params.get("CellularStrength")
    raw_strength = int(val) if val else 0
    self._net_strength = max(0, min(5, raw_strength + 1)) if raw_strength > 0 else 0
    
    net_state = ui_state.sm["deviceState"].networkInfo.state

    # Fallback missing signal to full bars if we are explicitly CONNECTED!
    if net_state == "CONNECTED" and self._net_strength == 0:
      self._net_strength = 5

    # Hide if there is no signal and we aren't connected
    self.set_visible(self._net_strength > 0)

  def _render(self, _):
    draw_net_txt = {0: self._cell_none_txt,
                    2: self._cell_low_txt,
                    3: self._cell_medium_txt,
                    4: self._cell_high_txt,
                    5: self._cell_full_txt}.get(self._net_strength, self._cell_none_txt)

    draw_x = self._rect.x + (self._rect.width - draw_net_txt.width) / 2
    draw_y = self._rect.y + (self._rect.height - draw_net_txt.height) / 2

    rl.draw_texture_ex(draw_net_txt, rl.Vector2(draw_x, draw_y), 0.0, 1.0, rl.Color(255, 255, 255, int(255 * 0.9)))


from openpilot.system.ui.lib.text_measure import measure_text_cached





class MiciHomeLayout(Widget):
  def __init__(self):
    super().__init__()
    self._on_settings_click: Callable | None = None
    self._on_alerts_click: Callable | None = None
    self._alert_count_callback: Callable[[], int] | None = None

    self._last_refresh = 0
    self._mouse_down_t: None | float = None
    self._did_long_press = False
    self._is_pressed_prev = False

    self._version_text = None
    self._experimental_mode = False

    self._experimental_icon = IconWidget("icons_mici/experimental_mode.png", (48, 48))
    self._mic_icon = IconWidget("icons_mici/microphone.png", (32, 46))

    self._alerts_pill = AlertsPill()

    self._cellular_icon = CellularIcon()

    self._status_bar_layout = HBoxLayout([
      IconWidget("icons_mici/settings.png", (48, 48), opacity=0.9),
      WifiIcon(),
      self._cellular_icon,
      self._experimental_icon,
      self._mic_icon,
    ], spacing=18)

    self._openpilot_label = UnifiedLabel("pingupilot", font_size=96, font_weight=FontWeight.DISPLAY, max_width=480, wrap_text=False)
    self._branch_label = UnifiedLabel("", font_size=36, text_color=rl.WHITE, font_weight=FontWeight.ROMAN, max_width=480, wrap_text=False)
    self._date_label = UnifiedLabel("", font_size=36, text_color=rl.GRAY, font_weight=FontWeight.ROMAN, max_width=480, wrap_text=False)
    self._version_commit_label = UnifiedLabel("", font_size=36, text_color=rl.WHITE, font_weight=FontWeight.ROMAN, max_width=480, wrap_text=False)
    self._version_description_label = UnifiedLabel("", font_size=36, text_color=rl.GRAY, font_weight=FontWeight.ROMAN, scroll=True)

  def show_event(self):
    super().show_event()
    self._version_info = self._get_version_info()
    self._update_params()

  def _update_params(self):
    self._experimental_mode = ui_state.params.get_bool("ExperimentalMode")
    effect_param = ui_state.params.get("OpenpilotTextEffect")
    new_text_effect = int(effect_param) if effect_param is not None else 0
    self._openpilot_label.set_effect(TextEffect(new_text_effect))

  def _update_state(self):
    self._cellular_icon._update_state()
    
    if self.is_pressed and not self._is_pressed_prev:
      self._mouse_down_t = time.monotonic()
    elif not self.is_pressed and self._is_pressed_prev:
      self._mouse_down_t = None
      self._did_long_press = False
    self._is_pressed_prev = self.is_pressed

    if self._mouse_down_t is not None:
      if time.monotonic() - self._mouse_down_t > 0.5:
        # long gating for experimental mode - only allow toggle if longitudinal control is available
        if ui_state.has_longitudinal_control:
          self._experimental_mode = not self._experimental_mode
          ui_state.params.put("ExperimentalMode", self._experimental_mode)
        self._mouse_down_t = None
        self._did_long_press = True

    if rl.get_time() - self._last_refresh > 5.0:
      # Update version text
      self._version_info = self._get_version_info()
      self._last_refresh = rl.get_time()
      self._update_params()

  def set_callbacks(self, on_settings: Callable | None = None, on_alerts: Callable | None = None,
                    alert_count_callback: Callable[[], int] | None = None):
    self._on_settings_click = on_settings
    self._on_alerts_click = on_alerts
    self._alert_count_callback = alert_count_callback
    self._alerts_pill.set_alert_count_callback(alert_count_callback)

  def _handle_mouse_release(self, mouse_pos: MousePos):
    if not self._did_long_press:
      relative_x = mouse_pos.x - self.rect.x
      has_alerts = self._alert_count_callback and self._alert_count_callback() > 0
      if relative_x < SETTINGS_ZONE_WIDTH:
        if self._on_settings_click:
          self._on_settings_click()
      elif has_alerts and relative_x > self.rect.width - ALERTS_ZONE_WIDTH:
        if self._on_alerts_click:
          self._on_alerts_click()
    self._did_long_press = False

  def _get_version_info(self) -> tuple[str, str, str, str] | None:
    branch = ui_state.params.get("GitBranch")
    commit = ui_state.params.get("GitCommit")
    description = ui_state.params.get("GitCommitDescription")

    if not all((branch, commit)):
      return None

    commit_date_raw = ui_state.params.get("GitCommitDate")
    try:
      # GitCommitDate format from get_commit_date(): '%ct %ci' e.g. "'1708012345 2024-02-15 ...'"
      unix_ts = int(commit_date_raw.strip("'").split()[0])
      date_str = datetime.datetime.fromtimestamp(unix_ts).strftime("%b %d")
    except (ValueError, IndexError, TypeError, AttributeError):
      date_str = ""

    return branch, date_str, commit[:7], (description or "")

  def _render(self, _):
    # TODO: why is there extra space here to get it to be flush?
    text_pos = rl.Vector2(self.rect.x - 2 + HOME_PADDING, self.rect.y - 16)
    self._openpilot_label.set_position(text_pos.x, text_pos.y)
    self._openpilot_label.render()

    if self._version_info is not None:
      branch, date_str, commit_hash, description = self._version_info
      # release branch
      release_branch = branch in RELEASE_BRANCHES

      # Line 2: Branch (White) + Date (Gray)
      line2_y = text_pos.y + self._openpilot_label.font_size + 16

      self._branch_label.set_text("release" if release_branch else branch)
      self._branch_label.set_position(text_pos.x, line2_y)
      self._branch_label.render()

      self._date_label.set_text(" " + date_str)
      self._date_label.set_position(text_pos.x + self._branch_label.text_width, line2_y)
      self._date_label.render()

      # Line 3: Hash (Static, Gray) + Title (Scrolling, Gray)
      if not release_branch:
        line3_y = line2_y + self._branch_label.font_size + 8
        hash_text = f"{commit_hash} "
        self._version_commit_label.set_text(hash_text)
        self._version_commit_label.set_position(text_pos.x, line3_y)
        self._version_commit_label.render()

        desc_x = text_pos.x + self._version_commit_label.text_width
        self._version_description_label.set_max_width(self.rect.width - desc_x - HOME_PADDING)
        self._version_description_label.set_text(description)
        self._version_description_label.set_position(desc_x, line3_y)
        self._version_description_label.render()

    # ***** Center-aligned bottom section icons *****
    self._experimental_icon.set_visible(self._experimental_mode)
    self._mic_icon.set_visible(ui_state.recording_audio)

    footer_rect = rl.Rectangle(self.rect.x + HOME_PADDING, self.rect.y + self.rect.height - 48, self.rect.width - HOME_PADDING, 48)
    self._status_bar_layout.render(footer_rect)

    # TODO: add alignment to hboxlayout and add to there
    self._alerts_pill.set_position(self.rect.x + self.rect.width - self._alerts_pill.rect.width - HOME_PADDING,
                                   self.rect.y + self.rect.height - self._alerts_pill.rect.height)
    self._alerts_pill.render()
