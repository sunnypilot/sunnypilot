"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

import openpilot.cereal.messaging as messaging
from openpilot.cereal import custom
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.car.cruise import V_CRUISE_UNSET
from openpilot.sunnypilot import PARAMS_UPDATE_PERIOD
from openpilot.sunnypilot.selfdrive.controls.lib.smart_cruise_control import MIN_V

VisionState = custom.LongitudinalPlanSP.SmartCruiseControl.VisionState

ACTIVE_STATES = (VisionState.entering, VisionState.turning, VisionState.leaving)
ENABLED_STATES = (VisionState.enabled, VisionState.overriding, *ACTIVE_STATES)

_ENTERING_PRED_LAT_ACC_TH = 1.3  # Predicted Lat Acc threshold to trigger entering turn state.
_ABORT_ENTERING_PRED_LAT_ACC_TH = 1.1  # Predicted Lat Acc threshold to abort entering state if speed drops.

_TURNING_LAT_ACC_TH = 1.6  # Lat Acc threshold to trigger turning state.
_URGENT_PRED_LAT_ACC_TH = 3.  # Predicted Lat Acc threshold that requires an immediate speed reduction.

_LEAVING_LAT_ACC_TH = 1.3  # Lat Acc threshold to trigger leaving turn state.
_FINISH_LAT_ACC_TH = 1.1  # Lat Acc threshold to trigger the end of the turn cycle.

_A_LAT_REG_MAX = 2.  # Maximum lateral acceleration

_RELIEF_CONFIRMATION_FRAMES = max(1, int(round(0.5 / DT_MDL)))
_TARGET_TIGHTEN_CONFIRMATION_FRAMES = max(1, int(round(0.1 / DT_MDL)))
_TARGET_RELEASE_CONFIRMATION_FRAMES = max(1, int(round(0.15 / DT_MDL)))
_TARGET_TIGHTEN_RATE = 5.  # m/s^2
_TARGET_RELEASE_RATE = 1.  # m/s^2
_BELOW_EGO_TARGET_RELEASE_RATE = 3.  # m/s^2
_MIN_PRED_SPEED = 1.  # m/s
_MIN_ACTIVATION_SPEED = 10.  # m/s


