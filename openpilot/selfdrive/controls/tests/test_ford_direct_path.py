"""Direct-path reference selection, independent channels, feedback and real CAN encoding."""
from types import SimpleNamespace

import numpy as np
import pytest

from opendbc.car import structs
from openpilot.cereal import custom
from openpilot.selfdrive.controls.lib.drive_helpers import clip_curvature
from openpilot.selfdrive.controls.lib.ford_model_action import FordModelActionController, encode_model_path
from openpilot.selfdrive.controls.lib.ford_path import FordPath
from openpilot.selfdrive.controls.tests.test_ford_model_action import circle, make_model, straight
from openpilot.selfdrive.controls.tests.test_ford_model_action_adapter import Subscriptions, pipeline  # noqa: F401
from openpilot.selfdrive.controls.tests.test_ford_model_action_selection import startup
from tools.ford_pscm_lab.model_action_replay import WireCheck


def step(controller, model, now, previous, *, measured=0., speed=5., **kwargs):
  desired, _ = clip_curvature(speed, previous, controller.path_curvature(model, speed), 0.)
  result = controller.update(model, desired, current_curvature=measured, speed=speed, yaw_rate=0., now=now,
                             measurement_time=now, model_time=now, reference_time=now, active=True, **kwargs)
  return desired, result


@pytest.mark.parametrize('speed', [2., 5., 15., 30.])
@pytest.mark.parametrize('time_based', [False, True])
def test_position_and_heading_sample_existing_distances_independently(speed, time_based):
  x = np.linspace(0, 80, 801)
  model = make_model(x, x*.03+.2, x*.002)
  target = encode_model_path(model, speed, c0_time_based=time_based)
  # Arc-length station differs from forward x on this sloping path.
  d0, d1 = (max(7., speed) if time_based else 7.), max(7., speed)
  assert target.path_offset == pytest.approx(.2+.03*d0/np.hypot(1., .03))
  assert target.path_angle == pytest.approx(.002*d1/np.hypot(1., .03))
  assert target.curvature == target.curvature_rate == 0.


def test_short_path_holds_endpoint_and_bad_path_never_leaves_old_commands():
  model = make_model([0., 1.], [0., .2], [0., .03])
  target = encode_model_path(model, 20.)
  assert target.valid and target.path_offset == pytest.approx(.2) and target.path_angle == pytest.approx(.03)
  controller = FordModelActionController(direct_path=True)
  desired, command = step(controller, model, 1., 0.)
  assert command.valid
  model.position.y[1] = np.nan
  assert step(controller, model, 1.01, desired)[1] == FordPath()
  assert controller.core.offset_reference is None
  assert controller.core.correction == 0.


@pytest.mark.parametrize('sign', [-1., 1.])
def test_lateral_position_changes_c0_without_inventing_heading(sign):
  controller = FordModelActionController(0., 0., c0_proportional_gain=0., direct_path=True)
  model = straight(sign*.4)
  desired = 0.
  for i in range(100):
    desired, command = step(controller, model, 1.+i*.01, desired)
  assert desired == 0.
  assert command.path_offset == pytest.approx(sign*.4)
  assert command.path_angle == 0.


@pytest.mark.parametrize('sign', [-1., 1.])
def test_heading_changes_c1_without_rebuilding_c0_as_a_circle(sign):
  controller = FordModelActionController(0., 0., c0_proportional_gain=0., direct_path=True)
  model = straight()
  model.orientation.z = np.full(len(model.position.x), sign*.07)
  desired = 0.
  for i in range(100):
    desired, command = step(controller, model, 1.+i*.01, desired)
  assert desired == pytest.approx(sign*.01)
  assert command.path_angle == pytest.approx(sign*.07)
  assert command.path_offset == 0.


def test_both_base_channels_retain_upstream_request_limits_on_entry_reversal_and_release():
  controller = FordModelActionController(0., 0., c0_proportional_gain=0., direct_path=True)
  desired = offset = 0.
  for i in range(300):
    sign = 1 if i < 100 else -1 if i < 200 else 0
    model = straight(sign*5.)
    model.orientation.z = np.full(len(model.position.x), sign*.4)
    requested_offset = 2.*sign*5./49.
    offset, _ = clip_curvature(20., offset, requested_offset, 0.)
    desired, command = step(controller, model, 1.+i*.01, desired, speed=20.)
    assert controller.core.offset_reference == pytest.approx(offset)
    assert abs(desired) <= 3./20.**2
    assert command.path_offset == pytest.approx(.5*offset*49., abs=.0051)
    assert command.path_angle == pytest.approx(desired*20., abs=.000251)
  assert abs(command.path_offset) < .01 and abs(command.path_angle) < .001


def test_feedback_tracks_path_heading_and_raw_torque_override_is_still_the_driven_baseline():
  controller = FordModelActionController(direct_path=True)
  model = circle(.01)
  desired = 0.
  for i in range(100):
    desired, _ = step(controller, model, 1.+i*.01, desired, measured=.005)
  assert controller.core.proportional > 0. and controller.core.correction > 0.
  retained = controller.core.correction
  desired, _ = step(controller, model, 2., desired, measured=desired)
  assert controller.core.proportional == pytest.approx(0.)
  assert controller.core.correction == pytest.approx(retained)
  step(controller, model, 2.01, desired, driver_torque=1.0625)
  assert controller.core.correction == controller.core.proportional == controller.core.offset_proportional == 0.


@pytest.mark.parametrize('geometry', [False, True])
@pytest.mark.parametrize('maneuver', [False, True])
def test_missing_geometry_reference_falls_back_to_action_through_controlsd_and_can(pipeline, geometry, maneuver):  # noqa: F811
  settings = {'FordModelActionController': True, 'FordGeometryReference': geometry}
  controls = startup(params=SimpleNamespace(get_bool=lambda key: settings.get(key, False)))
  controls.sm, controls.desired_curvature, controls.curvature = Subscriptions(maneuver), 0., 0.
  assert not controls.ford_path_controller.direct_path
  assert (controls.ford_path_controller.geometry_assist is not None) == geometry
  model = circle(.01)
  model.action = SimpleNamespace(desiredCurvature=-.03)  # Deliberately opposite to the model path.
  cc = structs.CarControl(latActive=True)
  cs = SimpleNamespace(vEgo=5., yawRate=0., canValid=True, steeringPressed=False, steeringTorque=0.)
  exec(pipeline[0], {'self': controls, 'CS': cs, 'CC': cc, 'actuators': cc.actuators, 'model_v2': model,
                    'lp': SimpleNamespace(roll=0.), 'clip_curvature': clip_curvature, 'time': SimpleNamespace(monotonic=lambda: 1.)})
  expected = -.002
  assert controls.desired_curvature == pytest.approx(expected)
  assert controls.ford_path_controller.core.feedback_curvature == controls.desired_curvature
  assert not controls.ford_path_controller.diagnostics['direct_path']
  assert controls.ford_path.path_angle*expected > 0.
  msg = custom.CarControlSP.new_message()
  exec(pipeline[1], {'self': controls, 'CC_SP': msg})
  assert msg.fordLateralPath.pathOffset == pytest.approx(controls.ford_path.path_offset)
  assert msg.fordLateralPath.pathAngle == pytest.approx(controls.ford_path.path_angle)
  WireCheck().check(controls.ford_path)
