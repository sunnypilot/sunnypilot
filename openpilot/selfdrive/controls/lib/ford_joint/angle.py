"""Measurement states of the recovered curvature-to-angle stage, before torque."""

import math

from openpilot.selfdrive.controls.lib.ford_joint.model import bracket, interp_int, clip


class AngleModel:
  def __init__(self, cal):
    self.cal = cal
    self.speed_bp = cal.read(0xFEF25E40, '8H')
    self.tables = {address: cal.read(address, '8H') for address in (0xFEF25CA0, 0xFEF25CB0)}
    self.yaw_acc = self.bank_residual = self.angle_bias = 0.0

  def step(self, speed_kmh, curvature, angle, yaw, accel, wheelbase, ratio):
    c = self.cal
    si, sf = bracket(int(speed_kmh * 256) & 0xFFFF, self.speed_bp)
    v = speed_kmh / 3.6
    self.yaw_acc += c.h(0xFEF25A90) / 65536 * (v * yaw - self.yaw_acc)
    self.bank_residual += c.h(0xFEF25A88) / 65536 * (accel - v * yaw - self.bank_residual)
    opposite = int(self.yaw_acc > 0) - int(self.yaw_acc < 0) != int(self.bank_residual > 0) - int(self.bank_residual < 0)
    allowance = 3.0 + (abs(self.bank_residual) if opposite else 0.0)
    requested_accel = clip(curvature * v * v, -allowance, allowance)
    control_accel = requested_accel * c.b(0xFEF25AB1) / 128 + interp_int(self.tables[0xFEF25CA0], si, sf) / 2048 * (requested_accel - self.yaw_acc)
    understeer = c.read(0xFEF25A9A, 'h')[0] / 16384
    floor_v = max(v, c.b(0xFEF25AB7) / 32, 1e-6)
    conversion = 180 / math.pi * ratio
    target = ((self.bank_residual * c.read(0xFEF25AB0, 'b')[0] / 64 + control_accel) * understeer + control_accel / floor_v**2 * wheelbase) * conversion
    error = (floor_v * understeer * yaw + yaw / floor_v * wheelbase) * conversion - angle - self.angle_bias
    self.angle_bias += interp_int(self.tables[0xFEF25CB0], si, sf) / 65536 * error
    return target + self.angle_bias * c.read(0xFEF25AB2, 'b')[0] / 64
