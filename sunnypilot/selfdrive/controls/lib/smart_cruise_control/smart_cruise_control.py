"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""


class SmartCruiseControl:
  def update(self, sm, v_ego, a_ego, v_cruise):
    # decoupled from carControl.longActive, so we allow ICBM to use this state
    long_active = sm['carControl'].enabled and not sm['carState'].gasPressed  # noqa: F841

    targets = {
      # FIXME-SP: remove cruise once we have additional sources
      'cruise': (v_cruise, a_ego),
    }

    src = min(targets, key=lambda k: targets[k][0])
    _v_target, _a_target = targets[src]

    return _v_target, _a_target
