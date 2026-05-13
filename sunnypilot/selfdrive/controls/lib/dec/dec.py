"""
Copyright (c) 2021-, rav4kumar, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
# Version = 2025-6-30
from typing import Literal

from cereal import messaging
from numpy import interp
from opendbc.car import structs

from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.sunnypilot.selfdrive.controls.lib.dec.constants import WMACConstants

TRAJECTORY_SIZE = 33
SET_MODE_TIMEOUT = 15

T_IDXS = ModelConstants.T_IDXS

ModeType = Literal['acc', 'blended']


class SmoothKalmanFilter:
  def __init__(self, initial_value=0, measurement_noise=0.1, process_noise=0.01,
               alpha=1.0, smoothing_factor=0.85):
    self.x = initial_value
    self.P = 1.0
    self.R = measurement_noise
    self.Q = process_noise
    self.alpha = alpha
    self.smoothing_factor = smoothing_factor
    self.initialized = False
    self.history = []
    self.max_history = 10
    self.confidence = 0.0

  def add_data(self, measurement):
    if len(self.history) >= self.max_history:
      self.history.pop(0)
    self.history.append(measurement)

    if not self.initialized:
      self.x = measurement
      self.initialized = True
      self.confidence = 0.1
      return

    self.P = self.alpha * self.P + self.Q

    K = self.P / (self.P + self.R)
    effective_K = K * (1.0 - self.smoothing_factor) + self.smoothing_factor * 0.1

    innovation = measurement - self.x
    self.x = self.x + effective_K * innovation
    self.P = (1 - effective_K) * self.P

    if abs(innovation) < 0.1:
      self.confidence = min(1.0, self.confidence + 0.05)
    else:
      self.confidence = max(0.1, self.confidence - 0.02)

  def get_value(self):
    return self.x if self.initialized else None

  def get_confidence(self):
    return self.confidence

  def reset_data(self):
    self.initialized = False
    self.history = []
    self.confidence = 0.0


class ModeTransitionManager:
  def __init__(self):
    self.current_mode: ModeType = 'acc'
    self.mode_confidence = {'acc': 1.0, 'blended': 0.0}
    self.transition_timeout = 0
    self.min_mode_duration = {'acc': 15, 'blended': 5}
    self.mode_duration = 0
    self.emergency_override = False

  def request_mode(self, mode: ModeType, confidence: float = 1.0, emergency: bool = False):
    if emergency:
      self.emergency_override = True
      self.current_mode = mode
      self.transition_timeout = SET_MODE_TIMEOUT
      self.mode_duration = 0
      return

    self.mode_confidence[mode] = min(1.0, self.mode_confidence[mode] + 0.1 * confidence)
    for m in self.mode_confidence:
      if m != mode:
        self.mode_confidence[m] = max(0.0, self.mode_confidence[m] - 0.05)

    if self.mode_duration < self.min_mode_duration[self.current_mode] and not self.emergency_override:
      return

    # asymmetric hysteresis: harder to enter blended, easier to return to acc
    if mode != self.current_mode:
      confidence_threshold = 0.6 if mode == 'blended' else 0.45
    else:
      confidence_threshold = 0.3

    if self.mode_confidence[mode] > confidence_threshold:
      if mode != self.current_mode and self.transition_timeout == 0:
        self.transition_timeout = SET_MODE_TIMEOUT
        self.current_mode = mode
        self.mode_duration = 0

  def update(self):
    if self.transition_timeout > 0:
      self.transition_timeout -= 1
    self.mode_duration += 1

    if self.emergency_override and self.mode_duration > 20:
      self.emergency_override = False

    for mode in self.mode_confidence:
      self.mode_confidence[mode] *= 0.96

  def get_mode(self) -> ModeType:
    return self.current_mode


class DynamicExperimentalController:
  def __init__(self, CP: structs.CarParams, mpc, params=None):
    self._CP = CP
    self._mpc = mpc
    self._params = params or Params()
    self._enabled: bool = self._params.get_bool("DynamicExperimentalControl")
    self._active: bool = False
    self._frame: int = 0
    self._urgency = 0.0

    self._mode_manager = ModeTransitionManager()

    self._lead_filter = SmoothKalmanFilter(measurement_noise=0.15, process_noise=0.05,
                                           alpha=1.02, smoothing_factor=0.8)
    self._slow_down_filter = SmoothKalmanFilter(measurement_noise=0.1, process_noise=0.1,
                                                alpha=1.05, smoothing_factor=0.55)
    self._slowness_filter = SmoothKalmanFilter(measurement_noise=0.1, process_noise=0.06,
                                               alpha=1.015, smoothing_factor=0.92)
    self._mpc_fcw_filter = SmoothKalmanFilter(measurement_noise=0.2, process_noise=0.1,
                                              alpha=1.1, smoothing_factor=0.5)

    self._has_lead_filtered = False
    self._has_slow_down = False
    self._has_slowness = False
    self._has_mpc_fcw = False
    self._has_model_stop = False
    self._has_standstill = False
    self._v_ego_kph = 0.0
    self._v_cruise_kph = 0.0
    self._mpc_fcw_crash_cnt = 0
    self._standstill_count = 0

    # debug
    self._endpoint_x = float('inf')
    self._expected_distance = 0.0
    self._trajectory_valid = False
    self._predicted_stop_t = float('inf')
    self._predicted_stop_d = float('inf')
    self._model_should_stop = False
    self._model_hard_brake = False
    self._brake_press_prob_max = 0.0
    self._hard_brake_3ms2_prob_max = 0.0
    self._hard_brake_5ms2_prob_max = 0.0

  def _read_params(self) -> None:
    if self._frame % int(1. / DT_MDL) == 0:
      self._enabled = self._params.get_bool("DynamicExperimentalControl")

  def mode(self) -> str:
    return self._mode_manager.get_mode()

  def enabled(self) -> bool:
    return self._enabled

  def active(self) -> bool:
    return self._active

  def set_mpc_fcw_crash_cnt(self) -> None:
    self._mpc_fcw_crash_cnt = self._mpc.crash_cnt

  def _update_calculations(self, sm: messaging.SubMaster) -> None:
    car_state = sm['carState']
    lead_one = sm['radarState'].leadOne
    md = sm['modelV2']

    self._v_ego_kph = car_state.vEgo * 3.6
    self._v_cruise_kph = car_state.vCruise
    self._has_standstill = car_state.standstill

    if self._has_standstill:
      self._standstill_count = min(20, self._standstill_count + 1)
    else:
      self._standstill_count = max(0, self._standstill_count - 1)

    self._lead_filter.add_data(float(lead_one.status))
    lead_value = self._lead_filter.get_value() or 0.0
    self._has_lead_filtered = lead_value > WMACConstants.LEAD_PROB

    fcw_filtered_value = self._mpc_fcw_filter.get_value() or 0.0
    self._mpc_fcw_filter.add_data(float(self._mpc_fcw_crash_cnt > 0))
    self._has_mpc_fcw = fcw_filtered_value > 0.5

    self._calculate_slow_down(md)

    if not (self._standstill_count > 5) and not self._has_slow_down:
      current_slowness = float(self._v_ego_kph <= (self._v_cruise_kph * WMACConstants.SLOWNESS_CRUISE_OFFSET))
      self._slowness_filter.add_data(current_slowness)
      slowness_value = self._slowness_filter.get_value() or 0.0
      threshold = WMACConstants.SLOWNESS_PROB * (0.8 if self._has_slowness else 1.1)
      self._has_slowness = slowness_value > threshold

  def _reset_slow_down_debug(self) -> None:
    self._endpoint_x = float('inf')
    self._trajectory_valid = False
    self._predicted_stop_t = float('inf')
    self._predicted_stop_d = float('inf')
    self._model_should_stop = False
    self._model_hard_brake = False
    self._brake_press_prob_max = 0.0
    self._hard_brake_3ms2_prob_max = 0.0
    self._hard_brake_5ms2_prob_max = 0.0

  def _calculate_slow_down(self, md) -> None:
    self._reset_slow_down_debug()
    urgency = 0.0

    if len(md.position.x) != TRAJECTORY_SIZE or len(md.orientation.x) != TRAJECTORY_SIZE:
      # invalid trajectory — stay at urgency=0; missing data is not a brake signal
      self._slow_down_filter.add_data(urgency)
      urgency_filtered = self._slow_down_filter.get_value() or 0.0
      self._has_slow_down = urgency_filtered > WMACConstants.SLOW_DOWN_PROB
      self._urgency = urgency_filtered
      self._has_model_stop = False
      return

    self._trajectory_valid = True

    # endpoint shortage
    endpoint_x = md.position.x[TRAJECTORY_SIZE - 1]
    self._endpoint_x = endpoint_x
    expected_distance = interp(self._v_ego_kph, WMACConstants.SLOW_DOWN_BP, WMACConstants.SLOW_DOWN_DIST)
    self._expected_distance = expected_distance

    if endpoint_x < expected_distance:
      shortage_ratio = (expected_distance - endpoint_x) / expected_distance
      urgency = min(1.0, shortage_ratio * 1.3)
      if endpoint_x < expected_distance * 0.3:
        urgency = min(1.0, urgency * 1.5)
      if self._v_ego_kph > 25.0:
        urgency = min(1.0, urgency * (1.0 + (self._v_ego_kph - 25.0) / 80.0))

    # predicted velocity-zero crossing — first horizon sample below V_STOP_THRESH
    if len(md.velocity.x) == TRAJECTORY_SIZE:
      v_pred = md.velocity.x
      for i in range(1, TRAJECTORY_SIZE):
        if T_IDXS[i] > WMACConstants.T_STOP_HORIZON:
          break
        if v_pred[i] < WMACConstants.V_STOP_THRESH:
          self._predicted_stop_t = T_IDXS[i]
          self._predicted_stop_d = md.position.x[i]
          break

      if self._predicted_stop_t < WMACConstants.T_STOP_HORIZON:
        stop_urgency = WMACConstants.V_STOP_URGENCY_CAP * (1.0 - self._predicted_stop_t / WMACConstants.T_STOP_HORIZON)
        urgency = max(urgency, stop_urgency)

    # model meta: brake-probability curves over t=[2,4,6,8,10]s
    dp = md.meta.disengagePredictions
    if len(dp.brakePressProbs):
      self._brake_press_prob_max = max(dp.brakePressProbs)
    if len(dp.brake3MetersPerSecondSquaredProbs):
      self._hard_brake_3ms2_prob_max = max(dp.brake3MetersPerSecondSquaredProbs)
    if len(dp.brake5MetersPerSecondSquaredProbs):
      self._hard_brake_5ms2_prob_max = max(dp.brake5MetersPerSecondSquaredProbs)
    self._model_hard_brake = bool(md.meta.hardBrakePredicted)

    if self._brake_press_prob_max > WMACConstants.BRAKE_PRESS_PROB_THRESH:
      urgency = max(urgency, min(1.0, self._brake_press_prob_max * 1.4))
    if self._hard_brake_3ms2_prob_max > WMACConstants.HARD_BRAKE_3MS2_PROB_THRESH:
      urgency = max(urgency, 0.85)
    if self._hard_brake_5ms2_prob_max > WMACConstants.HARD_BRAKE_5MS2_PROB_THRESH:
      urgency = 1.0

    # model action
    self._model_should_stop = bool(md.action.shouldStop)

    self._has_model_stop = (self._model_should_stop or self._model_hard_brake
                            or self._predicted_stop_t < WMACConstants.T_STOP_HORIZON)

    self._slow_down_filter.add_data(urgency)
    urgency_filtered = self._slow_down_filter.get_value() or 0.0
    self._has_slow_down = urgency_filtered > WMACConstants.SLOW_DOWN_PROB
    self._urgency = urgency_filtered

  def _request_slow_down(self) -> None:
    if self._urgency > 0.7:
      self._mode_manager.request_mode('blended', confidence=1.0, emergency=True)
    else:
      self._mode_manager.request_mode('blended', confidence=min(1.0, self._urgency * 1.3))

  def _radarless_mode(self) -> None:
    if self._has_mpc_fcw:
      self._mode_manager.request_mode('blended', confidence=1.0, emergency=True)
      return

    if self._has_model_stop and self._predicted_stop_t < 4.0:
      self._mode_manager.request_mode('blended', confidence=1.0, emergency=True)
      return

    if self._standstill_count > 3:
      self._mode_manager.request_mode('blended', confidence=0.9)
      return

    if self._has_slow_down:
      self._request_slow_down()
      return

    if self._has_slowness and not self._has_slow_down:
      self._mode_manager.request_mode('acc', confidence=0.8)
      return

    self._mode_manager.request_mode('acc', confidence=0.7)

  def _radar_mode(self) -> None:
    # lead present always routes to ACC; only FCW preempts. blended is reserved
    # for the no-lead case (model stop intent, trajectory shortening, standstill).
    if self._has_mpc_fcw:
      self._mode_manager.request_mode('blended', confidence=1.0, emergency=True)
      return

    if self._has_lead_filtered and not (self._standstill_count > 3):
      self._mode_manager.request_mode('acc', confidence=1.0)
      return

    if self._has_model_stop and self._predicted_stop_t < 4.0:
      self._mode_manager.request_mode('blended', confidence=1.0, emergency=True)
      return

    if self._has_slow_down:
      self._request_slow_down()
      return

    if self._standstill_count > 3:
      self._mode_manager.request_mode('blended', confidence=0.9)
      return

    if self._has_slowness and not self._has_slow_down:
      self._mode_manager.request_mode('acc', confidence=0.8)
      return

    self._mode_manager.request_mode('acc', confidence=0.7)

  def update(self, sm: messaging.SubMaster) -> None:
    self._read_params()
    self.set_mpc_fcw_crash_cnt()
    self._update_calculations(sm)

    if self._CP.radarUnavailable:
      self._radarless_mode()
    else:
      self._radar_mode()

    self._mode_manager.update()
    self._active = sm['selfdriveState'].experimentalMode and self._enabled
    self._frame += 1
