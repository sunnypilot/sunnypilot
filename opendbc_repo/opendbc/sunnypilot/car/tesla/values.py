"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from enum import IntFlag


class TeslaSafetyFlagsSP:
  DEFAULT = 0
  VIRTUAL_TORQUE_BLENDING = 1


class TeslaFlagsSP(IntFlag):
  VIRTUAL_TORQUE_BLENDING = 1
