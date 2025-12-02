from functools import partial
import time
from typing import Literal

import numpy as np
import pyray as rl

from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.animation import ease_out_cubic, LinearAnimation
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.button import ButtonStyle, Button
from openpilot.system.ui.widgets.inputbox import InputBox

# MICI keyboard (unmodified)
from openpilot.system.ui.widgets.mici_keyboard import (
  CHAR_FONT_SIZE,
  CHAR_NEAR_FONT_SIZE,
  KEYBOARD_COLUMN_PADDING,
  KEYBOARD_ROW_PADDING,
  KEY_TOUCH_AREA_OFFSET,
  MiciKeyboard,
  SELECTED_CHAR_FONT_SIZE,
  fast_euclidean_distance,
)


# ========= TIZI SCALING CONSTANTS (2160×1080) =========
PILL_W = 2000     # shortened overall keyboard width by ~60px
PILL_H = 600      # was 375
KEY_FONT_SIZE = 88     # final key letter size (larger keys)
ROW_SPACING = 1
KEY_SPACING = 1
KEYBOARD_INNER_PADDING_X = 80  # extra space inside pill before keys start
KEYBOARD_INNER_PADDING_Y = 60

KB_SCALE = 1.00      # global keyboard scale (keep 1.00)
CONTENT_MARGIN = 50
INPUT_TOP_MARGIN = 120
KEYBOARD_BOTTOM_MARGIN = 40

BACKSPACE_HOLD_DELAY = 0.45
BACKSPACE_HOLD_INTERVAL = 0.07

TOP_BAR_HEIGHT = 170
TOP_BAR_PADDING_X = 60
TOP_BAR_RADIUS = 0.18
TOP_BAR_BUTTON_WIDTH = 300
TOP_BAR_BUTTON_HEIGHT = 118
TOP_BAR_BUTTON_GAP = 24
TOP_BAR_SPACING = 36
TOP_BAR_BG = rl.Color(12, 12, 12, 235)
TOP_BAR_BORDER = rl.Color(255, 255, 255, 32)
ANIMATION_DURATION = 0.25  # seconds
ANIMATION_OFFSET = 160


def _color_with_alpha(color: rl.Color, alpha: float) -> rl.Color:
  alpha = np.clip(alpha, 0.0, 1.0)
  return rl.Color(color.r, color.g, color.b, int(color.a * alpha))


