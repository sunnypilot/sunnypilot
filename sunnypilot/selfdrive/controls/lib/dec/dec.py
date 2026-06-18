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
from openpilot.sunnypilot.selfdrive.controls.lib.dec.constants import WMACConstants

ModeType = Literal['acc', 'blended']


def clip01(value: float) -> float:
  return max(0.0, min(1.0, float(value)))


class SmoothedSignal:
  def __init__(self, rise_rate: float, fall_rate: float, initial_value: float = 0.0):
    self.rise_rate = clip01(rise_rate)
    self.fall_rate = clip01(fall_rate)
    self.value = clip01(initial_value)

  def update(self, measurement: float) -> float:
    measurement = clip01(measurement)
    rate = self.rise_rate if measurement > self.value else self.fall_rate
    self.value += (measurement - self.value) * rate
    return self.value

  def reset(self, value: float = 0.0) -> None:
    self.value = clip01(value)


class HysteresisSignal:
  def __init__(self, enter_threshold: float, exit_threshold: float, rise_rate: float, fall_rate: float):
    self.enter_threshold = clip01(enter_threshold)
    self.exit_threshold = clip01(exit_threshold)
    self.filter = SmoothedSignal(rise_rate, fall_rate)
    self.active = False

  def update(self, measurement: float) -> bool:
    value = self.filter.update(measurement)
    threshold = self.exit_threshold if self.active else self.enter_threshold
    self.active = value > threshold
    return self.active

  def reset(self) -> None:
    self.filter.reset()
    self.active = False

  @property
  def value(self) -> float:
    return self.filter.value


