"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from dataclasses import dataclass

@dataclass
class DynamicSteeringParams:
    steerMax: float
    steerDeltaUp: float
    steerDeltaDown: float
    kp: float
    ki: float
    kf: float

class ToyotaSafetyFlagsSP:
  DEFAULT = 0
  UNSUPPORTED_DSU = 1
