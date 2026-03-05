import os
import time
from collections.abc import Callable

import pyray as rl

from openpilot.common.params import Params
from openpilot.system.hardware import HARDWARE
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget

class ScreenSaverSP(Widget):
  def __init__(self):
    super().__init__()
    self.set_rect(rl.Rectangle(0, 0, gui_app.width, gui_app.height))
    self.screensaver_timeout = Params().get("ScreenSaverTimeout", return_default=True)
    self._is_mici = HARDWARE.get_device_type() == 'mici' or (HARDWARE.get_device_type() == "pc" and os.getenv("BIG") != "1")

    self.x = 0.0
    self.y = 100.0
    self.vx = 120.0 if self._is_mici else 300.0
    self.vy = 70.0 if self._is_mici else 200.0
    self._hue = 150
    self.color = rl.color_from_hsv(self._hue, 1, 1)

    self.text = "sunnypilot"
    self.font_size = 50 if self._is_mici else 200
    self._start_time = None
    self._dismiss = False
    self.dismiss_callback = None

  @property
  def was_dismissed(self) -> bool:
    return self._dismiss

  def initialize(self, dismiss_callback: Callable):
    if self._start_time is None:
      self._start_time = time.monotonic()
    self.dismiss_callback = dismiss_callback
    self._dismiss = False

  def deinit(self):
    self._dismiss = False
    self._start_time = None

  def _handle_mouse_press(self, mouse_pos) -> bool:
    self._reset()
    return super()._handle_mouse_press(mouse_pos)

  def _reset(self):
    self._dismiss = True
    self._start_time = None

  def _update_state(self):
    super()._update_state()

    self.font = gui_app.font(FontWeight.AUDIOWIDE)
    text_size = measure_text_cached(self.font, self.text, self.font_size, 0)
    self.logo_width = text_size.x
    self.logo_height = text_size.y

    if self._start_time and time.monotonic() - self._start_time > self.screensaver_timeout:
      self._reset()

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
      while not abs((new_hue := rl.get_random_value(0, 360)) - self._hue) >= 50:
        pass
      self._hue = new_hue
      self.color = rl.color_from_hsv(self._hue, 1, 1)

  def _render(self, rect: rl.Rectangle):
    if self._dismiss:
      self.dismiss_callback()
      return 0

    self.set_rect(rect)
    rl.clear_background(rl.BLACK)
    rl.draw_text_ex(self.font, self.text, rl.Vector2(int(self.x), int(self.y)), self.font_size, 0, self.color)
    return -1