class SmartCruiseControlVision:
  v_target: float = 0
  a_target: float = 0.
  v_ego: float = 0.
  a_ego: float = 0.
  output_v_target: float = V_CRUISE_UNSET
  output_a_target: float = 0.

  def __init__(self):
    self.params = Params()
    self.frame = -1
    self.long_enabled = False
    self.long_override = False
    self.is_enabled = False
    self.is_active = False
    self.enabled = self.params.get_bool("SmartCruiseControlVision")
    self.v_cruise_setpoint = 0.

    self.state = VisionState.disabled
    self.current_lat_acc = 0.
    self.max_pred_lat_acc = 0.
    self.relief_frames = 0
    self.tighten_frames = 0
    self.release_frames = 0

  def _v_demand(self) -> float:
    return max(MIN_V, min(self.v_target, self.v_cruise_setpoint))

  def _curve_is_urgent(self) -> bool:
    return self.current_lat_acc >= _TURNING_LAT_ACC_TH or self.max_pred_lat_acc >= _URGENT_PRED_LAT_ACC_TH

  def _filtered_v_target(self) -> float:
    demand = self._v_demand()

    if self.output_v_target == V_CRUISE_UNSET:
      self.tighten_frames = 0
      self.release_frames = 0
      if self._curve_is_urgent():
        return demand
      return max(demand, min(self.v_ego, self.v_cruise_setpoint))

    if demand < self.output_v_target:
      self.release_frames = 0
      if self._curve_is_urgent():
        self.tighten_frames = 0
        return demand

      self.tighten_frames += 1
      if self.tighten_frames < _TARGET_TIGHTEN_CONFIRMATION_FRAMES:
        return self.output_v_target
      return max(demand, self.output_v_target - _TARGET_TIGHTEN_RATE * DT_MDL)

    self.tighten_frames = 0
    releasing_brake = self.output_v_target < min(self.v_ego, demand)
    if not releasing_brake and self.relief_frames < _RELIEF_CONFIRMATION_FRAMES:
      self.release_frames = 0
      return self.output_v_target

    if demand > self.output_v_target:
      self.release_frames += 1
      if self.release_frames < _TARGET_RELEASE_CONFIRMATION_FRAMES:
        return self.output_v_target
    else:
      self.release_frames = 0

    release_rate = _BELOW_EGO_TARGET_RELEASE_RATE if releasing_brake else _TARGET_RELEASE_RATE
    return min(demand, self.output_v_target + release_rate * DT_MDL)

  def get_a_target_from_control(self) -> float:
    return self.a_ego

  def get_v_target_from_control(self) -> float:
    if self.is_active:
      return self._filtered_v_target()

    self.tighten_frames = 0
    self.release_frames = 0
    return V_CRUISE_UNSET

  def _update_params(self) -> None:
    if self.frame % int(PARAMS_UPDATE_PERIOD / DT_MDL) == 0:
      self.enabled = self.params.get_bool("SmartCruiseControlVision")

  def _update_calculations(self, sm: messaging.SubMaster) -> None:
    if not self.long_enabled:
      return

    rate_plan = np.asarray(np.abs(sm['modelV2'].orientationRate.z), dtype=float)
    vel_plan = np.asarray(sm['modelV2'].velocity.x, dtype=float)
    size = min(len(rate_plan), len(vel_plan))
    rate_plan, vel_plan = rate_plan[:size], vel_plan[:size]
    valid = np.isfinite(rate_plan) & np.isfinite(vel_plan) & (vel_plan >= _MIN_PRED_SPEED)

    self.current_lat_acc = self.v_ego ** 2 * abs(sm['controlsState'].curvature)
    self.max_pred_lat_acc = 0.
    self.v_target = V_CRUISE_UNSET
    if np.any(valid):
      self.max_pred_lat_acc = float(np.percentile(rate_plan[valid] * vel_plan[valid], 97))
      max_pred_curvature = float(np.percentile(rate_plan[valid] / vel_plan[valid], 97))
      if max_pred_curvature > 0.:
        self.v_target = min(float((_A_LAT_REG_MAX / max_pred_curvature) ** 0.5), V_CRUISE_UNSET)

  def _update_state_machine(self) -> tuple[bool, bool]:
    # ENABLED, ENTERING, TURNING, LEAVING, OVERRIDING
    relief = self.current_lat_acc < _FINISH_LAT_ACC_TH and self.max_pred_lat_acc < _ABORT_ENTERING_PRED_LAT_ACC_TH
    self.relief_frames = self.relief_frames + 1 if self.state in ACTIVE_STATES and relief else 0

    if self.state != VisionState.disabled:
      # longitudinal and feature disable always have priority in a non-disabled state
      if not self.long_enabled or not self.enabled:
        self.state = VisionState.disabled
      elif self.long_override:
        self.state = VisionState.overriding

      else:
        # ENABLED
        if self.state == VisionState.enabled:
          # Do not enter a turn control cycle if the speed is low.
          if self.v_ego <= _MIN_ACTIVATION_SPEED:
            pass
          # If significant lateral acceleration is predicted ahead, then move to Entering turn state.
          elif self.max_pred_lat_acc >= _ENTERING_PRED_LAT_ACC_TH:
            self.state = VisionState.entering

        # OVERRIDING
        elif self.state == VisionState.overriding:
          if not self.long_override:
            self.state = VisionState.enabled

        # ENTERING
        elif self.state == VisionState.entering:
          # Transition to Turning if current lateral acceleration is over the threshold.
          if self.current_lat_acc >= _TURNING_LAT_ACC_TH:
            self.state = VisionState.turning
          # Begin releasing only after both current and predicted lateral acceleration stay clear.
          elif self.relief_frames >= _RELIEF_CONFIRMATION_FRAMES:
            self.state = VisionState.leaving

        # TURNING
        elif self.state == VisionState.turning:
          # Transition out of Turning if current lateral acceleration drops below a threshold.
          if self.current_lat_acc <= _LEAVING_LAT_ACC_TH:
            self.state = VisionState.entering if self.max_pred_lat_acc >= _ENTERING_PRED_LAT_ACC_TH else VisionState.leaving

        # LEAVING
        elif self.state == VisionState.leaving:
          # Transition back to Turning if current lateral acceleration goes back over the threshold.
          if self.current_lat_acc >= _TURNING_LAT_ACC_TH:
            self.state = VisionState.turning
          # Start a new turn cycle immediately if another curve is predicted.
          elif self.max_pred_lat_acc >= _ENTERING_PRED_LAT_ACC_TH:
            self.state = VisionState.entering
          # Finish after confirmed relief and a gradual release to the cruise setpoint.
          elif self.relief_frames >= _RELIEF_CONFIRMATION_FRAMES and self.output_v_target >= self.v_cruise_setpoint:
            self.state = VisionState.enabled

    # DISABLED
    elif self.state == VisionState.disabled:
      if self.long_enabled and self.enabled:
        if self.long_override:
          self.state = VisionState.overriding
        else:
          self.state = VisionState.enabled

    enabled = self.state in ENABLED_STATES
    active = self.state in ACTIVE_STATES
    if not active:
      self.relief_frames = 0

    return enabled, active

  def update(self, sm: messaging.SubMaster, long_enabled: bool, long_override: bool, v_ego: float, a_ego: float,
             v_cruise_setpoint: float) -> None:
    self.long_enabled = long_enabled
    self.long_override = long_override
    self.v_ego = v_ego
    self.a_ego = a_ego
    self.v_cruise_setpoint = v_cruise_setpoint

    self._update_params()
    self._update_calculations(sm)

    self.is_enabled, self.is_active = self._update_state_machine()
    self.a_target = self.a_ego

    self.output_v_target = self.get_v_target_from_control()
    self.output_a_target = self.get_a_target_from_control()

    self.frame += 1
