"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from dataclasses import dataclass
from enum import Enum
import math
import random
import time

from openpilot.cereal import log
from openpilot.common.constants import CV
from openpilot.selfdrive.ui.mici.onroad.alert_renderer import Alert
from openpilot.selfdrive.ui.sunnypilot.mici.onroad.robotic.music_analyzer import MusicState
from openpilot.selfdrive.ui.sunnypilot.mici.onroad.robotic.music_visualizer import groove_prism_color
from openpilot.selfdrive.ui.ui_state import UIStatus

AlertStatus = log.SelfdriveState.AlertStatus
EventName = log.OnroadEvent.EventName

SET_SPEED_NA = 255
KM_TO_MILE = 0.621371

# Thresholds & hold durations (seconds)
HARD_DECEL_THRESHOLD = -3.0        # m/s^2 triggers startled star eyes
SHARP_ACCEL_THRESHOLD = 2.2        # m/s^2 triggers excited boost eyes
STANDSTILL_POUT_DELAY = 8.0        # seconds at standstill before pouting
STANDSTILL_SLEEPY_DELAY = 35.0     # seconds at standstill before sleepy
CURVE_STEER_THRESHOLD = 15.0       # degrees steering angle for curve tracking
SHARP_TURN_THRESHOLD = 45.0        # degrees steering angle for intense centrifugal lean
SET_SPEED_SHOW_DURATION = 3.0      # seconds to show speed arc on set-speed change
ENGAGE_HAPPY_DURATION = 0.9        # seconds of joyful crescent eyes on engage
ENGAGE_SPEED_CONFIRM = 2.0         # seconds of speed readout right after happy engage
STARTLED_HOLD_DURATION = 1.5       # seconds to hold star-shock expression
BOOST_HOLD_DURATION = 1.2          # seconds to hold sharp-accel boost expression
LOVE_HOLD_DURATION = 1.6           # seconds to hold heart/pet expression
MANUAL_SPEED_PEEK_DURATION = 4.0   # seconds for swipe-up speed peek


class RoboticMood(Enum):
  CRITICAL = "critical"
  DISTRACTED = "distracted"
  USER_PROMPT = "user_prompt"
  STARTLED_STARS = "startled_stars"
  LANE_CHANGE = "lane_change"
  BLIND_SPOT = "blind_spot"
  BOOKMARK_LOVE = "bookmark_love"
  HAPPY_ENGAGE = "happy_engage"
  BOOST_ACCEL = "boost_accel"
  TURN_SIGNAL = "turn_signal"
  SPEED_DISPLAY = "speed_display"
  POUT_STANDSTILL = "pout_standstill"
  SLEEPY = "sleepy"
  SHARP_TURN = "sharp_turn"
  CURVE_FOCUS = "curve_focus"
  MUSIC_GROOVE = "music_groove"
  CRUISING_HAPPY = "cruising_happy"
  IDLE_CURIOUS = "idle_curious"


class IdleAction(Enum):
  """Playful autonomous micro-behaviors during normal cruising & idle driving."""
  NONE = "none"
  HAPPY_SQUINT = "happy_squint"
  CURIOUS_LOOK = "curious_look"
  CHEEKY_WINK = "cheeky_wink"
  GROOVE_BOB = "groove_bob"


class EyeGlyph(Enum):
  ROUND_RECT = "round_rect"
  STAR = "star"
  HEART = "heart"
  CRESCENT = "crescent"
  ARROW_LEFT = "arrow_left"
  ARROW_RIGHT = "arrow_right"
  LASER_ALERT = "laser_alert"
  SPARKLE_BOOST = "sparkle_boost"


class MouthGlyph(Enum):
  NONE = "none"
  SMILE = "smile"
  BIG_GRIN = "big_grin"
  FROWN = "frown"
  SURPRISED = "surprised"


# Dynamic status & mood palette (RGB tuples)
PALETTE = {
  "engaged": (64, 240, 226),        # EMO vibrant cyan-emerald
  "lat_only": (255, 212, 178),      # Reference-video warm peach
  "long_only": (92, 198, 255),      # Sky cyan
  "disengaged": (218, 232, 248),    # Soft ice white
  "override": (255, 196, 68),       # Warm amber
  "boost": (76, 178, 255),          # Electric boost blue
  "prompt": (255, 125, 20),         # Vivid orange
  "critical": (255, 38, 48),        # Alert red
  "love": (255, 112, 168),          # Rose pink
}


