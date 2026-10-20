import pyray as rl

from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.selfdrive.ui.mici.onroad import SIDE_PANEL_WIDTH
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget

BOOST_SCALE_MAX = 0.35
BAR_WIDTH = 10
VALUE_FONT_SIZE = 17
LABEL_FONT_SIZE = 10

COLOR_TRACK = rl.Color(255, 255, 255, 40)
COLOR_TEXT = rl.Color(255, 255, 255, 235)

PROFILE_STYLES = {
  0: ("AGGR", rl.Color(255, 80, 60, 255)),
  1: ("STD", rl.Color(0, 230, 120, 255)),
  2: ("RELAX", rl.Color(70, 150, 255, 255)),
}


class AccelBoostIndicator(Widget):
  def __init__(self):
    super().__init__()
    self._boost_filter = FirstOrderFilter(0.0, 0.15, 1 / gui_app.target_fps)
    self._alpha_filter = FirstOrderFilter(0.0, 0.1, 1 / gui_app.target_fps)
    self._font = gui_app.font(FontWeight.BOLD)
    self._label_font = gui_app.font(FontWeight.MEDIUM)
    self._profile_label = "STD"
    self._profile_color = PROFILE_STYLES[1][1]

  def _update_state(self):
    sm = ui_state.sm
    visible = (ui_state.has_longitudinal_control and sm.alive['selfdriveState'] and sm.alive['longitudinalPlan'] and
               sm['selfdriveState'].enabled)
    self._alpha_filter.update(1.0 if visible else 0.0)
    self._boost_filter.update(float(sm['longitudinalPlan'].accelBoost) if visible else 0.0)

    if sm.alive['selfdriveState']:
      self._profile_label, self._profile_color = PROFILE_STYLES.get(sm['selfdriveState'].personality.raw, PROFILE_STYLES[1])

  def _render(self, _):
    alpha = self._alpha_filter.x
    if alpha < 0.01:
      return

    panel_x = self.rect.x + self.rect.width - SIDE_PANEL_WIDTH
    margin = min(120.0, max(56.0, self.rect.height * 0.14))
    track_top = self.rect.y + margin
    track_bottom = self.rect.y + self.rect.height - margin
    track_h = max(1.0, track_bottom - track_top)
    cx = panel_x + SIDE_PANEL_WIDTH / 2
    bar_x = cx - BAR_WIDTH / 2

    # track
    rl.draw_rectangle_rounded(rl.Rectangle(bar_x, track_top, BAR_WIDTH, track_h), 0.5, 12,
                              rl.Color(COLOR_TRACK.r, COLOR_TRACK.g, COLOR_TRACK.b, int(COLOR_TRACK.a * alpha)))

    boost = min(max(self._boost_filter.x, 0.0), BOOST_SCALE_MAX)
    fill_h = boost / BOOST_SCALE_MAX * track_h
    if fill_h > 0.0:
      fill = rl.Color(self._profile_color.r, self._profile_color.g, self._profile_color.b, int(255 * alpha))
      if fill_h < BAR_WIDTH:
        rl.draw_circle(int(cx), int(track_bottom - fill_h / 2), max(1, int(BAR_WIDTH / 2)), fill)
      else:
        rl.draw_rectangle_rounded(rl.Rectangle(bar_x, track_bottom - fill_h, BAR_WIDTH, fill_h), 0.5, 12, fill)

    label_size = measure_text_cached(self._label_font, self._profile_label, LABEL_FONT_SIZE)
    rl.draw_text_ex(self._label_font, self._profile_label, rl.Vector2(cx - label_size.x / 2, track_top - 42),
                    LABEL_FONT_SIZE, 0,
                    rl.Color(self._profile_color.r, self._profile_color.g, self._profile_color.b, int(230 * alpha)))

    value = f"+{boost:.2f}"
    value_size = measure_text_cached(self._font, value, VALUE_FONT_SIZE)
    rl.draw_text_ex(self._font, value, rl.Vector2(cx - value_size.x / 2, track_top - 30), VALUE_FONT_SIZE, 0,
                    rl.Color(COLOR_TEXT.r, COLOR_TEXT.g, COLOR_TEXT.b, int(COLOR_TEXT.a * alpha)))
