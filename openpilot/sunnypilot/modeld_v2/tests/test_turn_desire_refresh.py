"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np
import pytest

from openpilot.cereal import log
from openpilot.common.realtime import DT_MDL
from openpilot.sunnypilot.modeld_v2.turn_desire_refresh import (HISTORY_S, MAX_TRAVEL_M, MAX_TURNED_DEG, REFRESH_AFTER_S,
                                                                TurnDesireRefresh, desire_input)

LEFT, RIGHT, NONE = log.Desire.turnLeft, log.Desire.turnRight, log.Desire.none
LANE_CHANGE = log.Desire.laneChangeLeft


def model_pulses(desires, speeds, refresh=None, yaw_rates=None):
  """Frames on which the model gets a desire pulse, through the same rising-edge detector ModelState.run uses."""
  refresh = refresh or TurnDesireRefresh()
  yaw_rates = yaw_rates or [0.] * len(desires)
  prev = np.zeros(8, dtype=np.float32)
  pulses = []
  for i, (desire, v_ego, yaw_rate) in enumerate(zip(desires, speeds, yaw_rates, strict=True)):
    vec = desire_input(desire, 8, refresh.update(desire, v_ego, yaw_rate))
    vec[0] = 0
    if np.any(vec - prev > .99):
      pulses.append(i)
    prev = vec
  return pulses


def frames(seconds):
  return round(seconds / DT_MDL)


def test_refresh_lands_before_the_last_pulse_leaves_the_history():
  assert REFRESH_AFTER_S < HISTORY_S


@pytest.mark.parametrize("turn", [LEFT, RIGHT])
def test_held_turn_is_pulsed_again_before_the_model_forgets(turn):
  n = frames(12.)
  pulses = model_pulses([turn] * n, [3.] * n)
  assert pulses[0] == 0
  gaps = np.diff(pulses) * DT_MDL
  assert len(pulses) >= 3
  assert np.all(gaps <= HISTORY_S - 0.5)


def test_without_refresh_a_held_turn_is_pulsed_once():
  n = frames(12.)
  assert model_pulses([RIGHT] * n, [3.] * n, TurnDesireRefresh(enabled=False)) == [0]


def test_a_turn_held_through_a_red_light_is_pulsed_on_pull_away():
  # cued while rolling to the light, 20 s at the light, then away
  speeds = [2.] * frames(2.) + [0.] * frames(20.) + [1.5] * frames(3.)
  pulses = model_pulses([LEFT] * len(speeds), speeds)
  pull_away = frames(22.)
  assert pull_away in pulses or pull_away + 1 in pulses
  # and the turn never left the history while waiting
  assert np.all(np.diff(pulses) * DT_MDL <= HISTORY_S - 0.5)


def test_pull_away_right_after_a_pulse_does_not_double_pulse():
  # cued at the light, away 0.1 s after the second refresh: that pulse is fresh, so no extra one for the pull-away
  speeds = [0.] * frames(8.2) + [1.5] * frames(5.)
  pulses = model_pulses([RIGHT] * len(speeds), speeds)
  assert pulses[:3] == [0, 81, 162]
  assert pulses[3] == 243


def test_lane_change_desire_is_never_repeated():
  n = frames(12.)
  assert model_pulses([LANE_CHANGE] * n, [3.] * n) == [0]


def test_refresh_stops_once_the_car_has_gone_too_far_since_the_cue():
  v = 5.
  n = frames(30.)
  pulses = model_pulses([RIGHT] * n, [v] * n)
  last_refresh_at = pulses[-1] * DT_MDL * v
  assert last_refresh_at <= MAX_TRAVEL_M
  assert pulses[-1] * DT_MDL < 30. - HISTORY_S  # it really stopped, rather than running to the end


def test_pull_away_restarts_the_travel_budget():
  # cued 35 m before a stop: the turn comes after the light, so the budget starts again from the pull-away
  speeds = [5.] * frames(7.) + [0.] * frames(10.) + [3.] * frames(10.)
  pulses = model_pulses([RIGHT] * len(speeds), speeds)
  after_pull_away = [p for p in pulses if p > frames(17.)]
  assert len(after_pull_away) >= 2


def test_a_cue_past_its_travel_budget_is_not_revived_at_the_next_light():
  # blinker left on: 60 m down the road, then a light
  speeds = [5.] * frames(12.) + [0.] * frames(10.) + [2.] * frames(10.)
  pulses = model_pulses([RIGHT] * len(speeds), speeds)
  assert all(p * DT_MDL * 5. <= MAX_TRAVEL_M for p in pulses)
  assert not [p for p in pulses if p >= frames(12.)]


@pytest.mark.parametrize("turn,sign", [(LEFT, -1.), (RIGHT, 1.)])
def test_no_pulse_once_the_car_has_turned_most_of_the_way(turn, sign):
  # a slow 90 deg turn over 10 s (+ yaw is to the right), with the blinker still on as it straightens out
  n = frames(12.)
  yaw = [sign * np.radians(9.) if i < frames(10.) else 0. for i in range(n)]
  pulses = model_pulses([turn] * n, [2.] * n, yaw_rates=yaw)
  turned_at = [p * DT_MDL * 9. for p in pulses]
  assert len(pulses) >= 2
  assert max(turned_at) <= MAX_TURNED_DEG


def test_turning_the_other_way_does_not_use_up_the_turn():
  # a right turn cued on a left-hand bend
  n = frames(12.)
  pulses = model_pulses([RIGHT] * n, [2.] * n, yaw_rates=[-np.radians(9.)] * n)
  assert len(pulses) >= 3


def test_releasing_and_reapplying_the_turn_starts_over():
  desires = [RIGHT] * frames(3.) + [NONE] * frames(1.) + [RIGHT] * frames(3.)
  pulses = model_pulses(desires, [3.] * len(desires))
  assert pulses == [0, frames(4.)]


def test_switching_turn_direction_pulses_the_new_turn_at_once():
  desires = [LEFT] * frames(2.) + [RIGHT] * frames(2.)
  pulses = model_pulses(desires, [3.] * len(desires))
  assert pulses == [0, frames(2.)]


def test_desire_input_is_cleared_only_on_a_refresh_frame():
  assert desire_input(RIGHT, 8, False)[RIGHT] == 1
  assert not desire_input(RIGHT, 8, True).any()
  assert not desire_input(NONE, 8, False)[1:].any()
