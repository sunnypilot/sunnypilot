"""C1 overflow allocation and release; no assumptions about PSCM response."""
import pytest

from openpilot.selfdrive.controls.lib.ford_model_action import ModelActionController
from openpilot.selfdrive.controls.tests.test_ford_model_action import make_model, straight


@pytest.mark.parametrize('sign', [-1., 1.])
@pytest.mark.parametrize('speed', [3., 7., 20., 55.])
@pytest.mark.parametrize('heading,offset', [(.4, .2), (.5, .2), (.6, .9), (.8, 2.3)])
def test_clipped_base_heading_preserves_the_seven_metre_reference(sign, speed, heading, offset):
  controller = ModelActionController()
  desired = sign*heading/max(7., speed)
  for _ in range(150):
    out = controller.update(straight(sign*.2), desired, current_curvature=desired, speed=speed, dt=.01)
  assert controller.correction == 0.
  assert out.path_offset == pytest.approx(sign*offset)
  assert out.path_angle == pytest.approx(sign*min(heading, .5))
  assert out.path_offset+7.*out.path_angle == pytest.approx(sign*(.2+7.*heading))
  assert out.curvature == out.curvature_rate == 0.


@pytest.mark.parametrize('sign', [-1., 1.])
def test_combined_offset_is_clipped_after_allocating_heading(sign):
  controller = ModelActionController()
  for _ in range(200):
    out = controller.update(straight(sign*4.), sign*.1, current_curvature=sign*.1, speed=7., dt=.01)
  assert out.path_offset == pytest.approx(sign*5.11)
  assert out.path_angle == pytest.approx(sign*.5)


@pytest.mark.parametrize('sign', [-1., 1.])
def test_overflow_uses_existing_reference_with_short_model_path(sign):
  controller = ModelActionController()
  model = make_model([0., 1.], [0., sign*.2], [0., 0.])
  for _ in range(150):
    out = controller.update(model, sign*.03, current_curvature=sign*.03, speed=20., dt=.01)
  assert out.path_offset == pytest.approx(sign*.9)


@pytest.mark.parametrize('sign', [-1., 1.])
def test_extra_offset_releases_at_existing_slew_without_stored_overflow(sign):
  controller = ModelActionController()
  for _ in range(200):
    controller.update(straight(sign*.2), sign*.04, current_curvature=sign*.04, speed=20., dt=.01)
  assert controller.c0 == pytest.approx(sign*2.3)
  for i in range(60):
    before = controller.c0
    out = controller.update(straight(sign*.2), sign*.02, current_curvature=sign*.02, speed=20., dt=.01)
    assert sign*controller.c0 >= .2-1e-10
    assert sign*controller.c0 <= sign*before+1e-10
    assert abs(controller.c0-before) <= .04+1e-10
    if i == 0:
      assert controller.c0 == pytest.approx(sign*2.26)
  assert out.path_offset == pytest.approx(sign*.2)
  assert out.path_angle == pytest.approx(sign*.4)
  assert controller.correction == 0.


@pytest.mark.parametrize('sign', [-1., 1.])
def test_c1_feedback_saturation_does_not_spill_correction_into_c0(sign):
  controller = ModelActionController()
  for _ in range(200):
    out = controller.update(straight(sign*.2), sign*.02, current_curvature=0., speed=20., dt=.01)
  assert out.path_angle == pytest.approx(sign*.5)
  assert controller.correction == pytest.approx(sign*.1)
  assert out.path_offset == pytest.approx(sign*.2)


@pytest.mark.parametrize('sign', [-1., 1.])
@pytest.mark.parametrize('enabled,limited', [(False, False), (True, True)])
def test_overflow_is_base_geometry_with_existing_feedback_gates(sign, enabled, limited):
  controller = ModelActionController()
  for _ in range(150):
    out = controller.update(straight(sign*.2), sign*.03, current_curvature=sign*.02, speed=20., dt=.01,
                            feedback_enabled=enabled, pscm_limited=limited)
  assert out.path_offset == pytest.approx(sign*.9)
  assert out.path_angle == pytest.approx(sign*.5)
  assert controller.correction == 0.


@pytest.mark.parametrize('sign', [-1., 1.])
def test_overflow_cannot_replace_model_centering_confirmation_for_carryover_release(sign):
  controller = ModelActionController()
  controller.c0, controller.c1, controller.correction = sign*.6, -sign*.1, -sign*.6
  for _ in range(20):
    controller.update(straight(-sign*.1), sign*.03, current_curvature=-sign*.002, speed=20., dt=.01)
  assert sign*controller.c0 > 0.  # Overflow agrees with heading; model centering still opposes it.
  assert controller.carryover_release_count == 0
  assert sign*controller.correction < -.4
