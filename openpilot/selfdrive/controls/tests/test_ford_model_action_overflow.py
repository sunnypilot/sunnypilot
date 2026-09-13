"""C1 overflow allocation and release; no assumptions about PSCM response."""
import math

import pytest

from openpilot.selfdrive.controls.lib.ford_model_action import ModelActionController
from openpilot.selfdrive.controls.tests.test_ford_model_action import make_model, straight


@pytest.mark.parametrize('sign', [-1., 1.])
@pytest.mark.parametrize('speed', [3., 7., 20., 55.])
@pytest.mark.parametrize('heading', [.4, .5, .6, .8])
def test_clipped_base_heading_preserves_the_seven_metre_reference(sign, speed, heading):
  controller = ModelActionController()
  desired = sign*heading/max(7., speed)
  for _ in range(150):
    out = controller.update(straight(sign*.2), desired, current_curvature=desired, speed=speed, dt=.01)
  assert controller.correction == 0.
  arc = (1-math.cos(7.*desired))/desired
  assert controller.c0 == pytest.approx(arc+sign*7.*max(heading-.5, 0.))
  assert out.path_offset == pytest.approx(controller.c0, abs=.005)
  assert out.path_angle == pytest.approx(sign*min(heading, .5))
  assert out.path_offset+7.*out.path_angle == pytest.approx(arc+sign*7.*heading, abs=.005)
  assert out.curvature == out.curvature_rate == 0.


@pytest.mark.parametrize('sign', [-1., 1.])
def test_combined_offset_is_clipped_after_allocating_heading(sign):
  controller = ModelActionController()
  for _ in range(200):
    out = controller.update(straight(sign*4.), sign*.2, current_curvature=sign*.2, speed=7., dt=.01)
  assert out.path_offset == pytest.approx(sign*5.11)
  assert out.path_angle == pytest.approx(sign*.5)


@pytest.mark.parametrize('sign', [-1., 1.])
def test_overflow_uses_existing_reference_with_short_model_path(sign):
  controller = ModelActionController()
  model = make_model([0., 1.], [0., sign*.2], [0., 0.])
  for _ in range(150):
    out = controller.update(model, sign*.03, current_curvature=sign*.03, speed=20., dt=.01)
  assert out.path_offset == pytest.approx(sign*((1-math.cos(.21))/.03+.7), abs=.005)


@pytest.mark.parametrize('sign', [-1., 1.])
def test_extra_offset_releases_at_existing_slew_without_stored_overflow(sign):
  controller = ModelActionController()
  for _ in range(200):
    controller.update(straight(sign*.2), sign*.04, current_curvature=sign*.04, speed=20., dt=.01)
  start = sign*((1-math.cos(.28))/.04+2.1)
  target = sign*(1-math.cos(.14))/.02
  assert controller.c0 == pytest.approx(start)
  for i in range(70):
    before = controller.c0
    out = controller.update(straight(sign*.2), sign*.02, current_curvature=sign*.02, speed=20., dt=.01)
    assert sign*controller.c0 >= sign*target-1e-10
    assert sign*controller.c0 <= sign*before+1e-10
    assert abs(controller.c0-before) <= .04+1e-10
    if i == 0:
      assert controller.c0 == pytest.approx(start-sign*.04)
  assert out.path_offset == pytest.approx(sign*(1-math.cos(.14))/.02, abs=.005)
  assert out.path_angle == pytest.approx(sign*.4)
  assert controller.correction == 0.


@pytest.mark.parametrize('sign', [-1., 1.])
def test_c1_feedback_saturation_does_not_spill_correction_into_c0(sign):
  controller = ModelActionController(proportional_gain=0., integral_gain=1.)
  for _ in range(200):
    out = controller.update(straight(sign*.2), sign*.02, current_curvature=0., speed=20., dt=.01)
  assert out.path_angle == pytest.approx(sign*.5)
  assert controller.correction == pytest.approx(sign*.1)
  assert out.path_offset == pytest.approx(sign*(1-math.cos(.14))/.02, abs=.005)


@pytest.mark.parametrize('sign', [-1., 1.])
@pytest.mark.parametrize('enabled,limited', [(False, False), (True, True)])
def test_overflow_is_base_geometry_with_existing_feedback_gates(sign, enabled, limited):
  controller = ModelActionController()
  for _ in range(150):
    out = controller.update(straight(sign*.2), sign*.03, current_curvature=sign*.02, speed=20., dt=.01,
                            feedback_enabled=enabled, pscm_limited=limited)
  assert out.path_offset == pytest.approx(sign*((1-math.cos(.21))/.03+.7), abs=.005)
  assert out.path_angle == pytest.approx(sign*.5)
  assert controller.correction == 0.
