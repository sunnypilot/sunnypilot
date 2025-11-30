from functools import partial
import time
from typing import Literal

import pyray as rl

from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.button import ButtonStyle, Button
from openpilot.system.ui.widgets.inputbox import InputBox
from openpilot.system.ui.widgets.label import Label

# --- MICI keyboard ---
from openpilot.system.ui.widgets.mici_keyboard import MiciKeyboard

# layout & sizes
CONTENT_MARGIN = 50
INPUT_TOP_MARGIN = 160
KEYBOARD_BOTTOM_MARGIN = 40

KEY_FONT_SIZE_OVERRIDE = 96
INPUTBOX_FONT_SIZE = 72

BACKSPACE_HOLD_DELAY = 0.45
BACKSPACE_HOLD_INTERVAL = 0.07

# scaling
PILL_SCALE_X = 4.0
PILL_SCALE_Y = 5.0
KB_GLOBAL_SCALE = 1.35     # scales entire mici keyboard visually


class Keyboard(Widget):
  def __init__(self, max_text_size: int = 255, min_text_size: int = 0,
               password_mode: bool = False, show_password_toggle: bool = False):
    super().__init__()

    self._max_text_size = max_text_size
    self._min_text_size = min_text_size
    self._password_mode = password_mode
    self._show_password_toggle = show_password_toggle
    self._render_return_status = -1

    # title
    self._title = Label("", 90, FontWeight.BOLD, rl.GuiTextAlignment.TEXT_ALIGN_LEFT, text_padding=20)
    self._sub_title = Label("", 55, FontWeight.NORMAL, rl.GuiTextAlignment.TEXT_ALIGN_LEFT, text_padding=20)

    # input text box
    self._input_box = InputBox(max_text_size)
    self._input_box._font_size = INPUTBOX_FONT_SIZE

    # top buttons
    self._cancel_button = Button(lambda: tr("Cancel"), self._cancel_button_callback)
    self._done_button = Button(lambda: tr("Done"), self._done_button_callback, button_style=ButtonStyle.PRIMARY)

    # password toggle button
    self._eye_button = Button("", self._eye_button_callback, button_style=ButtonStyle.TRANSPARENT)
    self._eye_open_texture = gui_app.texture("icons/eye_open.png", 81, 54)
    self._eye_closed_texture = gui_app.texture("icons/eye_closed.png", 81, 54)

    # backspace button
    self._backspace_button = Button("", self._backspace_button_callback,
                                    icon=gui_app.texture("icons/backspace.png", 80, 80),
                                    button_style=ButtonStyle.TRANSPARENT)

    self._backspace_is_down = False
    self._backspace_down_time = 0.0
    self._backspace_last_repeat = 0.0

    # ---- MICI KEYBOARD (scaled, but not modified internally) ----
    self._mici_keyboard = MiciKeyboard()

    # override font size
    try:
      self._mici_keyboard.KEY_FONT_SIZE = KEY_FONT_SIZE_OVERRIDE
    except:
      pass

    # optional hitbox scaling (if supported)
    try:
      self._mici_keyboard.KEY_W_SCALE = 1.35
      self._mici_keyboard.KEY_H_SCALE = 1.35
    except:
      pass

    # override pill background texture scale
    try:
      self._mici_keyboard._txt_bg = gui_app.texture(
        "icons_mici/settings/keyboard/keyboard_background.png",
        int(520 * PILL_SCALE_X),
        int(170 * PILL_SCALE_Y),
        keep_aspect_ratio=False,
      )
    except:
      pass

  # ---------- API ----------
  def set_text(self, text: str):
    if len(text) > self._max_text_size:
      text = text[:self._max_text_size]
    self._mici_keyboard.set_text(text)
    self._input_box.text = text

  @property
  def text(self) -> str:
    return self._mici_keyboard.text()

  def clear(self):
    self._mici_keyboard.set_text("")
    self._input_box.clear()
    self._backspace_is_down = False

  def set_title(self, title: str, sub_title: str = ""):
    self._title.set_text(title)
    self._sub_title.set_text(sub_title)

  def reset(self, min_text_size: int | None = None):
    if min_text_size is not None:
      self._min_text_size = min_text_size
    self._render_return_status = -1
    self._backspace_is_down = False
    self.clear()

  # ---------- Button Callbacks ----------
  def _eye_button_callback(self):
    self._password_mode = not self._password_mode

  def _cancel_button_callback(self):
    self.clear()
    self._render_return_status = 0

  def _done_button_callback(self):
    if len(self.text) >= self._min_text_size:
      self._render_return_status = 1

  def _backspace_button_callback(self):
    self._mici_keyboard.backspace()
    self._input_box.text = self._mici_keyboard.text()
    self._backspace_is_down = True
    self._backspace_down_time = time.monotonic()
    self._backspace_last_repeat = self._backspace_down_time

  # ---------- Render ----------
  def _render(self, rect: rl.Rectangle):
    rect = rl.Rectangle(
      rect.x + CONTENT_MARGIN,
      rect.y + CONTENT_MARGIN,
      rect.width - 2 * CONTENT_MARGIN,
      rect.height - 2 * CONTENT_MARGIN,
    )

    # titles
    self._title.render(rl.Rectangle(rect.x, rect.y, rect.width, 95))
    self._sub_title.render(rl.Rectangle(rect.x, rect.y + 95, rect.width, 60))

    # buttons
    buttons_width = 360
    top_button_height = 125
    cancel_rect = rl.Rectangle(rect.x + rect.width - buttons_width * 2, rect.y, buttons_width, top_button_height)
    done_rect = rl.Rectangle(rect.x + rect.width - buttons_width, rect.y, buttons_width, top_button_height)

    self._cancel_button.render(cancel_rect)
    self._done_button.set_enabled(len(self.text) >= self._min_text_size)
    self._done_button.render(done_rect)

    # input box
    input_margin = 25
    input_rect = rl.Rectangle(
      rect.x + input_margin,
      rect.y + INPUT_TOP_MARGIN,
      rect.width - 2 * input_margin,
      105,
    )
    self._render_input_area(input_rect)

    self._update_backspace_repeat()

    # ----- MICI keyboard -----
    kb_height = self._mici_keyboard.get_keyboard_height() * KB_GLOBAL_SCALE

    kb_rect = rl.Rectangle(
      rect.x,
      rect.y + rect.height - kb_height - KEYBOARD_BOTTOM_MARGIN,
      rect.width,
      kb_height,
    )

    # scale around top-left corner
    rl.rl_push_matrix()
    rl.rl_translatef(kb_rect.x, kb_rect.y, 0)
    rl.rl_scalef(KB_GLOBAL_SCALE, KB_GLOBAL_SCALE, 1)
    rl.rl_translatef(-kb_rect.x, -kb_rect.y, 0)

    self._mici_keyboard.set_rect(kb_rect)
    self._mici_keyboard.render(kb_rect)

    rl.rl_pop_matrix()

    # sync text
    txt = self._mici_keyboard.text()
    if len(txt) > self._max_text_size:
      txt = txt[:self._max_text_size]
      self._mici_keyboard.set_text(txt)
    self._input_box.text = txt

    return self._render_return_status

  # ---------- Helpers ----------
  def _render_input_area(self, input_rect: rl.Rectangle):
    extra_w = 0
    if self._show_password_toggle:
      extra_w += 100
    extra_w += 110

    box_rect = rl.Rectangle(input_rect.x, input_rect.y, input_rect.width - extra_w, input_rect.height)

    self._input_box.set_password_mode(self._password_mode and self._show_password_toggle)
    self._input_box.render(box_rect)

    right_x = box_rect.x + box_rect.width

    # password eye
    if self._show_password_toggle:
      eye_rect = rl.Rectangle(right_x, input_rect.y, 100, input_rect.height)
      self._eye_button.render(eye_rect)
      eye_texture = self._eye_closed_texture if self._password_mode else self._eye_open_texture
      ex = eye_rect.x + (eye_rect.width - eye_texture.width) / 2
      ey = eye_rect.y + (eye_rect.height - eye_texture.height) / 2
      rl.draw_texture_v(eye_texture, rl.Vector2(ex, ey), rl.WHITE)
      right_x += 100

    # backspace
    backspace_rect = rl.Rectangle(right_x, input_rect.y, 110, input_rect.height)
    if not self._backspace_button.is_pressed:
      self._backspace_is_down = False
    self._backspace_button.render(backspace_rect)

    underline_y = input_rect.y + input_rect.height - 2
    rl.draw_line_ex(
      rl.Vector2(input_rect.x, underline_y),
      rl.Vector2(input_rect.x + input_rect.width, underline_y),
      3.0,
      rl.Color(189, 189, 189, 255),
    )

  def _update_backspace_repeat(self):
    if not self._backspace_is_down:
      return
    now = time.monotonic()
    if now - self._backspace_down_time < BACKSPACE_HOLD_DELAY:
      return
    if now - self._backspace_last_repeat >= BACKSPACE_HOLD_INTERVAL:
      self._mici_keyboard.backspace()
      self._input_box.text = self._mici_keyboard.text()
      self._backspace_last_repeat = now
