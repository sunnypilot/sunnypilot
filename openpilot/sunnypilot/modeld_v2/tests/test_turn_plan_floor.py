"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pytest

from openpilot.sunnypilot.modeld_v2.turn_plan_floor import TURN_PLAN_FLOOR_BP, TURN_PLAN_FLOOR_V, TURN_STATE_BP, apply_turn_plan_floor, \
  turn_plan_floor_scale, turn_state_gate

RIGHT, LEFT, NONE = 1., -1., 0.
LOW_SPEED_SCALE = TURN_PLAN_FLOOR_V[0]


def test_no_turn_leaves_action_alone():
  assert apply_turn_plan_floor(0.01, 0.2, NONE, LOW_SPEED_SCALE) == 0.01


@pytest.mark.parametrize("sign", [RIGHT, LEFT])
def test_weak_action_is_raised_to_scaled_plan(sign):
  # curvature is + to the right, so a left turn is negative
  assert apply_turn_plan_floor(sign * 0.03, sign * 0.10, sign, LOW_SPEED_SCALE) == pytest.approx(sign * LOW_SPEED_SCALE * 0.10)


@pytest.mark.parametrize("sign", [RIGHT, LEFT])
def test_strong_action_is_kept(sign):
  assert apply_turn_plan_floor(sign * 0.12, sign * 0.10, sign, LOW_SPEED_SCALE) == sign * 0.12


@pytest.mark.parametrize("sign", [RIGHT, LEFT])
def test_plan_against_the_turn_never_weakens_or_reverses(sign):
  assert apply_turn_plan_floor(sign * 0.05, -sign * 0.10, sign, LOW_SPEED_SCALE) == sign * 0.05


def test_floor_only_pushes_toward_the_requested_side():
  # a right-turn request must never add left curvature, even if action and plan both point left
  assert apply_turn_plan_floor(-0.02, -0.10, RIGHT, LOW_SPEED_SCALE) == -0.02


@pytest.mark.parametrize("sign", [RIGHT, LEFT])
def test_stale_turn_never_weakens_a_steer_the_plan_also_wants(sign):
  # a right turn still requested while plan and action both steer left (exit or a right straight into a left)
  assert apply_turn_plan_floor(-sign * 0.12, -sign * 0.10, sign, LOW_SPEED_SCALE) == -sign * 0.12


@pytest.mark.parametrize("sign", [RIGHT, LEFT])
def test_zero_scale_is_off_even_for_a_counter_steer(sign):
  # above the fade-out speed the action head steers alone, including small corrections against the turn
  assert apply_turn_plan_floor(-sign * 0.01, sign * 0.10, sign, 0.) == -sign * 0.01


def test_scale_is_full_at_low_speed_and_fades_out():
  low, high = TURN_PLAN_FLOOR_BP
  assert turn_plan_floor_scale(0.) == LOW_SPEED_SCALE
  assert turn_plan_floor_scale(low) == LOW_SPEED_SCALE
  assert turn_plan_floor_scale((low + high) / 2) == pytest.approx(LOW_SPEED_SCALE / 2)
  assert turn_plan_floor_scale(high) == 0.
  assert turn_plan_floor_scale(30.) == 0.


def _run_action(turn_sign, v_ego=2., k=0.1, action_share=0.5, turn_state=None):
  # a right turn the plan holds at curvature k while the action head asks for only part of it
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
  assert action.desiredCurvature == pytest.approx(LOW_SPEED_SCALE * state.turn_plan_curvature, rel=1e-5)


def test_no_turn_logs_no_plan_curvature():
  state, action = _run_action(NONE)
  assert state.turn_plan_curvature == 0.
  assert action.desiredCurvature == pytest.approx(state.action_curvature)


def test_turn_state_gate_is_off_below_and_full_above():
  low, high = TURN_STATE_BP
  assert turn_state_gate(0.) == 0.
  assert turn_state_gate(low) == 0.
  assert turn_state_gate((low + high) / 2) == pytest.approx(0.5)
  assert turn_state_gate(high) == 1.
  assert turn_state_gate(1.) == 1.


@pytest.mark.parametrize("sign", [RIGHT, LEFT])
def test_model_sure_of_the_turn_keeps_the_full_floor(sign):
  state, action = _run_action(sign, k=sign * 0.1, turn_state=0.95)
  assert action.desiredCurvature == pytest.approx(LOW_SPEED_SCALE * state.turn_plan_curvature, rel=1e-5)


@pytest.mark.parametrize("sign", [RIGHT, LEFT])
def test_model_that_lost_the_turn_leaves_the_action_alone(sign):
  # pulling away after a wait at a stop: the model's turn state has faded, so the action head steers
  state, action = _run_action(sign, k=sign * 0.1, turn_state=0.3)
  assert action.desiredCurvature == pytest.approx(state.action_curvature)


def test_half_sure_model_gets_a_partial_floor():
  low, high = TURN_STATE_BP
  state, action = _run_action(RIGHT, action_share=0.2, turn_state=(low + high) / 2)
  assert state.action_curvature < 0.5 * LOW_SPEED_SCALE * state.turn_plan_curvature  # so the half floor is what steers
  assert action.desiredCurvature == pytest.approx(0.5 * LOW_SPEED_SCALE * state.turn_plan_curvature, rel=1e-5)
