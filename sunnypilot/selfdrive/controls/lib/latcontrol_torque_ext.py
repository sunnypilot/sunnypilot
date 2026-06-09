"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np

from openpilot.sunnypilot.selfdrive.controls.lib.nnlc.nnlc import NeuralNetworkLateralControl
from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_torque_ext_override import LatControlTorqueExtOverride


class LatControlTorqueExt(NeuralNetworkLateralControl, LatControlTorqueExtOverride):
  def __init__(self, lac_torque, CP, CP_SP, CI):
    NeuralNetworkLateralControl.__init__(self, lac_torque, CP, CP_SP, CI)
    LatControlTorqueExtOverride.__init__(self, CP)

  def update(self, CS, VM, pid, params, ff, pid_log, setpoint, measurement, calibrated_pose, roll_compensation,
             desired_lateral_accel, actual_lateral_accel, lateral_accel_deadzone, gravity_adjusted_lateral_accel,
             desired_curvature, actual_curvature, steer_limited_by_safety, output_torque):
    # Store vEgo for update_override_torque_params (which runs before this, next frame)
    self._last_vego = CS.vEgo
    self._ff = ff
    self._pid = pid
    self._pid_log = pid_log
    self._setpoint = setpoint
    self._measurement = measurement
    self._roll_compensation = roll_compensation
    self._lateral_accel_deadzone = lateral_accel_deadzone
    self._desired_lateral_accel = desired_lateral_accel
    self._actual_lateral_accel = actual_lateral_accel
    self._desired_curvature = desired_curvature
    self._actual_curvature = actual_curvature
    self._gravity_adjusted_lateral_accel = gravity_adjusted_lateral_accel
    self._steer_limited_by_safety = steer_limited_by_safety
    self._output_torque = output_torque

    self.update_calculations(CS, VM, desired_lateral_accel)
    self.update_neural_network_feedforward(CS, params, calibrated_pose)

    return self._pid_log, self._output_torque

  def update_speed_dep_torque(self, tp):
    """Apply speed-dependent learned values from torqued.
    Uses learned values for valid bins. For invalid bins, falls back to
    TOML seed values if available for this car, otherwise global filtered."""
    speed_bp = list(tp.speedBinCenters)
    if not speed_bp:
      self._speed_dep_active = False
      return

    factors = list(tp.speedBinLatAccelFactors)
    frictions = list(tp.speedBinFrictions)
    valid_bp = list(tp.speedBinValid)

    if self._speed_dep_car_cfg is None:
      from opendbc.sunnypilot.car.interfaces import get_speed_dep_config
      self._speed_dep_car_cfg = get_speed_dep_config().get(self.CP.carFingerprint, {})
    cfg = self._speed_dep_car_cfg
    seed_lafs = cfg.get('laf_bp')
    seed_frictions = cfg.get('friction_bp')
    if (seed_lafs and seed_frictions and
        len(seed_lafs) == len(speed_bp) and len(seed_frictions) == len(speed_bp)):
      fallback_factors = seed_lafs
      fallback_frictions = seed_frictions
    else:
      global_factor = tp.latAccelFactorFiltered
      global_fric = tp.frictionCoefficientFiltered
      fallback_factors = [global_factor] * len(speed_bp)
      fallback_frictions = [global_fric] * len(speed_bp)

    self._speed_dep_active = True
    self._speed_dep_speed_bp = speed_bp
    self._speed_dep_lat_accel_factor_bp = [factors[i] if valid_bp[i] else fallback_factors[i] for i in range(len(speed_bp))]
    self._speed_dep_friction_bp = [frictions[i] if valid_bp[i] else fallback_frictions[i] for i in range(len(speed_bp))]

    # Set representative values at 20 m/s for PID limits (actual per-frame
    # interpolation happens in update_override_torque_params before each frame)
    self.lac_torque.torque_params.latAccelFactor = float(np.interp(20.0, speed_bp, self._speed_dep_lat_accel_factor_bp))
    self.lac_torque.torque_params.latAccelOffset = tp.latAccelOffsetFiltered
    self.lac_torque.torque_params.friction = float(np.interp(20.0, speed_bp, self._speed_dep_friction_bp))
    self.lac_torque.update_limits()
