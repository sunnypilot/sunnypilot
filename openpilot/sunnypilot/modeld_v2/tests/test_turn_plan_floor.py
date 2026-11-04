"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pytest

from openpilot.sunnypilot.modeld_v2.turn_plan_floor import TURN_PLAN_FLOOR, apply_turn_plan_floor

RIGHT, LEFT, NONE = 1., -1., 0.


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
