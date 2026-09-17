"""C0 trial command properties; these tests do not simulate PSCM stability."""
import math

import numpy as np
import pytest

from openpilot.selfdrive.controls.lib.ford_model_action import (
  C0_RESPONSE_CONSTANT, C0_RESPONSE_INVERSE_SPEED_SQUARED, ModelActionController,
)
from openpilot.selfdrive.controls.tests.test_ford_model_action import straight


def correction_for_linear_request(controller, request, **overrides):
  # Choose a curvature mismatch which previously produced `request` metres of P.
  response = C0_RESPONSE_CONSTANT+C0_RESPONSE_INVERSE_SPEED_SQUARED/100.
  controller.update(straight(), 0., current_curvature=-request*response, speed=10., dt=.01, feedback_dt=0., **overrides)
  return controller.offset_proportional


@pytest.mark.parametrize('sign', [-1., 1.])
def test_small_c0_correction_is_gentler_but_has_no_deadband(sign):
  core = ModelActionController()
  for magnitude in [1e-9, .001, .01]:
    correction = correction_for_linear_request(core, sign*magnitude)
    assert .4999*magnitude <= sign*correction <= .501*magnitude
  assert correction_for_linear_request(core, 0.) == 0.


@pytest.mark.parametrize('sign', [-1., 1.])
def test_large_entry_and_release_corrections_keep_strength(sign):
  core = ModelActionController()
  for magnitude in [1., 2., 5.]:
    correction = correction_for_linear_request(core, sign*magnitude)
    assert 0. < magnitude-sign*correction <= .125000001
    if magnitude >= 2.:
      assert sign*correction >= .9375*magnitude
  # No filter history or threshold state delays a reversal or a release.
  correction_for_linear_request(core, sign*2.)
  assert correction_for_linear_request(core, -sign*.01)*sign < 0.
  assert correction_for_linear_request(core, 0.) == 0.


def test_softening_never_adds_a_transition_with_higher_incremental_gain():
  core = ModelActionController()
  inputs = np.linspace(-2., 2., 2001)
  values = np.array([correction_for_linear_request(core, value) for value in inputs])
  slopes = np.diff(values)/np.diff(inputs)
  assert .499999 <= slopes.min() < .501
  assert slopes.max() <= 1.000001
  np.testing.assert_allclose(values, -values[::-1], atol=1e-12)
  assert np.all(abs(values) <= abs(inputs)+1e-12)


def test_shaping_c0_does_not_change_c1_or_integration():
  core = ModelActionController()
  without_c0 = ModelActionController(c0_proportional_gain=0.)
  model = straight()
  for i in range(600):
    desired = .04*math.sin(i*.017)
    args = {'current_curvature': .025*math.sin((i-16)*.017), 'speed': 10., 'dt': .01,
            'feedback_enabled': i % 29 != 0, 'pscm_limited': i % 17 == 0}
    first, second = [c.update(model, desired, **args) for c in (core, without_c0)]
    assert first.path_angle == second.path_angle
    assert core.correction == without_c0.correction
    assert core.proportional == without_c0.proportional
    assert first.curvature == first.curvature_rate == 0.


@pytest.mark.parametrize('direct_path', [False, True])
def test_softening_does_not_modify_the_base_or_override_behavior(direct_path):
  core = ModelActionController()
  without_c0 = ModelActionController(c0_proportional_gain=0.)
  for feedback_enabled, desired, measured in [(True, .01, .01), (False, .01, 0.), (True, 0., 0.)]:
    args = {'current_curvature': measured, 'speed': 10., 'dt': .01,
            'feedback_enabled': feedback_enabled, 'direct_path': direct_path}
    assert core.update(straight(), desired, **args) == without_c0.update(straight(), desired, **args)
    assert core.offset_proportional == 0.


def test_direct_path_trial_keeps_its_existing_linear_feedback():
  core = ModelActionController()
  for request in [-2., -.01, 0., .01, 2.]:
    assert correction_for_linear_request(core, request, direct_path=True) == pytest.approx(request)
