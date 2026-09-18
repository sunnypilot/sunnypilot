"""Causal target preview: numerical scoring and the real Ford transmit boundary."""
import copy
import math

import numpy as np
import pytest

from openpilot.selfdrive.car.tests.test_ford_joint_control import Pipeline
from openpilot.selfdrive.controls.lib.ford_joint.encoder import PairedRelease, parameters, state
from openpilot.selfdrive.controls.lib.ford_joint.inverse import static_pair, quantize
from openpilot.selfdrive.controls.lib.ford_joint.model import MainRequest


@pytest.mark.parametrize('speed', [18., 36., 90.])
@pytest.mark.parametrize('phase', range(10))
def test_preview_score_matches_explicit_forward_recurrence(speed, phase):
  m = MainRequest(native_lookup=True)
  m.c0, m.c1, m.filtered = .7, -.03, -.001
  curvature, rate, preview = .002, .015, .1
  bound = 3 / (speed / 3.6)**2
  encoder = PairedRelease(m)
  _, baseline = encoder.choose(speed, curvature, phase)
  pair, info = encoder.choose(speed, curvature, phase, curvature_rate=rate, preview=preview, curvature_bound=bound)
  p = parameters(m, speed)
  targets, prefs = [], []
  n = math.ceil(preview / .008)
  for j in range(n + 1):
    k = min(bound, max(-bound, curvature + rate * min(j * .008, preview)))
    pref = quantize(static_pair(m, k, speed, gains=(p[0], p[1])))
    prefs.append(pref)
    targets.append(p[0] * pref[0] + p[1] * pref[1])
  model, cost = copy.copy(m), 0.
  for j in range(1600):
    command = pair if j < info['count'] else prefs[min(j + 1, n)]
    model.step(speed, *command, freeze_i=True)
    cost += .008 * ((model.filtered - targets[min(j + 1, n)]) / .01)**2
    if j + 1 == info['count']:
      np.testing.assert_allclose(state(model), info['first_state'], atol=1e-14, rtol=0)
  assert info['cost'] == pytest.approx(cost, abs=2e-10, rel=2e-12)
  assert abs(info['first_state'][3] - baseline['planned_target']) <= baseline['immediate_error_bound'] + 1.1e-12


@pytest.mark.parametrize('curvature_rate,preview', [(0., .1), (.02, 0.)])
def test_constant_or_disabled_preview_preserves_ordinary_encoder(curvature_rate, preview):
  m = MainRequest(native_lookup=True)
  m.c0, m.c1, m.filtered = -1., .1, .004
  encoder = PairedRelease(m)
  expected, before = encoder.choose(36., .01)
  actual, after = encoder.choose(36., .01, curvature_rate=curvature_rate, preview=preview, curvature_bound=.03)
  assert actual == expected and after['cost'] == before['cost']
  np.testing.assert_array_equal(after['first_state'], before['first_state'])


@pytest.mark.parametrize('kwargs', [
  {'curvature_rate': math.nan}, {'preview': -.1}, {'preview': .16},
  {'preview': .1, 'curvature_bound': 0.}, {'preview': .1, 'curvature_bound': math.inf},
])
def test_invalid_forecast_is_rejected(kwargs):
  with pytest.raises(ValueError):
    PairedRelease(MainRequest(native_lookup=True)).choose(36., .002, **kwargs)


def test_target_trend_enters_real_adapter_without_changing_requested_angle():
  p = Pipeline()
  for i in range(81):
    p.tick(1. + i * .01, i * .5)
  d = p.joint.diagnostics
  assert d['requested_angle'] == 40.
  assert d['trimmed_angle'] == 40. + d['angle_trim']
  assert d['target_preview_seconds'] == .1
  assert 4.9 < d['target_preview_delta'] < 5.1
  assert d['wheel_rate'] == 0.
  p.tick(1.81, 40., active=False)
  p.tick(1.82, -40.)
  assert p.joint.diagnostics['target_preview_delta'] == 0.
