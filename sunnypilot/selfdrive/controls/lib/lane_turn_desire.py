"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import custom, log

from openpilot.common.constants import CV
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL

LANE_CHANGE_SPEED_MIN = 20 * CV.MPH_TO_MS

TURN_DESIRES = {
  custom.TurnDirection.none: log.Desire.none,
  custom.TurnDirection.turnLeft: log.Desire.turnLeft,
  custom.TurnDirection.turnRight: log.Desire.turnRight,
}


class LaneTurnController:
  def __init__(self, desire_helper):
    self.DH = desire_helper
    self.turn_direction = custom.TurnDirection.none
    self.params = Params()
    self.lane_turn_value = float(self.params.get("LaneTurnValue", return_default=True)) * CV.MPH_TO_MS
    self.param_read_counter = 0
    self.enabled = self.params.get_bool("LaneTurnDesire")
    self.lane_turn_nudge_timer = 0.0

  def read_params(self):
    self.enabled = self.params.get_bool("LaneTurnDesire")
    value = float(self.params.get("LaneTurnValue", return_default=True)) * CV.MPH_TO_MS
    self.lane_turn_value = min(float(LANE_CHANGE_SPEED_MIN), value)

  def update_params(self) -> None:
    if self.param_read_counter % 50 == 0:
      self.read_params()
    self.param_read_counter += 1

  def update_lane_turn(self, blindspot_left: bool, blindspot_right: bool, left_blinker: bool, right_blinker: bool, v_ego: float) -> None:
    if left_blinker and not right_blinker and v_ego < self.lane_turn_value and not blindspot_left:
      self.turn_direction = custom.TurnDirection.turnLeft
    elif right_blinker and not left_blinker and v_ego < self.lane_turn_value and not blindspot_right:
      self.turn_direction = custom.TurnDirection.turnRight
    else:
      self.turn_direction = custom.TurnDirection.none

  def get_turn_direction(self):
    if not self.enabled:
      return custom.TurnDirection.none
    return self.turn_direction

  def get_desire(self, nudge_mode: bool) -> log.Desire:
    # Return the current Desire for lane-turns.
    # disabled or no turn -> reset timer and return none
    if not self.enabled or self.turn_direction == custom.TurnDirection.none:
      self.lane_turn_nudge_timer = 0.0
      return log.Desire.none

    # Normal (non-nudge) behavior: persistent turn desire
    if not nudge_mode:
      return TURN_DESIRES[self.turn_direction]

    # Nudge mode: pulse a turn desire once per second
    self.lane_turn_nudge_timer += DT_MDL
    if self.lane_turn_nudge_timer > 1.0:
      # reset and show the short pulse
      self.lane_turn_nudge_timer = 0.0
      return TURN_DESIRES[self.turn_direction]

    # most of the second the desire is cleared
    return log.Desire.none
