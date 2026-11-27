"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl

from openpilot.cereal import log
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.selfdrive.ui.mici.onroad.augmented_road_view import BookmarkIcon
from openpilot.selfdrive.ui.sunnypilot.mici.onroad.robotic.alert_overlay import RoboticAlertOverlay
from openpilot.selfdrive.ui.sunnypilot.mici.onroad.robotic.expressions import (
  DrivingSnapshot,
  RoboticMoodEngine,
  snapshot_from_ui_state,
)
from openpilot.selfdrive.ui.sunnypilot.mici.onroad.robotic.face_renderer import ProceduralFaceRenderer
from openpilot.selfdrive.ui.sunnypilot.mici.onroad.robotic.speed_arc_renderer import SpeedArcRenderer
from openpilot.selfdrive.ui.sunnypilot.ui_state import OnroadTimerStatus
from openpilot.selfdrive.ui.ui_state import UIStatus, ui_state
from openpilot.system.ui.lib.application import (
  FontWeight,
  MouseEvent,
  MousePos,
  TextAlignment,
  TextAlignmentVertical,
  gui_app,
)
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.label import UnifiedLabel

VERTICAL_SWIPE_THRESHOLD = 45.0  # px


class RoboticOnroadView(Widget):
  """Full-screen EMO-inspired Robotic Companion onroad view for MICI (536x240 @ 60 FPS)."""

  def __init__(self, bookmark_callback=None):
    super().__init__()
    self._bookmark_callback = bookmark_callback

    self._mood_engine = RoboticMoodEngine()
    self._face_renderer = ProceduralFaceRenderer()
    self._speed_renderer = SpeedArcRenderer()
    self._alert_overlay = RoboticAlertOverlay()

    self._bookmark_icon = BookmarkIcon(self._on_bookmark_triggered)

    dt = 1.0 / max(gui_app.target_fps, 1)
    self._speed_blend = FirstOrderFilter(0.0, 0.08, dt)

    # Vertical swipe tracking (up = speed peek, down = pet robot)
    self._touch_start_y: float = 0.0
    self._touch_start_x: float = 0.0
    self._vertical_swipe_handled: bool = False

    self._offroad_label = UnifiedLabel(
      "start the car to\nuse sunnypilot",
      54,
      FontWeight.DISPLAY,
      text_color=rl.Color(255, 255, 255, int(255 * 0.9)),
      alignment=TextAlignment.CENTER,
      alignment_vertical=TextAlignmentVertical.MIDDLE,
    )

  def _on_bookmark_triggered(self) -> None:
    self._mood_engine.trigger_love(wink=True)
    if self._bookmark_callback is not None:
      self._bookmark_callback()

  def is_swiping_left(self) -> bool:
    """Match AugmentedRoadView API so MiciMainLayout disables horizontal scroller during bookmark swipe."""
    return self._bookmark_icon.is_swiping_left()

  def _update_state(self) -> None:
    super()._update_state()
    if ui_state.panda_type == log.PandaState.PandaType.unknown:
      self._offroad_label.set_text("system booting")
    elif ui_state.ignition and not ui_state.started:
      self._offroad_label.set_text("openpilot can't start\ncheck alerts")
    else:
      self._offroad_label.set_text("start the car to\nuse sunnypilot")

  def _handle_mouse_event(self, mouse_event: MouseEvent) -> None:
    if ui_state.started:
      if mouse_event.left_pressed:
        self._touch_start_x = mouse_event.pos.x
        self._touch_start_y = mouse_event.pos.y
        self._vertical_swipe_handled = False
      elif mouse_event.left_down and not self._vertical_swipe_handled:
        dx = abs(mouse_event.pos.x - self._touch_start_x)
        dy = mouse_event.pos.y - self._touch_start_y
        if abs(dy) > VERTICAL_SWIPE_THRESHOLD and abs(dy) > dx * 1.4:
          self._vertical_swipe_handled = True
          if dy < 0:
            self._mood_engine.trigger_speed_peek()
          else:
            self._mood_engine.trigger_love()

    self._bookmark_icon._handle_mouse_event(mouse_event)
    super()._handle_mouse_event(mouse_event)

  def _handle_mouse_release(self, mouse_pos: MousePos) -> None:
    if self._vertical_swipe_handled:
      self._vertical_swipe_handled = False
      return
    if not self._bookmark_icon.interacting():
      super()._handle_mouse_release(mouse_pos)

  def _render(self, _) -> None:
    rl.draw_rectangle_rec(self.rect, rl.BLACK)

    if not ui_state.started:
      # Keep subtle animated sleepy eyes behind the offroad message so the screen is never static
      sleepy_snap = DrivingSnapshot(started=False, standstill=True)
      eye_target = self._mood_engine.update(sleepy_snap)
      self._face_renderer.render(self.rect, eye_target, alpha=0.28, y_shift=16.0)
      self._offroad_label.render(self._rect)
      return

    alert = self._alert_overlay.get_alert()
    snap = snapshot_from_ui_state(ui_state, alert)
    self._render_from_snapshot(snap, alert)

    self._bookmark_icon.render(self.rect)

  def _render_from_snapshot(self, snap: DrivingSnapshot, alert) -> None:
    eye_target = self._mood_engine.update(snap)
    speed_alpha = self._speed_blend.update(1.0 if self._mood_engine.showing_speed else 0.0)
    face_alpha = 1.0 - speed_alpha

    # Shift eyes slightly upward when a bottom alert banner is visible
    alert_shift = -26.0 if alert is not None else 0.0

    if face_alpha > 0.01:
      self._face_renderer.render(self.rect, eye_target, alpha=face_alpha, y_shift=alert_shift)
      if alert is None:
        self._speed_renderer.render_corner_badge(self.rect, snap, alpha=face_alpha)

    if speed_alpha > 0.01:
      self._speed_renderer.render_speed_mode(
        self.rect,
        snap,
        alpha=speed_alpha,
        cruising_smoothly=self._mood_engine.cruising_smoothly,
        reason=self._mood_engine.speed_reason,
      )

    self._alert_overlay.render(self.rect, alert)

  def show_event(self) -> None:
    if gui_app.sunnypilot_ui():
      ui_state.reset_onroad_sleep_timer(OnroadTimerStatus.RESUME)

  def hide_event(self) -> None:
    if gui_app.sunnypilot_ui():
      ui_state.reset_onroad_sleep_timer(OnroadTimerStatus.PAUSE)


