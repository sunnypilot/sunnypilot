"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from opendbc.car.interfaces import LatControlInputs
from openpilot.common.params import Params

from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_torque_ext_base import LatControlTorqueExtBase


class LatControlTorqueEnhancedLateralAccel(LatControlTorqueExtBase):
  def __init__(self, lac_torque, CP, CP_SP):
    super().__init__(lac_torque, CP, CP_SP)
    self.params = Params()
    self.enabled = self.params.get_bool("LatTorqueControlEnhancedLateralAccel")

  def update_custom_lateral_acceleration(self, CS, roll_compensation, gravity_adjusted_lateral_accel):
    if not self.enabled:
      return

    friction_input = self.update_friction_input(self._desired_lateral_accel, self._actual_lateral_accel)

    torque_from_setpoint = self.torque_from_lateral_accel(
      LatControlInputs(self._setpoint, roll_compensation, CS.vEgo, CS.aEgo), self.torque_params,
      self.lateral_jerk_setpoint, self._lateral_accel_deadzone, friction_compensation=self.enabled, gravity_adjusted=False
    )

    torque_from_measurement = self.torque_from_lateral_accel(
      LatControlInputs(self._measurement, roll_compensation, CS.vEgo, CS.aEgo), self.torque_params,
      self.lateral_jerk_measurement, self._lateral_accel_deadzone, friction_compensation=self.enabled, gravity_adjusted=False
    )

    self._pid_log.error = float(torque_from_setpoint - torque_from_measurement)
    self._ff = self.torque_from_lateral_accel(LatControlInputs(gravity_adjusted_lateral_accel, roll_compensation, CS.vEgo, CS.aEgo), self.torque_params,
                                              friction_input, self._lateral_accel_deadzone, friction_compensation=True,
                                              gravity_adjusted=True)
