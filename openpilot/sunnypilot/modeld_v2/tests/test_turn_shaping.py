"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math

import numpy as np
import pytest

from openpilot.sunnypilot.modeld_v2.constants import ModelConstants
from openpilot.sunnypilot.modeld_v2 import turn_shaping as ts

T = np.array(ModelConstants.T_IDXS)
RIGHT, LEFT = 1., -1.


def corner_plan(corner_m, sign=RIGHT, v=3., k=0.12):
  """A plan driving straight `corner_m` metres from the camera, then an arc of curvature k toward the turn."""
  s = v * T
  arc = np.maximum(s - corner_m, 0.)
  yaws = sign * k * arc
  xs = np.where(s <= corner_m, s, corner_m + np.sin(k * arc) / k)
  ys = np.where(s <= corner_m, 0., sign * (1 - np.cos(k * arc)) / k)
  return xs, ys, yaws


def test_bend_distance_is_from_the_front_bumper_to_the_corner():
  xs, ys, yaws = corner_plan(10.)
  # heading reaches 5 deg a little past where the arc starts
  expected = 10. + ts.BEND_RAD / 0.12 - ts.CAMERA_TO_FRONT
  assert ts.plan_bend_distance(xs, ys, yaws, RIGHT) == pytest.approx(expected, abs=0.3)


def test_bend_distance_is_none_for_a_straight_plan_a_short_plan_or_the_wrong_side():
  xs, ys, yaws = corner_plan(500.)
  assert ts.plan_bend_distance(xs, ys, yaws, RIGHT) is None
  xs, ys, yaws = corner_plan(2., v=0.5)  # 5 m of plan: a car that's barely moving
  assert ts.plan_bend_distance(xs, ys, yaws, RIGHT) is None
  xs, ys, yaws = corner_plan(5., sign=LEFT)
  assert ts.plan_bend_distance(xs, ys, yaws, RIGHT) is None


def test_before_the_corner_the_hold_is_full_while_the_plan_has_a_corner_and_off_without_one():
  assert ts.approach_hold(10., 0.) == 1.
  assert ts.approach_hold(0.5, 0.) == 1.
  assert ts.approach_hold(None, 0.) == 0.
  assert ts.approach_hold(10., ts.APPROACH_MAX_S) == 0.


def test_past_the_corner_the_hold_lasts_its_distance_then_lets_go_over_the_last_metre():
  assert ts.past_corner_hold(0., 0.) == 1.
  assert ts.past_corner_hold(ts.PAST_CORNER_M - ts.PAST_CORNER_RAMP / 2, 0.5) == pytest.approx(0.5)
  assert ts.past_corner_hold(ts.PAST_CORNER_M, 0.5) == 0.
  assert ts.past_corner_hold(0., ts.HOLD_MAX_S) == 0.


def test_the_hold_fades_with_speed_and_is_gone_from_6_m_s():
  assert ts.speed_factor(3.) == 1.
  assert ts.speed_factor(5.) == pytest.approx(0.5)
  assert ts.speed_factor(6.) == 0.


@pytest.mark.parametrize("sign", [RIGHT, LEFT])
def test_holding_keeps_only_what_the_road_under_the_car_needs(sign):
  # the action wants 0.1 toward the turn, the road right here only 0.02
  assert ts.hold_turn_in(sign * 0.1, sign * 0.02, sign, 1.) == pytest.approx(sign * 0.02)
  assert ts.hold_turn_in(sign * 0.1, sign * 0.02, sign, 0.5) == pytest.approx(sign * 0.06)
  assert ts.hold_turn_in(sign * 0.1, sign * 0.02, sign, 0.) == sign * 0.1


@pytest.mark.parametrize("sign", [RIGHT, LEFT])
def test_holding_never_touches_steering_away_from_the_turn(sign):
  assert ts.hold_turn_in(-sign * 0.05, 0., sign, 1.) == -sign * 0.05
  # nor a road under the car that bends away
  assert ts.hold_turn_in(sign * 0.01, -sign * 0.03, sign, 1.) == pytest.approx(0.)


