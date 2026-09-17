"""Explicit PI experiment semantics; no simulated PSCM response."""
import math

import pytest

from openpilot.selfdrive.controls.lib.ford_model_action import FordModelActionController, ModelActionController
from openpilot.selfdrive.controls.lib.ford_path import FordPath
from openpilot.selfdrive.controls.tests.test_ford_model_action import straight


@pytest.mark.parametrize('gain', [.1, .25, .5, .75])
@pytest.mark.parametrize('sign', [-1., 1.])
def test_p_responds_without_waiting_for_integral_and_disappears_at_catchup(gain, sign):
  controller = ModelActionController(proportional_gain=gain)
  controller.c1 = sign*.2
  out = controller.update(straight(), sign*.01, current_curvature=sign*.009,
                          speed=20., dt=.1, feedback_dt=0.)
  assert .5*gain*.02 < sign*controller.proportional < gain*.02
  assert controller.correction == 0.
  assert out.path_angle == pytest.approx(sign*.2+controller.proportional, abs=.00025)
  out = controller.update(straight(), sign*.01, current_curvature=sign*.01, speed=20., dt=.1)
  assert controller.proportional == controller.correction == 0.
  assert out.path_angle == pytest.approx(sign*.2)


@pytest.mark.parametrize('sign', [-1., 1.])
def test_aligned_feedback_does_not_replace_current_feedforward_or_path(sign):
  controller = ModelActionController(proportional_gain=.25)
  controller.c0, controller.c1 = sign*.4, sign*.2
  out = controller.update(straight(sign*.4), sign*.01, current_curvature=sign*.008,
                          feedback_curvature=sign*.008, speed=20., dt=.1)
  assert controller.proportional == controller.correction == 0.
  assert out.path_offset == pytest.approx(sign*(1-math.cos(.07))/.01, abs=.005)
  assert out.path_angle == pytest.approx(sign*.2)
  # Latest request is ahead of measured steering, but the delay-aligned target
  # has already been exceeded. P and I must use the explicit feedback target.
  out = controller.update(straight(sign*.4), sign*.01, current_curvature=sign*.008,
                          feedback_curvature=sign*.006, speed=20., dt=.1)
  assert .005 < -sign*controller.proportional < .01
  assert sign*controller.correction < 0.
  assert sign*out.path_angle < .2


@pytest.mark.parametrize('sign', [-1., 1.])
@pytest.mark.parametrize('gain', [.5, .75])
def test_pi_combined_request_obeys_amplitude_and_does_not_wind_up_behind_p(sign, gain):
  controller = ModelActionController(proportional_gain=gain)
  for _ in range(200):
    out = controller.update(straight(), sign*.01, current_curvature=-sign*.1, speed=20., dt=.01)
    assert controller.c1 == pytest.approx(sign*.5)
    assert abs(out.path_angle) <= .50000001
    assert controller.correction == 0.  # Feedforward + P alone exceeds the cap.
  assert out.path_angle == pytest.approx(sign*.5)
  for _ in range(60):
    out = controller.update(straight(), sign*.01, current_curvature=sign*.01, speed=20., dt=.01)
  assert out.path_angle == pytest.approx(sign*.2)
  assert controller.correction == controller.proportional == 0.


@pytest.mark.parametrize('gain', [-.1, math.nan, math.inf, None, 'bad'])
def test_invalid_gain_is_rejected(gain):
  with pytest.raises(ValueError):
    ModelActionController(proportional_gain=gain)


@pytest.mark.parametrize('feedback', [math.nan, math.inf, 'bad', 1.001])
def test_invalid_feedback_target_clears_all_output(feedback):
  controller = ModelActionController(proportional_gain=.25)
  controller.c1, controller.correction = .2, .01
  out = controller.update(straight(), .01, current_curvature=.008, feedback_curvature=feedback, speed=20., dt=.01)
  assert out == FordPath()
  assert controller.proportional == controller.correction == controller.c1 == 0.


def test_overflowing_p_cannot_escape_as_an_active_command():
  controller = ModelActionController(proportional_gain=1e308)
  out = controller.update(straight(), 1., current_curvature=-1., speed=55., dt=.01)
  assert out == FordPath()


@pytest.mark.parametrize('limited', [False, True])
def test_driver_override_clears_both_p_and_i(limited):
  controller = ModelActionController(proportional_gain=.25)
  controller.c1, controller.correction = .2, .01
  controller.update(straight(), .01, current_curvature=.008, speed=20., dt=.01,
                    feedback_enabled=False, pscm_limited=limited)
  assert controller.proportional == controller.correction == 0.


def test_adapter_logs_separate_feedforward_p_i_and_explicit_feedback_target():
  controller = FordModelActionController(proportional_gain=.25)
  for i in range(30):
    now = 1.+i*.01
    controller.update(straight(), .004, current_curvature=.002, feedback_curvature=.003,
                      speed=20., yaw_rate=0., now=now, measurement_time=now, model_time=now,
                      reference_time=now, active=True)
  d = controller.diagnostics
  assert d['heading_feedforward'] == pytest.approx(.08)
  assert .0025 < d['heading_proportional'] < .005
  assert d['proportional_gain'] == .25 and d['feedback_curvature'] == .003
  assert d['heading_correction'] > 0.
  assert d['heading_request'] == pytest.approx(d['heading_feedforward']+d['heading_proportional']+d['heading_correction'])
