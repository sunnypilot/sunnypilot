"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from enum import IntEnum


class Policy(IntEnum):
  map_data_only = 0
  car_state_only = 1
  map_data_priority = 2
  car_state_priority = 3
  combined = 4
