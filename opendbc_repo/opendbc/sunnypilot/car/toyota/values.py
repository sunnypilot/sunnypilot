"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from enum import IntFlag

class ToyotaFlagsSP(IntFlag):
  SP_ENHANCED_BSM = 1
  SP_NEED_DEBUG_BSM = 2
  SP_AUTO_BRAKE_HOLD = 4

class ToyotaSafetyFlagsSP:
  DEFAULT = 0
  UNSUPPORTED_DSU = 1
