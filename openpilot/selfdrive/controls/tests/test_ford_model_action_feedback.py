"""C1 feedback behavior; these tests do not simulate a Ford steering plant."""
import math
from types import SimpleNamespace

import pytest

from openpilot.selfdrive.controls.lib.ford_model_action import FordModelActionController, ModelActionController
from openpilot.selfdrive.controls.lib.ford_path import FordPath
from openpilot.selfdrive.controls.tests.test_ford_model_action import straight


def tick(controller, desired, measured, **overrides):
  kwargs = {'current_curvature': measured, 'speed': 20., 'dt': .01}
  kwargs.update(overrides)
  return controller.update(straight(.4), desired, **kwargs)


@pytest.mark.parametrize('sign', [-1., 1.])
def test_feedback_builds_holds_and_unwinds_without_changing_c0(sign):
  controller, matched = ModelActionController(), ModelActionController()
  for _ in range(100):
    tick(controller, sign*.004, sign*.004)
  for _ in range(100):
    out = tick(controller, sign*.004, sign*.003)
    baseline = tick(matched, sign*.004, sign*.004)
  assert controller.correction == pytest.approx(sign*.02)
  assert out.path_angle == pytest.approx(sign*.1)
  assert out.path_offset == baseline.path_offset == pytest.approx(.4)
  for _ in range(100):
    out = tick(controller, sign*.004, sign*.004)
  assert controller.correction == pytest.approx(sign*.02)
  assert out.path_angle == pytest.approx(sign*.1)
  for _ in range(200):
    out = tick(controller, sign*.004, sign*.005)
  assert controller.correction == pytest.approx(-sign*.02)
  assert out.path_angle == pytest.approx(sign*.06)
  assert out.curvature == out.curvature_rate == 0.


@pytest.mark.parametrize('sign', [-1., 1.])
def test_amplitude_and_slew_limits_do_not_store_unavailable_feedback(sign):
  controller = ModelActionController()
  # The unchanged model request is already ahead of the output slew.
  for _ in range(10):
    tick(controller, sign*.01, 0.)
    assert controller.correction == 0.
  for _ in range(1000):
    before = controller.c1
    tick(controller, sign*.01, -sign*.9)
    assert abs(controller.c1-before) <= .0050000001
    assert abs(controller.correction) <= .3000000001
  assert controller.c1 == pytest.approx(sign*.5)
  assert controller.correction == pytest.approx(sign*.3)
  for _ in range(200):
    tick(controller, sign*.01, 0.)
  assert controller.correction == pytest.approx(sign*.3)
  tick(controller, sign*.01, sign*.02)
  assert sign*controller.correction < .3  # Unwind is allowed at the cap.
  assert sign*controller.c1 < .5


@pytest.mark.parametrize('sign', [-1., 1.])
def test_pscm_limit_only_blocks_feedback_further_into_measured_turn(sign):
  controller = ModelActionController()
  for _ in range(100):
    tick(controller, sign*.004, sign*.004)
  for _ in range(100):
    tick(controller, sign*.004, sign*.003, pscm_limited=True)
  assert controller.correction == 0.
  out = tick(controller, sign*.004, sign*.005, pscm_limited=True)
  assert sign*controller.correction < 0.
  # A limit cannot stall the new model request itself or its unwind slew.
  for _ in range(100):
    out = tick(controller, 0., 0., pscm_limited=True)
  assert abs(out.path_angle) < .001
  assert out.path_offset == pytest.approx(.4)


@pytest.mark.parametrize('sign', [-1., 1.])
def test_pscm_limit_cannot_trap_old_correction_below_the_model_request(sign):
  controller = ModelActionController()
  controller.correction = -sign*.02
  controller.c1 = sign*.06
  for _ in range(200):
    out = tick(controller, sign*.004, sign*.003, pscm_limited=True)
  assert controller.correction == pytest.approx(0.)
  assert out.path_angle == pytest.approx(sign*.08)


