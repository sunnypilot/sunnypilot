"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Shaping for signalled turns at a crawl (docs/superpowers/specs/2026-11-06-crawl-turns-design.md):

1. hold the turn-in until the model's corner reaches the front bumper, the way FSD goes past the entrance first,
2. then let the plan floor act in full, read further ahead so the rate-limited wheel arrives on time,
3. scaled up when the route says more turn is left than the plan has.

Routes 85/89 (Light Speed 2): the driver pushed against the turn at turn-in (median 12% of the turn done, the plan's
corner 1.4-3.5 m ahead of the camera), mostly while the floor set the command; above 4 m/s turns were fine. Replaying
those turns, the car already turned in about when the plan's corner reached the bumper (69 of 71 pushback frames came
after that), so the hold has to last past the corner: a further PAST_CORNER_M of travel, counted by speed, since a car
held at the corner gets a plan that turns right where it is.
"""
import math
from dataclasses import dataclass

import numpy as np

CAMERA_TO_FRONT = 1.52  # m, the comma's camera sits this far behind the front bumper (radard's RADAR_TO_CAMERA)
BEND_RAD = math.radians(5.)  # the plan's corner starts where its heading has turned this far toward the turn
TURN_IN_AT = 0.  # m ahead of the front bumper: the plan's corner is reached here
APPROACH_MAX_S = 8.  # s of creeping toward the corner, at most: a plan whose corner stays just out of reach can't pin it
MOVING = 0.5  # m/s: waiting at a stop doesn't use up the approach
PAST_CORNER_M = 2.0  # m travelled past the corner before turning in, like FSD going well past the entrance
PAST_CORNER_RAMP = 1.0  # m over which the hold lets go at the end of that
HOLD_MAX_S = 2.5  # s after reaching the corner, whatever the travel: the hold never outlasts this
DT = 0.05  # s between updates, the model's frame
HOLD_SPEED_BP = [4., 6.]  # m/s: full hold at a crawl, none from 13 mph, where turns were fine
MIN_PLAN_TRAVEL = 8.  # m: a plan covering less (a stopped car) has no corner to measure
LEAD_BP, LEAD_V = [4., 8.], [0.3, 0.]  # s of extra look-ahead for the floor: the wheel lags its command most at a crawl
NOW_T = 0.1  # s: reading the plan this soon gives the curvature of the road right under the car
NEAR_CORNER_M = 3.  # m: from this close the plan's curvature under the car is the turn itself, not the road before it
ROUTE_MARGIN_DEG = 10.  # the route has to want this much more turn than the plan before it counts
ROUTE_MIN_PLAN_DEG = 30.  # a plan that has barely started its turn isn't scaled from almost nothing
ROUTE_MAX_FACTOR = 1.3
ROUTE_MAX_AGE = 1.0  # s, an older route context is ignored
ROUTE_MIN_TURN_DEG = 15.
MAX_FLOOR_CURVATURE = 0.2  # 1/m, a 5 m radius
MAX_FLOOR_LAT_ACCEL = 3.0  # m/s^2


def plan_bend_distance(xs, ys, yaws, sign: float) -> float | None:
  """Distance from the front bumper, along the plan, to where its heading has turned BEND_RAD toward the turn.

  Negative once the bumper is past it. None when the plan never turns that far, or covers under MIN_PLAN_TRAVEL.
  """
  xs, ys, turned = np.asarray(xs, dtype=float), np.asarray(ys, dtype=float), sign * np.asarray(yaws, dtype=float)
  s = np.concatenate([[0.], np.cumsum(np.hypot(np.diff(xs), np.diff(ys)))])
  if s[-1] < MIN_PLAN_TRAVEL:
    return None
  past = np.flatnonzero(turned >= BEND_RAD)
  if not len(past):
    return None
  i = int(past[0])
  if i == 0:
    return float(s[0] - CAMERA_TO_FRONT)
  f = (BEND_RAD - turned[i - 1]) / (turned[i] - turned[i - 1])
  return float(s[i - 1] + f * (s[i] - s[i - 1]) - CAMERA_TO_FRONT)


def speed_factor(v_ego: float) -> float:
  return float(np.interp(v_ego, HOLD_SPEED_BP, [1., 0.]))


def approach_hold(bend: float | None, held_s: float) -> float:
  """Before the corner: the turn-in is held fully while the plan has a corner ahead, for APPROACH_MAX_S at most.
  No corner in the plan, no hold: it never pins the wheel on a plan that doesn't turn."""
  return 0. if bend is None or held_s >= APPROACH_MAX_S else 1.


def past_corner_hold(past_m: float, held_s: float) -> float:
  """Past the corner: held until PAST_CORNER_M of travel, letting go over the last PAST_CORNER_RAMP, never past HOLD_MAX_S."""
  if held_s >= HOLD_MAX_S:
    return 0.
  return float(np.interp(past_m, [PAST_CORNER_M - PAST_CORNER_RAMP, PAST_CORNER_M], [1., 0.]))


