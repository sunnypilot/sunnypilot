"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math

import numpy as np
import pyray as rl

from openpilot.system.ui.lib.application import TextAlignment, TextAlignmentVertical

from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.shader_polygon import draw_polygon, Gradient
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.sunnypilot.lib.styles import style
from openpilot.system.ui.sunnypilot.widgets.list_view import ListItemSP
from openpilot.system.ui.widgets.label import UnifiedLabel
from openpilot.system.ui.sunnypilot.lib.utils import UnifiedLabelSP
from openpilot.system.ui.widgets.list_view import ItemAction

FONT_SIZE = style.ITEM_TEXT_FONT_SIZE
ICON_SIZE = 56
ICON_PADDING = 12

BAR_WIDTH = 1100
BAR_HEIGHT = 20
SEGMENT_GAP = 24
SEGMENT_NAME_MAX_WIDTH = 380
BAR_GAP = 16
BAR_RADIUS = BAR_HEIGHT / 2
CAPSULE_POINTS = 24

RAIL_COLOR = rl.Color(60, 60, 60, 255)
FILL_COLOR = rl.Color(30, 121, 232, 255)
# rl.WHITE is a tuple; the shimmer path reads .a off the color
TEXT_COLOR = rl.Color(255, 255, 255, 255)

SWEEP_SPEED = 550.0  # px/s
SWEEP_BAND = 240.0   # highlight half-width, px
SWEEP_DIM = 0.65