def test_look_ahead_is_most_at_a_crawl_and_gone_by_8_m_s():
  assert ts.turn_lead(2.) == pytest.approx(0.3)
  assert ts.turn_lead(6.) == pytest.approx(0.15)
  assert ts.turn_lead(8.) == 0.


def drive(shaper, plan, v, frames, sign=RIGHT):
  return [shaper.update(*plan, sign, v).hold for _ in range(frames)]


def test_shaper_holds_to_the_corner_then_past_it_then_lets_go_for_the_turn():
  shaper = ts.TurnShaper()
  assert drive(shaper, corner_plan(12.), 3., 5) == [1.] * 5
  # the corner reaches the bumper: still held for the next 1.5 m, letting go over its last metre (0.15 m a frame at 3 m/s)
  holds = drive(shaper, corner_plan(0.), 3., 20)
  assert holds[:3] == [1.] * 3
  assert holds[-1] == 0. and shaper.released
  assert holds == sorted(holds, reverse=True)
  # turning, the plan's corner can look further off again: the hold doesn't come back
  assert drive(shaper, corner_plan(12.), 3., 3) == [0.] * 3


def test_a_corner_the_plan_keeps_just_ahead_is_still_reached_by_travel():
  # route 92: held straight at a crawl, the model re-plans its corner about 1 m ahead of the bumper, frame after frame
  plan = corner_plan(1.8)
  assert ts.plan_bend_distance(*plan, RIGHT) == pytest.approx(1., abs=0.1)
  shaper = ts.TurnShaper()
  holds = drive(shaper, plan, 2., 30)  # 0.1 m a frame: the corner after about 10, then 1.5 m more
  assert holds[:14] == [1.] * 14
  assert holds[-1] == 0. and shaper.released


def test_the_hold_can_be_turned_off_and_the_corner_is_still_measured():
  shaper = ts.TurnShaper()
  shaper.hold_enabled = False
  shape = shaper.update(*corner_plan(12.), RIGHT, 3.)
  assert shape.hold == 0.
  assert shape.bend == pytest.approx(12. + ts.BEND_RAD / 0.12 - ts.CAMERA_TO_FRONT, abs=0.3)


def test_waiting_at_the_corner_still_turns_in_after_hold_max_s():
  shaper = ts.TurnShaper()
  drive(shaper, corner_plan(0.), 3., 1)
  frames = int(ts.HOLD_MAX_S / ts.DT) + 1
  assert drive(shaper, corner_plan(0., v=0.), 0., frames)[-1] == 0.


def test_waiting_at_a_stop_before_the_corner_doesnt_use_up_the_approach():
  shaper = ts.TurnShaper()
  waited = drive(shaper, corner_plan(6.), 0., int(30. / ts.DT))  # a long red light, the plan still has the corner
  assert waited[-1] == 1.
  assert shaper.update(*corner_plan(6.), RIGHT, 1.).hold == 1.


def test_creeping_toward_a_corner_that_never_comes_lets_go_after_approach_max_s():
  shaper = ts.TurnShaper()
  frames = int(ts.APPROACH_MAX_S / ts.DT) + 3
  assert drive(shaper, corner_plan(6.), 1.5, frames)[-1] == 0.


def test_the_hold_keeps_to_the_road_from_before_the_corner_not_the_turn():
  shaper = ts.TurnShaper()
  # a gentle curve toward the turn on the way in, then the corner, where the plan's curvature under the car is the turn
  shaper.update(*corner_plan(12.), RIGHT, 3., 0.01)
  shaper.update(*corner_plan(2.), RIGHT, 3., 0.08)
  assert shaper.update(*corner_plan(0.), RIGHT, 3., 0.12).road == pytest.approx(0.01)


def test_a_plan_without_a_corner_is_never_held():
  assert drive(ts.TurnShaper(), corner_plan(500.), 3., 5) == [0.] * 5


def test_a_turn_signalled_at_speed_is_still_held_once_it_slows_for_the_corner():
  shaper = ts.TurnShaper()
  assert drive(shaper, corner_plan(40., v=10.), 10., 3) == [0.] * 3  # too fast to hold
  assert shaper.update(*corner_plan(12.), RIGHT, 3.).hold == 1.