@dataclass
class EyeTarget:
  width: float = 104.0
  height: float = 112.0
  roundness: float = 0.62       # Bubbly chunky squircle
  top_lid: float = 0.0          # 0..1 fraction covered from top
  bottom_lid: float = 0.0       # 0..1 fraction covered from bottom
  top_slant: float = 0.0        # degrees (+ = angry/inward, - = sad/outward)
  gaze_x: float = 0.0           # px shift (-42..+42)
  gaze_y: float = 0.0           # px shift (-22..+22)
  bounce_y: float = 0.0         # vertical expressiveness offset
  tilt_y: float = 0.0           # vertical asymmetry between left & right eye (playful head tilt)
  scale_x: float = 1.0          # squash-and-stretch horizontal multiplier
  scale_y: float = 1.0          # squash-and-stretch vertical multiplier
  wink_right: bool = False      # cute asymmetric wink on bookmark or cheeky idle wink
  squish_force: float = 0.0     # -1..+1 centrifugal push (-1 left wall, +1 right wall)
  pitch_offset_y: float = 0.0   # px vertical bob from pitch / pitch-rate (bumps, hills, dive)
  glyph: EyeGlyph = EyeGlyph.ROUND_RECT
  mouth: MouthGlyph = MouthGlyph.NONE
  color: tuple[int, int, int] = PALETTE["engaged"]
  pulse_speed: float = 0.0      # Hz for alert pulsing
  blind_spot_side: int = 0      # -1 left, +1 right, 0 none
  blinker_side: int = 0         # -1 left, +1 right, 0 none
  show_speed_lines: bool = False
  show_zzz: bool = False
  show_hearts: bool = False


@dataclass
class DrivingSnapshot:
  """Pure-data snapshot of driving signals for deterministic mood evaluation & testing."""
  started: bool = True
  engaged: bool = False
  status: UIStatus = UIStatus.DISENGAGED
  v_ego: float = 0.0            # m/s
  a_ego: float = 0.0            # m/s^2
  standstill: bool = False
  steering_angle_deg: float = 0.0
  yaw_rate: float = 0.0         # rad/s (+ = turning left -> centrifugal push right)
  pitch_rad: float = 0.0        # rad (+ = nose up / hill climb)
  pitch_rate: float = 0.0       # rad/s (bumps, crests, braking dive)
  curvature: float = 0.0        # rad/m fallback for centrifugal accel
  set_speed_kph: float = SET_SPEED_NA
  is_metric: bool = False
  left_blinker: bool = False
  right_blinker: bool = False
  left_blindspot: bool = False
  right_blindspot: bool = False
  pre_lane_change_left: bool = False
  pre_lane_change_right: bool = False
  lane_change: bool = False
  lane_change_blocked: bool = False
  dm_alert_level: int = 0       # 0=none, 1=warn, 2=critical
  alert: Alert | None = None
  music: MusicState | None = None


