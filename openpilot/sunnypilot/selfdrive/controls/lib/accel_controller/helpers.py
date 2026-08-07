import math

import numpy as np

from opendbc.car.interfaces import ACCEL_MIN, ACCEL_MAX
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import T_IDXS
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.constants import ACCEL_LIMIT_HORIZON_JERK, VEGO_NOISE_TOLERANCE


def is_valid_context(base_speed: float, v_ego: float, a_ego: float, planner_speed: float, planner_accel: float, stock_accel_max: float,
                     delay: float, engaged: bool, cruise_initialized: bool) -> bool:
  values = (base_speed, v_ego, a_ego, planner_speed, planner_accel, stock_accel_max, delay)
  return (engaged and cruise_initialized and base_speed >= 0.0 and v_ego >= -VEGO_NOISE_TOLERANCE
          and planner_speed >= 0.0 and stock_accel_max >= 0.0 and delay >= 0.0 and all(math.isfinite(value) for value in values))


def build_accel_ceiling(limit: float, planner_accel: float) -> tuple[float, ...] | None:
  if limit >= ACCEL_MAX - 1e-9:
    return None
  a0 = float(np.clip(planner_accel, ACCEL_MIN, ACCEL_MAX))
  ceiling = np.clip(np.maximum(limit, a0 - ACCEL_LIMIT_HORIZON_JERK * T_IDXS), 0.0, ACCEL_MAX)
  return tuple(float(value) for value in ceiling)
