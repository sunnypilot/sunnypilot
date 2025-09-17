"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import messaging


class SmartCruiseControl:

  def update(self, sm: messaging.SubMaster, v_ego: float, a_ego: float, v_cruise: float):
    pass