class RoboticMoodEngine:
  """Priority-based EMO-inspired mood & lively autonomous personality state machine."""

  def __init__(self, rng: random.Random | None = None):
    self._rng = rng or random.Random()
    self.mood: RoboticMood = RoboticMood.IDLE_CURIOUS
    self.idle_action: IdleAction = IdleAction.NONE
    self.showing_speed: bool = False
    self.speed_reason: str = ""  # "set_speed", "engage", "peek"
    self.cruising_smoothly: bool = False

    self._prev_engaged: bool = False
    self._prev_set_speed: float = SET_SPEED_NA
    self._standstill_since: float | None = None
    self._last_lane_dir: int = 0  # -1 left, +1 right

    # Hold / effect timers (monotonic timestamps)
    self._startled_until: float = 0.0
    self._boost_until: float = 0.0
    self._love_until: float = 0.0
    self._love_wink: bool = False
    self._happy_engage_until: float = 0.0
    self._speed_display_until: float = 0.0

    # Blink, gaze, and playful idle personality schedulers
    now = time.monotonic()
    self._next_blink_at: float = now + self._rng.uniform(1.8, 3.6)
    self._blink_end_at: float = 0.0
    self._blink_rebound_until: float = 0.0
    self._double_blink_pending: bool = False

    self._next_glance_at: float = now + self._rng.uniform(1.2, 2.6)
    self._idle_gaze_x: float = 0.0
    self._idle_gaze_y: float = 0.0
    self._idle_tilt_y: float = 0.0

    self._next_idle_action_at: float = now + self._rng.uniform(2.2, 3.8)
    self._idle_action_until: float = 0.0
    self._idle_action_dir: float = 1.0

  def trigger_love(self, now: float | None = None, wink: bool = False) -> None:
    t = time.monotonic() if now is None else now
    self._love_until = t + LOVE_HOLD_DURATION
    self._love_wink = wink

  def trigger_speed_peek(self, now: float | None = None) -> None:
    t = time.monotonic() if now is None else now
    self._speed_display_until = max(self._speed_display_until, t + MANUAL_SPEED_PEEK_DURATION)
    self.speed_reason = "peek"

  def trigger_startled(self, now: float | None = None) -> None:
    t = time.monotonic() if now is None else now
    self._startled_until = max(self._startled_until, t + STARTLED_HOLD_DURATION)

  def trigger_boost(self, now: float | None = None) -> None:
    t = time.monotonic() if now is None else now
    self._boost_until = max(self._boost_until, t + BOOST_HOLD_DURATION)

  def _status_color(self, snap: DrivingSnapshot) -> tuple[int, int, int]:
    if snap.status == UIStatus.ENGAGED:
      return PALETTE["engaged"]
    if snap.status == UIStatus.LAT_ONLY:
      return PALETTE["lat_only"]
    if snap.status == UIStatus.LONG_ONLY:
      return PALETTE["long_only"]
    if snap.status == UIStatus.OVERRIDE:
      return PALETTE["override"]
    return PALETTE["disengaged"]

  def _update_blink_and_personality(self, now: float, sleepy: bool) -> tuple[float, float, float]:
    """Returns (blink_closure, squash_x, stretch_y) and advances idle glances & micro-actions."""
    blink_closure = 0.0
    squash_x = 1.0
    stretch_y = 1.0

    if now < self._blink_end_at:
      blink_closure = 1.0
      squash_x = 1.16
      stretch_y = 0.86
    elif now < self._blink_rebound_until:
      # Juicy bubbly pop-open after blink
      squash_x = 0.93
      stretch_y = 1.10
    elif now >= self._next_blink_at:
      blink_dur = 0.22 if sleepy else 0.11
      self._blink_end_at = now + blink_dur
      self._blink_rebound_until = self._blink_end_at + 0.12
      blink_closure = 1.0
      squash_x = 1.16
      stretch_y = 0.86
      if not sleepy and not self._double_blink_pending and self._rng.random() < 0.30:
        self._double_blink_pending = True
        self._next_blink_at = self._blink_end_at + 0.13
      else:
        self._double_blink_pending = False
        lo, hi = (1.6, 3.0) if sleepy else (2.2, 4.4)
        self._next_blink_at = self._blink_end_at + self._rng.uniform(lo, hi)

    if now >= self._next_glance_at:
      roll = self._rng.random()
      if roll < 0.28:
        self._idle_gaze_x = 0.0
        self._idle_gaze_y = 0.0
        self._idle_tilt_y = 0.0
      else:
        self._idle_gaze_x = self._rng.uniform(-34.0, 34.0)
        self._idle_gaze_y = self._rng.uniform(-12.0, 10.0)
        self._idle_tilt_y = self._rng.uniform(-9.0, 9.0)
      self._next_glance_at = now + self._rng.uniform(1.3, 2.8)

    # Playful autonomous micro-behaviors during normal cruising/idle
    if now >= self._idle_action_until:
      self.idle_action = IdleAction.NONE
      if not sleepy and now >= self._next_idle_action_at:
        choice = self._rng.choice([
          IdleAction.HAPPY_SQUINT,
          IdleAction.CURIOUS_LOOK,
          IdleAction.CHEEKY_WINK,
          IdleAction.GROOVE_BOB,
        ])
        self.idle_action = choice
        self._idle_action_dir = -1.0 if self._rng.random() < 0.5 else 1.0
        dur = {
          IdleAction.HAPPY_SQUINT: 0.80,
          IdleAction.CURIOUS_LOOK: 1.50,
          IdleAction.CHEEKY_WINK: 0.55,
          IdleAction.GROOVE_BOB: 1.80,
        }[choice]
        self._idle_action_until = now + dur
        self._next_idle_action_at = self._idle_action_until + self._rng.uniform(2.0, 3.8)

    return blink_closure, squash_x, stretch_y

  def update(self, snap: DrivingSnapshot, now: float | None = None) -> EyeTarget:
    t = time.monotonic() if now is None else now

    # Track standstill duration
    if snap.standstill or not snap.started:
      if self._standstill_since is None:
        self._standstill_since = t
    else:
      self._standstill_since = None
    standstill_dur = (t - self._standstill_since) if self._standstill_since is not None else 0.0

    # Track engagement rising edge
    if snap.engaged and not self._prev_engaged:
      self._happy_engage_until = t + ENGAGE_HAPPY_DURATION
      self._speed_display_until = max(
        self._speed_display_until,
        t + ENGAGE_HAPPY_DURATION + ENGAGE_SPEED_CONFIRM,
      )
      self.speed_reason = "engage"
    self._prev_engaged = snap.engaged

    # Track set-speed change while cruise is set
    cruise_set = 0 < snap.set_speed_kph < SET_SPEED_NA
    if cruise_set and snap.set_speed_kph != self._prev_set_speed and self._prev_set_speed != SET_SPEED_NA:
      self._speed_display_until = max(self._speed_display_until, t + SET_SPEED_SHOW_DURATION)
      self.speed_reason = "set_speed"
    self._prev_set_speed = snap.set_speed_kph

    # Track startling events & sharp acceleration
    if snap.a_ego < HARD_DECEL_THRESHOLD or snap.lane_change_blocked:
      self._startled_until = max(self._startled_until, t + STARTLED_HOLD_DURATION)
    elif snap.a_ego > SHARP_ACCEL_THRESHOLD and not snap.standstill:
      self._boost_until = max(self._boost_until, t + BOOST_HOLD_DURATION)

    # Track lane change direction
    if snap.pre_lane_change_left:
      self._last_lane_dir = -1
    elif snap.pre_lane_change_right:
      self._last_lane_dir = 1
    elif not snap.lane_change:
      self._last_lane_dir = 0

    blinker_side = -1 if snap.left_blinker else (1 if snap.right_blinker else 0)

    bsm_side = 0
    if snap.left_blindspot and (snap.left_blinker or snap.pre_lane_change_left):
      bsm_side = -1
    elif snap.right_blindspot and (snap.right_blinker or snap.pre_lane_change_right):
      bsm_side = 1
    elif snap.left_blindspot and not snap.standstill:
      bsm_side = -1
    elif snap.right_blindspot and not snap.standstill:
      bsm_side = 1

    self.cruising_smoothly = snap.engaged and not snap.standstill and abs(snap.a_ego) < 0.8

    # Evaluate mood priority
    alert = snap.alert
    alert_status = alert.status if alert is not None else -1
    alert_type = alert.alert_type if alert is not None else ""
    is_dm_alert = snap.dm_alert_level >= 1 or "Distracted" in alert_type or "Unresponsive" in alert_type

    self.showing_speed = False

    # Compute physical centrifugal force (-1 = pushed left, +1 = pushed right) & pitch bob
    # Positive yaw_rate (turning left) pushes the bot toward the right wall (+1)
    effective_yaw = snap.yaw_rate
    if abs(effective_yaw) < 1e-4 and abs(snap.curvature) > 1e-5:
      effective_yaw = snap.v_ego * snap.curvature
    lat_accel = snap.v_ego * effective_yaw  # m/s^2
    # Blend true lateral G with direct gyro yaw-rate so even tight low-speed turns feel lively
    centrifugal_raw = (lat_accel / 4.2) + (effective_yaw / 1.4) * 0.35
    if abs(centrifugal_raw) < 0.05 and abs(snap.steering_angle_deg) > CURVE_STEER_THRESHOLD and not snap.standstill:
      # Fallback for desktop previews/simulators without IMU data
      centrifugal_raw = max(-1.0, min(1.0, (snap.steering_angle_deg / 90.0) * max(0.35, snap.v_ego / 20.0)))
    squish_force = max(-1.0, min(1.0, centrifugal_raw)) if not snap.standstill else 0.0
    if abs(squish_force) < 0.08:
      squish_force = 0.0
    pitch_offset_y = max(-22.0, min(22.0, snap.pitch_rad * 55.0 + snap.pitch_rate * 20.0))

    if alert is not None and alert_status == AlertStatus.critical:
      self.mood = RoboticMood.CRITICAL
    elif is_dm_alert:
      self.mood = RoboticMood.DISTRACTED
    elif alert is not None and alert_status == AlertStatus.userPrompt:
      self.mood = RoboticMood.USER_PROMPT
    elif t < self._startled_until:
      self.mood = RoboticMood.STARTLED_STARS
    elif snap.pre_lane_change_left or snap.pre_lane_change_right or snap.lane_change:
      self.mood = RoboticMood.LANE_CHANGE
    elif bsm_side != 0 and blinker_side != 0:
      self.mood = RoboticMood.BLIND_SPOT
    elif t < self._love_until:
      self.mood = RoboticMood.BOOKMARK_LOVE
    elif t < self._happy_engage_until:
      self.mood = RoboticMood.HAPPY_ENGAGE
    elif t < self._speed_display_until and snap.started:
      self.mood = RoboticMood.SPEED_DISPLAY
      self.showing_speed = True
    elif t < self._boost_until:
      self.mood = RoboticMood.BOOST_ACCEL
    elif blinker_side != 0:
      self.mood = RoboticMood.TURN_SIGNAL
    elif (abs(squish_force) >= 0.42 or abs(snap.steering_angle_deg) >= SHARP_TURN_THRESHOLD) and not snap.standstill:
      self.mood = RoboticMood.SHARP_TURN
    elif (abs(squish_force) >= 0.18 or abs(snap.steering_angle_deg) > CURVE_STEER_THRESHOLD) and not snap.standstill:
      self.mood = RoboticMood.CURVE_FOCUS
    elif snap.started and snap.music is not None and snap.music.is_music and alert is None:
      self.mood = RoboticMood.MUSIC_GROOVE
    elif not snap.started or standstill_dur >= STANDSTILL_SLEEPY_DELAY:
      self.mood = RoboticMood.SLEEPY
    elif standstill_dur >= STANDSTILL_POUT_DELAY:
      self.mood = RoboticMood.POUT_STANDSTILL
    elif snap.engaged:
      self.mood = RoboticMood.CRUISING_HAPPY
    else:
      self.mood = RoboticMood.IDLE_CURIOUS

    base_color = self._status_color(snap)
    blink, squash_x, stretch_y = self._update_blink_and_personality(t, sleepy=(self.mood == RoboticMood.SLEEPY))

    # Lively, clearly visible breathing & energetic bounce so the face is always bubbling with life
    energy = 1.0 + min(0.55, snap.v_ego / 35.0)
    breathe_y = math.sin(t * 2.8 * energy) * 6.5 + math.sin(t * 1.3) * 2.5
    breathe_scale = 1.0 + 0.035 * math.sin(t * 2.8 * energy - 0.35)
    micro_drift_x = math.sin(t * 1.1) * 6.0

    # Steering-coupled gaze (clamped to [-40, +40])
    steer_gaze = max(-40.0, min(40.0, -snap.steering_angle_deg * 0.78))

    target = EyeTarget(
      color=base_color,
      bounce_y=breathe_y,
      scale_x=squash_x * breathe_scale,
      scale_y=stretch_y * (2.0 - breathe_scale),
      squish_force=squish_force,
      pitch_offset_y=pitch_offset_y,
      blind_spot_side=bsm_side,
      blinker_side=blinker_side,
    )

    if self.mood == RoboticMood.CRITICAL:
      target.glyph = EyeGlyph.LASER_ALERT
      target.color = PALETTE["critical"]
      target.width = 114.0
      target.height = 84.0
      target.roundness = 0.42
      target.top_lid = 0.28
      target.top_slant = 18.0
      target.pulse_speed = 5.5
      target.bounce_y = math.sin(t * 28.0) * 3.5

    elif self.mood == RoboticMood.DISTRACTED:
      target.color = PALETTE["prompt"]
      target.width = 108.0
      target.height = 96.0
      target.roundness = 0.48
      target.top_lid = 0.32
      target.top_slant = 12.0
      target.gaze_x = math.sin(t * 5.2) * 18.0
      target.mouth = MouthGlyph.FROWN
      target.pulse_speed = 2.5

    elif self.mood == RoboticMood.USER_PROMPT:
      target.color = PALETTE["prompt"]
      target.width = 108.0
      target.height = 120.0
      target.top_lid = 0.06
      target.top_slant = -6.0
      target.gaze_x = micro_drift_x
      target.pulse_speed = 1.8

    elif self.mood == RoboticMood.STARTLED_STARS:
      target.glyph = EyeGlyph.STAR
      target.color = PALETTE["override"]
      target.width = 114.0
      target.height = 114.0
      target.mouth = MouthGlyph.SURPRISED
      target.bounce_y = math.sin(t * 26.0) * 6.0
      target.scale_x = 1.0 + 0.08 * math.sin(t * 22.0)
      target.scale_y = 1.0 - 0.08 * math.sin(t * 22.0)

    elif self.mood == RoboticMood.LANE_CHANGE:
      direction = -1 if snap.pre_lane_change_left else (1 if snap.pre_lane_change_right else self._last_lane_dir or 1)
      target.glyph = EyeGlyph.ARROW_LEFT if direction < 0 else EyeGlyph.ARROW_RIGHT
      target.gaze_x = direction * 32.0 + math.sin(t * 6.5) * 5.0
      target.height = 106.0
      target.top_lid = 0.10
      target.tilt_y = direction * 7.0
      target.mouth = MouthGlyph.SMILE

    elif self.mood == RoboticMood.BLIND_SPOT:
      target.color = PALETTE["override"]
      target.gaze_x = bsm_side * 38.0
      target.height = 102.0
      target.top_lid = 0.22
      target.top_slant = 9.0
      target.pulse_speed = 3.2

    elif self.mood == RoboticMood.BOOKMARK_LOVE:
      target.glyph = EyeGlyph.HEART
      target.color = PALETTE["love"]
      target.width = 114.0
      target.height = 114.0
      target.wink_right = self._love_wink
      target.mouth = MouthGlyph.BIG_GRIN
      target.bounce_y = -abs(math.sin(t * 10.5)) * 15.0
      target.show_hearts = True

    elif self.mood == RoboticMood.HAPPY_ENGAGE:
      target.glyph = EyeGlyph.CRESCENT
      target.color = PALETTE["engaged"]
      target.width = 116.0
      target.height = 100.0
      target.mouth = MouthGlyph.BIG_GRIN
      target.bounce_y = -abs(math.sin(t * 9.5)) * 16.0

    elif self.mood == RoboticMood.BOOST_ACCEL:
      target.glyph = EyeGlyph.SPARKLE_BOOST
      target.color = PALETTE["boost"]
      target.width = 116.0
      target.height = 120.0
      target.gaze_y = -7.0
      target.mouth = MouthGlyph.BIG_GRIN
      target.bounce_y = math.sin(t * 18.0) * 5.0
      target.show_speed_lines = True

    elif self.mood == RoboticMood.TURN_SIGNAL:
      beat = 0.5 + 0.5 * math.sin(t * 8.4)
      target.gaze_x = blinker_side * (22.0 + 14.0 * beat)
      target.tilt_y = blinker_side * 8.0
      target.width = 106.0
      target.height = 108.0
      target.top_lid = 0.08
      target.mouth = MouthGlyph.SMILE

    elif self.mood == RoboticMood.POUT_STANDSTILL:
      target.width = 98.0
      target.height = 84.0
      target.roundness = 0.34
      target.top_lid = 0.26 + 0.05 * math.sin(t * 1.8)
      target.gaze_x = self._idle_gaze_x * 0.75 + micro_drift_x
      target.gaze_y = 6.0
      target.tilt_y = self._idle_tilt_y * 0.7
      target.mouth = MouthGlyph.FROWN

    elif self.mood == RoboticMood.SLEEPY:
      target.width = 104.0
      target.height = 76.0
      target.roundness = 0.45
      target.top_lid = 0.58 + 0.09 * math.sin(t * 1.5)
      target.bottom_lid = 0.14
      target.gaze_y = 8.0
      target.gaze_x = math.sin(t * 0.7) * 8.0
      target.bounce_y = math.sin(t * 1.5) * 6.0
      target.show_zzz = True

    elif self.mood == RoboticMood.SHARP_TURN:
      intensity = max(abs(squish_force), min(1.0, abs(snap.steering_angle_deg) / 85.0))
      push_dir = 1.0 if squish_force > 0 else (-1.0 if squish_force < 0 else (1.0 if snap.steering_angle_deg > 0 else -1.0))
      target.squish_force = push_dir * intensity
      target.width = 108.0
      target.height = 104.0
      target.top_lid = 0.10 + 0.14 * intensity
      target.top_slant = 5.0 + 7.0 * intensity
      target.gaze_x = push_dir * 12.0  # squish renderer handles primary wall slide
      target.gaze_y = -3.0
      target.tilt_y = push_dir * (8.0 + 8.0 * intensity)
      target.mouth = MouthGlyph.SURPRISED if intensity >= 0.62 else MouthGlyph.SMILE

    elif self.mood == RoboticMood.CURVE_FOCUS:
      intensity = max(abs(squish_force), min(0.5, abs(snap.steering_angle_deg) / 70.0))
      push_dir = 1.0 if squish_force > 0 else (-1.0 if squish_force < 0 else (1.0 if snap.steering_angle_deg > 0 else -1.0))
      target.squish_force = push_dir * intensity
      target.width = 106.0
      target.height = 106.0
      target.top_lid = 0.08
      target.gaze_x = push_dir * 8.0
      target.gaze_y = -2.0
      target.tilt_y = push_dir * (5.0 + 6.0 * intensity)
      target.mouth = MouthGlyph.SMILE

    elif self.mood == RoboticMood.MUSIC_GROOVE:
      m = snap.music or MusicState()
      sway = math.sin(m.groove_phase)
      beat = m.beat_pulse
      target.color = groove_prism_color(t)
      target.width = 108.0
      target.height = 112.0
      target.gaze_x = sway * 22.0
      target.gaze_y = -6.0 - beat * 6.0
      target.tilt_y = sway * 12.0
      target.bounce_y = -14.0 * beat - abs(sway) * 6.0 - 8.0
      target.scale_x = 1.0 + 0.11 * beat
      target.scale_y = 1.0 - 0.08 * beat
      target.mouth = MouthGlyph.BIG_GRIN
      if beat > 0.58:
        target.glyph = EyeGlyph.CRESCENT

    elif self.mood == RoboticMood.CRUISING_HAPPY:
      target.width = 106.0
      target.height = 114.0
      target.mouth = MouthGlyph.SMILE
      target.gaze_x = steer_gaze * 0.35 + self._idle_gaze_x * 0.65 + micro_drift_x
      target.gaze_y = self._idle_gaze_y * 0.65
      target.tilt_y = self._idle_tilt_y * 0.75 + math.sin(t * 1.6) * 3.0
      self._apply_idle_action(target, t)

    else:  # IDLE_CURIOUS or SPEED_DISPLAY fallback
      target.width = 104.0
      target.height = 110.0
      target.mouth = MouthGlyph.SMILE
      target.gaze_x = self._idle_gaze_x + micro_drift_x
      target.gaze_y = self._idle_gaze_y
      target.tilt_y = self._idle_tilt_y + math.sin(t * 1.4) * 3.0
      self._apply_idle_action(target, t)

    # Apply natural blink closure to standard rounded-rect eyes
    if target.glyph == EyeGlyph.ROUND_RECT and not target.wink_right and blink > 0.0:
      target.top_lid = max(target.top_lid, 0.52 * blink)
      target.bottom_lid = max(target.bottom_lid, 0.48 * blink)

    return target

  def _apply_idle_action(self, target: EyeTarget, t: float) -> None:
    """Layer bubbly autonomous micro-behaviors onto normal cruising/idle states."""
    if self.idle_action == IdleAction.HAPPY_SQUINT:
      target.glyph = EyeGlyph.CRESCENT
      target.mouth = MouthGlyph.BIG_GRIN
      target.bounce_y = -abs(math.sin(t * 9.0)) * 12.0
    elif self.idle_action == IdleAction.CURIOUS_LOOK:
      target.gaze_x = self._idle_action_dir * 34.0
      target.gaze_y = -6.0
      target.tilt_y = self._idle_action_dir * 10.0
      target.height = 118.0
    elif self.idle_action == IdleAction.CHEEKY_WINK:
      target.wink_right = True
      target.mouth = MouthGlyph.BIG_GRIN
      target.tilt_y = 6.0
      target.bounce_y = -8.0
    elif self.idle_action == IdleAction.GROOVE_BOB:
      target.bounce_y = math.sin(t * 7.2) * 11.0
      target.tilt_y = math.sin(t * 3.6) * 8.0
      target.mouth = MouthGlyph.BIG_GRIN


