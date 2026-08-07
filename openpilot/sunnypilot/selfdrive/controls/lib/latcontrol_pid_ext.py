"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math

from openpilot.common.pid import PIDController
from openpilot.selfdrive.controls.lib.latcontrol_pid import LatControlPID

DECAY_TAU = 2.0  # seconds; starting guess, not validated against a real car


class DecayingIntegratorPIDController(PIDController):
  def __init__(self, *args, decay_tau=DECAY_TAU, **kwargs):
    super().__init__(*args, **kwargs)
    self.decay_tau = decay_tau

  def update(self, error, error_rate=0.0, speed=0.0, feedforward=0., freeze_integrator=False):
    if freeze_integrator:
      self.i *= math.exp(-self.i_dt / self.decay_tau)
    return super().update(error, error_rate=error_rate, speed=speed, feedforward=feedforward, freeze_integrator=freeze_integrator)


class LatControlPidSmooth(LatControlPID):
  def __init__(self, CP, CP_SP, CI, dt, decay_tau=DECAY_TAU):
    super().__init__(CP, CP_SP, CI, dt)
    self.pid = DecayingIntegratorPIDController(
      (CP.lateralTuning.pid.kpBP, CP.lateralTuning.pid.kpV),
      (CP.lateralTuning.pid.kiBP, CP.lateralTuning.pid.kiV),
      pos_limit=self.steer_max, neg_limit=-self.steer_max, decay_tau=decay_tau)
