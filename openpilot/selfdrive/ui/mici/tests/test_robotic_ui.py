"""Tests for MICI Robotic Companion onroad UI mood engine and telemetry helpers."""
import random

from openpilot.cereal import log
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.ui.mici.onroad.alert_renderer import Alert
from openpilot.selfdrive.ui.sunnypilot.mici.onroad.robotic.expressions import (
  DrivingSnapshot,
  EyeGlyph,
  MouthGlyph,
  PALETTE,
  RoboticMood,
  RoboticMoodEngine,
  STANDSTILL_POUT_DELAY,
  STANDSTILL_SLEEPY_DELAY,
  display_speed_and_set_speed,
)
from openpilot.selfdrive.ui.ui_state import UIStatus

AlertStatus = log.SelfdriveState.AlertStatus


class TestRoboticMoodEngine(OpenpilotTestCase):
  def _engine(self) -> RoboticMoodEngine:
    return RoboticMoodEngine(rng=random.Random(42))

  def test_engaged_happy_then_speed_then_cruising(self):
    engine = self._engine()
    # Initially disengaged
    snap = DrivingSnapshot(started=True, engaged=False, status=UIStatus.DISENGAGED, v_ego=20.0)
    target = engine.update(snap, now=10.0)
    assert engine.mood == RoboticMood.IDLE_CURIOUS
    assert target.color == PALETTE["disengaged"]

    # Engage triggers HAPPY_ENGAGE crescent eyes
    snap_eng = DrivingSnapshot(started=True, engaged=True, status=UIStatus.ENGAGED, v_ego=25.0, set_speed_kph=100.0)
    target = engine.update(snap_eng, now=11.0)
    assert engine.mood == RoboticMood.HAPPY_ENGAGE
    assert target.glyph == EyeGlyph.CRESCENT
    assert target.color == PALETTE["engaged"]

    # After happy hold, briefly shows speed confirmation
    engine.update(snap_eng, now=12.2)
    assert engine.mood == RoboticMood.SPEED_DISPLAY
    assert engine.showing_speed is True

    # After speed confirm expires, settles into CRUISING_HAPPY
    target = engine.update(snap_eng, now=15.0)
    assert engine.mood == RoboticMood.CRUISING_HAPPY
    assert engine.showing_speed is False
    assert target.color == PALETTE["engaged"]

  def test_critical_alert_overrides_all_moods(self):
    engine = self._engine()
    engine.trigger_love(now=10.0)
    engine.trigger_speed_peek(now=10.0)
    alert = Alert("TAKE CONTROL IMMEDIATELY", "Steering Required", status=AlertStatus.critical)
    snap = DrivingSnapshot(started=True, engaged=True, status=UIStatus.ENGAGED, alert=alert)

    target = engine.update(snap, now=10.1)
    assert engine.mood == RoboticMood.CRITICAL
    assert target.glyph == EyeGlyph.LASER_ALERT
    assert target.color == PALETTE["critical"]
    assert engine.showing_speed is False

  def test_distracted_driver_monitoring(self):
    engine = self._engine()
    snap = DrivingSnapshot(started=True, engaged=True, status=UIStatus.ENGAGED, dm_alert_level=1)
    target = engine.update(snap, now=20.0)
    assert engine.mood == RoboticMood.DISTRACTED
    assert target.color == PALETTE["prompt"]
    assert target.mouth == MouthGlyph.FROWN

  def test_hard_decel_triggers_star_eyes(self):
    engine = self._engine()
    snap = DrivingSnapshot(started=True, engaged=True, status=UIStatus.ENGAGED, a_ego=-3.8)
    target = engine.update(snap, now=30.0)
    assert engine.mood == RoboticMood.STARTLED_STARS
    assert target.glyph == EyeGlyph.STAR
    assert target.mouth == MouthGlyph.SURPRISED

  def test_lane_change_and_blind_spot(self):
    engine = self._engine()
    snap_lc = DrivingSnapshot(started=True, engaged=True, status=UIStatus.ENGAGED, pre_lane_change_left=True)
    target = engine.update(snap_lc, now=40.0)
    assert engine.mood == RoboticMood.LANE_CHANGE
    assert target.glyph == EyeGlyph.ARROW_LEFT
    assert target.gaze_x < 0

    snap_bsm = DrivingSnapshot(started=True, engaged=True, status=UIStatus.ENGAGED, right_blinker=True, right_blindspot=True)
    target = engine.update(snap_bsm, now=41.0)
    assert engine.mood == RoboticMood.BLIND_SPOT
    assert target.gaze_x > 0
    assert target.blind_spot_side == 1

  def test_standstill_pout_and_sleepy_progression(self):
    engine = self._engine()
    snap = DrivingSnapshot(started=True, engaged=True, status=UIStatus.ENGAGED, standstill=True)
    engine.update(snap, now=100.0)
    # Past happy engage & speed confirm, still before pout
    engine.update(snap, now=105.0)
    assert engine.mood == RoboticMood.CRUISING_HAPPY

    # Past pout threshold
    target = engine.update(snap, now=100.0 + STANDSTILL_POUT_DELAY + 1.0)
    assert engine.mood == RoboticMood.POUT_STANDSTILL
    assert target.mouth == MouthGlyph.FROWN

    # Past sleepy threshold
    target = engine.update(snap, now=100.0 + STANDSTILL_SLEEPY_DELAY + 1.0)
    assert engine.mood == RoboticMood.SLEEPY
    assert target.top_lid >= 0.5

  def test_set_speed_change_triggers_speed_display(self):
    engine = self._engine()
    snap1 = DrivingSnapshot(started=True, engaged=True, status=UIStatus.ENGAGED, v_ego=25.0, set_speed_kph=100.0)
    engine.update(snap1, now=10.0)
    engine.update(snap1, now=15.0)
    assert engine.showing_speed is False

    snap2 = DrivingSnapshot(started=True, engaged=True, status=UIStatus.ENGAGED, v_ego=25.0, set_speed_kph=110.0)
    engine.update(snap2, now=16.0)
    assert engine.mood == RoboticMood.SPEED_DISPLAY
    assert engine.showing_speed is True
    assert engine.speed_reason == "set_speed"

  def test_mads_lat_only_warm_peach_palette(self):
    engine = self._engine()
    snap = DrivingSnapshot(started=True, engaged=True, status=UIStatus.LAT_ONLY, v_ego=18.0)
    engine.update(snap, now=10.0)
    target = engine.update(snap, now=15.0)
    assert target.color == PALETTE["lat_only"]

  def test_display_speed_conversion(self):
    snap_mph = DrivingSnapshot(v_ego=26.8224, set_speed_kph=100.0, is_metric=False)
    cur, set_s = display_speed_and_set_speed(snap_mph)
    assert cur == 60
    assert set_s == 62

    snap_kph = DrivingSnapshot(v_ego=27.7778, set_speed_kph=100.0, is_metric=True)
    cur, set_s = display_speed_and_set_speed(snap_kph)
    assert cur == 100
    assert set_s == 100

  def test_sharp_accel_turn_signal_sharp_turn_and_continuous_motion(self):
    engine = self._engine()
    # Sharp acceleration triggers BOOST_ACCEL with speed lines
    snap_boost = DrivingSnapshot(started=True, engaged=True, status=UIStatus.ENGAGED, v_ego=22.0, a_ego=2.8)
    engine.update(snap_boost, now=10.0)
    target = engine.update(snap_boost, now=14.0)
    # Trigger fresh boost after engage hold expires
    snap_boost2 = DrivingSnapshot(started=True, engaged=True, status=UIStatus.ENGAGED, v_ego=24.0, a_ego=2.9)
    target = engine.update(snap_boost2, now=15.0)
    assert engine.mood == RoboticMood.BOOST_ACCEL
    assert target.glyph == EyeGlyph.SPARKLE_BOOST
    assert target.show_speed_lines is True

    # Turn indicator triggers TURN_SIGNAL with blinker side
    snap_turn = DrivingSnapshot(started=True, engaged=False, status=UIStatus.DISENGAGED, v_ego=15.0, left_blinker=True)
    target = engine.update(snap_turn, now=20.0)
    assert engine.mood == RoboticMood.TURN_SIGNAL
    assert target.blinker_side == -1

    # Sharp turn triggers SHARP_TURN with centrifugal tilt
    snap_sharp = DrivingSnapshot(started=True, engaged=False, status=UIStatus.DISENGAGED, v_ego=12.0, steering_angle_deg=55.0)
    target = engine.update(snap_sharp, now=25.0)
    assert engine.mood == RoboticMood.SHARP_TURN
    assert abs(target.tilt_y) >= 10.0

    # Bookmark wink triggers love with wink_right=True
    engine.trigger_love(now=30.0, wink=True)
    target = engine.update(DrivingSnapshot(started=True, engaged=False), now=30.2)
    assert engine.mood == RoboticMood.BOOKMARK_LOVE
    assert target.wink_right is True
    assert target.show_hearts is True

    # Continuous motion check: idle bounce_y & gaze_x are never frozen across frames
    snap_idle = DrivingSnapshot(started=True, engaged=False, status=UIStatus.DISENGAGED, v_ego=0.0)
    t1 = engine.update(snap_idle, now=40.0)
    t2 = engine.update(snap_idle, now=40.5)
    assert (t1.bounce_y != t2.bounce_y) or (t1.gaze_x != t2.gaze_x)