def snapshot_from_ui_state(ui_state, alert: Alert | None) -> DrivingSnapshot:
  """Build a DrivingSnapshot safely from ui_state.sm."""
  sm = ui_state.sm
  cs = sm["carState"]
  controls = sm["controlsState"]
  dm = sm["driverMonitoringState"]
  events = sm["onroadEvents"]

  v_cruise_cluster = cs.vCruiseCluster
  set_speed_kph = controls.deprecated.vCruise if v_cruise_cluster == 0.0 else v_cruise_cluster

  pre_left = any(e.name == EventName.preLaneChangeLeft for e in events)
  pre_right = any(e.name == EventName.preLaneChangeRight for e in events)
  lane_change = any(e.name == EventName.laneChange for e in events)
  lane_blocked = any(e.name == EventName.laneChangeBlocked for e in events)

  v_ego_cluster = cs.vEgoCluster
  v_ego = v_ego_cluster if v_ego_cluster != 0.0 else cs.vEgo

  # Extract pitch, pitch rate, and yaw rate from modelV2 orientation + gyroscope (104 Hz)
  yaw_rate = 0.0
  pitch_rad = 0.0
  pitch_rate = 0.0
  if sm.valid.get("modelV2"):
    mv2 = sm["modelV2"]
    if len(mv2.orientation.y) > 0:
      pitch_rad = float(mv2.orientation.y[0])
    if len(mv2.orientationRate.y) > 0 and len(mv2.orientationRate.z) > 0:
      pitch_rate = float(mv2.orientationRate.y[0])
      yaw_rate = float(mv2.orientationRate.z[0])
  if sm.valid.get("gyroscope"):
    gv = sm["gyroscope"].gyro.v
    if len(gv) >= 3:
      # Blend crisp high-rate gyro directly with model orientation rate
      pitch_rate = 0.5 * pitch_rate + 0.5 * float(gv[1]) if pitch_rate != 0.0 else float(gv[1])
      yaw_rate = 0.5 * yaw_rate + 0.5 * float(gv[2]) if yaw_rate != 0.0 else float(gv[2])

  return DrivingSnapshot(
    started=ui_state.started,
    engaged=ui_state.engaged,
    status=ui_state.status,
    v_ego=max(0.0, float(v_ego)),
    a_ego=float(cs.aEgo),
    standstill=bool(cs.standstill),
    steering_angle_deg=float(cs.steeringAngleDeg),
    yaw_rate=yaw_rate,
    pitch_rad=pitch_rad,
    pitch_rate=pitch_rate,
    curvature=float(controls.curvature) if sm.valid.get("controlsState") else 0.0,
    set_speed_kph=float(set_speed_kph),
    is_metric=bool(ui_state.is_metric),
    left_blinker=bool(cs.leftBlinker),
    right_blinker=bool(cs.rightBlinker),
    left_blindspot=bool(cs.leftBlindspot),
    right_blindspot=bool(cs.rightBlindspot),
    pre_lane_change_left=pre_left,
    pre_lane_change_right=pre_right,
    lane_change=lane_change,
    lane_change_blocked=lane_blocked,
    dm_alert_level=int(dm.alertLevel.raw) if sm.valid["driverMonitoringState"] else 0,
    alert=alert,
  )


def display_speed_and_set_speed(snap: DrivingSnapshot) -> tuple[int, int | None]:
  """Convert current speed and cruise set speed to display units (mph or km/h)."""
  speed_conv = CV.MS_TO_KPH if snap.is_metric else CV.MS_TO_MPH
  cur_speed = round(max(0.0, snap.v_ego * speed_conv))
  if 0 < snap.set_speed_kph < SET_SPEED_NA:
    set_val = snap.set_speed_kph if snap.is_metric else snap.set_speed_kph * KM_TO_MILE
    return cur_speed, round(set_val)
  return cur_speed, None
