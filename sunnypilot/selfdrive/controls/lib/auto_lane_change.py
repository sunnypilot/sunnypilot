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
  TWO_SECONDS = 5
  THREE_SECONDS = 6  # default


AUTO_LANE_CHANGE_TIMER = {
  AutoLaneChangeState.OFF: 0.0,                    # Off
  AutoLaneChangeState.NUDGE: 0.0,                  # Nudge
  AutoLaneChangeState.NUDGELESS: 0.1,              # Nudgeless
  AutoLaneChangeState.HALF_SECOND: 0.5,            # 0.5-second delay
  AutoLaneChangeState.ONE_SECOND: 1.0,             # 1-second delay
  AutoLaneChangeState.TWO_SECONDS: 2.0,            # 2-second delay
  AutoLaneChangeState.THREE_SECONDS: 3.0,          # 3-second delay
}

TIMER_DISABLED = -1


class AutoLaneChangeController:
  def __init__(self, desire_helper):
    self.DH = desire_helper
    self.params = Params()
    self.lane_change_wait_timer = 0.0
    self.param_read_counter = 0
    self.lane_change_set_timer = AutoLaneChangeState.NUDGE
    self.lane_change_bsm_delay = False
    self.prev_brake_pressed = False
    self.lane_change_delay = 0.0
    self._blindspot_detected = False
    self._brake_pressed = False
    self.auto_lane_change_allowed = False
    self.read_params()

  def reset(self):
    # Auto reset if parent state indicates we should
    if self.DH.lane_change_state == log.LaneChangeState.off and \
       self.DH.lane_change_direction == log.LaneChangeDirection.none:
      self.lane_change_wait_timer = 0.0
      self.prev_brake_pressed = False

  def read_params(self):
    self.param_read_counter += 1
    if self.param_read_counter % 50 == 0:
      self.lane_change_bsm_delay = self.params.get_bool("AutoLaneChangeBsmDelay")
      try:
        self.lane_change_set_timer = int(self.params.get("AutoLaneChangeTimer", encoding="utf8"))
      except (ValueError, TypeError):
        self.lane_change_set_timer = AutoLaneChangeState.NUDGE

  def update_lane_change_timers(self):
    self.lane_change_delay = AUTO_LANE_CHANGE_TIMER.get(self.lane_change_set_timer,
                                                        AUTO_LANE_CHANGE_TIMER[AutoLaneChangeState.THREE_SECONDS])

    self.lane_change_wait_timer += DT_MDL

    if self.lane_change_bsm_delay and self._blindspot_detected and self.lane_change_delay:
      if self.lane_change_delay == AUTO_LANE_CHANGE_TIMER[AutoLaneChangeState.NUDGELESS]:
        self.lane_change_wait_timer = TIMER_DISABLED
      else:
        self.lane_change_wait_timer = self.lane_change_delay - 1

  def update_allowed(self):
    # Auto lane change allowed if:
    # 1. A valid delay is set (non-zero)
    # 2. We've waited long enough
    # 3. Brake wasn't previously pressed
    self.auto_lane_change_allowed = self.lane_change_delay and \
                                    self.lane_change_wait_timer > self.lane_change_delay and \
                                    not self.prev_brake_pressed

  def update(self, blindspot_detected: bool, brake_pressed: bool):
    self.read_params()
    self._blindspot_detected = blindspot_detected
    self._brake_pressed = brake_pressed

    self.update_lane_change_timers()
    self.update_allowed()

    self.prev_brake_pressed = self._brake_pressed
