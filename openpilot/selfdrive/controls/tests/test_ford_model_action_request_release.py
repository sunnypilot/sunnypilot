"""Changed requests should not wait for obsolete C1 correction to integrate away.

These exercise command delay, not a simulated PSCM or predicted wheel angle.
"""
import pytest

from openpilot.selfdrive.controls.lib.ford_model_action import FordModelActionController, ModelActionController
from openpilot.selfdrive.controls.tests.test_ford_model_action import straight


@pytest.mark.parametrize('sign', [-1., 1.])
@pytest.mark.parametrize('unwind', [False, True])
def test_changed_request_retires_opposing_correction_within_output_slew(sign, unwind):
  controller = ModelActionController()
  desired = sign*.035
  model = straight(sign*.4)
  for _ in range(100):
    controller.update(model, desired, current_curvature=desired, speed=4., dt=.01)
  # Build old unwind (or turn-in) correction while retaining the same request.
  old_error = sign*(.01 if unwind else -.01)
  for _ in range(50):
    controller.update(model, desired, current_curvature=desired-old_error, speed=4., dt=.01)
  assert controller.correction == pytest.approx(old_error*2.)
  # The model now moves in the opposite direction to the stored correction.
  # Actual steering is on the other side of the new target: the old correction
  # is delaying exactly the response now needed. Both remain in the same turn.
  changed = desired-old_error
  before = controller.c1
  for _ in range(20):
    out = controller.update(model, changed, current_curvature=desired, speed=4., dt=.01)
  assert abs(controller.c1-before) <= .100000001
  assert out.path_offset == pytest.approx(sign*.4)
  assert (out.path_angle-7.*changed)*old_error <= 1e-10, 'Old correction still opposes the changed model request'


@pytest.mark.parametrize('sign', [-1., 1.])
@pytest.mark.parametrize('case', ['unchanged', 'matched', 'still_short', 'helpful', 'small_error', 'small_change', 'speed_only', 'clipped_base'])
def test_request_release_preserves_correction_without_confirming_evidence(sign, case):
  controller = ModelActionController()
  previous, desired, measured, correction, speed = .035, .025, .035, .02, 4.
  if case == 'unchanged':
    desired = previous
    measured = .05
  elif case == 'matched':
    measured = desired
  elif case == 'still_short':
    measured = .015
  elif case == 'helpful':
    correction = -.02
  elif case == 'small_error':
    measured = desired+.00001
  elif case == 'small_change':
    desired, measured = previous-.00001, .05
  elif case == 'speed_only':
    desired, measured, speed = previous, .05, 10.
  elif case == 'clipped_base':
    previous, desired, measured = .1, .09, .11
  controller.c0, controller.c1, controller.correction = sign*.4, sign*.2, sign*correction
  controller.last_feedback_desired = sign*previous
  controller.update(straight(sign*.4), sign*desired, current_curvature=sign*measured, speed=speed, dt=.01)
  assert controller.request_release == 0.
  assert abs(controller.correction-sign*correction) <= abs(desired-measured)*speed*.01+1e-10


@pytest.mark.parametrize('sign', [-1., 1.])
def test_small_request_change_cannot_erase_the_entire_correction(sign):
  controller = ModelActionController()
  controller.c0, controller.c1, controller.correction = sign*.4, sign*.265, sign*.02
  controller.last_feedback_desired = sign*.035
  controller.update(straight(sign*.4), sign*.034, current_curvature=sign*.05, speed=4., dt=.01)
  assert sign*controller.correction > .01  # Most of the original 0.02 rad must survive.
  assert 0. < -sign*controller.request_release <= .0070000001


@pytest.mark.parametrize('sign', [-1., 1.])
def test_small_target_and_measurement_noise_cannot_erase_steady_correction(sign):
  controller = ModelActionController()
  controller.c0, controller.c1, controller.correction = sign*.4, sign*.265, sign*.02
  controller.last_feedback_desired = sign*.035
  for i in range(1000):
    desired = sign*(.035+(.00001 if i % 2 else -.00001))
    measured = sign*.035
    controller.update(straight(sign*.4), desired, current_curvature=measured, speed=4., dt=.01)
    assert controller.request_release == 0.
  assert controller.correction == pytest.approx(sign*.02)


@pytest.mark.parametrize('sign', [-1., 1.])
@pytest.mark.parametrize('limited', [False, True])
def test_retiring_correction_at_pscm_limit_never_builds_extra_turn_demand(sign, limited):
  controller = ModelActionController()
  controller.c0, controller.c1, controller.correction = sign*.4, sign*.225, -sign*.02
  controller.last_feedback_desired = sign*.035
  controller.update(straight(sign*.4), sign*.045, current_curvature=sign*.035, speed=4., dt=.01, pscm_limited=limited)
  assert controller.correction == 0.  # Slew/limit still prevents a new outward increment here.
  assert controller.request_release == pytest.approx(sign*.02)
  assert controller.c1 == pytest.approx(sign*.23)


def test_adapter_retires_request_once_per_fresh_measurement_and_reset_clears_history():
  controller = FordModelActionController()
  def tick(now, desired, measured, stamp, **kwargs):
    return controller.update(straight(.4), desired, current_curvature=measured, speed=4., yaw_rate=0., now=now,
                             measurement_time=stamp, model_time=now, reference_time=now, active=True, **kwargs)
  for i in range(150):
    now = 1.+i*.01
    tick(now, .035, .035 if i < 100 else .025, now)
  before = controller.core.correction
  tick(2.50, .025, .035, 2.49)
  assert controller.core.correction == before
  assert controller.core.last_feedback_desired == .035
  assert controller.diagnostics['request_release'] == 0.
  tick(2.51, .025, .035, 2.51)
  assert controller.diagnostics['request_release'] == pytest.approx(-before)
  assert controller.core.last_feedback_desired == .025
  tick(2.52, .025, .035, 2.51)
  assert controller.diagnostics['request_release'] == 0.
  tick(2.53, .025, .035, 2.53, valid=False)
  assert controller.core.last_feedback_desired is None
  assert controller.core.request_release == 0.


def test_driver_override_clears_correction_and_cannot_leave_a_pending_release():
  controller = ModelActionController()
  controller.correction, controller.last_feedback_desired = .02, .035
  controller.update(straight(.4), .025, current_curvature=.035, speed=4., dt=.01, feedback_enabled=False)
  assert controller.correction == controller.request_release == 0.
  controller.update(straight(.4), .025, current_curvature=.035, speed=4., dt=.01)
  assert controller.request_release == 0.
