import math
from types import SimpleNamespace

import numpy as np
import pytest

from opendbc.can import CANPacker, CANParser
from opendbc.car.ford.fordcan import CanBus, create_lat_ctl2_msg
from openpilot.cereal import custom
from openpilot.selfdrive.controls.lib.ford_path import FordPath
from openpilot.selfdrive.controls.lib.ford_model_action import ModelActionController, encode_model_action


def make_model(x, y, heading):
  times = np.linspace(0., 3., len(x))
  return SimpleNamespace(position=SimpleNamespace(t=times, x=x, y=y), orientation=SimpleNamespace(t=times, z=heading))


def circle(curvature):
  s = np.linspace(0., 60., 601)
  return make_model(np.sin(curvature*s)/curvature, (1-np.cos(curvature*s))/curvature, curvature*s)


def straight(offset=0., heading=0.):
  x = np.linspace(0., 60., 121)
  return make_model(x*np.cos(heading), offset+x*np.sin(heading), np.full_like(x, heading))


def test_model_heading_is_used_even_when_scalar_action_differs():
  model = circle(.02)
  for desired in (0., -.004, .004):
    target = encode_model_action(model, desired, 20.)
    assert target.path_angle == pytest.approx(.4)
    assert target.path_offset == pytest.approx((1-math.cos(.4))/.02)


def test_straight_centering_and_matched_model_circles():
  for speed in (2., 7., 20., 35.):
    assert encode_model_action(straight(.4), 0., speed) == FordPath(True, .4, 0., 0., 0.)
  for sign in (-1, 1):
    target = encode_model_action(circle(sign*.01), sign*.01, 20.)
    assert target.path_offset == pytest.approx(sign*(1-math.cos(.2))/.01)
    assert target.path_angle == pytest.approx(sign*.2)


def test_two_actuator_positions_are_sufficient_for_every_next_output():
  controller = ModelActionController()
  assert not hasattr(controller, '__dict__')
  for i in range(300):
    copied = ModelActionController()
    copied.c0, copied.c1 = controller.c0, controller.c1
    model = straight(.2*math.sin(i*.1))
    kwargs = {'speed': 20., 'dt': .01}
    desired = .005*math.cos(i*.03)
    assert controller.update(model, desired, **kwargs) == copied.update(model, desired, **kwargs)


def test_held_turn_releases_using_new_model_geometry_without_retained_bias():
  for sign in (-1., 1.):
    controller = ModelActionController()
    for _ in range(400):
      out = controller.update(circle(sign*.01), sign*.01, speed=20., dt=.01)
    assert out.path_angle == pytest.approx(sign*.2)
    previous = np.array([controller.c0, controller.c1])
    for _ in range(100):
      out = controller.update(straight(), sign*.01, speed=20., dt=.01)
      expected = previous+np.clip(-previous, [-.04, -.005], [.04, .005])
      values = np.array([controller.c0, controller.c1])
      np.testing.assert_allclose(values, expected, atol=1e-10)
      previous = values
    assert out == FordPath(True, 0., 0., 0., 0.)


def test_current_model_replacement_leaves_only_independent_actuator_slew():
  controller = ModelActionController()
  for _ in range(150):
    controller.update(straight(1.-20*math.sin(.4), .4), .04, speed=20., dt=.01)
  for _ in range(25):
    out = controller.update(straight(), 0., speed=20., dt=.01)
  assert out.path_offset == pytest.approx(0.)
  assert out.path_angle > 0.  # C1 cannot hold C0 during its longer release.
  for _ in range(75):
    out = controller.update(straight(), 0., speed=20., dt=.01)
  assert out == FordPath(True, 0., 0., 0., 0.)


@pytest.mark.parametrize('overrides', [{'active': False}, {'valid': False}, {'dt': .2}, {'speed': math.nan}])
def test_invalid_or_inactive_input_clears_state_before_reengagement(overrides):
  controller = ModelActionController()
  for _ in range(100):
    controller.update(straight(.5), .01, speed=20., dt=.01)
  kwargs = {'speed': 20., 'dt': .01, 'active': True, 'valid': True}
  kwargs.update(overrides)
  assert controller.update(straight(), 0., **kwargs) == FordPath()
  assert (controller.c0, controller.c1) == (0., 0.)
  assert controller.update(straight(), 0., speed=20., dt=.01) == FordPath(True, 0., 0., 0., 0.)


def test_malformed_geometry_and_nonfinite_action_never_create_an_active_command():
  for model, desired in ((None, 0.), (straight(), math.nan), (straight(), math.inf)):
    assert not encode_model_action(model, desired, 20.).valid


