"""C1 release geometry checks; none predicts a PSCM or vehicle response."""
import math
from types import SimpleNamespace

import numpy as np
import pytest

from openpilot.selfdrive.controls.lib.ford_model_action import ModelActionController, encode_model_action


def model_path(headings, *, origin=0., offset=.3, sign=1.):
  # Known chord lengths make spatial heading profiles independent of speed.
  station = (0., 6., 18., 30.)
  heading = [sign*(origin+value) for value in headings]
  x, y = [0.], [sign*offset]
  for i in range(1, len(station)):
    direction = (heading[i-1]+heading[i])/2
    distance = station[i]-station[i-1]
    x.append(x[-1]+distance*math.cos(direction))
    y.append(y[-1]+distance*math.sin(direction))
  times = [0., .5, 1.5, 2.5]
  return SimpleNamespace(position=SimpleNamespace(t=times, x=x, y=y),
                         orientation=SimpleNamespace(t=times, z=heading))


@pytest.mark.parametrize('sign', [-1., 1.])
@pytest.mark.parametrize('origin', [0., .15])
def test_constant_spatial_curvature_preserves_original_heading(sign, origin):
  model = model_path([0., .12, .36, .60], origin=origin, sign=sign)
  out = encode_model_action(model, 0., 20.)
  # The selected point is halfway from 6 m to 18 m: psi = psi0 + .02*12.
  assert out.valid
  assert out.path_angle == pytest.approx(sign*(origin+.24))
  assert out.curvature == out.curvature_rate == 0.


@pytest.mark.parametrize('heading', [-.3, .3])
def test_constant_heading_line_keeps_its_nonzero_heading(heading):
  out = encode_model_action(model_path([0.]*4, origin=heading), 0., 20.)
  assert out.valid
  assert out.path_angle == pytest.approx(heading)


@pytest.mark.parametrize('sign', [-1., 1.])
def test_increasing_spatial_curvature_cannot_amplify_c1(sign):
  # Selected heading .24; terminal curvature .03/m would yield .36 rad.
  model = model_path([0., .06, .42, .90], sign=sign)
  out = encode_model_action(model, 0., 20.)
  assert out.path_angle == pytest.approx(sign*.24)


@pytest.mark.parametrize('sign', [-1., 1.])
@pytest.mark.parametrize('origin', [0., .15])
def test_decreasing_spatial_curvature_unloads_c1_without_erasing_origin(sign, origin):
  # Selected heading is psi0+.36; terminal curvature .02/m gives psi0+.24.
  model = model_path([0., .24, .48, .54], origin=origin, sign=sign)
  out = encode_model_action(model, 0., 20.)
  assert out.path_angle == pytest.approx(sign*(origin+.24))
  assert abs(out.path_angle) < origin+.36


@pytest.mark.parametrize('sign', [-1., 1.])
def test_opposite_terminal_curvature_releases_without_inventing_a_reversal(sign):
  model = model_path([0., .30, .10, -.30], sign=sign)
  out = encode_model_action(model, 0., 20.)
  # The selected model heading is still sign*.20, though its slope has reversed.
  assert out.valid
  assert out.path_angle == 0.


def test_exact_model_knot_uses_incoming_segment():
  model = SimpleNamespace(position=SimpleNamespace(t=[0., .5, 1., 2.], x=[0., 6., 12., 24.], y=[.3]*4),
                          orientation=SimpleNamespace(t=[0., .5, 1., 2.], z=[0., .24, .48, .48]))
  assert encode_model_action(model, 0., 20.).path_angle == pytest.approx(.48)


@pytest.mark.parametrize('sign', [-1., 1.])
def test_duplicate_selected_station_retains_original_c1(sign):
  times = [0., .5, 1., 2.]
  model = SimpleNamespace(position=SimpleNamespace(t=times, x=[0., 7., 7., 14.], y=[sign*.4]*4),
                          orientation=SimpleNamespace(t=times, z=[0., sign*.3, sign*.2, sign*.2]))
  out = encode_model_action(model, 0., 20.)
  assert out.valid
  assert out.path_offset == sign*.4
  assert out.path_angle == pytest.approx(sign*.2)


def test_actual_model_reversal_uses_existing_slew_and_reaches_opposite_c1():
  controller = ModelActionController()
  positive = model_path([0., .12, .36, .60])
  negative = model_path([0., .12, .36, .60], sign=-1.)
  for _ in range(50):
    controller.update(positive, 0., speed=20., dt=.01)
  before = controller.c1
  first = controller.update(negative, 0., speed=20., dt=.01)
  assert controller.c1 == pytest.approx(before-.005)
  assert first.path_angle > 0.
  for _ in range(100):
    final = controller.update(negative, 0., speed=20., dt=.01)
  assert final.path_angle == pytest.approx(-.24)


def test_release_preserves_c0_exactly_through_target_slew_and_packing():
  actual, reference = ModelActionController(), ModelActionController()
  for i in range(240):
    model = model_path([0., .24, .48, .54], offset=8.*math.sin(i*.04), sign=1. if i < 120 else -1.)
    # C0's reference has byte-for-byte identical position and clocks, but no C1.
    zero_heading = SimpleNamespace(position=model.position,
                                   orientation=SimpleNamespace(t=model.orientation.t, z=[0.]*4))
    target = encode_model_action(model, 0., 20.)
    c0_target = encode_model_action(zero_heading, 0., 20.)
    assert target.path_offset == c0_target.path_offset
    output = actual.update(model, 0., speed=20., dt=.01)
    c0_output = reference.update(zero_heading, 0., speed=20., dt=.01)
    assert actual.c0 == reference.c0
    assert output.path_offset == c0_output.path_offset


@pytest.mark.parametrize('sign', [-1., 1.])
def test_large_geometry_keeps_existing_field_caps_and_zero_c2_c3(sign):
  controller = ModelActionController()
  model = model_path([0.]*4, origin=.8, offset=20., sign=sign)
  for _ in range(150):
    out = controller.update(model, 0., speed=20., dt=.01)
    assert out.valid
    assert abs(out.path_offset) <= 5.11+1e-12
    assert abs(out.path_angle) <= .5+1e-12
    assert out.curvature == out.curvature_rate == 0.
  assert out.path_offset == pytest.approx(sign*5.11)
  assert out.path_angle == pytest.approx(sign*.5)


@pytest.mark.parametrize('field', ['x', 'y', 'z'])
def test_nonfinite_geometry_cannot_publish_a_release_request(field):
  model = model_path([0., .24, .48, .54])
  values = getattr(model.orientation if field == 'z' else model.position, field)
  values[2] = math.nan
  assert not encode_model_action(model, 0., 20.).valid


def test_unrepresentable_terminal_slope_falls_back_to_finite_original_heading():
  times = [0., .5, 1.]
  model = SimpleNamespace(position=SimpleNamespace(t=times, x=[0., 5e-320, 1e-319], y=[0.]*3),
                          orientation=SimpleNamespace(t=times, z=[0., .2, .4]))
  out = encode_model_action(model, 0., 20.)
  assert out.valid
  assert np.isfinite(out.path_angle)
  assert out.path_angle == pytest.approx(.4)
