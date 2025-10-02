"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np

from opendbc.car import structs, DT_CTRL, rate_limit
from opendbc.car.hyundai.values import HyundaiFlags
from opendbc.sunnypilot.car.hyundai.longitudinal.config import CarTuningConfig, TUNING_CONFIGS, CAR_SPECIFIC_CONFIGS

JERK_THRESHOLD = 0.1
JERK_STEP = 0.1


class LongitudinalTuningType:
  OFF = 0
  DYNAMIC = 1
  PREDICTIVE = 2


def create_config_from_params(params_dict: dict[str, str], base_config: CarTuningConfig) -> CarTuningConfig:
  """Create a CarTuningConfig from parameter values."""
  return CarTuningConfig(
    accel_min=float(params_dict.get("LongTuningAccelMin", str(base_config.accel_min))),
    accel_max=float(params_dict.get("LongTuningAccelMax", str(base_config.accel_max))),
    v_ego_stopping=float(params_dict.get("LongTuningVEgoStopping", str(base_config.v_ego_stopping))),
    stopping_decel_rate=float(params_dict.get("LongTuningStoppingDecelRate", str(base_config.stopping_decel_rate))),
    jerk_limits=float(params_dict.get("LongTuningJerkLimits", str(base_config.jerk_limits))),
    min_upper_jerk=float(params_dict.get("LongTuningMinUpperJerk", str(base_config.min_upper_jerk))),
    min_lower_jerk=float(params_dict.get("LongTuningMinLowerJerk", str(base_config.min_lower_jerk))),
  )


def get_car_config(CP: structs.CarParams, params_dict: dict[str, str] = None) -> CarTuningConfig:
  base_config = _get_base_config(CP)

  if params_dict and int(params_dict.get("LongTuningCustomToggle", 0)) == 1:
    return create_config_from_params(params_dict, base_config)

  return base_config


def _get_base_config(CP: structs.CarParams) -> CarTuningConfig:
  """Extract base config selection logic for reuse."""
  base_config = CAR_SPECIFIC_CONFIGS.get(CP.carFingerprint)
  if base_config is None:
    if CP.flags & HyundaiFlags.CANFD:
      base_config = TUNING_CONFIGS["CANFD"]
    elif CP.flags & HyundaiFlags.EV:
      base_config = TUNING_CONFIGS["EV"]
    elif CP.flags & HyundaiFlags.HYBRID:
      base_config = TUNING_CONFIGS["HYBRID"]
    else:
      base_config = TUNING_CONFIGS["DEFAULT"]
  return base_config


def get_longitudinal_tune(CP: structs.CarParams, params_dict: dict[str, str] = None) -> None:
  config = get_car_config(CP, params_dict)
  CP.vEgoStopping = config.v_ego_stopping
  CP.vEgoStarting = config.v_ego_starting
  CP.stoppingDecelRate = config.stopping_decel_rate
  CP.startingState = False
  CP.longitudinalActuatorDelay = config.longitudinal_actuator_delay


def jerk_limited_integrator(desired_accel, last_accel, jerk_upper, jerk_lower) -> float:
  if desired_accel >= last_accel:
    val = jerk_upper * DT_CTRL * 2
  else:
    val = jerk_lower * DT_CTRL * 2

  return rate_limit(desired_accel, last_accel, -val, val)


def ramp_update(current, target, min_value=None):
  error = target - current
  if abs(error) > JERK_THRESHOLD:
    next_val = current + float(np.clip(error, -JERK_STEP, JERK_STEP))
  else:
    next_val = target
  if min_value is not None:
    next_val = max(min_value, next_val)
  return next_val
