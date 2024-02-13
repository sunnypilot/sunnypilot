# PFEIFER - VTSC

# Acknowledgements:
# Past versions of this code were based on the move-fast teams vtsc
# implementation. (https://github.com/move-fast/openpilot) Huge thanks to them
# for their initial implementation. I also used sunnypilot as a reference.
# (https://github.com/sunnyhaibin/sunnypilot) Big thanks for sunny's amazing work

import numpy as np
import time
from cereal import custom
from openpilot.common.conversions import Conversions as CV
from openpilot.common.params import Params
from openpilot.selfdrive.controls.lib.sunnypilot.helpers import debug

TARGET_LAT_A = 1.9  # m/s^2
MIN_TARGET_V = 5  # m/s

PARAMS_UPDATE_PERIOD = 5.

VisionTurnControllerState = custom.LongitudinalPlanSP.VisionTurnControllerState


def _description_for_state(turn_controller_state):
  if turn_controller_state == VisionTurnControllerState.disabled:
    return 'DISABLED'
  if turn_controller_state == VisionTurnControllerState.entering:
    return 'ENTERING'
  if turn_controller_state == VisionTurnControllerState.turning:
    return 'TURNING'
  if turn_controller_state == VisionTurnControllerState.leaving:
    return 'LEAVING'


class VisionTurnController:
  def __init__(self, CP):
    self._params = Params()
    self._CP = CP
    self._op_enabled = False
    self._gas_pressed = False
    self._is_enabled = self._params.get_bool("TurnVisionControl")
    self._last_params_update = 0.
    self._v_ego = 0.
    self._v_target = MIN_TARGET_V
    self._current_lat_acc = 0.
    self._max_pred_lat_acc = 0.
    self._v_cruise = 0.
    self._state = VisionTurnControllerState.disabled

    self._reset()

  @property
  def state(self):
    return self._state

  @state.setter
  def state(self, value):
    if value != self._state:
      debug(f"V-TSC: VisionTurnControllerState state: {_description_for_state(value)}")
      if value == VisionTurnControllerState.disabled:
        self._reset()
    self._state = value

  @property
  def v_target(self):
    return self._v_target

  @property
  def is_active(self):
    return self._state != VisionTurnControllerState.disabled and self._is_enabled

  @property
  def current_lat_acc(self):
    return self._current_lat_acc

  @property
  def max_pred_lat_acc(self):
    return self._max_pred_lat_acc

  def _reset(self):
    self._current_lat_acc = 0.
    self._max_pred_lat_acc = 0.

  def _update_params(self):
    t = time.monotonic()
    if t > self._last_params_update + PARAMS_UPDATE_PERIOD:
      self._is_enabled = self._params.get_bool("TurnVisionControl")
      self._last_params_update = t

  def _update_calculations(self, sm):
    rate_plan = np.array(np.abs(sm['modelV2'].orientationRate.z))
    vel_plan = np.array(sm['modelV2'].velocity.x)

    current_curvature = abs(
      sm['carState'].steeringAngleDeg * CV.DEG_TO_RAD / (self._CP.steerRatio * self._CP.wheelbase))
    self._current_lat_acc = current_curvature * self._v_ego**2

    # get the maximum lat accel from the model
    predicted_lat_accels = rate_plan * vel_plan
    self._max_pred_lat_acc = np.amax(predicted_lat_accels)

    # get the maximum curve based on the current velocity
    v_ego = max(self._v_ego, 0.1)  # ensure a value greater than 0 for calculations
    max_curve = self.max_pred_lat_acc / (v_ego**2)

    # Get the target velocity for the maximum curve
    self._v_target = (TARGET_LAT_A / max_curve) ** 0.5
    self._v_target = max(self._v_target, MIN_TARGET_V)

  def _state_transition(self):
    if not self._op_enabled or not self._is_enabled or self._gas_pressed or self._v_ego < MIN_TARGET_V:
      self.state = VisionTurnControllerState.disabled
      return

    # DISABLED
    if self.state == VisionTurnControllerState.disabled:
      if self._v_cruise > self._v_target:
        self.state = VisionTurnControllerState.turning
    # TURNING
    elif self.state == VisionTurnControllerState.turning:
      if not (self._v_cruise > self._v_target):
        self.state = VisionTurnControllerState.disabled

  def update(self, enabled, v_ego, v_cruise, sm):
    self._op_enabled = enabled
    self._gas_pressed = sm['carState'].gasPressed
    self._v_ego = v_ego
    self._v_cruise = v_cruise

    self._update_params()
    self._update_calculations(sm)
    self._state_transition()
