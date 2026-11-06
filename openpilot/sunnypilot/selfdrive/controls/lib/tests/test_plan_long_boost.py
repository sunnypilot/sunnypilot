"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from types import SimpleNamespace

import pytest

from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.controls.lib.accel_boost import AccelBoost
from openpilot.sunnypilot.selfdrive.controls.lib.accel_boost import ACCEL_BOOST_BUILD, ACCEL_BOOST_MAX, ACCEL_BOOST_RELEASE, AccelBoostSP
from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import PLAN_LONG_BOOST_ACCEL, LongitudinalPlannerSP

BOOST_MAX = ACCEL_BOOST_MAX[0]  # aggressive
SLOWING, NOT_SLOWING = -0.15, 0.3  # plan accel, m/s^2; -0.15 is where the boost alone is still at full strength


def make_sm(brake_prob=0.05, v_ego=30.0, enabled=True):
  meta = SimpleNamespace(disengagePredictions=SimpleNamespace(brakePressProbs=[0.0, brake_prob, 0.0, 0.0, 0.0, 0.0],
                                                              gasPressProbs=[0.0, 0.3, 0.0, 0.0, 0.0, 0.0]))
  action = SimpleNamespace(shouldStop=False, desiredCurvature=0.0)
  return {'modelV2': SimpleNamespace(meta=meta, action=action), 'carState': SimpleNamespace(vEgo=v_ego),
          'selfdriveState': SimpleNamespace(enabled=enabled, personality=0)}


def make_planner(plan_long, boost=None):
  return SimpleNamespace(plan_long=plan_long, accel_boost=boost if boost is not None else AccelBoostSP())


def run(planner, plan_accel, frames=200, sm=None):
  sm = sm if sm is not None else make_sm()
  out = plan_accel
  for _ in range(frames):
    out = LongitudinalPlannerSP.update_accel_boost(planner, sm, plan_accel, 9.0, 9.0)
  return out


def test_plan_braking_off_boosts_a_gentle_slowdown():
  # the boost on its own stays at full strength down to -0.2 m/s^2
  planner = make_planner(plan_long=False)
  assert run(planner, SLOWING) == pytest.approx(SLOWING + BOOST_MAX)


def test_plan_braking_keeps_the_plans_slowdown():
  planner = make_planner(plan_long=True)
  assert run(planner, SLOWING) == pytest.approx(SLOWING)
  assert planner.accel_boost.total_boost == 0.0


def test_plan_braking_boosts_when_the_plan_is_not_slowing():
  planner = make_planner(plan_long=True)
  assert run(planner, NOT_SLOWING) == pytest.approx(NOT_SLOWING + BOOST_MAX)


def test_gate_is_off_at_the_bottom_and_full_at_the_top():
  low, high = PLAN_LONG_BOOST_ACCEL
  assert run(make_planner(plan_long=True), low) == pytest.approx(low)
  assert run(make_planner(plan_long=True), high) == pytest.approx(high + BOOST_MAX)
  mid = (low + high) / 2
  assert run(make_planner(plan_long=True), mid) == pytest.approx(mid + BOOST_MAX / 2)


def test_boost_builds_at_its_rate_when_the_plan_stops_slowing():
  planner = make_planner(plan_long=True)
  run(planner, SLOWING)
  run(planner, NOT_SLOWING, frames=1)
  assert planner.accel_boost.total_boost == pytest.approx(ACCEL_BOOST_BUILD * DT_MDL)
  run(planner, NOT_SLOWING, frames=9)
  assert planner.accel_boost.total_boost == pytest.approx(10 * ACCEL_BOOST_BUILD * DT_MDL)


def test_boost_releases_at_its_rate_when_the_plan_starts_slowing():
  planner = make_planner(plan_long=True)
  run(planner, NOT_SLOWING)
  run(planner, SLOWING, frames=1)
  assert planner.accel_boost.total_boost == pytest.approx(BOOST_MAX - ACCEL_BOOST_RELEASE * DT_MDL)
  run(planner, SLOWING, frames=int(BOOST_MAX / (ACCEL_BOOST_RELEASE * DT_MDL)))
  assert planner.accel_boost.total_boost == 0.0


def test_model_expecting_a_brake_still_holds_the_boost_off():
  planner = make_planner(plan_long=True)
  assert run(planner, NOT_SLOWING, sm=make_sm(brake_prob=0.5)) == pytest.approx(NOT_SLOWING)


@pytest.mark.parametrize("plan_accel", [SLOWING, NOT_SLOWING])
def test_stock_boost_stays_off_with_plan_braking(plan_accel):
  stock = AccelBoost()
  stock.total_boost = 0.2  # latched on after a gas override
  planner = make_planner(plan_long=True, boost=stock)
  assert run(planner, plan_accel, frames=1) == plan_accel
  assert stock.total_boost == 0.0
