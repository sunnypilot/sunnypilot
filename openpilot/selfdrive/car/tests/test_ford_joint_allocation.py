"""A field reaching its bound must not discard a jointly reachable target."""
import pytest

from openpilot.selfdrive.controls.lib.ford_joint.angle import AngleModel
from openpilot.selfdrive.controls.lib.ford_joint.encoder import PairedRelease
from openpilot.selfdrive.controls.lib.ford_joint.inverse import C0_BOUND, C1_BOUND, invert_angle, static_pair
from openpilot.selfdrive.controls.lib.ford_joint.model import MainRequest


@pytest.mark.parametrize('sign', [-1., 1.])
def test_joint_encoder_preserves_large_reachable_target(sign):
  request = MainRequest(native_lookup=True)
  speed = 15 * 1.609344
  inverse = invert_angle(AngleModel(request.cal), speed, sign * 280., 0., 0., 0., 3.7, 16.9)
  assert not inverse['accel_limited']
  probe = MainRequest(native_lookup=True).step(speed, 0., 0., freeze_i=True)
  c0, c1 = static_pair(request, inverse['curvature'], speed)
  assert abs(c1) <= C1_BOUND
  assert abs(c0) <= C0_BOUND
  assert probe['g0'] * c0 + probe['g1'] * c1 == pytest.approx(inverse['curvature'], abs=1e-12)

  _, info = PairedRelease(request).choose(speed, inverse['curvature'])
  # The planned target is the CAN-quantized steady pair, not next-tick wheel motion.
  quantization_error = probe['g0'] * .005 + probe['g1'] * .00025
  assert abs(info['planned_target'] - inverse['curvature']) <= quantization_error + 1e-12


@pytest.mark.parametrize('speed', [8., 15., 19.312128, 24.14016, 28.968192, 50., 100., 180.])
@pytest.mark.parametrize('fraction', [-2., -1., -.8, -.3, 0., .3, .8, 1., 2.])
def test_static_allocation_uses_available_combined_field_range(speed, fraction):
  request = MainRequest(native_lookup=True)
  probe = request.step(speed, 0., 0., freeze_i=True)
  g0, g1 = probe['g0'], probe['g1']
  capacity = g0 * C0_BOUND + g1 * C1_BOUND
  c0, c1 = static_pair(request, fraction * capacity, speed)
  assert abs(c0) <= C0_BOUND and abs(c1) <= C1_BOUND
  expected = max(-capacity, min(capacity, fraction * capacity))
  assert g0 * c0 + g1 * c1 == pytest.approx(expected, abs=1e-12)


@pytest.mark.parametrize('sign', [-1., 1.])
def test_unsaturated_pair_reaches_both_endpoints_together(sign):
  request = MainRequest(native_lookup=True)
  speed = 15 * 1.609344
  inverse = invert_angle(AngleModel(request.cal), speed, sign * 180., 0., 0., 0., 3.7, 16.9)
  c0, c1 = static_pair(request, inverse['curvature'], speed)
  assert c0 / request.cal.f(0xFEF259F8) == pytest.approx(c1 / request.cal.f(0xFEF25A08))
  probe = request.step(speed, 0., 0., freeze_i=True)
  assert probe['g0'] * c0 + probe['g1'] * c1 == pytest.approx(inverse['curvature'])