class ModeTransitionManager:
  def __init__(self):
    self.current_mode: ModeType = 'acc'
    self.mode_duration = 0
    self._pending_mode: ModeType = 'acc'
    self._pending_count = 0
    self._blended_hold_frames = 0

  def request_mode(self, mode: ModeType, immediate: bool = False, hold_frames: int = 0, cancel_hold: bool = False) -> None:
    if immediate:
      self._blended_hold_frames = max(self._blended_hold_frames, hold_frames)
      self._pending_mode = mode
      self._pending_count = 0
      self._switch_mode(mode)
      return

    if cancel_hold and mode == 'acc':
      self._blended_hold_frames = 0

    if self._blended_hold_frames > 0:
      mode = 'blended'

    if mode == self.current_mode:
      self._pending_mode = mode
      self._pending_count = 0
      return

    if mode != self._pending_mode:
      self._pending_mode = mode
      self._pending_count = 1
    else:
      self._pending_count += 1

    if self.mode_duration < WMACConstants.MIN_MODE_DURATION[self.current_mode]:
      return

    required_count = WMACConstants.ENTER_BLENDED_FRAMES if mode == 'blended' else WMACConstants.EXIT_BLENDED_FRAMES
    if self._pending_count >= required_count:
      self._switch_mode(mode)

  def update(self) -> None:
    if self._blended_hold_frames > 0:
      self._blended_hold_frames -= 1
    self.mode_duration += 1

  def get_mode(self) -> ModeType:
    return self.current_mode

  def _switch_mode(self, mode: ModeType) -> None:
    if mode == self.current_mode:
      return

    self.current_mode = mode
    self.mode_duration = 0
    self._pending_mode = mode
    self._pending_count = 0


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

    self._lead_tracker = HysteresisSignal(
      enter_threshold=WMACConstants.LEAD_PROB,
      exit_threshold=WMACConstants.LEAD_EXIT_PROB,
      rise_rate=WMACConstants.LEAD_RISE_RATE,
      fall_rate=WMACConstants.LEAD_FALL_RATE,
    )
    self._radar_acc_lead_tracker = HysteresisSignal(
      enter_threshold=WMACConstants.RADAR_LEAD_ACC_PROB,
      exit_threshold=WMACConstants.RADAR_LEAD_ACC_EXIT_PROB,
      rise_rate=WMACConstants.RADAR_LEAD_ACC_RISE_RATE,
      fall_rate=WMACConstants.RADAR_LEAD_ACC_FALL_RATE,
    )
    self._slow_down_tracker = HysteresisSignal(
      enter_threshold=WMACConstants.SLOW_DOWN_PROB,
      exit_threshold=WMACConstants.SLOW_DOWN_EXIT_PROB,
      rise_rate=WMACConstants.SLOW_DOWN_RISE_RATE,
      fall_rate=WMACConstants.SLOW_DOWN_FALL_RATE,
    )
    self._slowness_tracker = HysteresisSignal(
      enter_threshold=WMACConstants.SLOWNESS_PROB,
      exit_threshold=WMACConstants.SLOWNESS_EXIT_PROB,
      rise_rate=WMACConstants.SLOWNESS_RISE_RATE,
      fall_rate=WMACConstants.SLOWNESS_FALL_RATE,
    )

    self._has_lead_filtered = False
    self._has_radar_acc_lead = False
    self._has_slow_down = False
    self._has_slowness = False
    self._has_mpc_fcw = False
    self._v_ego_kph = 0.0
    self._v_cruise_kph = 0.0
    self._has_standstill = False
    self._mpc_fcw_crash_cnt = 0
    self._standstill_count = 0

    self._endpoint_x = float('inf')
    self._expected_distance = 0.0
    self._trajectory_valid = False
    self._raw_urgency = 0.0

  def _read_params(self) -> None:
    if self._frame % WMACConstants.PARAM_READ_FRAMES == 0:
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
      self._standstill_count = min(WMACConstants.STANDSTILL_FRAMES * 3, self._standstill_count + 1)
    else:
      self._standstill_count = max(0, self._standstill_count - 1)

    self._has_lead_filtered = self._lead_tracker.update(float(lead_one.status))
    self._has_radar_acc_lead = self._radar_acc_lead_tracker.update(self._radar_acc_lead_score(lead_one))
    self._has_mpc_fcw = self._mpc_fcw_crash_cnt > 0
    self._calculate_slow_down(md)

    if self._standstill_count > WMACConstants.STANDSTILL_FRAMES or self._has_slow_down:
      self._slowness_tracker.reset()
      self._has_slowness = False
    else:
      current_slowness = float(self._v_ego_kph <= (self._v_cruise_kph * WMACConstants.SLOWNESS_CRUISE_OFFSET))
      self._has_slowness = self._slowness_tracker.update(current_slowness)

  def _calculate_slow_down(self, md) -> None:
    self._endpoint_x = float('inf')
    self._expected_distance = 0.0
    self._trajectory_valid = False

    urgency = self._model_action_urgency(md)
    position_valid = len(md.position.x) == WMACConstants.TRAJECTORY_SIZE

    if position_valid:
      self._trajectory_valid = True
      self._endpoint_x = md.position.x[WMACConstants.TRAJECTORY_SIZE - 1]
      self._expected_distance = interp(self._v_ego_kph, WMACConstants.SLOW_DOWN_BP, WMACConstants.SLOW_DOWN_DIST)
      urgency = max(urgency, self._endpoint_urgency(self._endpoint_x, self._expected_distance))

    self._raw_urgency = clip01(urgency)
    self._has_slow_down = self._slow_down_tracker.update(self._raw_urgency)
    self._urgency = self._slow_down_tracker.value

  def _radar_acc_lead_score(self, lead_one) -> float:
    if not lead_one.status:
      return 0.0

    d_rel = float(getattr(lead_one, 'dRel', float('inf')))
    v_rel = float(getattr(lead_one, 'vRel', 0.0))
    if d_rel <= WMACConstants.RADAR_LEAD_ACC_MAX_DREL:
      return 1.0
    if v_rel <= WMACConstants.RADAR_LEAD_ACC_MIN_CLOSING_SPEED and d_rel / max(-v_rel, 0.1) <= WMACConstants.RADAR_LEAD_ACC_MAX_TTC:
      return 1.0
    return 0.0

  def _model_action_urgency(self, md) -> float:
    action = getattr(md, 'action', None)
    if action is None:
      return 0.0

    urgency = 1.0 if getattr(action, 'shouldStop', False) else 0.0
    desired_accel = getattr(action, 'desiredAcceleration', 0.0)
    if desired_accel < WMACConstants.MODEL_DECEL_START:
      urgency = max(urgency, min(1.0, (WMACConstants.MODEL_DECEL_START - desired_accel) / WMACConstants.MODEL_DECEL_RANGE))
    return urgency

  def _endpoint_urgency(self, endpoint_x: float, expected_distance: float) -> float:
    if endpoint_x >= expected_distance:
      return 0.0

    shortage_ratio = (expected_distance - endpoint_x) / expected_distance
    urgency = min(1.0, shortage_ratio * WMACConstants.ENDPOINT_URGENCY_GAIN)

    if endpoint_x < expected_distance * WMACConstants.CRITICAL_ENDPOINT_FACTOR:
      urgency = min(1.0, urgency * WMACConstants.CRITICAL_URGENCY_GAIN)

    if self._v_ego_kph > WMACConstants.SPEED_URGENCY_MIN:
      speed_factor = 1.0 + (self._v_ego_kph - WMACConstants.SPEED_URGENCY_MIN) / WMACConstants.SPEED_URGENCY_RANGE
      urgency = min(1.0, urgency * speed_factor)

    return urgency

  def _desired_mode(self) -> tuple[ModeType, bool]:
    if not self._CP.radarUnavailable and self._has_radar_acc_lead:
      return 'acc', False

    if self._has_mpc_fcw:
      return 'blended', True

    standstill = self._standstill_count > WMACConstants.STANDSTILL_FRAMES
    urgent_slow_down = self._has_slow_down and self._raw_urgency > WMACConstants.URGENT_SLOW_DOWN_PROB

    if self._CP.radarUnavailable:
      if standstill or self._has_slow_down:
        return 'blended', urgent_slow_down
      return 'acc', False

    if standstill or self._has_slow_down:
      return 'blended', urgent_slow_down

    return 'acc', False

  def update(self, sm: messaging.SubMaster) -> None:
    self._read_params()
    self.set_mpc_fcw_crash_cnt()
    self._update_calculations(sm)

    mode, immediate = self._desired_mode()
    self._mode_manager.request_mode(mode, immediate=immediate, hold_frames=WMACConstants.EMERGENCY_HOLD_FRAMES,
                                    cancel_hold=self._has_radar_acc_lead)
    self._mode_manager.update()

    self._active = sm['selfdriveState'].experimentalMode and self._enabled
    self._frame += 1
