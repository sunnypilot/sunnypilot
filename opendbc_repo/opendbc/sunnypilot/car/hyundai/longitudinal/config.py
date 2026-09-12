"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from dataclasses import dataclass, field

from opendbc.car.hyundai.values import CAR


@dataclass
class CarTuningConfig:
  lookahead_jerk_bp: list[float] = field(default_factory=lambda: [2., 5., 20.])
  lookahead_jerk_upper_v: list[float] = field(default_factory=lambda: [0.3, 0.45, 0.6])
  lookahead_jerk_lower_v: list[float] = field(default_factory=lambda: [0.3, 0.45, 0.6])
  longitudinal_actuator_delay: float = 0.50
  jerk_limits: float = 4.0


# Default configurations for different car types
TUNING_CONFIGS = {
  "CANFD": CarTuningConfig(),
  "EV": CarTuningConfig(),
  "HYBRID": CarTuningConfig(),
  "DEFAULT": CarTuningConfig(),
}

# Car-specific configs
CAR_SPECIFIC_CONFIGS = {
  CAR.KIA_NIRO_EV: CarTuningConfig(
    jerk_limits=3.3,
  ),
  CAR.KIA_NIRO_PHEV_2022: CarTuningConfig(
    jerk_limits=5.0,
  ),
}
