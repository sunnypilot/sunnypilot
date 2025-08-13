"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

from opendbc.car import structs
from opendbc.car.interfaces import CarStateBase

TORQUE_TO_ANGLE_MULTIPLIER_OUTER = 4  # Higher = easier to influence when manually steering more than OP
TORQUE_TO_ANGLE_MULTIPLIER_INNER = 8  # Higher = easier to influence when manually steering less than OP
TORQUE_TO_ANGLE_DEADZONE = 0.5  # This equates to hands-on level 1, so we don't allow override if not hands-on
TORQUE_TO_ANGLE_CLIP = 10.  # Steering (usually) disengages at 2.5 Nm, this limit exists only in case the EPAS gives bad data
CONTINUED_OVERRIDE_ANGLE = 10.  # The angle difference between OP and user to continue overriding steering (prevents oscillation)

LOW_SPEED_ALLOWED = False
LOW_SPEED_THRESHOLD = 6.7  # ~15 MPH


def get_allowed_speed(speed: float) -> bool:
  return (LOW_SPEED_ALLOWED and speed < LOW_SPEED_THRESHOLD) or speed >= LOW_SPEED_THRESHOLD


class TorqueBlendingCarController:
  def __init__(self):
    self.enabled = True  # TODO-SP: always on for now, couple with toggle
    self.steering_override = False

  @staticmethod
  def torque_blended_angle(apply_angle, torsion_bar_torque):
    deadzone = TORQUE_TO_ANGLE_DEADZONE
    if abs(torsion_bar_torque) < deadzone:
      return apply_angle

    limit = TORQUE_TO_ANGLE_CLIP
    if apply_angle * torsion_bar_torque >= 0:
      # user override in the same direction
      strength = TORQUE_TO_ANGLE_MULTIPLIER_OUTER
    else:
      # user override in the opposite direction
      strength = TORQUE_TO_ANGLE_MULTIPLIER_INNER

    torque = torsion_bar_torque - deadzone if torsion_bar_torque > 0 else torsion_bar_torque + deadzone
    return apply_angle + np.clip(torque, -limit, limit) * strength

  def update_torque_blending(self, CS: CarStateBase, CC: structs.CarControl, lat_active: bool, apply_angle: float) -> tuple[bool, float]:
    if not self.enabled or not get_allowed_speed(CS.out.vEgo):
      return lat_active, apply_angle

    # Detect user override of the steering wheel
    self.steering_override = CS.hands_on_level >= 3 or \
                             (CS.out.steeringPressed and
                              abs(CS.out.steeringAngleDeg - apply_angle) > CONTINUED_OVERRIDE_ANGLE and
                              not CS.out.standstill)

    # Reset steering override when lateral control is inactive
    if not CC.latActive:
      self.steering_override = False

    lat_active = CC.latActive and not self.steering_override

    apply_angle = self.torque_blended_angle(apply_angle, CS.out.steeringTorque)

    return lat_active, apply_angle


class TorqueBlendingCarState:
  def __init__(self):
    self.enabled = True  # TODO-SP: always on for now, couple with toggle

  def update_torque_blending(self, ret: structs.CarState, eac_status: str, eac_error_code: str) -> None:
    if not self.enabled or not get_allowed_speed(ret.vEgo):
      return

    ret.steeringDisengage = (eac_status == "EAC_INHIBITED" and eac_error_code == "EAC_ERROR_HIGH_ANGLE_RATE_SAFETY")
