"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import log
from openpilot.common.realtime import DT_MDL
from openpilot.common.params import Params

AUTO_LANE_CHANGE_TIMER = {
  -1: 0.0,
  0: 0.0,
  1: 0.1,
  2: 0.5,
  3: 1.0,
  4: 1.5,
}


class AutoLaneChangeController:
  def __init__(self, desire_helper):
    self.desire_helper = desire_helper
    self.param_s = Params()
    self.lane_change_wait_timer = 0.0
    self.param_read_counter = 0
    self.lane_change_set_timer = 1
    self.lane_change_bsm_delay = False
    self.prev_brake_pressed = False
    self.read_params()

  def reset(self):
    self.lane_change_wait_timer = 0.0
    self.prev_brake_pressed = False

  def read_params(self):
    self.lane_change_bsm_delay = self.param_s.get_bool("AutoLaneChangeBsmDelay")
    try:
      self.lane_change_set_timer = int(self.param_s.get("AutoLaneChangeTimer", encoding="utf8"))
    except (ValueError, TypeError):
      self.lane_change_set_timer = 1

  def update(self, blindspot_detected: bool, brake_pressed: bool):
    if self.param_read_counter % 50 == 0:
      self.read_params()
    self.param_read_counter += 1

    lane_change_auto_timer = AUTO_LANE_CHANGE_TIMER.get(self.lane_change_set_timer, 2.0)

    self.lane_change_wait_timer += DT_MDL

    if self.lane_change_bsm_delay and blindspot_detected and lane_change_auto_timer:
      if lane_change_auto_timer == 0.1:
        self.lane_change_wait_timer = -1
      else:
        self.lane_change_wait_timer = lane_change_auto_timer - 1

    # Don't allow auto lane change if brake was previously pressed
    auto_lane_change_allowed = (lane_change_auto_timer and
                                self.lane_change_wait_timer > lane_change_auto_timer and
                                not self.prev_brake_pressed)

    # Update previous brake state
    self.prev_brake_pressed = brake_pressed

    # Auto reset if parent state indicates we should
    if self.desire_helper.lane_change_state == log.LaneChangeState.off and \
       self.desire_helper.lane_change_direction == log.LaneChangeDirection.none:
      self.reset()

    return auto_lane_change_allowed
