"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math

import pytest

from openpilot.cereal import custom
from openpilot.common.constants import CV
from openpilot.sunnypilot.selfdrive.controls.lib import turn_speed as tsp

NOW = 100.


def context(**changes):
  base = {'status': 'ready', 'direction': 'right', 'locationValid': True, 'headingValid': True, 'updatedAt': NOW - 0.2,
          'incomingBearingDeg': 0., 'exitBearingDeg': 90., 'entered': False, 'completed': False, 'distanceM': 50.}
  return base | changes


def test_approaching_a_90_degree_turn_slows_to_10_mph_by_the_junction():
  expected = math.sqrt(4.5 ** 2 + 2. * tsp.APPROACH_DECEL * (50. - tsp.CORNER_MARGIN))
  assert tsp.corner_speed_target(context(), False, True, NOW) == pytest.approx(expected)
  assert tsp.corner_speed_target(context(distanceM=3.), False, True, NOW) == pytest.approx(4.5)


def test_the_corner_speed_holds_through_the_junction_until_its_completed():
  assert tsp.corner_speed_target(context(entered=True, distanceM=-5.), False, True, NOW) == pytest.approx(4.5)
  assert tsp.corner_speed_target(context(entered=True, completed=True), False, True, NOW) == math.inf


def test_sharper_turns_get_slower_corners():
  right_90 = tsp.corner_speed_target(context(distanceM=0.), False, True, NOW)
  right_45 = tsp.corner_speed_target(context(distanceM=0., exitBearingDeg=45.), False, True, NOW)
  left_135 = tsp.corner_speed_target(context(distanceM=0., direction='left', exitBearingDeg=225.), True, False, NOW)
  assert left_135 < right_90 < right_45


@pytest.mark.parametrize("ctx,left,right", [
  (context(), False, False),  # no blinker
  (context(), True, False),  # the route is for the other side
  (context(), True, True),  # hazards
  (context(status='unavailable'), False, True),
  (context(locationValid=False), False, True),
  (context(updatedAt=NOW - 3.), False, True),  # stale
  (context(distanceM=150.), False, True),  # too far out yet
  (context(exitBearingDeg=10.), False, True),  # barely a turn
  (context(distanceM='x'), False, True),
  (None, False, True),
])
def test_no_usable_route_means_no_corner_speed(ctx, left, right):
  assert tsp.corner_speed_target(ctx, left, right, NOW) == math.inf


class Params:
  def __init__(self, ctx=None, lane_turns=True, lane_turn_mph=19.):
    self.values = {'MapboxTurnContext': ctx, 'LaneTurnDesire': lane_turns, 'LaneTurnValue': lane_turn_mph}
    self.reads = 0

  def get_bool(self, key):
    return bool(self.values[key])

  def get(self, key, return_default=False):
    if key == 'MapboxTurnContext':
      self.reads += 1
    return self.values[key]


def turn_speed(**kw):
  return tsp.TurnSpeed(Params(**kw), clock=lambda: NOW)


def test_a_signalled_turn_at_a_crawl_gets_its_corner_speed():
  assert turn_speed(ctx=context(distanceM=0.)).update(False, True, 5.) == pytest.approx(4.5)


def test_a_blinker_on_the_highway_is_a_lane_change_and_never_slows_the_car():
  # navd can find the next right turn while you signal a lane change at 70 mph
  ts = turn_speed(ctx=context(distanceM=60.))
  assert ts.update(False, True, 70 * CV.MPH_TO_MS) == math.inf
  assert ts.update(False, True, 21 * CV.MPH_TO_MS) == math.inf  # over the 20 mph cap on the lane-turn speed


def test_lane_turns_off_means_no_corner_speed():
  assert turn_speed(ctx=context(distanceM=0.), lane_turns=False).update(False, True, 5.) == math.inf


def test_the_route_is_read_at_4_hz_and_only_while_a_turn_is_signalled():
  ts = turn_speed(ctx=context())
  for _ in range(20):
    ts.update(False, False, 5.)
  assert ts.params.reads == 0
  for _ in range(20):
    ts.update(False, True, 5.)
  assert ts.params.reads == 20 // tsp.READ_EVERY


def test_the_planner_has_a_source_for_it():
  assert custom.LongitudinalPlanSP.LongitudinalPlanSource.turnSpeed is not None
