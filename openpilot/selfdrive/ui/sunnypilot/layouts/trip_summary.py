"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import time
import pyray as rl

from opendbc.car.structs import car

from openpilot.common.constants import CV
from openpilot.selfdrive.ui.onroad.augmented_road_view import BORDER_COLORS
from openpilot.selfdrive.ui.ui_state import ui_state, UIStatus
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget

MIN_DISTANCE = 160.
AUTO_DISMISS = 20.
FADE_IN, FADE_OUT = 0.35, 0.3
LAT = (UIStatus.ENGAGED, UIStatus.LAT_ONLY)
LONG = (UIStatus.ENGAGED, UIStatus.LONG_ONLY)
GEAR = car.CarState.GearShifter
FORWARD = (GEAR.drive, GEAR.sport, GEAR.low, GEAR.brake, GEAR.eco, GEAR.manumatic)


class TripTracker:
  def __init__(self):
    self.reset()

  def reset(self):
    self.segments: list[list] = []
    self.seconds = 0.
    self.takeovers = 0
    self._t = None
    self._status = None

  def update(self, driving: bool):
    now = time.monotonic()
    if not driving:
      self._t = None
      self._status = None
      return
    dt = 0. if self._t is None else min(now - self._t, 0.5)
    self._t = now
    self.seconds += dt
    if self._status not in (None, UIStatus.DISENGAGED) and ui_state.status == UIStatus.DISENGAGED:
      self.takeovers += 1
    self._status = ui_state.status
    d = max(ui_state.sm["carState"].vEgo, 0.) * dt
    if d <= 0.:
      return
    if self.segments and self.segments[-1][0] == ui_state.status:
      self.segments[-1][1] += d
    else:
      self.segments.append([ui_state.status, d])

  def total(self, statuses=None) -> float:
    return sum(m for s, m in self.segments if statuses is None or s in statuses)


class TripSummary:
  def __init__(self):
    self._trip = TripTracker()
    self._dialog: TripSummaryDialog | None = None
    self._gear = None
    self._drove = False
    gui_app.add_nav_stack_tick(self._tick)

  def _tick(self):
    gear = ui_state.sm["carState"].gearShifter if ui_state.started else None
    self._trip.update(gear not in (None, GEAR.park))
    self._drove |= gear in FORWARD
    if gear == self._gear:
      return
    self._gear = gear

    if gear not in (None, GEAR.park):
      self._pop()
    elif gear == GEAR.park and self._drove and ui_state.trip_summary and not ui_state.is_body and self._trip.total() >= MIN_DISTANCE:
      self._dialog = TripSummaryDialog(self._trip, gui_app.get_active_widget(), self._pop)
      gui_app.push_widget(self._dialog)
    if gear is None:
      self._trip.reset()
    if gear in (None, GEAR.park):
      self._drove = False

  def _pop(self):
    if self._dialog is not None and gui_app.get_active_widget() is self._dialog:
      gui_app.pop_widget()
    self._dialog = None


def _ease(t: float) -> float:
  t = min(max(t, 0.), 1.)
  return 1 - (1 - t) ** 3


def _fade(c, a: float) -> rl.Color:
  r, g, b, al = c if isinstance(c, tuple) else (c.r, c.g, c.b, c.a)
  return rl.Color(r, g, b, int(al * a))