class DownloadStatusAction(ItemAction):
  """Model download row: a name + percent over a progress rail while downloading, a name + icon otherwise."""

  def __init__(self):
    super().__init__(width=BAR_WIDTH)
    self.name = ""
    self.status_text = ""
    self.segments: list[tuple[str, rl.Color, str | None, rl.Color | None]] | None = None
    self._segment_labels: list[UnifiedLabelSP] = []
    self.downloading = False
    self.text_color = rl.GRAY
    self.icon: str | None = None
    self.icon_color: rl.Color | None = None
    self._font = gui_app.font(FontWeight.NORMAL)
    # raw progress arrives in steps, one per progress report from the manager
    self._progress = FirstOrderFilter(0.0, 0.5, 1 / gui_app.target_fps)
    # integrated per frame; (t * speed) % span jumps whenever the fill width changes
    self._sweep = 0.0

    self._name_label = UnifiedLabel("", font_size=FONT_SIZE, font_weight=FontWeight.NORMAL, text_color=TEXT_COLOR,
                                    alignment=TextAlignment.LEFT,
                                    alignment_vertical=TextAlignmentVertical.MIDDLE)
    self._percent_label = UnifiedLabel("", font_size=FONT_SIZE, font_weight=FontWeight.NORMAL, text_color=TEXT_COLOR,
                                       alignment=TextAlignment.RIGHT,
                                       alignment_vertical=TextAlignmentVertical.MIDDLE)

  def update(self, name, downloading=False, progress=0.0, status_text="", text_color=rl.GRAY, icon=None, icon_color=None, segments=None):
    self.segments = segments
    if downloading and not self.downloading:
      self._name_label.reset_shimmer()
      self._progress.x = progress
      self._sweep = 0.0
    self.name = name
    self.downloading = downloading
    self.status_text = status_text
    self.text_color = text_color
    self.icon = icon
    self.icon_color = icon_color
    self._name_label._shimmer = downloading
    if downloading:
      self._progress.update(progress)
      self._sweep += SWEEP_SPEED / gui_app.target_fps

  @property
  def _idle_text(self) -> str:
    return f"{self.name} - {self.status_text}" if self.status_text else self.name

  def get_width_hint(self) -> float:
    if self.downloading:
      return BAR_WIDTH
    if self.segments:
      return sum(total for _, _, total in self._measured_segments())
    width = measure_text_cached(self._font, self._idle_text, FONT_SIZE).x
    if self.icon:
      width += ICON_SIZE + ICON_PADDING
    return width

  def _measured_segments(self):
    """[(segment, text width, total width incl. icon and gap)]"""
    out = []
    for i, seg in enumerate(self.segments or []):
      text_width = min(measure_text_cached(self._font, seg[0], FONT_SIZE).x, SEGMENT_NAME_MAX_WIDTH)
      total = text_width + (ICON_PADDING + ICON_SIZE if seg[2] else 0) + (SEGMENT_GAP if i else 0)
      out.append((seg, text_width, total))
    return out

  def _render(self, rect: rl.Rectangle):
    if self.downloading:
      self._render_downloading(rect)
    else:
      self._render_idle(rect)

  def _sweep_gradient(self, width: float) -> Gradient:
    # clearance at both ends keeps the wrap offscreen
    center = (self._sweep % (width + 2 * SWEEP_BAND)) - SWEEP_BAND

    def band(x: float) -> float:
      return max(0.0, 1.0 - abs(x - center) / SWEEP_BAND)

    # sampling the corners is exact for a piecewise linear band
    xs = sorted({0.0, width} | {min(max(center + o, 0.0), width) for o in (-SWEEP_BAND, 0.0, SWEEP_BAND)}, reverse=True)
    # the gradient axis runs right-to-left in screen space
    stops = [1.0 - x / width for x in xs]
    # alpha here is the lift over the SWEEP_DIM base, not the final opacity
    colors = [rl.Color(FILL_COLOR.r, FILL_COLOR.g, FILL_COLOR.b, int(255 * band(x))) for x in xs]
    return Gradient(start=(0.0, 0.0), end=(1.0, 0.0), colors=colors, stops=stops)

  @staticmethod
  def _capsule(rect: rl.Rectangle) -> np.ndarray:
    """Rounded-end ribbon so the gradient covers the caps."""
    r = rect.height / 2
    cy = rect.y + r
    top, bottom = [], []
    for i in range(CAPSULE_POINTS):
      x = rect.x + rect.width * i / (CAPSULE_POINTS - 1)
      d = min(x - rect.x, rect.x + rect.width - x, r)
      h = math.sqrt(max(r * r - (r - d) ** 2, 0.0))
      top.append((x, cy - h))
      bottom.append((x, cy + h))
    return np.array(top + bottom[::-1], dtype=np.float32)

  def _draw_fill(self, rail: rl.Rectangle, fill_width: float):
    if fill_width <= 0:
      return
    fill = rl.Rectangle(rail.x, rail.y, fill_width, rail.height)
    rl.draw_rectangle_rounded(fill, 1.0, 10, rl.Color(FILL_COLOR.r, FILL_COLOR.g, FILL_COLOR.b, int(255 * SWEEP_DIM)))
    draw_polygon(fill, self._capsule(fill), gradient=self._sweep_gradient(fill_width))

  def _render_downloading(self, rect: rl.Rectangle):
    percent = f"{int(self._progress.x)}%"
    if self.status_text:
      percent = f"{self.status_text} {percent}"
    text_height = measure_text_cached(self._font, percent, FONT_SIZE).y
    top = rect.y + (rect.height - (text_height + BAR_GAP + BAR_HEIGHT)) / 2

    text_rect = rl.Rectangle(rect.x, top, rect.width, text_height)
    self._name_label.set_text(self.name)
    self._name_label.render(text_rect)
    self._percent_label.set_text(percent)
    self._percent_label.render(text_rect)

    rail = rl.Rectangle(rect.x, top + text_height + BAR_GAP, rect.width, BAR_HEIGHT)
    rl.draw_rectangle_rounded(rail, 1.0, 10, RAIL_COLOR)
    self._draw_fill(rail, max(0.0, min(rect.width, rect.width * (self._progress.x / 100.0))))

  def _render_idle(self, rect: rl.Rectangle):
    if self.segments:
      self._render_segments(rect)
      return
    text = self._idle_text
    text_size = measure_text_cached(self._font, text, FONT_SIZE)
    right = rect.x + rect.width

    if self.icon:
      texture = gui_app.texture(self.icon, ICON_SIZE, ICON_SIZE, keep_aspect_ratio=True)
      rl.draw_texture_v(texture, rl.Vector2(right - texture.width, rect.y + (rect.height - texture.height) / 2),
                        self.icon_color or self.text_color)
      right -= texture.width + ICON_PADDING

    rl.draw_text_ex(self._font, text, rl.Vector2(right - text_size.x, rect.y + (rect.height - text_size.y) / 2),
                    FONT_SIZE, 0, self.text_color)

  def _render_segments(self, rect: rl.Rectangle):
    measured = self._measured_segments()
    while len(self._segment_labels) < len(measured):
      self._segment_labels.append(UnifiedLabelSP("", font_size=FONT_SIZE, max_width=SEGMENT_NAME_MAX_WIDTH,
                                                 scroll=True, wrap_text=False))
    x = rect.x + rect.width - sum(total for _, _, total in measured)
    for i, ((text, color, icon, icon_color), text_width, _) in enumerate(measured):
      if i:
        x += SEGMENT_GAP
      label = self._segment_labels[i]
      if label.text != text:
        label.set_text(text)
      label.set_text_color(color)
      text_height = measure_text_cached(self._font, text, FONT_SIZE).y
      label.set_position(x, rect.y + (rect.height - text_height) / 2)
      label.render()
      x += text_width
      if icon:
        texture = gui_app.texture(icon, ICON_SIZE, ICON_SIZE, keep_aspect_ratio=True)
        rl.draw_texture_v(texture, rl.Vector2(x + ICON_PADDING, rect.y + (rect.height - texture.height) / 2),
                          icon_color or color)
        x += ICON_PADDING + ICON_SIZE


def download_status_item(title):
  return ListItemSP(title=title, action_item=DownloadStatusAction(), title_color=style.ITEM_TEXT_COLOR)
