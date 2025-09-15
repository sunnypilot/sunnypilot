"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.sunnypilot.selfdrive.controls.lib.smart_cruise_control.vision_controller import SmartCruiseControlVision


class SmartCruiseControl:
  def __init__(self, CP):
    self.vision = SmartCruiseControlVision(CP)

  def update(self, sm, v_ego, a_ego, v_cruise):
    # decoupled from carControl.longActive, so we allow ICBM to use this state
    long_active = sm['carControl'].enabled and not sm['carState'].gasPressed

    self.vision.update(sm, long_active, v_ego, a_ego, v_cruise)

    targets = {
      'scc_v': (self.vision.output_v_target, self.vision.output_a_target),
    }

    src = min(targets, key=lambda k: targets[k][0])
    _v_target, _a_target = targets[src]

    return _v_target, _a_target
