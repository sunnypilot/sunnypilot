"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from opendbc.car.lateral import FRICTION_THRESHOLD
from opendbc.sunnypilot.car.interfaces import LatControlInputs
from opendbc.sunnypilot.car.lateral_ext import get_friction as get_friction_in_torque_space
from openpilot.common.params import Params

from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_torque_ext_base import LatControlTorqueExtBase


class LatControlTorqueJerkAware(LatControlTorqueExtBase):
  def __init__(self, lac_torque, CP, CP_SP, CI):
    super().__init__(lac_torque, CP, CP_SP, CI)
    self.params = Params()
    self._jerk_aware_enabled = self.params.get_bool("LateralJerkTorqueController")

  def update_limits(self):
    if not self._jerk_aware_enabled:
      return
    self._pid.set_limits(self.lac_torque.steer_max, -self.lac_torque.steer_max)

  def update_jerk_aware_torque_control(self, CS, roll_compensation, gravity_adjusted_lateral_accel):
    if not self._jerk_aware_enabled:
      return

    torque_from_setpoint = self.torque_from_lateral_accel_in_torque_space(
      LatControlInputs(self._setpoint, roll_compensation, CS.vEgo, CS.aEgo), self.torque_params, gravity_adjusted=False
    )
    torque_from_measurement = self.torque_from_lateral_accel_in_torque_space(
      LatControlInputs(self._measurement, roll_compensation, CS.vEgo, CS.aEgo), self.torque_params, gravity_adjusted=False
    )

    self._pid_log.error = float(torque_from_setpoint - torque_from_measurement)  # ty: ignore[invalid-assignment]
    self._ff = self.torque_from_lateral_accel_in_torque_space(
      LatControlInputs(gravity_adjusted_lateral_accel, roll_compensation, CS.vEgo, CS.aEgo), self.torque_params, gravity_adjusted=True
    )

    friction_input = self.update_friction_input(self._desired_lateral_accel, self._actual_lateral_accel)
    self._ff += get_friction_in_torque_space(friction_input, self._lateral_accel_deadzone, FRICTION_THRESHOLD, self.torque_params)

    self.update_output_torque(CS)
