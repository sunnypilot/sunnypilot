import numpy as np
import pytest

from openpilot.sunnypilot.modeld_v2 import path_steering as ps

T = np.linspace(0., 10., 33) ** 2 / 10.  # like ModelConstants.T_IDXS: dense near 0


def arc_plan(curvature_at, speed_at):
  """A plan driven at speed_at(t) along a path whose curvature at arc length s is curvature_at(s)."""
  t = np.linspace(0., 10., 4001)
  v = speed_at(t)
  s = np.concatenate([[0.], np.cumsum((v[1:] + v[:-1]) / 2 * np.diff(t))])
  yaw = np.concatenate([[0.], np.cumsum((curvature_at(s[1:]) + curvature_at(s[:-1])) / 2 * np.diff(s))])
  x = np.concatenate([[0.], np.cumsum(np.cos(yaw[1:]) * np.diff(s))])
  y = np.concatenate([[0.], np.cumsum(np.sin(yaw[1:]) * np.diff(s))])
  return (np.interp(T, t, x), np.interp(T, t, y), np.interp(T, t, yaw), float(curvature_at(np.array([0.]))[0] * v[0]))


def test_straight_plan_steers_straight():
  x, y, yaw, rate = arc_plan(lambda s: np.zeros_like(s), lambda t: np.full_like(t, 3.))
  assert ps.path_curvature(x, y, yaw, rate, 3., 0., 0.55) == pytest.approx(0., abs=1e-6)


def test_a_steady_arc_gives_its_curvature_at_any_speed():
  for v_car in (1.5, 3., 6.):
    x, y, yaw, rate = arc_plan(lambda s: np.full_like(s, 0.1), lambda t: np.full_like(t, 4.))
    assert ps.path_curvature(x, y, yaw, 0.1 * v_car, v_car, 0., 0.55) == pytest.approx(0.1, rel=0.03)


def test_a_car_slower_than_the_plan_turns_in_less_on_a_tightening_entry():
  # entering a corner: curvature builds 0.03 1/m per metre; the plan pulls through it at 4 m/s, the car crawls at 2
  entry = lambda s: np.minimum(0.03 * s, 0.15)  # noqa: E731
  x, y, yaw, rate = arc_plan(entry, lambda t: np.full_like(t, 4.))
  from openpilot.selfdrive.controls.lib.drive_helpers import get_curvature_from_plan
  time_based = get_curvature_from_plan(yaw, np.full_like(T, rate), T, 2., 0.55)
  path_based = ps.path_curvature(x, y, yaw, rate, 2., 0., 0.55)
  assert 0. < path_based < 0.75 * time_based


def test_short_distances_are_floored():
  x, y, yaw, rate = arc_plan(lambda s: np.full_like(s, 0.1), lambda t: np.full_like(t, 2.))
  near_stop = ps.path_curvature(x, y, yaw, 0., 0.05, 0., 0.55)
  assert np.isfinite(near_stop) and abs(near_stop) < 0.3


def test_weight_is_full_when_slow_and_gone_by_the_blend_end():
  assert ps.path_weight(0.) == ps.path_weight(ps.FULL_SPEED) == 1.
  assert ps.path_weight(ps.BLEND_END) == ps.path_weight(20.) == 0.
  assert 0. < ps.path_weight((ps.FULL_SPEED + ps.BLEND_END) / 2) < 1.
  assert ps.apply_path_steering(0.2, 0.14, 3.) == pytest.approx(0.14)
  assert ps.apply_path_steering(0.2, 0.14, 10.) == pytest.approx(0.2)
