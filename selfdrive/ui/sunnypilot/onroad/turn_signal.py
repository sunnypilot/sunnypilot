"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl
import time
from dataclasses import dataclass

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.selfdrive.ui.mici.onroad.alert_renderer import IconSide, TURN_SIGNAL_BLINK_PERIOD
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets import Widget
from openpilot.common.filter_simple import FirstOrderFilter


@dataclass(frozen=True)
class TurnSignalConfig:
  left_x: int = 80
  left_y: int = 190
  right_x: int = 80
  right_y: int = 190
  size: int = 150


class TurnSignalWidget(Widget):
  def __init__(self, direction: IconSide):
    super().__init__()
    self._direction = direction
    self._active = False
    self._type = 'signal'

    self._turn_signal_timer = 0.0
    self._turn_signal_alpha_filter = FirstOrderFilter(0.0, 0.3, 1 / gui_app.target_fps)

    self._signal_texture = gui_app.texture(f'icons_mici/onroad/turn_signal_{direction}.png', 120, 109)
    self._blind_spot_texture = gui_app.texture(f'icons_mici/onroad/blind_spot_{direction}.png', 120, 109)
    self._texture = self._signal_texture

  def _render(self, _):
    if not self._active:
      return

    if self._type == 'signal':
      if time.monotonic() - self._turn_signal_timer > TURN_SIGNAL_BLINK_PERIOD:
        self._turn_signal_timer = time.monotonic()
        self._turn_signal_alpha_filter.x = 255 * 2
      else:
        self._turn_signal_alpha_filter.update(255 * 0.2)
      icon_alpha = int(min(self._turn_signal_alpha_filter.x, 255))
    else:
      icon_alpha = 255

    self._texture = self._blind_spot_texture if self._type == 'blind_spot' else self._signal_texture

    if self._texture:
      pos_x = int(self._rect.x + (self._rect.width - self._texture.width) / 2)
      pos_y = int(self._rect.y + (self._rect.height - self._texture.height) / 2)
      color = rl.Color(255, 255, 255, icon_alpha)
      rl.draw_texture(self._texture, pos_x, pos_y, color)

  def activate(self, _type: str = 'signal'):
    if not self._active or self._type != _type:
      self._turn_signal_timer = 0.0
    self._active = True
    self._type = _type

  def deactivate(self):
    self._active = False
    self._turn_signal_timer = 0.0


class TurnSignalController:
  def __init__(self):
    self._config = TurnSignalConfig()
    self._left_signal = TurnSignalWidget(direction=IconSide.left)
    self._right_signal = TurnSignalWidget(direction=IconSide.right)

  @staticmethod
  def _update_signal(signal, blindspot, blinker):
    if ui_state.blindspot and blindspot:
      signal.activate('blind_spot')
    elif ui_state.turn_signals and blinker:
      signal.activate('signal')
    else:
      signal.deactivate()

  def update(self):
    CS = ui_state.sm['carState']

    self._update_signal(self._left_signal, CS.leftBlindspot, CS.leftBlinker)
    self._update_signal(self._right_signal, CS.rightBlindspot, CS.rightBlinker)

  def render(self, rect: rl.Rectangle):
    if not ui_state.turn_signals and not ui_state.blindspot:
      return

    x = rect.x + rect.width / 2

    left_x = x - self._config.left_x - self._config.size
    left_y = rect.y + self._config.left_y

    right_x = x + self._config.right_x
    right_y = rect.y + self._config.right_y

    if self._left_signal._active:
      self._left_signal.render(rl.Rectangle(left_x, left_y, self._config.size, self._config.size))

    if self._right_signal._active:
      self._right_signal.render(rl.Rectangle(right_x, right_y, self._config.size, self._config.size))

  @property
  def config(self) -> TurnSignalConfig:
    return self._config

  @config.setter
  def config(self, new_config: TurnSignalConfig):
    self._config = new_config