class ScaledMiciKeyboard(MiciKeyboard):
  """
  Wrapper around MiciKeyboard that keeps the original visuals intact while allowing
  font size and row/key spacing to be adjusted from keyboard.py.
  """

  def __init__(self, *, key_font_size: float, row_spacing: float, key_spacing: float):
    super().__init__()
    self._row_spacing = row_spacing
    self._key_spacing = key_spacing

    # scale the various font sizes proportionally to the base key font size
    font_scale = key_font_size / CHAR_FONT_SIZE
    self._base_font_size = key_font_size
    self._near_font_size = CHAR_NEAR_FONT_SIZE * font_scale
    self._selected_font_size = SELECTED_CHAR_FONT_SIZE * font_scale

  def _lay_out_keys(self, bg_x, bg_y, keys: list[list["Key"]]):
    key_rect = rl.Rectangle(
      bg_x + KEYBOARD_INNER_PADDING_X,
      bg_y + KEYBOARD_INNER_PADDING_Y,
      max(self._txt_bg.width - 2 * KEYBOARD_INNER_PADDING_X, 1),
      max(self._txt_bg.height - 2 * KEYBOARD_INNER_PADDING_Y, 1),
    )
    row_count = max(len(keys) - 1, 1)
    available_height = (key_rect.height - 2 * KEYBOARD_COLUMN_PADDING) - self._row_spacing * row_count
    step_y = max(available_height, 1) / row_count

    for row_idx, row in enumerate(keys):
      padding = KEYBOARD_ROW_PADDING.get(row_idx, 0)
      col_count = max(len(row) - 1, 1)
      available_width = (key_rect.width - 2 * padding) - self._key_spacing * col_count
      step_x = max(available_width, 1) / col_count

      for key_idx, key in enumerate(row):
        base_x = key_rect.x + padding + key_idx * (step_x + self._key_spacing)
        base_y = key_rect.y + KEYBOARD_COLUMN_PADDING + row_idx * (step_y + self._row_spacing)

        # ensure proximity checks stay aligned even as the keyboard slides in/out
        key.original_position = rl.Vector2(base_x, base_y + KEY_TOUCH_AREA_OFFSET)

        key_x = base_x
        key_y = base_y

        if self._closest_key[0] is None:
          key.set_alpha(1.0)
          key.set_font_size(self._base_font_size)
        elif key == self._closest_key[0]:
          # push key up with a max and inward so user can see key easier
          key_y = max(key_y - 120, 40)
          key_x += np.interp(key_x, [self._rect.x, self._rect.x + self._rect.width], [100, -100])
          key.set_alpha(1.0)
          key.set_font_size(self._selected_font_size)

          # draw black circle behind selected key
          rl.draw_circle_gradient(int(key_x + key.rect.width / 2), int(key_y + key.rect.height / 2),
                                  self._selected_font_size, rl.Color(0, 0, 0, 225), rl.BLANK)
        else:
          dx = key.original_position.x - self._closest_key[0].original_position.x
          dy = key.original_position.y - self._closest_key[0].original_position.y
          distance_from_selected_key = fast_euclidean_distance(dx, dy)

          inv = 1 / (distance_from_selected_key or 1.0)
          ux = dx * inv
          uy = dy * inv

          push_pixels = np.interp(distance_from_selected_key, [0, 250], [20, 0])
          key_x += ux * push_pixels
          key_y += uy * push_pixels

          font_size = np.interp(distance_from_selected_key, [0, 150], [self._near_font_size, self._base_font_size])
          key_alpha = np.interp(distance_from_selected_key, [0, 100], [1.0, 0.35])
          key.set_alpha(key_alpha)
          key.set_font_size(font_size)

        key.set_position(key_x, key_y)


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

    self._title_text = ""
    self._sub_title_text = ""

    # Input box
    self._input_box = InputBox(max_text_size)
    self._input_box._font_size = 56  # tuned for Tizi

    # Top buttons + icons
    self._cancel_button = Button(
      lambda: tr("Cancel"),
      self._cancel_button_callback,
      button_style=ButtonStyle.NORMAL,
      border_radius=54,
      text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER,
    )
    self._done_button = Button(
      lambda: tr("Done"),
      self._done_button_callback,
      button_style=ButtonStyle.PRIMARY,
      border_radius=54,
      text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER,
    )

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
    self._anim = LinearAnimation(ANIMATION_DURATION, initial_progress=0.0)
    self._anim.start('in')
    self._dismissing = False
    self._pending_return_status: int | None = None

    # ========== MICI Keyboard (Tuned) ==========
    self._mici_keyboard = ScaledMiciKeyboard(
      key_font_size=KEY_FONT_SIZE,
      row_spacing=ROW_SPACING,
      key_spacing=KEY_SPACING,
    )

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
    self._title_text = title
    self._sub_title_text = sub_title

  def reset(self, min_text_size=None):
    if min_text_size is not None:
      self._min_text_size = min_text_size
    self._render_return_status = -1
    self._backspace_is_down = False
    self.clear()
    self._anim.start('in')
    self._dismissing = False
    self._pending_return_status = None


  # ===== Button Callbacks =====
  def _eye_button_callback(self):
    self._password_mode = not self._password_mode

  def _cancel_button_callback(self):
    self.clear()
    self._start_dismiss(0)

  def _done_button_callback(self):
    if len(self.text) >= self._min_text_size:
      self._start_dismiss(1)

  def _backspace_button_callback(self):
    self._mici_keyboard.backspace()
    self._input_box.text = self._mici_keyboard.text()
    self._backspace_is_down = True
    self._backspace_down_time = time.monotonic()
    self._backspace_last_repeat = self._backspace_down_time

  def _start_dismiss(self, status: int):
    if self._pending_return_status == status and self._dismissing:
      return
    self._pending_return_status = status
    self._dismissing = True
    self._anim.start('out')



  # ===== Render =====
  def _render(self, rect: rl.Rectangle):
    self._update_animation()
    if self._render_return_status != -1:
      return self._render_return_status

    # outer margin
    rect = rl.Rectangle(
      rect.x + CONTENT_MARGIN,
      rect.y + CONTENT_MARGIN,
      rect.width - 2 * CONTENT_MARGIN,
      rect.height - 2 * CONTENT_MARGIN,
    )

    eased = ease_out_cubic(self._anim.progress)
    slide_offset = (1.0 - eased) * ANIMATION_OFFSET
    rect = rl.Rectangle(rect.x, rect.y + slide_offset, rect.width, rect.height)

    # top button row (no background container)
    top_bar_rect = rl.Rectangle(rect.x, rect.y, rect.width, TOP_BAR_HEIGHT)

    button_y = top_bar_rect.y + (TOP_BAR_HEIGHT - TOP_BAR_BUTTON_HEIGHT) / 2 - 6
    cancel_rect = rl.Rectangle(top_bar_rect.x + TOP_BAR_PADDING_X - 12, button_y,
                   TOP_BAR_BUTTON_WIDTH, TOP_BAR_BUTTON_HEIGHT)
    done_rect = rl.Rectangle(top_bar_rect.x + top_bar_rect.width - TOP_BAR_PADDING_X - TOP_BAR_BUTTON_WIDTH + 12,
                 button_y, TOP_BAR_BUTTON_WIDTH, TOP_BAR_BUTTON_HEIGHT)

    self._cancel_button.set_enabled(not self._dismissing)
    self._cancel_button.render(cancel_rect)
    self._done_button.set_enabled((not self._dismissing) and len(self.text) >= self._min_text_size)
    self._done_button.render(done_rect)

    # input
    input_rect = rl.Rectangle(
      rect.x + 25,
      top_bar_rect.y + TOP_BAR_HEIGHT + TOP_BAR_SPACING - 8,
      rect.width - 50,
      105,
    )
    self._render_input_area(input_rect, eased)

    self._update_backspace_repeat()

    # keyboard
    # ====== KEYBOARD RENDER (with Tizi scaling) ======

    kb_height = self._mici_keyboard.get_keyboard_height()

    # unscaled keyboard rectangle
    kb_rect = rl.Rectangle(
      rect.x,
      rect.y + rect.height - kb_height - KEYBOARD_BOTTOM_MARGIN,
      rect.width,
      kb_height,
    )

    # pass the real rect through so mouse hit testing matches what is drawn
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
  def _render_input_area(self, input_rect: rl.Rectangle, eased: float):
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
      _color_with_alpha(rl.Color(189, 189, 189, 255), eased),
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

  def _update_animation(self):
    self._anim.step()

    if self._dismissing and not self._anim.active and self._pending_return_status is not None:
      self._render_return_status = self._pending_return_status