def test_selected_core_reversal_through_float32_and_wire_keeps_sign_and_zero_c2():
  controller = ModelActionController()
  packer = CANPacker('ford_lincoln_base_pt')
  parser = CANParser('ford_lincoln_base_pt', [('LateralMotionControl2', 100)], 0)
  bus = CanBus(fingerprint={0: {}})
  previous = np.zeros(2)
  for i in range(600):
    sign = 1. if i < 300 else -1.
    out = controller.update(straight(sign*8., sign*.8), sign*.1, speed=30., dt=.01)
    fields = np.array([out.path_offset, out.path_angle])
    assert (abs(fields) <= [5.1100001, .5000001]).all()
    assert (abs(fields-previous) <= [.0500001, .0055001]).all()
    previous = fields
    message = custom.CarControlSP.new_message()
    message.fordLateralPath.pathOffset = out.path_offset
    message.fordLateralPath.pathAngle = out.path_angle
    packet = create_lat_ctl2_msg(packer, bus, 2, -message.fordLateralPath.pathOffset,
                                -message.fordLateralPath.pathAngle, out.curvature, out.curvature_rate, i % 16)
    parser.update([i*10_000_000, [packet]])
    decoded = parser.vl['LateralMotionControl2']
    assert decoded['LatCtlPathOffst_L_Actl'] == pytest.approx(-out.path_offset)
    assert decoded['LatCtlPath_An_Actl'] == pytest.approx(-out.path_angle)
    assert decoded['LatCtlCurv_No_Actl'] == decoded['LatCtlCrv_NoRate2_Actl'] == 0.


def test_short_path_holds_available_endpoint_without_extrapolation():
  model = make_model([0., 1.], [0., .1], [0., 0.])
  assert encode_model_action(model, .01, 20.) == FordPath(True, .1, 0., 0., 0.)


def test_overflowing_arc_resets_instead_of_publishing_invalid_geometry():
  model = make_model([0., 1e308, -1e308], [0., 0., 0.], [0., 0., 0.])
  controller = ModelActionController()
  controller.update(straight(.4), .01, speed=20., dt=.01)
  assert controller.update(model, .01, speed=20., dt=.01) == FordPath()
  assert (controller.c0, controller.c1) == (0., 0.)


@pytest.mark.parametrize('value', [None, 'bad', 10**400])
@pytest.mark.parametrize('field', ['dt', 'speed', 'desired_curvature'])
def test_malformed_numeric_input_resets_without_throwing(field, value):
  controller = ModelActionController()
  kwargs = {'speed': 20., 'dt': .01, 'desired_curvature': .01}
  controller.update(straight(.4), **kwargs)
  kwargs[field] = value
  assert controller.update(straight(.4), **kwargs) == FordPath()
  assert (controller.c0, controller.c1) == (0., 0.)


@pytest.mark.parametrize('model', [
  make_model([], [], []), make_model([0.], [0.], [0.]),
  make_model([0., 10.], [0.], [0., 0.]), make_model([0., 10.], [0., 0.], [0.]),
  make_model([0., 0.], [0., 0.], [0., 0.]),
  make_model([0., 10.], [0., math.nan], [0., 0.]), make_model([0., math.inf], [0., 0.], [0., 0.]),
  make_model([0., 10.], [0., 0.], [0., math.inf]),
  make_model([0., 10**400], [0., 0.], [0., 0.]),
  make_model([0., 10.], [0., 0.], [1e308, -1e308]),
])
def test_malformed_model_arrays_cannot_reuse_a_previous_valid_command(model):
  controller = ModelActionController()
  controller.update(straight(.4), .01, speed=20., dt=.01)
  assert controller.update(model, .01, speed=20., dt=.01) == FordPath()
  assert (controller.c0, controller.c1) == (0., 0.)


@pytest.mark.parametrize('field,value,valid', [
  ('speed', .2999, False), ('speed', .3, True), ('speed', 55., True), ('speed', 55.0001, False),
  ('desired_curvature', -1., True), ('desired_curvature', 1., True), ('desired_curvature', -1.0001, False),
  ('dt', .001999, False), ('dt', .002, True), ('dt', .1, True), ('dt', .100001, False), ('dt', 0., False),
])
def test_domain_and_elapsed_time_boundaries(field, value, valid):
  kwargs = {'speed': 20., 'desired_curvature': .01, 'dt': .01}
  kwargs[field] = value
  assert ModelActionController().update(straight(.4), **kwargs).valid == valid


def test_arc_station_floor_not_forward_x_determines_offset():
  x = np.array([0., 6., 12.])
  y = .4+x*.75
  target = encode_model_action(make_model(x, y, [.4, .4, .4]), -.01, 20.)
  # At one second arc station is 5 m; the 7 m minimum gives x=5.6, y=4.6.
  assert target.path_offset == pytest.approx(4.6)
  assert target.path_angle == pytest.approx(.4)


def test_duplicate_stations_keep_valid_geometry_and_first_cycle_slew():
  model = make_model([0., 0., 10.], [.4, .4, .4], [0., 0., 0.])
  assert encode_model_action(model, 0., 20.) == FordPath(True, .4, 0., 0., 0.)
  out = ModelActionController().update(model, .01, speed=20., dt=.002)
  assert out.path_offset == pytest.approx(.01)
  assert out.path_angle == 0.
