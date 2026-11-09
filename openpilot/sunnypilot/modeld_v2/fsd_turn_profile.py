"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

# FSD-timed turns: the model's plan says where the corner is and how much it turns; FSD's own turns say when to start
# turning and how hard. From qlogs of routes 85-b1 (curvature from the wheel angle), FSD's 21 turns of 60-120 deg:
#   peak curvature = 0.190 - 0.018 v (held out, within 0.010 1/m; the driver's own turns sit at 1.05x of it)
#   and its curvature over time around the half-heading point follows TEMPLATE (median of 23 FSD turns >= 45 deg,
#   normalized to its peak): rising from ~3 s before, peaking just after, gone ~3 s after.
# openpilot's turns (mostly Light Speed 2) turned in 1.7 m earlier than that and peaked 0.93x.
# A turn's profile here is the rule's peak at the car's speed, the template stretched in time so the turn adds up to
# the heading the plan (plus what is already turned) says it needs, placed at the plan's half-heading point.
TAU = np.arange(-5.0, 5.01, 0.1)  # s from the half-heading point
# Per direction (curvature and yaw + right): FSD's rights rise later and end sooner than its lefts (25% of peak from
# 2.0 s before to 2.2 s after the middle, vs 2.3 s and 2.5 s) and peak 4% higher. One shared template turned the rights
# in early on route b2 (the driver held back at the peak) while the lefts were fine.
_RIGHT_FACTOR = 1.037
_TEMPLATE_RIGHT = np.array([
  0.000, 0.000, 0.000, 0.000, 0.003, 0.006, 0.003, 0.000, 0.002, 0.008, 0.014, 0.019, 0.022, 0.027, 0.033, 0.041, 0.050,
  0.061, 0.072, 0.085, 0.099, 0.114, 0.130, 0.146, 0.162, 0.176, 0.189, 0.203, 0.217, 0.231, 0.261, 0.300, 0.340, 0.383,
  0.427, 0.473, 0.551, 0.644, 0.704, 0.753, 0.808, 0.848, 0.874, 0.896, 0.920, 0.940, 0.959, 0.971, 0.987, 0.992, 0.997,
  0.999, 1.000, 0.993, 0.983, 0.965, 0.938, 0.905, 0.866, 0.820, 0.771, 0.717, 0.658, 0.598, 0.554, 0.515, 0.479, 0.445,
  0.410, 0.374, 0.339, 0.306, 0.275, 0.238, 0.192, 0.158, 0.138, 0.120, 0.103, 0.089, 0.076, 0.065, 0.055, 0.047, 0.038,
  0.032, 0.027, 0.022, 0.018, 0.013, 0.012, 0.011, 0.010, 0.010, 0.009, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000,
])
_LEFT_FACTOR = 1.003
_TEMPLATE_LEFT = np.array([
  0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.002, 0.002, 0.003, 0.007, 0.006, 0.004, 0.005, 0.009, 0.021, 0.022,
  0.025, 0.029, 0.036, 0.050, 0.067, 0.086, 0.108, 0.135, 0.171, 0.217, 0.269, 0.326, 0.386, 0.448, 0.508, 0.565, 0.621,
  0.673, 0.726, 0.796, 0.853, 0.882, 0.914, 0.942, 0.968, 0.989, 0.997, 1.000, 0.988, 0.984, 0.984, 0.987, 0.994, 0.994,
  0.994, 0.993, 0.991, 0.979, 0.959, 0.932, 0.902, 0.868, 0.832, 0.794, 0.755, 0.716, 0.673, 0.635, 0.605, 0.573, 0.526,
  0.485, 0.456, 0.414, 0.389, 0.360, 0.330, 0.300, 0.271, 0.242, 0.218, 0.200, 0.182, 0.166, 0.153, 0.136, 0.113, 0.091,
  0.074, 0.061, 0.054, 0.049, 0.046, 0.042, 0.037, 0.033, 0.030, 0.028, 0.026, 0.025, 0.009, 0.000, 0.000, 0.000,
])
TEMPLATES = {1.: (_TEMPLATE_RIGHT / _TEMPLATE_RIGHT.max(), _RIGHT_FACTOR), -1.: (_TEMPLATE_LEFT / _TEMPLATE_LEFT.max(), _LEFT_FACTOR)}
RULE_INTERCEPT, RULE_SLOPE = 0.190, -0.018  # 1/m, 1/m per m/s
RULE_SPEEDS = (3.0, 8.0)  # m/s: the FSD turns it was fitted on; below, its crawl value, above, its lateral accel
# First road test: a quarter of FSD's turns replayed 20%+ over FSD's own peak (corners the speed rule can't see), and
# 10-20% too much already felt like far too much on the road, so the rule is taken 8% low: an under-turn can be helped.
PEAK_SCALE = 0.92
MIN_TURN = np.radians(45.)  # heading change that makes it a turn (as the labels)
MIN_TURN_NO_CUE = np.radians(60.)
MAX_SPEED = 9.0  # m/s
CONFIRM_FRAMES = 10  # the plan must show the turn for 0.5 s before it is taken over
BLEND_IN_S, BLEND_OUT_S = 0.5, 1.0
END_LEVEL = 0.05  # past the half-heading point, hand back once the profile is this low
PHANTOM = np.radians(15.)  # before the half-heading point, a turn the plan no longer shows is dropped
TIMING_SPEED = 3.0  # m/s: below it the time to the half-heading point is counted at this speed, so the wheel winds in
                    # while pulling away from a stop the way FSD does, instead of waiting until the car is moving
