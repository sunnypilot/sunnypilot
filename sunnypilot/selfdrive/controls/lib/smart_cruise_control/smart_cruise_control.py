"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import messaging


class SmartCruiseControl:

  def update(self, sm: messaging.SubMaster, v_ego: float, a_ego: float, v_cruise: float) -> tuple[float, float]:
    targets = {
      # FIXME-SP: remove cruise once we have additional sources
      'cruise': (v_cruise, a_ego),
    }

    src = min(targets, key=lambda k: targets[k][0])
    _v_target, _a_target = targets[src]

    return _v_target, _a_target
