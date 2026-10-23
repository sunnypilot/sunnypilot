"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from openpilot.sunnypilot import IntEnumBase


class Policy(IntEnumBase):
  car_state_only = 0
  map_data_only = 1
  car_state_priority = 2
  map_data_priority = 3
  combined = 4


class OffsetType(IntEnumBase):
  off = 0
  fixed = 1
  percentage = 2


class Mode(IntEnumBase):
  off = 0
  information = 1
  warning = 2
  assist = 3