def test_a_new_turn_or_none_resets_the_shaper():
  shaper = ts.TurnShaper()
  drive(shaper, corner_plan(0.), 3., 30)
  assert shaper.released
  assert shaper.update(None, None, None, 0., 3.).hold == 0.
  assert shaper.update(*corner_plan(12., sign=LEFT), LEFT, 3.).hold == 1.


def context(**changes):
  base = {'status': 'ready', 'direction': 'right', 'locationValid': True, 'headingValid': True, 'updatedAt': 100.,
          'incomingBearingDeg': 0., 'exitBearingDeg': 90., 'entered': False, 'exitHeadingErrorDeg': 90.}
  return base | changes


def test_route_remaining_is_the_bearing_change_before_the_junction():
  assert ts.route_turn_remaining(context(), RIGHT, 100.2) == pytest.approx(90.)
  assert ts.route_turn_remaining(context(direction='left', exitBearingDeg=270.), LEFT, 100.2) == pytest.approx(90.)
  # bearings across north
  assert ts.route_turn_remaining(context(incomingBearingDeg=350., exitBearingDeg=80.), RIGHT, 100.2) == pytest.approx(90.)


def test_route_remaining_is_the_exit_heading_error_once_in_the_junction():
  assert ts.route_turn_remaining(context(entered=True, exitHeadingErrorDeg=35.), RIGHT, 100.2) == pytest.approx(35.)


@pytest.mark.parametrize("changes,sign,now", [
  ({}, LEFT, 100.2),  # the route is for the other side
  ({'status': 'unavailable'}, RIGHT, 100.2),
  ({'locationValid': False}, RIGHT, 100.2),
  ({'headingValid': False}, RIGHT, 100.2),
  ({'completed': True}, RIGHT, 100.2),
  ({}, RIGHT, 101.5),  # stale
  ({'exitBearingDeg': 5.}, RIGHT, 100.2),  # barely a turn
  ({'exitBearingDeg': 'x'}, RIGHT, 100.2),
  ({'updatedAt': None}, RIGHT, 100.2),
])
def test_route_remaining_is_none_without_a_fresh_valid_route(changes, sign, now):
  assert ts.route_turn_remaining(context(**changes), sign, now) is None


def test_route_remaining_is_none_without_a_context():
  assert ts.route_turn_remaining(None, RIGHT, 100.) is None
  assert ts.route_turn_remaining(context(), 0., 100.2) is None


def yaws_ending_at(deg, sign=RIGHT):
  return np.linspace(0., sign * math.radians(deg), len(T))


def test_route_scales_a_plan_that_turns_too_little_up_to_1_3x():
  assert ts.route_factor(90., yaws_ending_at(75.), RIGHT) == pytest.approx(90. / 75.)
  assert ts.route_factor(90., yaws_ending_at(40.), RIGHT) == pytest.approx(ts.ROUTE_MAX_FACTOR)


def test_route_leaves_a_plan_that_already_turns_enough_alone():
  assert ts.route_factor(90., yaws_ending_at(85.), RIGHT) == 1.
  assert ts.route_factor(None, yaws_ending_at(10.), RIGHT) == 1.
  assert ts.route_factor(45., yaws_ending_at(100.), RIGHT) == 1.


def test_route_doesnt_scale_a_plan_that_has_barely_started_from_almost_nothing():
  # 35 deg over a 5 deg plan would be 7x; it's measured against 30 deg instead
  assert ts.route_factor(35., yaws_ending_at(5.), RIGHT) == pytest.approx(35. / ts.ROUTE_MIN_PLAN_DEG)


def test_the_floor_is_limited_in_curvature_and_lateral_acceleration():
  assert ts.limit_floor(0.5, 2.) == ts.MAX_FLOOR_CURVATURE
  assert ts.limit_floor(-0.5, 2.) == -ts.MAX_FLOOR_CURVATURE
  assert ts.limit_floor(0.15, 6.) == pytest.approx(ts.MAX_FLOOR_LAT_ACCEL / 36.)
  assert ts.limit_floor(0.05, 3.) == 0.05
