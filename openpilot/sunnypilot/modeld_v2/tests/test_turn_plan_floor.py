"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pytest

from openpilot.sunnypilot.modeld_v2.turn_plan_floor import TURN_PLAN_FLOOR_BP, TURN_PLAN_FLOOR_V, apply_turn_plan_floor, \
  turn_plan_floor_scale

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
