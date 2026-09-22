"""A field reaching its bound must not discard a jointly reachable target."""
import pytest

from openpilot.selfdrive.controls.lib.ford_joint.angle import AngleModel
from openpilot.selfdrive.controls.lib.ford_joint.encoder import PairedRelease
from openpilot.selfdrive.controls.lib.ford_joint.inverse import C0_BOUND, C0_SUPERVISOR_SATURATION, C1_BOUND, invert_angle, static_pair
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
  # Below the supervisor's C0 saturation the endpoint is still equal arrival.
  request = MainRequest(native_lookup=True)
  speed = 15 * 1.609344
  inverse = invert_angle(AngleModel(request.cal), speed, sign * 40., 0., 0., 0., 3.7, 16.9)
  c0, c1 = static_pair(request, inverse['curvature'], speed)
  assert abs(c0) < C0_SUPERVISOR_SATURATION
  assert c0 / request.cal.f(0xFEF259F8) == pytest.approx(c1 / request.cal.f(0xFEF25A08))
  probe = request.step(speed, 0., 0., freeze_i=True)
  assert probe['g0'] * c0 + probe['g1'] * c1 == pytest.approx(inverse['curvature'])


@pytest.mark.parametrize('speed', [8., 15., 19.312128, 24.14016, 28.968192, 50., 100., 180.])
@pytest.mark.parametrize('fraction', [.05, .2, .4, .6, .8, .95, 1.])
@pytest.mark.parametrize('sign', [-1., 1.])
def test_endpoint_holds_c0_at_supervisor_saturation(speed, fraction, sign):
  request = MainRequest(native_lookup=True)
  probe = request.step(speed, 0., 0., freeze_i=True)
  g0, g1 = probe['g0'], probe['g1']
  curvature = sign * fraction * (g0 * C0_BOUND + g1 * C1_BOUND)
  c0, c1 = static_pair(request, curvature, speed)
  assert g0 * c0 + g1 * c1 == pytest.approx(curvature, abs=1e-12)
  # Held C0 exceeds the supervisor saturation only when C1 alone cannot carry the rest.
  assert abs(c0) <= C0_SUPERVISOR_SATURATION + 1e-12 or abs(c1) == C1_BOUND
  assert static_pair(request, -curvature, speed) == pytest.approx((-c0, -c1), abs=1e-15)


def _equal_arrival(request, curvature, speed_kmh, *, gains):
  r0, r1 = request.cal.f(0xFEF259F8), request.cal.f(0xFEF25A08)
  duration = curvature / (gains[0] * r0 + gains[1] * r1)
  return duration * r0, duration * r1


@pytest.mark.parametrize('speed,curvature', [(15., .06), (20., .05), (25., .04)])
def test_capped_endpoint_keeps_entry_and_parks_c0_before_release(monkeypatch, speed, curvature):
  """Production selector, quantized packets: same rise, less held C0 at the end of the hold."""
  from openpilot.selfdrive.controls.lib.ford_joint import encoder
  from openpilot.selfdrive.controls.lib.ford_joint.inverse import quantize

  def run():
    m = MainRequest(native_lookup=True)
    selector = PairedRelease(m)
    sent, phase, rise = (0., 0.), 0., None
    for i in range(500):  # 5 s step-and-hold at 100 Hz
      phase += .01
      ticks = int((phase + 1e-12) / .008)
      phase -= ticks * .008
      for _ in range(ticks):
        m.step(speed, *sent, freeze_i=True)
      if rise is None and m.filtered >= .9 * curvature:
        rise = i * .01
      count = max(1, min(2, int((phase + .01 + 1e-12) / .008)))
      command, _ = selector.choose(speed, curvature, phase=0 if count == 2 else 2)
      sent = quantize(command)
    return rise, m.c0, m.filtered

  capped = run()
  monkeypatch.setattr(encoder, 'static_pair', _equal_arrival)
  equal = run()
  assert capped[0] == pytest.approx(equal[0], abs=.02)
  assert capped[2] == pytest.approx(curvature, rel=.01)
  assert abs(capped[1]) <= C0_SUPERVISOR_SATURATION + .15 < abs(equal[1])
