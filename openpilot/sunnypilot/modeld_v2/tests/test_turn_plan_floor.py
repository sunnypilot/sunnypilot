"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pytest

from openpilot.sunnypilot.modeld_v2.turn_plan_floor import TURN_PLAN_FLOOR, apply_turn_plan_floor

RIGHT, LEFT, NONE = 1., -1., 0.


def test_the_floor_is_three_quarters_of_the_plan():
  assert TURN_PLAN_FLOOR == 0.75


def test_no_turn_leaves_action_alone():
  assert apply_turn_plan_floor(0.01, 0.2, NONE) == 0.01


@pytest.mark.parametrize("sign", [RIGHT, LEFT])
def test_weak_action_is_raised_to_scaled_plan(sign):
  # curvature is + to the right, so a left turn is negative
  assert apply_turn_plan_floor(sign * 0.03, sign * 0.10, sign) == pytest.approx(sign * TURN_PLAN_FLOOR * 0.10)


@pytest.mark.parametrize("sign", [RIGHT, LEFT])
def test_strong_action_is_kept(sign):
  assert apply_turn_plan_floor(sign * 0.12, sign * 0.10, sign) == sign * 0.12


@pytest.mark.parametrize("sign", [RIGHT, LEFT])
def test_plan_against_the_turn_never_weakens_or_reverses(sign):
  assert apply_turn_plan_floor(sign * 0.05, -sign * 0.10, sign) == sign * 0.05


def test_floor_only_pushes_toward_the_requested_side():
  # a right-turn request must never add left curvature, even if action and plan both point left
  assert apply_turn_plan_floor(-0.02, -0.10, RIGHT) == -0.02


@pytest.mark.parametrize("sign", [RIGHT, LEFT])
def test_stale_turn_never_weakens_a_steer_the_plan_also_wants(sign):
  # a right turn still requested while plan and action both steer left (exit or a right straight into a left)
  assert apply_turn_plan_floor(-sign * 0.12, -sign * 0.10, sign) == -sign * 0.12


def _run_action(turn_sign, v_ego=2., k=0.1, action_share=0.5, turn_state=None):
  # a turn the plan holds at curvature k while the action head asks for only part of it
  from typing import Any
  import numpy as np
  from openpilot.cereal import log
  from openpilot.sunnypilot.modeld_v2.constants import ModelConstants, Plan
  from openpilot.sunnypilot.modeld_v2.modeld import ModelState

  class State:
    pass
  state: Any = State()
  state.LONG_SMOOTH_SECONDS, state.LAT_SMOOTH_SECONDS, state.MIN_LAT_CONTROL_SPEED, state.generation = 0.3, 0., 0.3, 12
  state.constants = ModelConstants
  t = np.array(ModelConstants.T_IDXS)
  plan = np.zeros((len(t), ModelConstants.PLAN_WIDTH), dtype=np.float32)
  plan[:, Plan.POSITION.start] = v_ego * t
  plan[:, Plan.T_FROM_CURRENT_EULER.start + 2] = k * v_ego * t
  plan[:, Plan.ORIENTATION_RATE.start + 2] = k * v_ego
  out = {'plan': plan[None], 'action': np.array([[action_share * k * v_ego ** 2, 0.]], dtype=np.float32)}
  if turn_state is not None:
    desire_state = np.zeros((1, ModelConstants.DESIRE_PRED_WIDTH), dtype=np.float32)
    desire_state[0, int(log.Desire.turnRight if turn_sign > 0 else log.Desire.turnLeft)] = turn_state
    out['desire_state'] = desire_state
  action = ModelState.get_action_from_model(state, out, log.ModelDataV2.Action(), 0.3, 0.3, v_ego, turn_sign=turn_sign)
  return state, action


def test_logs_the_action_before_the_floor_and_the_plan_it_compares_against():
  state, action = _run_action(RIGHT)
  assert state.action_curvature == pytest.approx(0.05)
  assert state.turn_plan_curvature == pytest.approx(0.1, rel=1e-3)
  assert action.desiredCurvature == pytest.approx(TURN_PLAN_FLOOR * state.turn_plan_curvature, rel=1e-5)


def test_no_turn_logs_no_plan_curvature():
  state, action = _run_action(NONE)
  assert state.turn_plan_curvature == 0.
  assert action.desiredCurvature == pytest.approx(state.action_curvature)


@pytest.mark.parametrize("sign", [RIGHT, LEFT])
@pytest.mark.parametrize("v_ego", [1., 4., 8.])
def test_the_floor_acts_at_every_turn_speed(sign, v_ego):
  state, action = _run_action(sign, v_ego=v_ego, k=sign * 0.1)
  assert action.desiredCurvature == pytest.approx(TURN_PLAN_FLOOR * state.turn_plan_curvature, rel=1e-5)


@pytest.mark.parametrize("sign", [RIGHT, LEFT])
def test_the_floor_follows_the_plan_even_when_the_model_has_lost_the_turn(sign):
  # pulling away after a wait at a stop the model's own turn state has faded; the plan alone decides
  state, action = _run_action(sign, k=sign * 0.1, turn_state=0.1)
  assert action.desiredCurvature == pytest.approx(TURN_PLAN_FLOOR * state.turn_plan_curvature, rel=1e-5)
