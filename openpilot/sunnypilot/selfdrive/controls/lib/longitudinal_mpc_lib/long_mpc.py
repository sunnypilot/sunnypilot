"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np

from opendbc.car.interfaces import ACCEL_MIN, ACCEL_MAX


class LongitudinalMpcSP:
  def __init__(self) -> None:
    self._accel_max_trajectory: tuple[float, ...] | None = None
    self._cruise_accel_max: float | None = None
    self._jerk_cost_multiplier = 1.0
    self.last_solution_status = 0

  def set_accel_controller_params(self, accel_max: tuple[float, ...] | None, jerk_cost_multiplier: float,
                                  cruise_accel_max: float | None = None) -> None:
    self._accel_max_trajectory = accel_max
    self._cruise_accel_max = cruise_accel_max
    self._jerk_cost_multiplier = jerk_cost_multiplier

  def cruise_accel_max(self, stock_accel_max: float) -> float:
    if self._cruise_accel_max is None or not np.isfinite(self._cruise_accel_max):
      return stock_accel_max
    return min(max(self._cruise_accel_max, 0.0), stock_accel_max)

  def scale_jerk_cost(self, jerk_cost: float) -> float:
    return jerk_cost * self._jerk_cost_multiplier

  def apply_accel_limits(self) -> None:
    if self._accel_max_trajectory is None:
      return

    accel_max = np.asarray(self._accel_max_trajectory)
    if accel_max.shape != self.params[:, 1].shape or accel_max.dtype.kind not in "iuf" or not np.all(np.isfinite(accel_max)):
      return

    self.params[:, 1] = np.clip(accel_max, 0.0, ACCEL_MAX)
    self.params[0, 1] = max(self.params[0, 1], float(np.clip(self.x0[2], ACCEL_MIN, ACCEL_MAX)))

  def save_solution_status(self) -> None:
    self.last_solution_status = self.solution_status
