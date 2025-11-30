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

# MICI keyboard (unmodified)
from openpilot.system.ui.widgets.mici_keyboard import MiciKeyboard


# ========= TIZI SCALING CONSTANTS (2160×1080) =========
PILL_W = 2000     # was 1500
PILL_H = 625      # was 375
KEY_FONT_SIZE = 96     # final key letter size
ROW_SPACING = 48
KEY_SPACING = 54

KB_SCALE = 1.00        # global keyboard scale (keep 1.00)
CONTENT_MARGIN = 50
INPUT_TOP_MARGIN = 160
KEYBOARD_BOTTOM_MARGIN = 40

BACKSPACE_HOLD_DELAY = 0.45
BACKSPACE_HOLD_INTERVAL = 0.07



class Keyboard(Widget):
  """
  Full Tizi keyboard using MICI keyboard graphics + layout, but scaled correctly
  for the 2160×1080 Huawei C3X screen.
  """

  def __init__(self, max_text_size: int = 255, min_text_size: int = 0,
               password_mode: bool = False, show_password_toggle: bool = False):
    super().__init__()

    self._max_text_size = max_text_size
    self._min_text_size = min_text_size
    self._password_mode = password_mode
    self._show_password_toggle = show_password_toggle
    self._render_return_status = -1

    # Title + subtitle
    self._title = Label("", 90, FontWeight.BOLD, rl.GuiTextAlignment.TEXT_ALIGN_LEFT, text_padding=20)
    self._sub_title = Label("", 55, FontWeight.NORMAL, rl.GuiTextAlignment.TEXT_ALIGN_LEFT, text_padding=20)

    # Input box
    self._input_box = InputBox(max_text_size)
    self._input_box._font_size = 56  # tuned for Tizi

    # Top buttons
    self._cancel_button = Button(lambda: tr("Cancel"), self._cancel_button_callback)
    self._done_button = Button(lambda: tr("Done"), self._done_button_callback, button_style=ButtonStyle.PRIMARY)

    # Eye toggle
    self._eye_button = Button("", self._eye_button_callback, button_style=ButtonStyle.TRANSPARENT)
    self._eye_open_texture = gui_app.texture("icons/eye_open.png", 81, 54)
    self._eye_closed_texture = gui_app.texture("icons/eye_closed.png", 81, 54)

    # Backspace
    self._backspace_button = Button("", self._backspace_button_callback,
                                    icon=gui_app.texture("icons/backspace.png", 80, 80),
                                    button_style=ButtonStyle.TRANSPARENT)

    self._backspace_is_down = False
    self._backspace_down_time = 0.0
    self._backspace_last_repeat = 0.0

    # ========== MICI Keyboard (Tuned) ==========
    self._mici_keyboard = MiciKeyboard()

    # override pill background EXACTLY
    try:
      self._mici_keyboard._txt_bg = gui_app.texture(
        "icons_mici/settings/keyboard/keyboard_background.png",
        PILL_W,
        PILL_H,
        keep_aspect_ratio=False,
      )
    except Exception as e:
      print("Pill BG override failed:", e)

    # override MICI internal layout values
    self._mici_keyboard._pill_w = PILL_W
    self._mici_keyboard._pill_h = PILL_H
    self._mici_keyboard._key_font_size = KEY_FONT_SIZE
    self._mici_keyboard._row_spacing = ROW_SPACING
    self._mici_keyboard._key_spacing = KEY_SPACING



  # ===== API =====
  def set_text(self, text: str):
    if len(text) > self._max_text_size:
      text = text[:self._max_text_size]
    self._mici_keyboard.set_text(text)
    self._input_box.text = text

  @property
  def text(self):
    return self._mici_keyboard.text()

  def clear(self):
    self._mici_keyboard.set_text("")
    self._input_box.clear()
    self._backspace_is_down = False

  def set_title(self, title: str, sub_title: str = ""):
    self._title.set_text(title)
    self._sub_title.set_text(sub_title)

  def reset(self, min_text_size=None):
    if min_text_size is not None:
      self._min_text_size = min_text_size
    self._render_return_status = -1
    self._backspace_is_down = False
    self.clear()


  # ===== Button Callbacks =====
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



  # ===== Render =====
  def _render(self, rect: rl.Rectangle):
    # outer margin
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
    cancel_rect = rl.Rectangle(rect.x + rect.width - buttons_width * 2, rect.y, buttons_width, 125)
    done_rect = rl.Rectangle(rect.x + rect.width - buttons_width, rect.y, buttons_width, 125)

    self._cancel_button.render(cancel_rect)
    self._done_button.set_enabled(len(self.text) >= self._min_text_size)
    self._done_button.render(done_rect)

    # input
    input_rect = rl.Rectangle(
      rect.x + 25,
      rect.y + INPUT_TOP_MARGIN,
      rect.width - 50,
      105,
    )
    self._render_input_area(input_rect)

    self._update_backspace_repeat()

    # keyboard
    kb_height = self._mici_keyboard.get_keyboard_height()

    kb_rect = rl.Rectangle(
      rect.x,
      rect.y + rect.height - kb_height - KEYBOARD_BOTTOM_MARGIN,
      rect.width,
      kb_height,
    )

    self._mici_keyboard.set_rect(kb_rect)
    self._mici_keyboard.render(kb_rect)

    # sync text
    new_text = self._mici_keyboard.text()
    if len(new_text) > self._max_text_size:
      new_text = new_text[:self._max_text_size]
      self._mici_keyboard.set_text(new_text)

    self._input_box.text = new_text

    return self._render_return_status



  # ===== Input Field =====
  def _render_input_area(self, input_rect: rl.Rectangle):
    extra_w = 110
    if self._show_password_toggle:
      extra_w += 100

    box_rect = rl.Rectangle(
      input_rect.x,
      input_rect.y,
      input_rect.width - extra_w,
      input_rect.height,
    )

    self._input_box.set_password_mode(self._password_mode and self._show_password_toggle)
    self._input_box.render(box_rect)

    right_x = box_rect.x + box_rect.width

    # password toggle
    if self._show_password_toggle:
      eye_rect = rl.Rectangle(right_x, input_rect.y, 100, input_rect.height)
      self._eye_button.render(eye_rect)
      tex = self._eye_closed_texture if self._password_mode else self._eye_open_texture
      rl.draw_texture_v(
        tex,
        rl.Vector2(eye_rect.x + (eye_rect.width - tex.width) / 2,
                   eye_rect.y + (eye_rect.height - tex.height) / 2),
        rl.WHITE,
      )
      right_x += 100

    # backspace
    backspace_rect = rl.Rectangle(right_x, input_rect.y, 110, input_rect.height)

    if not self._backspace_button.is_pressed:
      self._backspace_is_down = False

    self._backspace_button.render(backspace_rect)

    # underline
    underline_y = input_rect.y + input_rect.height - 2
    rl.draw_line_ex(
      rl.Vector2(input_rect.x, underline_y),
      rl.Vector2(input_rect.x + input_rect.width, underline_y),
      3.0,
      rl.Color(189, 189, 189, 255),
    )



  # ===== Backspace hold behavior =====
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
