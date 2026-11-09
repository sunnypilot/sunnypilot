import pytest

from openpilot.sunnypilot.modeld_v2 import turn_correction as tc

C = tc.TurnCorrection('test', v_full=6., v_end=10., theta_path=0.1, theta_time=0.8)


def test_no_change_at_road_speed_and_full_below_v_full():
  assert tc.apply_turn_correction(C, 0.05, 0.10, 0.12, 12.) == 0.05
  full = tc.apply_turn_correction(C, 0.05, 0.10, 0.12, 3.)
  assert full == pytest.approx(0.05 + 0.1 * 0.07 + 0.8 * 0.05)
  half = tc.apply_turn_correction(C, 0.05, 0.10, 0.12, 8.)
  assert half == pytest.approx(0.05 + 0.5 * (full - 0.05))


def test_it_stays_within_the_models_own_range():
  # the plan's time axis says far more than both the action and the line at the car's speed: bounded at path + 10%
  assert tc.apply_turn_correction(C, 0.10, 0.40, 0.14, 3.) == pytest.approx(0.14 + 0.1 * 0.04)
  # a turn the action and the line both say is straight is not invented from the time axis
  assert tc.apply_turn_correction(C, 0.0, 0.2, 0.0, 3.) == 0.0
  # nor reversed: action and line right, the time axis left
  assert tc.apply_turn_correction(C, 0.1, -0.2, 0.1, 3.) == pytest.approx(0.1)


def test_it_can_lower_an_overcommitted_action_toward_the_line():
  lower = tc.TurnCorrection('test', 4.5, 7., theta_path=0.9, theta_time=0.)
  assert tc.apply_turn_correction(lower, -0.21, -0.21, -0.14, 3.) == pytest.approx(-0.21 + 0.9 * 0.07)


def test_lookup_by_ref_and_local_prefix(monkeypatch):
  monkeypatch.setattr(tc, 'CORRECTIONS', {'abc': C, 'local-ff_turns_600-': C})
  assert tc.correction_for('abc') is C
  assert tc.correction_for('local-ff_turns_600-0123456789abcdef') is C
  assert tc.correction_for('local-other-0123') is None
  assert tc.correction_for('') is None
