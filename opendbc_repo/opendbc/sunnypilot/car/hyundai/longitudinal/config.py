"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from dataclasses import dataclass, field

from opendbc.car.hyundai.values import CAR


@dataclass
class CarTuningConfig:
  v_ego_stopping: float = 0.285
  v_ego_starting: float = 0.10
  stopping_decel_rate: float = 0.30
  lookahead_jerk_bp: list[float] = field(default_factory=lambda: [2., 5., 20.])
  lookahead_jerk_upper_v: list[float] = field(default_factory=lambda: [0.25, 0.5, 1.0])
  lookahead_jerk_lower_v: list[float] = field(default_factory=lambda: [0.05, 0.10, 0.30])
  longitudinal_actuator_delay: float = 0.45
  jerk_limits: float = 4.0
  upper_jerk_v: list[float] = field(default_factory=lambda: [3.0, 3.0, 1.5])
  lower_jerk_v: list[float] = field(default_factory=lambda: [5.0, 8.0, 5.0])
  min_upper_jerk: float = 0.5
  min_lower_jerk: float = 1.6
  accel_min: float = -3.5
  accel_max: float = 2.0


# Default configurations for different car types
TUNING_CONFIGS = {
  "CANFD": CarTuningConfig(
    v_ego_stopping=0.365,
    lookahead_jerk_bp=[2., 5., 20.],
    lookahead_jerk_upper_v=[0.25, 0.5, 1.0],
    lookahead_jerk_lower_v=[0.10, 0.125, 0.325],
  ),
  "EV": CarTuningConfig(
    stopping_decel_rate=0.45,
    v_ego_stopping=0.3,
    lookahead_jerk_bp=[2., 5., 20.],
    lookahead_jerk_upper_v=[0.25, 0.5, 1.0],
    lookahead_jerk_lower_v=[0.10, 0.10, 0.30],
  ),
  "HYBRID": CarTuningConfig(
    v_ego_starting=0.15,
    stopping_decel_rate=0.45,
    v_ego_stopping=0.3,
  ),
  "DEFAULT": CarTuningConfig(
  )
}

# Car-specific configs
CAR_SPECIFIC_CONFIGS = {
  CAR.KIA_NIRO_EV: CarTuningConfig(
    stopping_decel_rate=0.05,
    v_ego_stopping=0.05,
    lower_jerk_v=[2.0, 3.0, 3.0],
    lookahead_jerk_bp=[2., 5., 20.],
    lookahead_jerk_upper_v=[1.0, 1.0, 1.0],
    lookahead_jerk_lower_v=[0.25, 0.35, 0.45],
    jerk_limits=2.5,
    accel_min=-2.5,
    accel_max=1.0,
  ),
  CAR.KIA_NIRO_PHEV_2022: CarTuningConfig(
    v_ego_stopping=0.3,
    upper_jerk_v=[2.0, 3.0, 1.6],
    jerk_limits=5.0,
    min_lower_jerk=3.0,
  )
}