MODE_PROFILE, MODE_MAX = 'profile', 'max'  # the profile alone, or whichever of action and profile turns more


def rule_peak(v_ego: float) -> float:
  v = float(np.clip(v_ego, *RULE_SPEEDS))
  peak = RULE_INTERCEPT + RULE_SLOPE * v
  if v_ego > RULE_SPEEDS[1]:  # past the fitted speeds, hold its lateral acceleration rather than its curvature
    peak *= (RULE_SPEEDS[1] / v_ego) ** 2
  return PEAK_SCALE * peak


def _shape(direction: float):
  template, factor = TEMPLATES[1. if direction >= 0. else -1.]
  width = float(np.trapezoid(template, TAU))  # s: the integral of curvature / peak over time
  return template, factor, width, np.concatenate([[0.], np.cumsum((template[1:] + template[:-1]) / 2 * np.diff(TAU))])


def turn_peak(v_ego: float, direction: float) -> float:
  return _shape(direction)[1] * rule_peak(v_ego)


def _width(v_ego: float, total: float, direction: float) -> float:
  return float(np.clip(total / (max(v_ego, 1.0) * turn_peak(v_ego, direction)), 1.5, 8.0))  # s, so it adds up to the turn


def profile(tau: float, v_ego: float, total: float, direction: float = 1.) -> float:
  """Curvature toward the turn tau s from its half-heading point, for a turn of `total` rad at v_ego."""
  template, _, width, _ = _shape(direction)
  return turn_peak(v_ego, direction) * float(np.interp(tau * width / _width(v_ego, total, direction), TAU, template,
                                                       left=0., right=0.))


def heading_left(tau: float, v_ego: float, total: float, direction: float = 1.) -> float:
  """Heading (rad) the profile still turns from tau s to its end."""
  _, _, width, cumulative = _shape(direction)
  scale = width / _width(v_ego, total, direction)
  return turn_peak(v_ego, direction) * max(v_ego, 1.0) * float(cumulative[-1] - np.interp(tau * scale, TAU, cumulative)) / scale


