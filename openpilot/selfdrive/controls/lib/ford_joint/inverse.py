"""Invert the recovered angle-target stage; no torque or wheel plant model."""

import copy
import math

from openpilot.selfdrive.controls.lib.ford_joint.model import clip, interp_int, bracket

C0_BOUND = 5.11
C1_BOUND = 0.5
# Reference-calibration supervisor centre term clip(0.5 * held C0, +-0.5) saturates
# here. Held C0 beyond it adds primary curvature but no turn-direction supervisor
# allowance, and on release the supervisor keeps excluding zero demand until held
# C0 slews (1.5 m/s) back below about 0.41 m.
C0_SUPERVISOR_SATURATION = 1.0


def invert_angle(output, speed_kmh, target_angle, angle, yaw, accel, wheelbase, ratio, accel_allowance=3.0):
  """Invert 0x1818e6 BEFORE its separate angle-reference filter.

  The angle equation is affine in acceleration within the acceleration bounds.
  Predict only the measurement-driven states it updates this cycle. The unknown
  assist/load input occurs downstream and does not enter this calculation.
  """
  if not all(math.isfinite(x) for x in (speed_kmh, target_angle, angle, yaw, accel, wheelbase, ratio)):
    raise ValueError('Nonfinite input')
  if speed_kmh <= 0 or wheelbase <= 0 or ratio <= 0:
    raise ValueError('A moving vehicle with positive geometry is required')
  c = output.cal
  si, sf = bracket(int(speed_kmh * 256) & 0xFFFF, output.speed_bp)

  def tab(a):
    return interp_int(output.tables[a], si, sf)

  v = speed_kmh / 3.6
  yaw_acc = output.yaw_acc + c.h(0xFEF25A90) / 65536 * (v * yaw - output.yaw_acc)
  bank = output.bank_residual + c.h(0xFEF25A88) / 65536 * (accel - v * yaw - output.bank_residual)
  floor_v = max(v, c.b(0xFEF25AB7) / 32, 1e-6)
  understeer = c.read(0xFEF25A9A, 'h')[0] / 16384
  conversion = 180 / math.pi * ratio
  bias_error = (floor_v * understeer * yaw + yaw / floor_v * wheelbase) * conversion - angle - output.angle_bias
  bias = output.angle_bias + tab(0xFEF25CB0) / 65536 * bias_error
  p = tab(0xFEF25CA0) / 2048
  slope = (c.b(0xFEF25AB1) / 128 + p) * (understeer + wheelbase / floor_v**2) * conversion
  intercept = (-p * yaw_acc * (understeer + wheelbase / floor_v**2) + bank * c.read(0xFEF25AB0, 'b')[0] / 64 * understeer) * conversion
  intercept += bias * c.read(0xFEF25AB2, 'b')[0] / 64
  def sign(x):
    return int(x > 0) - int(x < 0)
  allowance = accel_allowance + (abs(bank) if sign(yaw_acc) != sign(bank) else 0)
  wanted_accel = (target_angle - intercept) / slope
  bounded_accel = clip(wanted_accel, -allowance, allowance)
  return {
    'curvature': bounded_accel / v**2,
    'wanted_accel': wanted_accel,
    'bounded_accel': bounded_accel,
    'allowance': allowance,
    'reachable_target': intercept + slope * bounded_accel,
    'accel_limited': abs(wanted_accel) > allowance,
    'slope_per_curvature': slope * v**2,
    'intercept': intercept,
  }


def static_pair(request, curvature, speed_kmh, *, gains=None):
  """Allocate equal nominal buildup times, hold C0 at most at the supervisor's C0
  saturation, then use remaining field capacity."""
  if gains is None:
    probe = copy.copy(request).step(speed_kmh, request.c0, request.c1, freeze_i=True)
    gains = probe['g0'], probe['g1']
  # Recovered normal held-input rates; the dynamic selector still accounts for
  # current held states, the fast latch, heading-dependent filter and release.
  r0, r1 = request.cal.f(0xFEF259F8), request.cal.f(0xFEF25A08)
  duration = curvature / (gains[0] * r0 + gains[1] * r1)
  p0, p1 = duration * r0, duration * r1
  if abs(p0) > C0_SUPERVISOR_SATURATION and gains[1]:
    # Only the held endpoint moves: the selector still builds with both fields,
    # then trades C0 for C1 at constant curvature before a release is needed.
    p0 = math.copysign(C0_SUPERVISOR_SATURATION, p0)
    p1 = (curvature - gains[0] * p0) / gains[1]
  c0, c1 = clip(p0, -C0_BOUND, C0_BOUND), clip(p1, -C1_BOUND, C1_BOUND)
  if abs(p0) > C0_BOUND or abs(p1) > C1_BOUND:
    # Clipping one field must not silently lower a target the pair can encode.
    if gains[0]:
      c0 = clip((curvature - gains[1] * c1) / gains[0], -C0_BOUND, C0_BOUND)
    if gains[1]:
      c1 = clip((curvature - gains[0] * c0) / gains[1], -C1_BOUND, C1_BOUND)
  return c0, c1


def quantize(pair):
  """Existing symmetric controller bounds; DBC LSBs, round nearest."""
  return (clip(round(pair[0] / 0.01) * 0.01, -C0_BOUND, C0_BOUND), clip(round(pair[1] / 0.0005) * 0.0005, -C1_BOUND, C1_BOUND))
