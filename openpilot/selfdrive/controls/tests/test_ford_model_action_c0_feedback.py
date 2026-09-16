"""C0 proportional correction semantics, independent of simulated PSCM motion."""
import math

import pytest

from openpilot.selfdrive.controls.lib.ford_model_action import ModelActionController
from openpilot.selfdrive.controls.lib.ford_path import FordPath
from openpilot.selfdrive.controls.tests.test_ford_model_action import straight
from openpilot.selfdrive.controls.tests.test_ford_model_action_selection import startup


@pytest.mark.parametrize('sign', [-1., 1.])
def test_c0_helps_entry_then_releases_at_catchup_without_accumulation(sign):
  controller = ModelActionController(c0_proportional_gain=.5)
  matched = ModelActionController(c0_proportional_gain=0.)
  kwargs = {'speed': 5., 'dt': .01, 'feedback_dt': 0., 'curvature_scale': 1.2}
  base = matched.update(straight(), sign*.02, current_curvature=sign*.01, **kwargs)
  first = controller.update(straight(), sign*.02, current_curvature=sign*.01, **kwargs)
  assert sign*(first.path_offset-base.path_offset) > .4
  assert controller.offset_proportional*sign > 0.
  for _ in range(500):
    held = controller.update(straight(), sign*.02, current_curvature=sign*.01, **kwargs)
  assert held == first
  caught = controller.update(straight(), sign*.02, current_curvature=sign*.02, **kwargs)
  assert controller.offset_proportional == 0.
  assert caught.path_offset == base.path_offset
  overshot = controller.update(straight(), sign*.02, current_curvature=sign*.03, **kwargs)
  assert sign*(overshot.path_offset-base.path_offset) < -.4


@pytest.mark.parametrize('sign', [-1., 1.])
def test_zero_target_commands_opposite_c0_and_does_not_retain_old_correction(sign):
  core = ModelActionController(c0_proportional_gain=.5)
  core.update(straight(), sign*.1, current_curvature=0., speed=5., dt=.01)
  out = core.update(straight(), 0., current_curvature=sign*.03, speed=5., dt=.01, feedback_dt=0.)
  assert sign*out.path_offset < 0.
  out = core.update(straight(), 0., current_curvature=0., speed=5., dt=.01)
  assert out.path_offset == core.offset_proportional == 0.


def test_new_c0_does_not_change_c1_or_its_integral_for_identical_measurements():
  old, new = ModelActionController(c0_proportional_gain=0.), ModelActionController(c0_proportional_gain=.5)
  for i in range(200):
    desired, measured = .03*math.sin(i/13), .025*math.sin((i-5)/13)
    kwargs = {'current_curvature': measured, 'speed': 12., 'dt': .01, 'feedback_enabled': i % 7 != 0, 'pscm_limited': i % 9 == 0}
    a, b = [c.update(straight(), desired, **kwargs) for c in (old, new)]
    assert a.path_angle == b.path_angle
    assert (old.correction, old.proportional) == (new.correction, new.proportional)
    assert b.curvature == b.curvature_rate == 0.


def test_c0_is_disabled_by_existing_feedback_arbitration_and_reset():
  core = ModelActionController(c0_proportional_gain=.5)
  core.update(straight(), .02, current_curvature=0., speed=5., dt=.01)
  assert core.offset_proportional > 0.
  disabled = core.update(straight(), .02, current_curvature=0., speed=5., dt=.01, feedback_enabled=False)
  assert core.offset_proportional == 0.
  core.reset()
  assert core.c0 == core.offset_proportional == 0.
  assert disabled.path_offset > 0.  # Existing feedforward remains available.


@pytest.mark.parametrize('scale', [0., -1., math.nan, math.inf, None])
def test_bad_curvature_conversion_cannot_send_a_command(scale):
  core = ModelActionController()
  assert core.update(straight(), .02, current_curvature=0., speed=5., dt=.01, curvature_scale=scale) == FordPath()
  assert core.c0 == core.offset_proportional == 0.


@pytest.mark.parametrize('gain', [-1., math.nan, math.inf, None])
def test_bad_c0_gain_is_rejected(gain):
  with pytest.raises(ValueError):
    ModelActionController(c0_proportional_gain=gain)


def test_c0_uses_feedback_reference_and_stays_inside_field_bounds():
  core = ModelActionController(c0_proportional_gain=.5)
  core.update(straight(), .03, current_curvature=.02, feedback_curvature=.02, speed=5., dt=.01)
  assert core.offset_proportional == 0.
  for sign in (-1., 1.):
    out = core.update(straight(), sign*.9, current_curvature=-sign*.9, speed=55., dt=.01, curvature_scale=3.)
    assert out.path_offset == pytest.approx(sign*5.11)


def test_c0_response_units_and_explicit_gain():
  core = ModelActionController(c0_proportional_gain=.5)
  core.update(straight(), .01, current_curvature=0., speed=5., dt=.01, curvature_scale=1.2)
  # Fitted C0 gain is geometric curvature per metre of command, not road curvature.
  response = .010717679293424373+.018122981795212647/25.
  assert core.offset_proportional == pytest.approx(.5*.01*1.2/response)


@pytest.mark.parametrize('speed', [1., 5., 20., 40.])
@pytest.mark.parametrize('stiffness,ratio,roll', [(.3, 14., -.1), (1., 16.9, 0.), (2., 20., .1)])
def test_curvature_error_conversion_matches_normal_desired_wheel_angle(speed, stiffness, ratio, roll):
  controls = startup()
  vm, cp = controls.VM, controls.CP
  vm.update_params(stiffness, ratio)
  angle, angle_offset, desired = 15., 1.5, .002
  measured = -vm.calc_curvature(math.radians(angle-angle_offset), speed, roll)
  target = math.degrees(vm.get_steer_from_curvature(-desired, speed, roll))+angle_offset
  scale = vm.get_steer_from_curvature(1., speed, 0.)/(cp.steerRatio*cp.wheelbase)
  converted_error = -(desired-measured)*scale*cp.steerRatio*cp.wheelbase*180/math.pi
  assert converted_error == pytest.approx(target-angle)