class FsdTurnProfile:
  def __init__(self, mode: str = MODE_PROFILE):
    self.mode = mode
    self.reset()

  def reset(self):
    self.active, self.direction, self.confirm = False, 0., 0
    self.done = self.total = self.since_mid = 0.
    self.past_mid = False
    self.v_mid = 0.
    self.weight = 0.
    self.last = 0.

  def update(self, plan_x: np.ndarray, plan_y: np.ndarray, plan_yaw: np.ndarray, yaw_rate: float, v_ego: float,
             dt: float, action: float, turn_sign: float = 0., lead: float = 0.55) -> float:
    """The steering command: the action, or a turn's FSD-timed profile while one is being taken (blended at the
    ends). Curvature, yaw and yaw rate share the plan's sign convention; turn_sign is the held turn cue (0 = none).
    lead is lat_action_t: the template is the curvature the car had, so the command looks it up that much ahead."""
    remaining = float(plan_yaw[-1])  # heading the plan still turns over its horizon
    if not self.active:
      cued = turn_sign != 0. and np.sign(turn_sign) == np.sign(remaining)
      wanted = abs(remaining) >= (MIN_TURN if cued else MIN_TURN_NO_CUE) and v_ego < MAX_SPEED
      self.confirm = self.confirm + 1 if wanted and (self.confirm == 0 or np.sign(remaining) == self.direction) else 0
      self.direction = float(np.sign(remaining)) if wanted else 0.
      if self.confirm >= CONFIRM_FRAMES:
        self.active, self.done, self.total, self.past_mid, self.since_mid = True, 0., abs(remaining), False, 0.
      self.weight = max(self.weight - dt / BLEND_OUT_S, 0.)
      command = self.weight * self.last + (1. - self.weight) * action
      return float(command)

    self.done += self.direction * yaw_rate * dt
    estimate = max(self.done + self.direction * remaining, self.done)
    if self.past_mid:  # past the half-heading point the plan's remaining heading starts to include the road beyond the
      estimate = min(estimate, self.total)  # corner, so the turn's size can only be revised down
    self.total += 0.2 * (estimate - self.total)
    half = self.total / 2.
    if not self.past_mid and self.done >= half:
      self.past_mid, self.v_mid = True, v_ego
    if self.past_mid:
      # the template's time is distance from the half-heading point over the speed there; cars speed up out of a turn
      self.since_mid += max(v_ego, 0.) * dt
      tau = self.since_mid / max(self.v_mid, TIMING_SPEED)
    else:
      arc = np.concatenate([[0.], np.cumsum(np.hypot(np.diff(plan_x), np.diff(plan_y)))])
      heading = self.done + self.direction * np.asarray(plan_yaw)
      reach = np.flatnonzero(heading >= half)
      to_mid = float(np.interp(half, heading[:reach[0] + 1], arc[:reach[0] + 1])) if len(reach) and reach[0] > 0 else (
        0. if len(reach) else float(arc[-1]))
      tau = -to_mid / max(v_ego, TIMING_SPEED)
    v_profile = self.v_mid if self.past_mid else v_ego
    level = profile(tau + lead, v_profile, self.total, self.direction)
    if self.past_mid:
      # past the middle the plan sees the street the turn goes into, so what the turn still needs is known: the rest of
      # the profile may not turn more than that (route b2: on two right turns it kept turning ~1 s after the action
      # unwound and ended 4-8 deg past the turn, until the driver pulled it back). It only ever lowers the profile.
      left = heading_left(tau + lead, v_profile, self.total, self.direction)
      need = max(self.total - self.done, 0.)
      if left > need:
        level *= need / max(left, 1e-6)
    self.last = self.direction * level
    if self.mode == MODE_MAX:  # the action keeps its own timing where it leads; the profile lifts it to FSD's turn
      self.last = self.direction * max(level, self.direction * action)
    self.weight = min(self.weight + dt / BLEND_IN_S, 1.)
    ended = self.past_mid and level < END_LEVEL * turn_peak(self.v_mid, self.direction)
    phantom = not self.past_mid and self.direction * remaining < PHANTOM and self.done < PHANTOM
    if ended or phantom or v_ego > MAX_SPEED + 2.:
      self.active, self.confirm, self.direction = False, 0, 0.
    return float(self.weight * self.last + (1. - self.weight) * action)
