"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np
from dataclasses import dataclass

from opendbc.car import structs, DT_CTRL
from opendbc.car.interfaces import CarStateBase
from opendbc.car.hyundai.values import CarControllerParams
from opendbc.sunnypilot.car.hyundai.longitudinal.helpers import get_car_config, jerk_limited_integrator
from opendbc.sunnypilot.car.hyundai.values import HyundaiFlagsSP

LongCtrlState = structs.CarControl.Actuators.LongControlState

MIN_JERK = 0.5


@dataclass
class LongitudinalState:
  desired_accel: float = 0.0
  actual_accel: float = 0.0
  accel_last: float = 0.0
  jerk_upper: float = 0.0
  jerk_lower: float = 0.0
  comfort_band_upper: float = 0.0
  comfort_band_lower: float = 0.0
  stopping: bool = False


class LongitudinalController:
  """Longitudinal controller which gets injected into CarControllerParams."""

  def __init__(self, CP: structs.CarParams, CP_SP: structs.CarParamsSP) -> None:
    self.CP = CP
    self.CP_SP = CP_SP

    self.tuning = LongitudinalState()
    self.car_config = get_car_config(CP)
    self.long_control_state_last = LongCtrlState.off
    self.stopping_count = 0

    self.accel_cmd = 0.0
    self.desired_accel = 0.0
    self.actual_accel = 0.0
    self.accel_last = 0.0
    self.jerk_upper = 0.0
    self.jerk_lower = 0.0
    self.comfort_band_upper = 0.0
    self.comfort_band_lower = 0.0
    self.stopping = False

  @property
  def enabled(self) -> bool:
    return bool(self.CP_SP.flags & (HyundaiFlagsSP.LONG_TUNING_DYNAMIC | HyundaiFlagsSP.LONG_TUNING_PREDICTIVE))

  def get_stopping_state(self, actuators: structs.CarControl.Actuators) -> None:
    stopping = actuators.longControlState == LongCtrlState.stopping

    # If custom tuning is not enabled, use upstream stopping logic
    if not self.enabled:
      self.stopping = stopping
      self.stopping_count = 0
      return

    # Reset stopping state when not in stopping mode
    if not stopping:
      self.stopping = False
      self.stopping_count = 0
      return

    # When transitioning from off state to stopping
    if self.long_control_state_last == LongCtrlState.off:
      self.stopping = True
      return

    # Keep track of time in stopping state (in control cycles)
    if self.stopping_count > 1 / (DT_CTRL * 5):
      self.stopping = True

    self.stopping_count += 1

  def _calculate_speed_based_jerk_limits(self, velocity: float, long_control_state: LongCtrlState) -> tuple[float, float]:
    """Calculate jerk limits based on vehicle speed according to ISO 15622:2018.

    Args:
        velocity: Current vehicle speed (m/s)
        long_control_state: Current longitudinal control state

    Returns:
        Tuple of (upper_limit, lower_limit) in m/s³
    """

    if long_control_state == LongCtrlState.pid:
      upper_limit = float(np.interp(velocity, [0.0, 5.0, 20.0], [2.0, 3.0, 2.0]))
    else:
      upper_limit = 0.5  # Default for non-PID states

    if self.CP_SP.flags & HyundaiFlagsSP.LONG_TUNING_PREDICTIVE:
      lower_limit = float(np.interp(velocity, [0.0, 5.0, 20.0], [5.0, 3.5, 3.0]))
    else:
      lower_limit = float(np.interp(velocity, [0.0, 5.0, 20.0], [3.5, 3.5, 3.0]))

    return upper_limit, lower_limit

  def _calculate_lookahead_jerk(self, accel_error: float, velocity: float) -> tuple[float, float]:
    """Calculate lookahead jerk needed to reach target acceleration.

    Args:
        accel_error: Difference between target and current acceleration (m/s²)
        velocity: Current vehicle speed (m/s)

    Returns:
        Tuple of (upper_jerk, lower_jerk) in m/s³
    """

    # Time window to reach target acceleration, varies with speed
    future_t_upper = float(np.interp(velocity, self.car_config.lookahead_jerk_bp, self.car_config.lookahead_jerk_upper_v))
    future_t_lower = float(np.interp(velocity, self.car_config.lookahead_jerk_bp, self.car_config.lookahead_jerk_lower_v))

    # Required jerk to reach target acceleration in lookahead window
    j_ego_upper = accel_error / future_t_upper
    j_ego_lower = accel_error / future_t_lower

    jerk_limit = self.car_config.jerk_limits
    j_ego_upper = np.clip(j_ego_upper, -jerk_limit, jerk_limit)
    j_ego_lower = np.clip(j_ego_lower, -jerk_limit, jerk_limit)

    return float(j_ego_upper), float(j_ego_lower)

  def calculate_jerk(self, CC: structs.CarControl, CS: CarStateBase, long_control_state: LongCtrlState) -> None:
    """Calculate appropriate jerk limits for smooth acceleration/deceleration.

    Args:
        CC: Car control signals
        CS: Car state
        long_control_state: Current longitudinal control state
    """

    # If custom tuning is disabled, use upstream fixed values
    if not self.enabled:
      jerk_limit = 3.0 if long_control_state == LongCtrlState.pid else 1.0
      self.jerk_upper = jerk_limit
      self.jerk_lower = 5.0
      return

    velocity = CS.out.vEgo
    accel_error = self.accel_cmd - self.accel_last

    # Calculate jerk limits based on speed
    upper_speed_factor, lower_speed_factor = self._calculate_speed_based_jerk_limits(velocity, long_control_state)

    # Apply jerk limits based on tuning approach
    # Predictive tuning uses calculated desired jerk directly
    # Minimal Dynamic tuning applies only a speed based approach
    if self.CP_SP.flags & HyundaiFlagsSP.LONG_TUNING_PREDICTIVE:
      j_ego_upper, j_ego_lower = self._calculate_lookahead_jerk(accel_error, velocity)
      desired_jerk_upper = min(max(j_ego_upper, MIN_JERK), upper_speed_factor)
      desired_jerk_lower = min(max(-j_ego_lower, MIN_JERK), lower_speed_factor)

      self.jerk_upper = desired_jerk_upper
      self.jerk_lower = desired_jerk_lower if not self.CP.radarUnavailable else 5.0
    else:
      self.jerk_upper = upper_speed_factor
      self.jerk_lower = lower_speed_factor

    # Disable jerk when longitudinal control is inactive
    if not CC.longActive:
      self.jerk_upper = 0.0
      self.jerk_lower = 0.0

  def calculate_accel(self, CC: structs.CarControl) -> None:
    """Calculate commanded acceleration using jerk-limited approach.

    Args:
        CC: Car control signals
    """

    # Skip custom processing if tuning is disabled or radar unavailable
    if not self.enabled:
      self.desired_accel = self.accel_cmd
      self.actual_accel = self.accel_cmd
      return

    # Reset acceleration when control is inactive
    if not CC.longActive:
      self.desired_accel = 0.0
      self.actual_accel = 0.0
      self.accel_last = 0.0
      return

    # Force zero acceleration during stopping
    if self.stopping:
      self.desired_accel = 0.0
    else:
      self.desired_accel = float(np.clip(self.accel_cmd, CarControllerParams.ACCEL_MIN, CarControllerParams.ACCEL_MAX))

    # Apply jerk-limited integration to get smooth acceleration
    if not self.CP.radarUnavailable:
      self.actual_accel = jerk_limited_integrator(self.desired_accel, self.accel_last, self.jerk_upper, self.jerk_lower)
    else:
      self.actual_accel = self.desired_accel

    self.accel_last = self.actual_accel

  def calculate_comfort_band(self, CC: structs.CarControl, CS: CarStateBase) -> None:
    if not self.enabled or not CC.longActive:
      self.comfort_band_upper = 0.0
      self.comfort_band_lower = 0.0
      return

    accel = CS.out.aEgo
    accel_vals = [0.0, 0.3, 0.6, 0.9, 1.2, 2.0]
    decel_vals = [-3.5, -2.5, -1.5, -1.0, -0.5, -0.05]
    comfort_band_vals = [0.0, 0.02, 0.04, 0.06, 0.08, 0.10]

    if self.CP_SP.flags & HyundaiFlagsSP.LONG_TUNING_PREDICTIVE:
      self.comfort_band_upper = float(np.interp(accel, accel_vals, comfort_band_vals))
      self.comfort_band_lower = float(np.interp(accel, decel_vals, comfort_band_vals[::-1]))
    else:
      self.comfort_band_upper = float(np.interp(accel, [0.0, 2.0], [0.0, 0.04]))
      self.comfort_band_lower = float(np.interp(accel, [-3.5, -0.05], [0.04, 0.0]))

  def get_tuning_state(self) -> None:
    """Update the tuning state object with current control values.

    External components depend on this state for longitudinal control.
    """

    self.tuning = LongitudinalState(
      desired_accel=self.desired_accel,
      actual_accel=self.actual_accel,
      accel_last=self.accel_last,
      jerk_upper=self.jerk_upper,
      jerk_lower=self.jerk_lower,
      comfort_band_upper=self.comfort_band_upper,
      comfort_band_lower=self.comfort_band_lower,
      stopping=self.stopping,
    )

  def update(self, CC: structs.CarControl, CS: CarStateBase) -> None:
    """Update longitudinal control calculations.

    This is the main entry point called externally.

    Args:
        CC: Car control signals including actuators
        CS: Car state information
    """

    actuators = CC.actuators
    long_control_state = actuators.longControlState
    self.accel_cmd = CC.actuators.accel

    self.get_stopping_state(actuators)
    self.calculate_jerk(CC, CS, long_control_state)
    self.calculate_accel(CC)
    self.calculate_comfort_band(CC, CS)
    self.get_tuning_state()

    self.long_control_state_last = long_control_state

# TODO-SP Why were we calculating both jerks at once lol