def test_driver_intervention_clears_feedback_through_existing_output_slew():
  controller = ModelActionController()
  for _ in range(100):
    tick(controller, .004, .004)
  for _ in range(100):
    tick(controller, .004, .003)
  assert controller.correction > 0.
  previous = controller.c1
  tick(controller, .004, -.01, feedback_enabled=False)
  assert controller.correction == 0.
  assert abs(controller.c1-previous) <= .0050000001
  for _ in range(100):
    out = tick(controller, .004, -.01, feedback_enabled=False)
  assert controller.correction == 0.
  assert out.path_angle == pytest.approx(.08)


@pytest.mark.parametrize('field,value', [('current_curvature', math.nan), ('current_curvature', None),
                                       ('current_curvature', 1.01), ('feedback_dt', math.nan),
                                       ('feedback_dt', -.001), ('feedback_dt', .151), ('active', False)])
def test_bad_feedback_inputs_and_disengagement_clear_every_control_state(field, value):
  controller = ModelActionController()
  controller.correction = .03
  out = tick(controller, .004, .003, **{field: value})
  assert out == FordPath()
  assert (controller.c0, controller.c1, controller.correction) == (0., 0., 0.)


def adapter_tick(controller, now, **overrides):
  kwargs = {'current_curvature': .003, 'speed': 20., 'yaw_rate': 0., 'now': now,
            'measurement_time': now, 'model_time': now, 'reference_time': now, 'active': True}
  kwargs.update(overrides)
  return controller.update(straight(.4), .004, **kwargs)


def status(now, **overrides):
  fields = {'valid': True, 'canMonoTime': round(now*1e9), 'limit': 0, 'lateralState': 2, 'denied': False}
  fields.update(overrides)
  return SimpleNamespace(**fields)


def test_repeated_steering_samples_only_advance_output_slew():
  controller = FordModelActionController()
  for i in range(100):
    adapter_tick(controller, 1.+i*.01, current_curvature=.004)
  before = controller.core.correction
  for i in range(1, 6):
    adapter_tick(controller, 1.99+i*.01, measurement_time=1.99)
    assert controller.core.correction == before
  adapter_tick(controller, 2.05)
  assert controller.core.correction == pytest.approx(.02*.06)
  assert controller.diagnostics['feedback_dt'] == pytest.approx(.06)


@pytest.mark.parametrize('overrides', [{'driver_pressed': True}, {'driver_torque': 1.01},
                                     {'driver_torque': -1.01}, {'driver_torque': math.nan},
                                     {'pscm_status': status(2.01, limit=3)},
                                     {'pscm_status': status(2.01, denied=True)},
                                     {'pscm_status': status(2.01, lateralState=1)}])
def test_adapter_clears_feedback_when_driver_or_pscm_overrides(overrides):
  controller = FordModelActionController()
  for i in range(101):
    adapter_tick(controller, 1.+i*.01)
  assert controller.core.correction > 0.
  assert adapter_tick(controller, 2.01, **overrides).valid
  assert controller.core.correction == 0.
  assert not controller.diagnostics['feedback_enabled']


@pytest.mark.parametrize('overrides,limited', [({}, True), ({'valid': False}, False),
                                            ({'canMonoTime': 0}, False), ({'canMonoTime': 1_800_000_000}, False),
                                            ({'canMonoTime': 2_020_000_000}, False), ({'limit': 1}, False)])
def test_only_fresh_reached_pscm_limit_blocks_outward_integration(overrides, limited):
  controller = FordModelActionController()
  for i in range(100):
    adapter_tick(controller, 1.+i*.01, current_curvature=.004)
  adapter_tick(controller, 2., pscm_status=status(2., **{'limit': 2, **overrides}))
  assert controller.diagnostics['pscm_limited'] is limited
  assert (controller.core.correction == 0.) is limited


def test_measurement_cadence_preserves_elapsed_distance_integration():
  results = []
  for period in (1, 2, 5):
    controller = FordModelActionController()
    for i in range(101):
      now = 1.+i*.01
      adapter_tick(controller, now, current_curvature=.004)
    for i in range(1, 101):
      now = 2.+i*.01
      adapter_tick(controller, now, measurement_time=2.+(i//period)*period*.01)
    results.append(controller.core.correction)
  assert results == pytest.approx([.02, .02, .02])