if __name__ == "__main__":
  from openpilot.selfdrive.ui.mici.onroad.alert_renderer import Alert

  gui_app.init_window("MICI Robotic Companion Preview")
  view = RoboticOnroadView()
  view.set_rect(rl.Rectangle(0, 0, gui_app.width, gui_app.height))
  snap = DrivingSnapshot(started=True, engaged=True, status=UIStatus.ENGAGED, v_ego=29.0, set_speed_kph=105.0)

  print("Keys: [1] Engaged  [2] MADS  [3] Disengaged  [4] Speed Peek  [5] Stars  [6] Love  [7] Prompt  [8] Critical  [9] Pout  [Left/Right] Steer")
  for _ in gui_app.render():
    if rl.is_key_pressed(rl.KeyboardKey.KEY_ONE):
      snap = DrivingSnapshot(started=True, engaged=True, status=UIStatus.ENGAGED, v_ego=29.0, set_speed_kph=105.0)
    elif rl.is_key_pressed(rl.KeyboardKey.KEY_TWO):
      snap = DrivingSnapshot(started=True, engaged=True, status=UIStatus.LAT_ONLY, v_ego=20.0, set_speed_kph=90.0)
    elif rl.is_key_pressed(rl.KeyboardKey.KEY_THREE):
      snap = DrivingSnapshot(started=True, engaged=False, status=UIStatus.DISENGAGED, v_ego=15.0)
    elif rl.is_key_pressed(rl.KeyboardKey.KEY_FOUR):
      view._mood_engine.trigger_speed_peek()
    elif rl.is_key_pressed(rl.KeyboardKey.KEY_FIVE):
      view._mood_engine.trigger_startled()
    elif rl.is_key_pressed(rl.KeyboardKey.KEY_SIX):
      view._mood_engine.trigger_love()
    elif rl.is_key_pressed(rl.KeyboardKey.KEY_SEVEN):
      snap.alert = Alert("Pay Attention", "Eyes on road", status=log.SelfdriveState.AlertStatus.userPrompt)
    elif rl.is_key_pressed(rl.KeyboardKey.KEY_EIGHT):
      snap.alert = Alert("TAKE CONTROL IMMEDIATELY", "Steering Required", status=log.SelfdriveState.AlertStatus.critical)
    elif rl.is_key_pressed(rl.KeyboardKey.KEY_NINE):
      snap = DrivingSnapshot(started=True, engaged=True, status=UIStatus.ENGAGED, standstill=True)
    elif rl.is_key_down(rl.KeyboardKey.KEY_LEFT):
      snap.steering_angle_deg = 30.0
    elif rl.is_key_down(rl.KeyboardKey.KEY_RIGHT):
      snap.steering_angle_deg = -30.0
    else:
      snap.steering_angle_deg = 0.0

    rl.draw_rectangle_rec(view.rect, rl.BLACK)
    view._render_from_snapshot(snap, snap.alert)
