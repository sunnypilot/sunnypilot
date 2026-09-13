"""Unwind correction must not become a new turn after a confirmed catch-up.

These reproduce controller memory, not the PSCM's physical steering response.
"""
import pytest

from openpilot.selfdrive.controls.lib.ford_model_action import FordModelActionController, ModelActionController
from openpilot.selfdrive.controls.tests.test_ford_model_action import straight


def unwind(controller, sign):
  for _ in range(30):
    controller.update(straight(-sign*.5), -sign*.02, current_curvature=-sign*.02, speed=4., dt=.01)
  # Selected curvature relaxes, but the wheel is still too far into the old
  # turn. Feedback builds the same opposite-direction correction seen in 115.
  for _ in range(50):
    controller.update(straight(-sign*.5), -sign*.01, current_curvature=-sign*.04, speed=4., dt=.01)
  assert sign*controller.correction > .04
  assert controller.unwind_direction == sign
  for _ in range(30):
    controller.update(straight(sign*.05), 0., current_curvature=-sign*.01, speed=4., dt=.01)
  assert sign*controller.correction > .04


@pytest.mark.parametrize('sign', [-1., 1.])
@pytest.mark.parametrize('requested', [0., .0001])
def test_completed_unwind_does_not_keep_requesting_a_new_turn(sign, requested):
  controller = ModelActionController()
  unwind(controller, sign)
  before = controller.c1
  # The model path now confirms the unwind direction and actual steering has
  # caught the near-zero/new-direction request. Allow the original output slew
  # to finish; the old unwind correction must no longer prop up C1.
  for _ in range(20):
    out = controller.update(straight(sign*.05), sign*requested, current_curvature=sign*requested, speed=4., dt=.01)
  assert abs(controller.c1-before) <= .100000001
  assert out.path_offset == pytest.approx(sign*.05)
  assert controller.correction == 0., 'Stored unwind correction remains after catch-up'
  assert abs(out.path_angle-7.*sign*requested) <= .000500001
  assert controller.unwind_direction == 0.


@pytest.mark.parametrize('sign', [-1., 1.])
@pytest.mark.parametrize('case', ['not_caught', 'old_side_request', 'model_c0_old', 'model_c0_neutral', 'slewed_c0_old',
                                  'correction_not_dominant', 'opposite_correction', 'no_unwind', 'duplicate'])
def test_unwind_release_requires_catchup_and_confirmed_new_direction(sign, case):
  controller = ModelActionController()
  unwind(controller, sign)
  desired = measured = 0.
  offset, feedback_dt = sign*.05, .01
  if case == 'not_caught':
    measured = -sign*.005
  elif case == 'old_side_request':
    desired = measured = -sign*.001
  elif case == 'model_c0_old':
    offset = -sign*.05
  elif case == 'model_c0_neutral':
    offset = 0.
  elif case == 'slewed_c0_old':
    controller.c0 = -sign*.5
  elif case == 'correction_not_dominant':
    desired = measured = sign*.02
  elif case == 'opposite_correction':
    controller.correction = -sign*.01
  elif case == 'no_unwind':
    controller.unwind_direction = 0.
  elif case == 'duplicate':
    feedback_dt = 0.
  before = controller.correction
  controller.update(straight(offset), desired, current_curvature=measured, speed=4., dt=.01, feedback_dt=feedback_dt)
  assert controller.unwind_release == 0.
  assert abs(controller.correction-before) <= abs(desired-measured)*4.*feedback_dt+1e-10


@pytest.mark.parametrize('sign', [-1., 1.])
@pytest.mark.parametrize('desired', [0., .004])
def test_steady_tracking_correction_survives_matched_steering_and_noise(sign, desired):
  controller = ModelActionController()
  controller.correction, controller.c1, controller.c0 = sign*.05, sign*(7.*desired+.05), sign*.05
  for i in range(300):
    measured = sign*(desired+(1 if i % 2 else -1)*.000001)
    controller.update(straight(sign*.05), sign*desired, current_curvature=measured, speed=4., dt=.01)
    assert controller.unwind_direction == controller.unwind_release == 0.
  assert controller.correction == pytest.approx(sign*.05)


@pytest.mark.parametrize('limited', [False, True])
def test_catchup_release_uses_existing_slew_and_is_consumed_once(limited):
  controller = ModelActionController()
  unwind(controller, 1.)
  before, correction = controller.c1, controller.correction
  controller.update(straight(.05), 0., current_curvature=.001, speed=4., dt=.01, pscm_limited=limited)
  assert controller.unwind_release == correction
  assert controller.c1 == pytest.approx(before-.005)
  assert controller.correction <= 0.  # Remaining feedback can only correct the overshoot.
  assert controller.unwind_direction == 0.
  controller.update(straight(.05), 0., current_curvature=.001, speed=4., dt=.01)
  assert controller.unwind_release == 0.


@pytest.mark.parametrize('override', ['driver', 'invalid', 'inactive'])
def test_unwind_history_is_cleared_by_override_and_reset(override):
  controller = ModelActionController()
  unwind(controller, 1.)
  kwargs = {'driver': {'feedback_enabled': False}, 'invalid': {'valid': False}, 'inactive': {'active': False}}[override]
  controller.update(straight(.05), 0., current_curvature=0., speed=4., dt=.01, **kwargs)
  assert controller.unwind_direction == controller.unwind_release == controller.correction == 0.


def test_duplicate_adapter_measurement_cannot_consume_unwind_until_fresh_catchup():
  controller = FordModelActionController()
  for frame in range(130):
    now = 1.+frame*.01
    desired = -.02 if frame < 30 else -.01 if frame < 80 else 0.
    measured = -.02 if frame < 30 else -.04 if frame < 80 else -.01
    controller.update(straight(-.5 if frame < 80 else .05), desired, current_curvature=measured,
                      speed=4., yaw_rate=0., now=now, measurement_time=now, model_time=now, reference_time=now, active=True)
  assert controller.core.unwind_direction == 1.
  before = controller.core.correction
  for now, stamp in [(2.30, 2.29), (2.31, 2.31), (2.32, 2.31)]:
    controller.update(straight(.05), 0., current_curvature=0., speed=4., yaw_rate=0., now=now,
                      measurement_time=stamp, model_time=now, reference_time=now, active=True)
    if now == 2.30:
      assert controller.core.correction == before and controller.core.unwind_direction == 1.
    else:
      assert controller.core.correction == controller.core.unwind_direction == 0.
    assert controller.diagnostics['unwind_release'] == (before if now == 2.31 else 0.)
