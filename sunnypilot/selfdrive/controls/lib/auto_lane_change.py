"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from enum import IntEnum

from cereal import log
from openpilot.common.realtime import DT_MDL
from openpilot.common.params import Params


class AutoLaneChangeState(IntEnum):
  OFF = -1
  NUDGE = 0
  NUDGELESS = 1
  HALF_SECOND = 2
  ONE_SECOND = 3
  ONE_POINT_FIVE_SECOND = 4
  TWO_SECONDS = 5  # default


AUTO_LANE_CHANGE_TIMER = {
  AutoLaneChangeState.OFF: 0.0,                    # Off
  AutoLaneChangeState.NUDGE: 0.0,                  # Nudge
  AutoLaneChangeState.NUDGELESS: 0.1,              # Nudgeless
  AutoLaneChangeState.HALF_SECOND: 0.5,            # 0.5-second delay
  AutoLaneChangeState.ONE_SECOND: 1.0,             # 1-second delay
  AutoLaneChangeState.ONE_POINT_FIVE_SECOND: 1.5,  # 1.5-second delay
  AutoLaneChangeState.TWO_SECONDS: 2.0,            # 2 second delay default
}

TIMER_DISABLED = -1


class AutoLaneChangeController:
  def __init__(self, desire_helper):
    self.desire_helper = desire_helper
    self.param_s = Params()
    self.lane_change_wait_timer = 0.0
    self.param_read_counter = 0
    self.lane_change_set_timer = AutoLaneChangeState.NUDGE
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
      self.lane_change_set_timer = AutoLaneChangeState.NUDGE

  def update(self, blindspot_detected: bool, brake_pressed: bool):
    if self.param_read_counter % 50 == 0:
      self.read_params()
    self.param_read_counter += 1

    lane_change_delay = AUTO_LANE_CHANGE_TIMER.get(self.lane_change_set_timer,
                                                   AUTO_LANE_CHANGE_TIMER[AutoLaneChangeState.TWO_SECONDS])

    self.lane_change_wait_timer += DT_MDL

    if self.lane_change_bsm_delay and blindspot_detected and lane_change_delay:
      if lane_change_delay == AUTO_LANE_CHANGE_TIMER[AutoLaneChangeState.NUDGELESS]:
        self.lane_change_wait_timer = TIMER_DISABLED
      else:
        self.lane_change_wait_timer = lane_change_delay - 1


    # Auto lane change allowed if:
    # 1. A valid delay is set (non-zero)
    # 2. We've waited long enough
    # 3. Brake wasn't previously pressed
    auto_lane_change_allowed = lane_change_delay and \
                               self.lane_change_wait_timer > lane_change_delay and \
                               not self.prev_brake_pressed

    # Update previous brake state
    self.prev_brake_pressed = brake_pressed

    # Auto reset if parent state indicates we should
    if self.desire_helper.lane_change_state == log.LaneChangeState.off and \
       self.desire_helper.lane_change_direction == log.LaneChangeDirection.none:
      self.reset()

    return auto_lane_change_allowed
