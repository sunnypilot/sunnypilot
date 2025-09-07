"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import custom, log

from openpilot.common.constants import CV
from openpilot.common.params import Params

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

  def read_params(self):
    self.enabled = self.params.get_bool("LaneTurnDesire")
    value = float(self.params.get("LaneTurnValue", return_default=True)) * CV.MPH_TO_MS
    self.lane_turn_value = min(float(LANE_CHANGE_SPEED_MIN), value)

  def update_params(self) -> None:
    if self.param_read_counter % 50 == 0:
      self.read_params()
    self.param_read_counter += 1

  def update_lane_turn(self, blindspot_left: bool, blindspot_right: bool, left_blinker: bool, right_blinker: bool, v_ego: float) -> None:
    if self.enabled and left_blinker and not right_blinker and v_ego < self.lane_turn_value and not blindspot_left:
      self.turn_direction = custom.TurnDirection.turnLeft
    elif self.enabled and right_blinker and not left_blinker and v_ego < self.lane_turn_value and not blindspot_right:
      self.turn_direction = custom.TurnDirection.turnRight
    else:
      self.turn_direction = custom.TurnDirection.none

  def return_desire(self, nudge_mode: bool, steering_pressed: bool, steering_torque: float) -> log.Desire:
    # Return the current Desire for lane-turns.
    # disabled or no turn -> return none
    if not self.enabled or self.turn_direction == custom.TurnDirection.none:
      return log.Desire.none

    if nudge_mode:
      # In nudge mode, require steering torque for lane turn
      turn_torque_applied = steering_pressed and ((steering_torque > 0 and self.turn_direction == custom.TurnDirection.turnLeft) or
                             (steering_torque < 0 and self.turn_direction == custom.TurnDirection.turnRight))
      if not turn_torque_applied:
        return log.Desire.none

    return TURN_DESIRES[self.turn_direction]

  def update(self, blindspot_left: bool, blindspot_right: bool, left_blinker: bool, right_blinker: bool, v_ego: float,
             lane_change_nudge_mode: bool, steering_pressed: bool, steering_torque: float) -> log.Desire:
    self.update_params()
    self.update_lane_turn(blindspot_left, blindspot_right, left_blinker, right_blinker, v_ego)
    self.DH.lane_turn_direction = self.turn_direction
    return self.return_desire(lane_change_nudge_mode, steering_pressed, steering_torque)
