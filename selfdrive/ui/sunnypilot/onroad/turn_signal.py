"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl
import time
from dataclasses import dataclass

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets import Widget
from openpilot.common.filter_simple import FirstOrderFilter

TURN_SIGNAL_BLINK_PERIOD = 1 / (80 / 60)


@dataclass(frozen=True)
class TurnSignalConfig:
  left_x: int = 870
  left_y: int = 220
  right_x: int = 1140
  right_y: int = 220
  size: int = 150


class TurnSignalWidget(Widget):
  def __init__(self, direction: int):
    super().__init__()
    self._direction = direction
    self._active = False

    self._turn_signal_timer = 0.0
    self._turn_signal_alpha_filter = FirstOrderFilter(0.0, 0.3, 1 / gui_app.target_fps)

    try:
      texture_path = f'icons_mici/onroad/turn_signal_{"left" if direction == -1 else "right"}.png'
      self._texture = gui_app.texture(texture_path, 100, 91)
      self._use_texture = True
    except Exception:
      self._texture = None
      self._use_texture = False

  def _render(self, _):
    if not self._active:
      return

    if time.monotonic() - self._turn_signal_timer > TURN_SIGNAL_BLINK_PERIOD:
      self._turn_signal_timer = time.monotonic()
      self._turn_signal_alpha_filter.x = 255 * 2
    else:
      self._turn_signal_alpha_filter.update(255 * 0.2)

    icon_alpha = int(min(self._turn_signal_alpha_filter.x, 255))

    if self._use_texture and self._texture:
      pos_x = int(self._rect.x + (self._rect.width - self._texture.width) / 2)
      pos_y = int(self._rect.y + (self._rect.height - self._texture.height) / 2)
      color = rl.Color(255, 255, 255, icon_alpha)
      rl.draw_texture(self._texture, pos_x, pos_y, color)
    else:
      self._render_fallback(icon_alpha)

  def _render_fallback(self, alpha: int):
    center_x = self._rect.x + self._rect.width / 2
    center_y = self._rect.y + self._rect.height / 2
    arrow_size = 40
    color = rl.Color(128, 216, 166, alpha)

    if self._direction == 1:
      p1 = rl.Vector2(center_x - arrow_size/2, center_y - arrow_size/2)
      p2 = rl.Vector2(center_x - arrow_size/2, center_y + arrow_size/2)
      p3 = rl.Vector2(center_x + arrow_size/2, center_y)
    else:
      p1 = rl.Vector2(center_x + arrow_size/2, center_y - arrow_size/2)
      p2 = rl.Vector2(center_x + arrow_size/2, center_y + arrow_size/2)
      p3 = rl.Vector2(center_x - arrow_size/2, center_y)

    rl.draw_triangle(p1, p2, p3, color)

  def activate(self):
    if not self._active:
      self._turn_signal_timer = 0.0
    self._active = True

  def deactivate(self):
    self._active = False
    self._turn_signal_timer = 0.0


class TurnSignalController:
  def __init__(self, config: TurnSignalConfig = None):
    self._config = config or TurnSignalConfig()
    self._left_signal = TurnSignalWidget(direction=-1)
    self._right_signal = TurnSignalWidget(direction=1)
    self._last_icon_side = None

  def update(self):
    sm = ui_state.sm
    ss = sm['selfdriveState']

    event_name = ss.alertType.split('/')[0] if ss.alertType else ''

    if event_name == 'preLaneChangeLeft':
      self._last_icon_side = 'left'
      self._left_signal.activate()
      self._right_signal.deactivate()

    elif event_name == 'preLaneChangeRight':
      self._last_icon_side = 'right'
      self._right_signal.activate()
      self._left_signal.deactivate()

    elif event_name == 'laneChange':
      if self._last_icon_side == 'left':
        self._left_signal.activate()
        self._right_signal.deactivate()
      elif self._last_icon_side == 'right':
        self._right_signal.activate()
        self._left_signal.deactivate()

    else:
      self._last_icon_side = None
      self._left_signal.deactivate()
      self._right_signal.deactivate()

  def render(self):
    if self._last_icon_side == 'left':
      self._left_signal.render(rl.Rectangle(
        self._config.left_x,
        self._config.left_y,
        self._config.size,
        self._config.size
      ))
    elif self._last_icon_side == 'right':
      self._right_signal.render(rl.Rectangle(
        self._config.right_x,
        self._config.right_y,
        self._config.size,
        self._config.size
      ))

  @property
  def config(self) -> TurnSignalConfig:
    return self._config

  @config.setter
  def config(self, new_config: TurnSignalConfig):
    self._config = new_config
