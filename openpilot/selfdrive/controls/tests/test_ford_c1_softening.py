"""C1 small-error command properties; no simulated wheel response."""
import numpy as np
import pytest

from openpilot.selfdrive.controls.lib.ford_model_action import ModelActionController
from openpilot.selfdrive.controls.tests.test_ford_model_action import straight


def correction_for_error(core, error, **overrides):
  core.update(straight(), 0., current_curvature=-error, speed=10., dt=.01, feedback_dt=0., **overrides)
  return core.proportional


@pytest.mark.parametrize('sign', [-1., 1.])
@pytest.mark.parametrize('c0_gain', [0., .5, 1.])
def test_small_c1_correction_has_half_slope_without_a_deadband(sign, c0_gain):
  core = ModelActionController(c0_proportional_gain=c0_gain)
  for magnitude in (1e-10, 1e-7, 1e-5):
    p = sign*correction_for_error(core, sign*magnitude)
    linear = .75*10.*magnitude
    assert .4999*linear <= p <= .501*linear
  assert correction_for_error(core, 0.) == 0.


@pytest.mark.parametrize('sign', [-1., 1.])
def test_large_c1_correction_keeps_strength_and_releases_in_the_same_cycle(sign):
  core = ModelActionController()
  for magnitude in (.05, .1):
    p = sign*correction_for_error(core, sign*magnitude)
    linear = .75*10.*magnitude
    assert .97*linear <= p < linear
  assert sign*correction_for_error(core, -sign*.001) < 0.
  assert correction_for_error(core, 0.) == core.correction == core.c1 == 0.


def test_c1_error_shaping_is_symmetric_monotonic_and_cannot_amplify_p():
  core = ModelActionController()
  errors = np.linspace(-.02, .02, 1001)
  values = np.array([correction_for_error(core, error) for error in errors])
  linear = .75*10.*errors
  slopes = np.diff(values)/np.diff(linear)
  assert .499999 <= slopes.min() < .501
  assert slopes.max() <= 1.000001
  np.testing.assert_allclose(values, -values[::-1], atol=1e-12)
  assert np.all(abs(values) <= abs(linear)+1e-12)


@pytest.mark.parametrize('direct_path', [False, True])
def test_c1_gain_does_not_change_c0_or_the_base_when_feedback_is_disabled(direct_path):
  core = ModelActionController()
  without_c1_p = ModelActionController(proportional_gain=0.)
  for error in (-.03, -.001, 0., .001, .03):
    for enabled in (True, False):
      args = {'current_curvature': .01-error, 'speed': 10., 'dt': .01, 'feedback_dt': 0.,
              'feedback_enabled': enabled, 'direct_path': direct_path}
      a, b = [c.update(straight(), .01, **args) for c in (core, without_c1_p)]
      assert a.path_offset == b.path_offset
      assert core.offset_proportional == without_c1_p.offset_proportional
      assert a.curvature == a.curvature_rate == 0.
      if not enabled or error == 0.:
        assert a == b
        assert core.proportional == core.correction == 0.


def test_direct_path_trial_keeps_linear_c1_feedback():
  core = ModelActionController()
  for error in (-.03, -.001, 0., .001, .03):
    assert correction_for_error(core, error, direct_path=True) == pytest.approx(.75*10.*error)
