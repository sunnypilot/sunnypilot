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

# --- MICI keyboard imports ---
# Adjust this import if your mici_keyboard.py lives somewhere else.
from openpilot.system.ui.widgets.mici_keyboard import MiciKeyboard  # :contentReference[oaicite:0]{index=0}

KEY_FONT_SIZE = 96
DOUBLE_CLICK_THRESHOLD = 0.5  # seconds

# layout / margins
CONTENT_MARGIN = 50
INPUT_TOP_MARGIN = 160
KEYBOARD_BOTTOM_MARGIN = 40

# Special behaviour
BACKSPACE_HOLD_DELAY = 0.45
BACKSPACE_HOLD_INTERVAL = 0.07

# Tici scaling for MICI keyboard background
TICI_KB_SCALE_X = 3.0
TICI_KB_SCALE_Y = 3.0


class Keyboard(Widget):
  """
  TICI keyboard overlay that uses the MICI keyboard for key entry but keeps the
  classic API:

    - set_title(title, subtitle)
    - .text (property)
    - render() -> -1 (running), 0 (cancel), 1 (done)

  The MICI keyboard handles keys/animations. We show the text in the InputBox
  area and provide Cancel / Done / Backspace buttons.
  """

  def __init__(self, max_text_size: int = 255, min_text_size: int = 0,
               password_mode: bool = False, show_password_toggle: bool = False):
    super().__init__()

    # state
    self._max_text_size = max_text_size
    self._min_text_size = min_text_size
    self._password_mode = password_mode
    self._show_password_toggle = show_password_toggle
    self._render_return_status = -1

    # title + subtitle
    self._title = Label("", 90, FontWeight.BOLD, rl.GuiTextAlignment.TEXT_ALIGN_LEFT, text_padding=20)
    self._sub_title = Label("", 55, FontWeight.NORMAL, rl.GuiTextAlignment.TEXT_ALIGN_LEFT, text_padding=20)

    # text entry
    self._input_box = InputBox(max_text_size)

    # buttons
    self._cancel_button = Button(lambda: tr("Cancel"), self._cancel_button_callback)
    self._done_button = Button(lambda: tr("Done"), self._done_button_callback, button_style=ButtonStyle.PRIMARY)

    self._eye_button = Button("", self._eye_button_callback, button_style=ButtonStyle.TRANSPARENT)
    self._eye_open_texture = gui_app.texture("icons/eye_open.png", 81, 54)
    self._eye_closed_texture = gui_app.texture("icons/eye_closed.png", 81, 54)

    # backspace button (since MICI keyboard itself has no delete key)
    self._backspace_button = Button("", self._backspace_button_callback,
                                    icon=gui_app.texture("icons/backspace.png", 80, 80),
                                    button_style=ButtonStyle.TRANSPARENT)

    # backspace hold-to-repeat
    self._backspace_is_down: bool = False
    self._backspace_down_time: float = 0.0
    self._backspace_last_repeat: float = 0.0

    # MICI keyboard instance, scaled up for TICI
    self._mici_keyboard = MiciKeyboard()
    # overwrite background with a larger texture so it fills more width/height on TICI
    try:
      self._mici_keyboard._txt_bg = gui_app.texture(
        "icons_mici/settings/keyboard/keyboard_background.png",
        int(520 * TICI_KB_SCALE_X),
        int(170 * TICI_KB_SCALE_Y),
        keep_aspect_ratio=False,
      )
    except Exception:
      # if path ever changes, at least don't crash – keyboard will use its default size
      pass

  # ---------- public API ----------

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
    self._backspace_down_time = 0.0
    self._backspace_last_repeat = 0.0
    self.clear()

  # ---------- button callbacks ----------

  def _eye_button_callback(self):
    self._password_mode = not self._password_mode

  def _cancel_button_callback(self):
    self.clear()
    self._render_return_status = 0

  def _done_button_callback(self):
    if len(self.text) >= self._min_text_size:
      self._render_return_status = 1

  def _backspace_button_callback(self):
    # single tap delete
    self._mici_keyboard.backspace()
    self._input_box.text = self._mici_keyboard.text()
    # start repeat behaviour
    self._backspace_is_down = True
    self._backspace_down_time = time.monotonic()
    self._backspace_last_repeat = self._backspace_down_time

  # ---------- core render ----------

  def _render(self, rect: rl.Rectangle):
    # inset outer margins
    rect = rl.Rectangle(
      rect.x + CONTENT_MARGIN,
      rect.y + CONTENT_MARGIN,
      rect.width - 2 * CONTENT_MARGIN,
      rect.height - 2 * CONTENT_MARGIN,
    )

    # titles
    self._title.render(rl.Rectangle(rect.x, rect.y, rect.width, 95))
    self._sub_title.render(rl.Rectangle(rect.x, rect.y + 95, rect.width, 60))

    # Cancel and Done buttons in top-right
    buttons_width = 360
    top_button_height = 125
    cancel_rect = rl.Rectangle(rect.x + rect.width - buttons_width * 2, rect.y, buttons_width, top_button_height)
    done_rect = rl.Rectangle(rect.x + rect.width - buttons_width, rect.y, buttons_width, top_button_height)
    self._cancel_button.render(cancel_rect)
    self._done_button.set_enabled(len(self.text) >= self._min_text_size)
    self._done_button.render(done_rect)

    # --- text line with password toggle + backspace button ---
    input_margin = 25
    input_rect = rl.Rectangle(
      rect.x + input_margin,
      rect.y + INPUT_TOP_MARGIN,
      rect.width - 2 * input_margin,
      105,
    )
    self._render_input_area(input_rect)

    # backspace hold-to-repeat
    self._update_backspace_repeat()

    # --- MICI keyboard at the bottom ---
    kb_height = self._mici_keyboard.get_keyboard_height()
    kb_rect = rl.Rectangle(
      rect.x,
      rect.y + rect.height - kb_height - KEYBOARD_BOTTOM_MARGIN,
      rect.width,
      kb_height + KEYBOARD_BOTTOM_MARGIN,
    )
    self._mici_keyboard.set_rect(kb_rect)
    self._mici_keyboard.render(kb_rect)

    # sync text from MICI → InputBox (respect max length)
    new_text = self._mici_keyboard.text()
    if len(new_text) > self._max_text_size:
      new_text = new_text[:self._max_text_size]
      self._mici_keyboard.set_text(new_text)
    self._input_box.text = new_text

    return self._render_return_status

  # ---------- helpers ----------

  def _render_input_area(self, input_rect: rl.Rectangle):
    """
    Draws the InputBox plus password eye (optional) and backspace button.
    """
    # how much width to keep for eye + backspace
    extra_w = 0
    if self._show_password_toggle:
      extra_w += 100  # eye
    extra_w += 110      # backspace

    box_rect = rl.Rectangle(input_rect.x, input_rect.y, input_rect.width - extra_w, input_rect.height)

    # password mode
    self._input_box.set_password_mode(self._password_mode and self._show_password_toggle)
    self._input_box.render(box_rect)

    right_x = box_rect.x + box_rect.width

    # password eye toggle (if enabled)
    if self._show_password_toggle:
      eye_rect = rl.Rectangle(right_x, input_rect.y, 100, input_rect.height)
      self._eye_button.render(eye_rect)
      eye_texture = self._eye_closed_texture if self._password_mode else self._eye_open_texture
      eye_x = eye_rect.x + (eye_rect.width - eye_texture.width) / 2
      eye_y = eye_rect.y + (eye_rect.height - eye_texture.height) / 2
      rl.draw_texture_v(eye_texture, rl.Vector2(eye_x, eye_y), rl.WHITE)
      right_x += eye_rect.width

    # backspace button at far right
    backspace_rect = rl.Rectangle(right_x, input_rect.y, 110, input_rect.height)
    # detect if the Button is currently pressed so we can drive repeat logic
    if not self._backspace_button.is_pressed:
      # if released, stop repeating
      self._backspace_is_down = False
    self._backspace_button.render(backspace_rect)

    # underline for input box (across whole width)
    underline_y = input_rect.y + input_rect.height - 2
    rl.draw_line_ex(
      rl.Vector2(input_rect.x, underline_y),
      rl.Vector2(input_rect.x + input_rect.width, underline_y),
      3.0,
      rl.Color(189, 189, 189, 255),
    )

  def _update_backspace_repeat(self):
    """Implements press-and-hold behaviour for the backspace button."""
    if not self._backspace_is_down:
      return

    now = time.monotonic()
    if now - self._backspace_down_time < BACKSPACE_HOLD_DELAY:
      return

    if now - self._backspace_last_repeat >= BACKSPACE_HOLD_INTERVAL:
      self._mici_keyboard.backspace()
      self._input_box.text = self._mici_keyboard.text()
      self._backspace_last_repeat = now


if __name__ == "__main__":
  # Simple local test harness
  gui_app.init_window("Keyboard")
  keyboard = Keyboard(min_text_size=3, show_password_toggle=True)
  for _ in gui_app.render():
    keyboard.set_title("Keyboard Input", "Type your text below")
    result = keyboard.render(rl.Rectangle(0, 0, gui_app.width, gui_app.height))
    if result == 1:
      print(f"You typed: {keyboard.text}")
      gui_app.request_close()
    elif result == 0:
      print("Canceled")
      gui_app.request_close()
  gui_app.close()
