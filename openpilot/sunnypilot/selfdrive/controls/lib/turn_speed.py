"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Corner speed for a signalled turn, from navd's signal route (MapboxTurnContext, no destination needed): a cap on the
cruise target by the turn's angle, approached gently from the distance to the junction and held through it. It only
ever lowers the target, and only matters with openpilot longitudinal. The route's few metres of GPS error are fine for
a speed; it never times the steering (docs/superpowers/specs/2026-11-06-crawl-turns-design.md).
"""
import math
import time

import numpy as np

from openpilot.common.constants import CV
from openpilot.common.params import Params

CORNER_SPEED_BP = [20., 45., 90., 135.]  # deg of turn
CORNER_SPEED_V = [12., 7., 4.5, 3.5]  # m/s: 90 deg is 10 mph
APPROACH_DECEL = 1.0  # m/s^2 from the junction distance down to the corner speed
CORNER_MARGIN = 5.  # m before the junction by which the corner speed is reached
MAX_DISTANCE = 100.  # m: further from the junction than this it doesn't act yet
LANE_CHANGE_SPEED_MIN = 20 * CV.MPH_TO_MS  # the blinker above the lane-turn speed means a lane change, as in lane_turn_desire
PARAMS_EVERY = 100  # planner frames between reads of the lane-turn settings: 5 s
MIN_TURN_DEG = 20.
MAX_AGE = 1.5  # s, an older route context is ignored
READ_EVERY = 5  # planner frames between reads of the context: 4 Hz


def _wrap_deg(deg: float) -> float:
  return (deg + 180.) % 360. - 180.


def corner_speed_target(context, left_blinker: bool, right_blinker: bool, now: float) -> float:
  """The speed (m/s) to keep under for the signalled turn ahead, or inf when there's no usable route."""
  signal = 'left' if left_blinker and not right_blinker else 'right' if right_blinker and not left_blinker else None
  if signal is None or not isinstance(context, dict):
    return math.inf
  try:
    if context.get('status') != 'ready' or context.get('direction') != signal or context.get('locationValid') is not True:
      return math.inf
    if context.get('completed') is True or not 0. <= now - float(context['updatedAt']) <= MAX_AGE:
      return math.inf
    sign = 1. if signal == 'right' else -1.
    turn = sign * _wrap_deg(float(context['exitBearingDeg']) - float(context['incomingBearingDeg']))
    if not math.isfinite(turn) or turn < MIN_TURN_DEG:
      return math.inf
    corner = float(np.interp(turn, CORNER_SPEED_BP, CORNER_SPEED_V))
    if context.get('entered') is True:
      return corner  # held through the corner until navd calls it completed
    distance = float(context['distanceM'])
    if not math.isfinite(distance) or not 0. <= distance <= MAX_DISTANCE:
      return math.inf
    return math.sqrt(corner ** 2 + 2. * APPROACH_DECEL * max(distance - CORNER_MARGIN, 0.))
  except (KeyError, TypeError, ValueError):
    return math.inf


class TurnSpeed:
  """Only for a turn as lane_turn_desire sees one: lane turns on and the blinker under the lane-turn speed. A blinker on
  the highway is a lane change, and navd's next turn on that side must never slow the car for it."""

  def __init__(self, params: Params | None = None, clock=time.monotonic):
    self.params = params if params is not None else Params()
    self.clock = clock
    self.frame = 0
    self.context = None
    self.v_target = math.inf
    self.enabled, self.lane_turn_value = False, 0.

  def _read_settings(self) -> None:
    self.enabled = self.params.get_bool("LaneTurnDesire")
    value = float(self.params.get("LaneTurnValue", return_default=True)) * CV.MPH_TO_MS
    self.lane_turn_value = min(float(LANE_CHANGE_SPEED_MIN), value)

  def update(self, left_blinker: bool, right_blinker: bool, v_ego: float) -> float:
    if self.frame % PARAMS_EVERY == 0:
      self._read_settings()
    if not (left_blinker or right_blinker) or not self.enabled or v_ego > self.lane_turn_value:
      self.frame += 1
      self.context, self.v_target = None, math.inf  # no turn signalled, or it's a lane change: nothing to read
      return self.v_target
    if self.frame % READ_EVERY == 0 or self.context is None:
      self.context = self.params.get('MapboxTurnContext')
    self.frame += 1
    self.v_target = corner_speed_target(self.context, left_blinker, right_blinker, self.clock())
    return self.v_target
