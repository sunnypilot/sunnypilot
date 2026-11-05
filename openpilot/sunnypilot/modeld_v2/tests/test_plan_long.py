"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from typing import Any

import numpy as np
import pytest

from openpilot.cereal import log
from openpilot.sunnypilot.modeld_v2.constants import ModelConstants, Plan
from openpilot.sunnypilot.modeld_v2.modeld import ModelState
from openpilot.sunnypilot.modeld_v2.plan_long import PlanLong, get_accel_from_plan_horizon

T = np.array(ModelConstants.T_IDXS)
ACTION_T = 0.3
X_STD = 0.5


def make_plan(speeds, x=None, y=None):
  plan = np.zeros((len(T), ModelConstants.PLAN_WIDTH), dtype=np.float32)
  plan[:, Plan.VELOCITY.start] = speeds
  plan[:, Plan.ACCELERATION.start] = np.gradient(speeds, T)
  plan[:, Plan.POSITION.start] = np.concatenate(([0.], np.cumsum(np.diff(T) * (speeds[1:] + speeds[:-1]) / 2))) if x is None else x
  if y is not None:
    plan[:, Plan.POSITION.start + 1] = y
  stds = np.full_like(plan, X_STD)
  return plan, stds


def cruise_then_stop(v0=15., cruise_t=3., decel=3.):
  # holds speed, then brakes hard to a stop: the plan sees the stop well before its first seconds do
  return np.where(T < cruise_t, v0, np.maximum(v0 - decel * (T - cruise_t), 0.))


def horizon(a_now, plan, stds):
  return get_accel_from_plan_horizon(a_now, plan[:, Plan.VELOCITY][:, 0], plan[:, Plan.ACCELERATION][:, 0], plan[:, Plan.POSITION][:, 0],
                                     plan[:, Plan.POSITION][:, 1], stds[:, Plan.POSITION][:, 0], T, ACTION_T)


@pytest.mark.parametrize("a_now", [-0.5, 0., 0.5])
def test_constant_speed_plan_leaves_accel_alone(a_now):
  plan, stds = make_plan(np.full(len(T), 15.))
  assert horizon(a_now, plan, stds) == pytest.approx(a_now)


def test_slows_early_for_a_stop_the_plan_sees_ahead():
  plan, stds = make_plan(cruise_then_stop())
  assert horizon(0., plan, stds) < -1.0


def test_stops_accelerating_when_the_plan_slows_later():
  plan, stds = make_plan(cruise_then_stop())
  assert horizon(0.5, plan, stds) < 0.


def test_never_weakens_harder_braking():
  plan, stds = make_plan(cruise_then_stop())
  assert horizon(-2.5, plan, stds) == -2.5


def test_curved_path_is_not_mistaken_for_slowing():
  # x alone is short in a curve; the distance along the path is what the speed covers
  v, radius = 10., 100.
  speeds = np.full(len(T), v)
  angle = v * T / radius
  plan, stds = make_plan(speeds, x=radius * np.sin(angle), y=radius * (1 - np.cos(angle)))
  assert horizon(0., plan, stds) == pytest.approx(0., abs=1e-3)


def test_action_sets_the_speed_level():
  # the plan's level drifts above what the road needs; after a few seconds the action's level wins
  plan, stds = make_plan(np.full(len(T), 15.))
  plan_long = PlanLong()
  for _ in range(int(15. / 0.05)):
    accel = plan_long.update(plan, stds, T, ACTION_T, action_accel=-0.3)
  assert accel == pytest.approx(-0.3, abs=0.01)


def test_reset_clears_the_level_offset():
  plan, stds = make_plan(np.full(len(T), 15.))
  plan_long = PlanLong()
  for _ in range(100):
    plan_long.update(plan, stds, T, ACTION_T, action_accel=-0.3)
  plan_long.reset()
  assert plan_long.update(plan, stds, T, ACTION_T) == pytest.approx(0.)


class MockStruct:
  def __init__(self, **kwargs):
    for k, v in kwargs.items():
      setattr(self, k, v)


def run_action(plan_long):
  state: Any = MockStruct(PLANPLUS_CONTROL=1.0, LONG_SMOOTH_SECONDS=0.3, LAT_SMOOTH_SECONDS=0.1, MIN_LAT_CONTROL_SPEED=0.3, mlsim=False,
                          generation=12, constants=MockStruct(T_IDXS=ModelConstants.T_IDXS))
  plan, stds = make_plan(cruise_then_stop())
  model_output = {'plan': plan[None], 'plan_stds': stds[None], 'action': np.array([[0., 0.]], dtype=np.float32)}
  return ModelState.get_action_from_model(state, model_output, log.ModelDataV2.Action(), 0.3, ACTION_T, 15.,  # type: ignore[arg-type]
                                          plan_long=plan_long)


def test_toggle_off_uses_the_action_accel():
  assert run_action(None).desiredAcceleration == 0.


def test_toggle_on_brakes_early_from_the_plan():
  assert run_action(PlanLong()).desiredAcceleration < 0.
