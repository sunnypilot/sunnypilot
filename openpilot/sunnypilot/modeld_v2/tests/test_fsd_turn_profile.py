import numpy as np
import pytest

from openpilot.sunnypilot.modeld_v2 import fsd_turn_profile as ftp

T = np.linspace(0., 10., 33) ** 2 / 10.  # like ModelConstants.T_IDXS
DT = 0.05
RIGHT_90 = float(np.radians(90.))


def corner_plan(distance_to_corner, turn, v):
  """A plan driving straight distance_to_corner metres, then turning `turn` rad over an arc of radius 8 m."""
  s = v * T
  radius = 8.
  arc = abs(turn) * radius
  yaw = np.sign(turn) * np.clip((s - distance_to_corner) / radius, 0., abs(turn))
  x = np.concatenate([[0.], np.cumsum(np.cos(yaw[1:]) * np.diff(s))])
  y = np.concatenate([[0.], np.cumsum(np.sin(yaw[1:]) * np.diff(s))])
  return x, y, yaw, arc


def drive(turn=RIGHT_90, v=5., start=40., cue=1., steps=400, action=None):
  """Toy closed loop: the car takes each command 0.55 s later (the lead the controller looks ahead by), the plan shows
  the corner where it still is, and the model's action steers what the turn still needs over the next 8 m."""
  controller = ftp.FsdTurnProfile()
  heading, travelled = 0., 0.
  commands, delay = [], round(0.55 / DT)
  for _ in range(steps):
    remaining = turn - heading
    x, y, yaw, _ = corner_plan(max(start - travelled, 0.), remaining, v)
    model = action if action is not None else (float(np.clip(remaining / 8., -0.2, 0.2)) if travelled > start - 5. else 0.)
    applied = commands[-delay] if len(commands) >= delay else 0.
    commands.append(controller.update(x, y, yaw, applied * v, v, DT, model, cue))
    heading += applied * v * DT
    travelled += v * DT
  return np.asarray(commands), heading, controller


def test_a_cued_right_turn_follows_the_speed_rule_and_completes():
  commands, heading, controller = drive()
  assert np.max(commands) == pytest.approx(ftp.rule_peak(5.), rel=0.1)
  assert np.degrees(heading) == pytest.approx(90., abs=8.)
  assert not controller.active and abs(commands[-1]) < 0.01


def test_left_turns_mirror_right_turns():
  right, _, _ = drive(turn=np.radians(90.), cue=1.)
  left, _, _ = drive(turn=np.radians(-90.), cue=-1.)
  assert np.allclose(left, -right, atol=1e-6)


def test_no_cue_needs_a_bigger_turn():
  commands, _, controller = drive(turn=np.radians(50.), cue=0., action=0.)
  assert np.max(np.abs(commands)) == 0.
  commands, _, _ = drive(turn=np.radians(90.), cue=0.)
  assert np.max(commands) > 0.05


def test_road_speed_is_left_to_the_model():
  commands, _, _ = drive(v=12., action=0.01)
  assert np.allclose(commands, 0.01)


def test_a_turn_the_plan_stops_showing_is_dropped_back_to_the_action():
  controller = ftp.FsdTurnProfile()
  x, y, yaw, _ = corner_plan(30., np.radians(90.), 5.)
  for _ in range(20):
    controller.update(x, y, yaw, 0., 5., DT, 0.02, 1.)
  assert controller.active
  straight = (5. * T, np.zeros_like(T), np.zeros_like(T))
  for _ in range(40):
    command = controller.update(*straight, 0., 5., DT, 0.02, 1.)
  assert not controller.active and command == pytest.approx(0.02, abs=1e-3)


def test_the_peak_rule_holds_lateral_accel_past_its_speeds():
  assert ftp.rule_peak(1.) == ftp.rule_peak(3.)
  assert ftp.rule_peak(10.) * 10. ** 2 == pytest.approx(ftp.rule_peak(8.) * 8. ** 2)
  assert ftp.rule_peak(3.) == pytest.approx(ftp.PEAK_SCALE * (0.190 - 0.018 * 3.))


def test_pulling_away_from_a_stop_winds_in_before_the_car_is_moving():
  controller = ftp.FsdTurnProfile()
  x, y, yaw, _ = corner_plan(4., np.radians(90.), 3.)
  command = 0.
  for _ in range(40):  # stopped 4 m from the corner with the turn cued
    command = controller.update(x, y, yaw, 0., 0.2, DT, 0., 1.)
  assert command > 0.03
