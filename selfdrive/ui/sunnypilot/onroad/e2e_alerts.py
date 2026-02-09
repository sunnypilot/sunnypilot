"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl

from cereal import log
from openpilot.selfdrive.ui import UI_BORDER_SIZE
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.selfdrive.ui.sunnypilot.onroad.developer_ui import DeveloperUiRenderer
from openpilot.system.ui.lib.application import gui_app, FontWeight, FONT_SCALE
from openpilot.system.ui.lib.text_measure import measure_text_cached


class E2eAlertsRenderer:
  def __init__(self):
    self._green_light_alert_img = gui_app.texture("../../sunnypilot/selfdrive/assets/images/green_light.png", 250, 250)
    self._lead_depart_alert_img = gui_app.texture("../../sunnypilot/selfdrive/assets/images/lead_depart.png", 250, 250)

    self._e2e_alert_display_timer = 0
    self._e2e_alert_frame = 0
    self._green_light_alert = False
    self._lead_depart_alert = False
    self._alert_text = ""
    self._alert_img = None
    self._allow_e2e_alerts = False

  def update(self) -> None:
    sm = ui_state.sm
    lp_sp = sm['longitudinalPlanSP']
    self._green_light_alert = lp_sp.e2eAlerts.greenLightAlert
    self._lead_depart_alert = lp_sp.e2eAlerts.leadDepartAlert

    self._allow_e2e_alerts = sm['selfdriveState'].alertSize == log.SelfdriveState.AlertSize.none and \
                             sm.recv_frame['driverStateV2'] > ui_state.started_frame

    if self._green_light_alert or self._lead_depart_alert:
      self._e2e_alert_display_timer = 3 * gui_app.target_fps

    if self._e2e_alert_display_timer > 0:
      self._e2e_alert_frame += 1
      self._e2e_alert_display_timer -= 1

      if self._green_light_alert:
        self._alert_text = "GREEN\nLIGHT"
        self._alert_img = self._green_light_alert_img
      elif self._lead_depart_alert:
        self._alert_text = "LEAD VEHICLE\nDEPARTING"
        self._alert_img = self._lead_depart_alert_img
    else:
      self._e2e_alert_frame = 0

  def render(self, rect: rl.Rectangle) -> None:
    if not self._allow_e2e_alerts or self._e2e_alert_display_timer <= 0:
      return

    e2e_alert_size = 250
    dev_ui_width_adjustment = 180 if ui_state.developer_ui in (DeveloperUiRenderer.DEV_UI_RIGHT, DeveloperUiRenderer.DEV_UI_BOTH) else 100

    x = rect.x + rect.width - e2e_alert_size - dev_ui_width_adjustment - (UI_BORDER_SIZE * 3)
    y = rect.y + rect.height / 2 + 20

    alert_rect = rl.Rectangle(x - e2e_alert_size, y - e2e_alert_size, e2e_alert_size * 2, e2e_alert_size * 2)
    center = rl.Vector2(alert_rect.x + alert_rect.width / 2, alert_rect.y + alert_rect.height / 2)

    # Pulse logic
    is_pulsing = (self._e2e_alert_frame % gui_app.target_fps) < (gui_app.target_fps / 2.5)
    frame_color = rl.Color(255, 255, 255, 75) if is_pulsing else rl.Color(0, 255, 0, 75)

    # Draw Circle
    rl.draw_circle_v(center, e2e_alert_size, rl.Color(0, 0, 0, 190))
    # Draw Ring (Border)
    rl.draw_ring(center, e2e_alert_size - 7.5, e2e_alert_size + 7.5, 0, 360, 0, frame_color)

    # Draw Image
    if self._alert_img:
      img_x = int(center.x - self._alert_img.width / 2)
      img_y = int(center.y - self._alert_img.height / 2)
      rl.draw_texture(self._alert_img, img_x, img_y, rl.WHITE)

    # Draw Text
    txt_color = rl.Color(255, 255, 255, 255) if is_pulsing else rl.Color(0, 255, 0, 190)
    font = gui_app.font(FontWeight.BOLD)
    text_size = 48
    spacing = 0

    lines = self._alert_text.split('\n')

    # Position text at bottom of alert circle
    bottom_y = (alert_rect.y + alert_rect.height) - (alert_rect.height / 7)

    # Draw lines upwards from bottom
    current_y = bottom_y - (len(lines) * text_size * FONT_SCALE)

    for line in lines:
      measure = measure_text_cached(font, line, text_size, spacing)
      line_x = center.x - measure.x / 2
      rl.draw_text_ex(font, line, rl.Vector2(line_x, current_y), text_size, spacing, txt_color)
      current_y += text_size * FONT_SCALE
