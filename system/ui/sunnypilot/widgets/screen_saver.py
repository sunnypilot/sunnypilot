import os

import pyray as rl

from openpilot.system.hardware import HARDWARE
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets import Widget


class ScreenSaverSP(Widget):
  def __init__(self):
    super().__init__()
    self.set_rect(rl.Rectangle(0, 0, gui_app.width, gui_app.height))
    self._is_mici = HARDWARE.get_device_type() == 'mici' or (HARDWARE.get_device_type() == "pc" and os.getenv("BIG") != "1")
    self.logo_width = self.logo_height = 120 if self._is_mici else 400

    self.x = 0.0
    self.y = 100.0
    self.vx = 120.0 if self._is_mici else 300.0
    self.vy = 70.0 if self._is_mici else 200.0
    self._logo = gui_app.texture("../../sunnypilot/selfdrive/assets/icons/sp-logo.png", self.logo_width, self.logo_height)
    self.color = rl.Color(0, 255, 0, 255)

    self._dismiss = False

  def _handle_mouse_press(self, mouse_pos) -> bool:
    self._dismiss = True
    return super()._handle_mouse_press(mouse_pos)

  def _update_state(self):
    super()._update_state()

    dt = rl.get_frame_time()

    self.x += self.vx * dt
    self.y += self.vy * dt

    hit_x = hit_y = False
    if self.x + self.logo_width > self.rect.width:
      self.vx *= -1
      self.x = self.rect.width - self.logo_width
      hit_x = True
    elif self.x < 0:
      self.vx *= -1
      self.x = 0
      hit_x = True

    if self.y + self.logo_height > self.rect.height:
      self.vy *= -1
      self.y = self.rect.height - self.logo_height
      hit_y = True
    elif self.y < 0:
      self.vy *= -1
      self.y = 0
      hit_y = True

    if hit_x or hit_y:
      self.color = rl.color_from_hsv(rl.get_random_value(0, 360), 1, 1)

  def _render(self, rect: rl.Rectangle):
    if self._dismiss:
      return 0

    self.set_rect(rect)
    rl.clear_background(rl.BLACK)
    rl.draw_texture_ex(self._logo, rl.Vector2(self.x, self.y), 0.0, 1.0, self.color)
    return -1
