"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import custom, log

from openpilot.common.constants import CV
from openpilot.common.params import Params

LANE_CHANGE_SPEED_MIN = 50 * CV.MPH_TO_MS

TURN_STATE = {
  'OFF': 0,
  'NUDGE': 1,
  'NUDGELESS': 2
}

TURN_DESIRES = {
  custom.TurnDirection.none: log.Desire.none,
  custom.TurnDirection.turnLeft: log.Desire.turnLeft,
  custom.TurnDirection.turnRight: log.Desire.turnRight,
}


class LaneTurnController:
  def __init__(self):
    self.turn_direction = custom.TurnDirection.none
    self.params = Params()
    self.lane_turn_value = float(self.params.get("LaneTurnValue", return_default=True)) * CV.MPH_TO_MS
    self.param_read_counter = 0
    self.lane_turn_type = int(self.params.get("LaneTurnDesire", return_default=True))

  def read_params(self):
    self.lane_turn_type = int(self.params.get("LaneTurnDesire", return_default=True))
    value = float(self.params.get("LaneTurnValue", return_default=True)) * CV.MPH_TO_MS
    self.lane_turn_value = min(float(LANE_CHANGE_SPEED_MIN), value)

  def update_params(self) -> None:
    if self.param_read_counter % 50 == 0:
      self.read_params()
    self.param_read_counter += 1

  def update_lane_turn(self, blindspot_left: bool, blindspot_right: bool, left_blinker: bool, right_blinker: bool, v_ego: float) -> None:
    if self.lane_turn_type != TURN_STATE['OFF'] and left_blinker and not right_blinker and v_ego < self.lane_turn_value and not blindspot_left:
      self.turn_direction = custom.TurnDirection.turnLeft
    elif self.lane_turn_type != TURN_STATE['OFF'] and right_blinker and not left_blinker and v_ego < self.lane_turn_value and not blindspot_right:
      self.turn_direction = custom.TurnDirection.turnRight
    else:
      self.turn_direction = custom.TurnDirection.none

  def return_desire(self, steering_pressed: bool, steering_torque: float) -> log.Desire:
    # disabled or no turn -> return none
    if self.lane_turn_type == TURN_STATE['OFF'] or self.turn_direction == custom.TurnDirection.none:
      return log.Desire.none

    if self.lane_turn_type == TURN_STATE['NUDGE']:
      # In nudge mode, require steering press for turn desire
      turn_torque_applied = steering_pressed and ((steering_torque > 0 and self.turn_direction == custom.TurnDirection.turnLeft) or
                             (steering_torque < 0 and self.turn_direction == custom.TurnDirection.turnRight))
      if not turn_torque_applied:
        return log.Desire.none

    return TURN_DESIRES[self.turn_direction]

  def update(self, blindspot_left: bool, blindspot_right: bool, left_blinker: bool, right_blinker: bool, v_ego: float,
             steering_pressed: bool, steering_torque: float) -> log.Desire:
    self.update_params()
    self.update_lane_turn(blindspot_left, blindspot_right, left_blinker, right_blinker, v_ego)
    return self.return_desire(steering_pressed, steering_torque)

  def get_lane_turn_direction(self) -> custom.TurnDirection:
    return self.turn_direction