class TripSummaryDialog(Widget):
  def __init__(self, trip: TripTracker, below: Widget | None, on_closed):
    super().__init__()
    self._below = below
    self._on_closed = on_closed
    self._segments = segments = trip.segments
    total = sum(m for _, m in segments)

    def pct(statuses):
      return 100 * sum(m for s, m in segments if s in statuses) / total

    dist = total * (CV.MS_TO_KPH if ui_state.is_metric else CV.MS_TO_MPH) / 3600
    dist_fmt = "{:.1f}" if dist < 9.95 else "{:.0f}"
    self._stats = [
      (dist, dist_fmt, "km" if ui_state.is_metric else "mi", "driven"),
      (pct(LAT + LONG), "{:.0f}", "%", "engaged"),
      (pct(LAT), "{:.0f}", "%", "lateral"),
      (pct(LONG), "{:.0f}", "%", "longitudinal"),
    ]
    mins = round(trip.seconds / 60)
    self._details = [
      (f"{mins // 60}h {mins % 60}" if mins >= 60 else f"{mins}", "min"),
      (f"{trip.takeovers}", "takeover" if trip.takeovers == 1 else "takeovers"),
    ]
    self._bold = gui_app.font(FontWeight.BOLD)
    self._semi = gui_app.font(FontWeight.SEMI_BOLD)
    self._normal = gui_app.font(FontWeight.NORMAL)
    self._big = gui_app.big_ui()
    self._shown_t = rl.get_time()
    self._closing_t: float | None = None
    self.set_click_callback(self.close)

  def close(self):
    if self._closing_t is None:
      self._closing_t = rl.get_time()

  def _render(self, rect: rl.Rectangle):
    t = rl.get_time() - self._shown_t
    if self._closing_t is None and t > AUTO_DISMISS:
      self.close()
    out = 0. if self._closing_t is None else (rl.get_time() - self._closing_t) / FADE_OUT
    if out >= 1.:
      self._on_closed()
      return
    bg = 1 - _ease(out)
    a = _ease(t / FADE_IN) * bg

    if self._big and self._below is not None and bg < 1.:
      self._below.render(rect)
    rl.draw_rectangle_rec(rect, _fade(rl.BLACK, bg))

    k = rect.height / 1080 * (1.0 if self._big else 1.22)
    pad = 120 * k
    x, w = rect.x + pad, rect.width - 2 * pad
    y = rect.y + (rect.height - 850 * k) / 2

    rl.draw_text_ex(self._bold, "trip summary", rl.Vector2(x, y), int(150 * k), 0, _fade(rl.WHITE, a))
    y += 260 * k

    col_w = w / len(self._stats)
    for i, (target, fmt, unit, label) in enumerate(self._stats):
      cx = x + col_w * (i + 0.5)
      v = measure_text_cached(self._bold, fmt.format(target), int(170 * k))
      u = measure_text_cached(self._semi, unit, int(80 * k))
      vx = cx - (v.x + 10 * k + u.x) / 2
      rl.draw_text_ex(self._bold, fmt.format(target), rl.Vector2(vx, y), int(170 * k), 0, _fade(rl.WHITE, a))
      rl.draw_text_ex(self._semi, unit, rl.Vector2(vx + v.x + 10 * k, y + 75 * k), int(80 * k), 0, _fade(rl.WHITE, a))
      lb = measure_text_cached(self._normal, label, int(70 * k))
      rl.draw_text_ex(self._normal, label, rl.Vector2(cx - lb.x / 2, y + 180 * k), int(70 * k), 0, _fade(rl.Color(200, 200, 200, 255), a))
    y += 330 * k

    bar = rl.Rectangle(x, y, w, 90 * k)
    total = sum(m for _, m in self._segments)
    sx = bar.x
    for status, m in self._segments:
      sw = bar.width * m / total
      rl.draw_rectangle_rec(rl.Rectangle(sx, bar.y, min(sw + 1, bar.x + bar.width - sx), bar.height), _fade(BORDER_COLORS[status], a))
      sx += sw
    rl.draw_rectangle_rounded_lines_ex(bar, 1.0, 20, 30 * k, _fade(rl.BLACK, a))

    y += (90 + 70) * k

    size = int(90 * k)
    parts = []
    for i, (value, unit) in enumerate(self._details):
      if i:
        parts.append(("     ", self._normal, None))
      parts += [(value, self._bold, rl.WHITE), (" " + unit, self._normal, rl.Color(170, 170, 170, 255))]
    widths = [measure_text_cached(f, t, size).x for t, f, _ in parts]
    lx = x + (w - sum(widths)) / 2
    for (text, font, color), tw in zip(parts, widths, strict=True):
      if color is None:
        rl.draw_circle(int(lx + tw / 2), int(y + size * 0.6), 12 * k, _fade(rl.Color(110, 110, 110, 255), a))
      else:
        rl.draw_text_ex(font, text, rl.Vector2(lx, y), size, 0, _fade(color, a))
      lx += tw
