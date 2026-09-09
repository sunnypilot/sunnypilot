"""Model geometry contract, independent of any PSCM response model."""
from types import SimpleNamespace

import numpy as np
import pytest

from openpilot.selfdrive.controls.lib.ford_model_action import encode_model_action


def model_points(t, x, y, heading):
  return SimpleNamespace(position=SimpleNamespace(t=t, x=x, y=y), orientation=SimpleNamespace(t=t, z=heading))


def test_both_fields_sample_the_same_model_time_without_constant_speed_assumption():
  # Accelerating plan: one second is 12 m along this straight inclined path.
  s = np.array([0., 4., 12., 30.])
  heading = .1
  m = model_points([0., .5, 1., 2.], s*np.cos(heading), .3+s*np.sin(heading), np.full(4, heading))
  out = encode_model_action(m, -.01, 20.)
  assert out.path_offset == pytest.approx(.3+12*np.sin(heading))
  assert out.path_angle == pytest.approx(.1)
  assert out.curvature == out.curvature_rate == 0.
  assert encode_model_action(m, .01, 30.) == out


def test_low_speed_floor_uses_one_shared_seven_metre_station():
  m = model_points([0., 1., 2.], [0., 3., 9.], [0., 0., 0.], [0., .03, .09])
  out = encode_model_action(m, .01, 3.)
  assert out.path_offset == 0.
  assert out.path_angle == pytest.approx(.07)


def test_short_plan_holds_both_endpoint_values_without_extrapolation():
  m = model_points([0., .5], [0., 2.], [0., .4], [0., .2])
  out = encode_model_action(m, -.01, 20.)
  assert out.path_offset == .4
  assert out.path_angle == pytest.approx(.2)


@pytest.mark.parametrize('times', [[], [0.], [0., 0., 1.], [0., 1., .5], [0., float('nan'), 1.], [.1, .5, 1.]])
def test_invalid_model_clock_cannot_publish_an_active_path(times):
  m = model_points(times, [0., 10., 20.], [0., .1, .4], [0., .02, .04])
  assert not encode_model_action(m, .01, 20.).valid


def test_orientation_and_position_must_describe_the_same_times():
  m = model_points([0., .5, 1.], [0., 10., 20.], [0., .1, .4], [0., .02, .04])
  m.orientation.t = [0., .6, 1.]
  assert not encode_model_action(m, .01, 20.).valid


def test_model_heading_unwraps_before_interpolation():
  m = model_points([0., .5, 1.5], [0., 10., 30.], [0., 0., 0.], [3., 3.1, -3.1])
  assert encode_model_action(m, 0., 20.).path_angle == pytest.approx(np.pi)