def hold_turn_in(action_curvature: float, road: float, turn_sign: float, hold: float) -> float:
  """Hold steering toward the turn back to what the road needs. Curvature is + to the right.

  Only the part toward the turn beyond `road` is held, by `hold` (0-1); steering away from the turn is never touched.
  """
  toward, allowed = turn_sign * action_curvature, max(turn_sign * road, 0.)
  if turn_sign == 0. or hold <= 0. or toward <= allowed:
    return action_curvature
  return turn_sign * (allowed + (1. - hold) * (toward - allowed))


def turn_lead(v_ego: float) -> float:
  return float(np.interp(v_ego, LEAD_BP, LEAD_V))


def _wrap_deg(deg: float) -> float:
  return (deg + 180.) % 360. - 180.


def route_turn_remaining(context, turn_sign: float, now: float) -> float | None:
  """Degrees of turn the signal route still wants, from navd's MapboxTurnContext; None without a fresh, valid one.

  Before the junction it's the change from the entry to the exit bearing, once in it the heading's error to the exit.
  """
  if not isinstance(context, dict) or turn_sign == 0.:
    return None
  try:
    if context.get('status') != 'ready' or context.get('direction') != ('right' if turn_sign > 0 else 'left'):
      return None
    if context.get('locationValid') is not True or context.get('headingValid') is not True or context.get('completed') is True:
      return None
    age = now - float(context['updatedAt'])
    turn = turn_sign * _wrap_deg(float(context['exitBearingDeg']) - float(context['incomingBearingDeg']))
    if not (0. <= age <= ROUTE_MAX_AGE) or not math.isfinite(turn) or turn < ROUTE_MIN_TURN_DEG:
      return None
    error = context.get('exitHeadingErrorDeg')
    if context.get('entered') is True and isinstance(error, (int, float)) and math.isfinite(error):
      return float(min(abs(error), turn))
    return float(turn)
  except (KeyError, TypeError, ValueError):
    return None


def route_factor(remaining_deg: float | None, yaws, turn_sign: float) -> float:
  """How much to scale the floor's plan curvature when the route wants more turn than the plan's horizon has."""
  if remaining_deg is None or turn_sign == 0.:
    return 1.
  plan_deg = math.degrees(turn_sign * float(yaws[-1]))
  if remaining_deg - plan_deg <= ROUTE_MARGIN_DEG:
    return 1.
  return float(np.clip(remaining_deg / max(plan_deg, ROUTE_MIN_PLAN_DEG), 1., ROUTE_MAX_FACTOR))


def limit_floor(curvature: float, v_ego: float) -> float:
  limit = min(MAX_FLOOR_CURVATURE, MAX_FLOOR_LAT_ACCEL / max(v_ego, 1.) ** 2)
  return float(np.clip(curvature, -limit, limit))


@dataclass
class TurnShape:
  hold: float = 0.
  lead: float = 0.
  factor: float = 1.
  bend: float = -1.  # m, -1 when the plan has no corner to measure
  route_deg: float = -1.  # -1 without a route
  road: float = 0.  # curvature toward the turn the hold still allows: the road's from before the corner


class TurnShaper:
  """Per signalled turn: approach the corner held, reach it, go PAST_CORNER_M further, then let go for good that turn."""

  def __init__(self):
    self.reset(0.)
    self.shape = TurnShape()

  def reset(self, turn_sign: float) -> None:
    self.sign = turn_sign
    self.reached = False  # the plan's corner has come to the bumper
    self.approach_s = 0.  # s held before the corner
    self.past_m, self.held_s = 0., 0.  # travel and time since the corner
    self.road = 0.  # the road's curvature under the car while the corner was still NEAR_CORNER_M away
    self.released = False

  def update(self, xs, ys, yaws, turn_sign: float, v_ego: float, road_now: float = 0., route_remaining: float | None = None) -> TurnShape:
    """road_now: the plan's curvature right under the car (+ right). Near the corner that's the turn, so the hold keeps
    to the road's curvature from before it: a curving approach is still followed, the turn waits."""
    if turn_sign != self.sign:
      self.reset(turn_sign)
    if turn_sign == 0.:
      self.shape = TurnShape()
      return self.shape
    bend = plan_bend_distance(xs, ys, yaws, turn_sign)
    if not self.reached and (bend is None or bend > NEAR_CORNER_M):
      self.road = road_now
    # only the corner starts the countdown: a turn signalled at speed still gets held once it slows for the corner
    if not self.reached and bend is not None and bend <= TURN_IN_AT:
      self.reached = True
    if self.reached and not self.released:
      self.past_m += max(v_ego, 0.) * DT
      self.held_s += DT
      if past_corner_hold(self.past_m, self.held_s) <= 0.:
        self.released = True
    if self.released:
      hold = 0.
    elif self.reached:
      hold = past_corner_hold(self.past_m, self.held_s)
    else:
      hold = approach_hold(bend, self.approach_s)
      if hold > 0. and MOVING < v_ego and speed_factor(v_ego) > 0.:
        self.approach_s += DT
    self.shape = TurnShape(hold=hold * speed_factor(v_ego), lead=turn_lead(v_ego),
                           factor=route_factor(route_remaining, yaws, turn_sign), bend=-1. if bend is None else bend,
                           route_deg=-1. if route_remaining is None else route_remaining, road=self.road)
    return self.shape
