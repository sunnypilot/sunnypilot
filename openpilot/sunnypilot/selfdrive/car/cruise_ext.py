"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np
import math
import time

from openpilot.cereal import custom
from opendbc.car.structs import car
from opendbc.car import structs
from openpilot.common.constants import CV
from openpilot.common.params import Params
from openpilot.sunnypilot.selfdrive.car.intelligent_cruise_button_management.helpers import get_minimum_set_speed
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.speed_limit_assist import ACTIVE_STATES as SLA_ACTIVE_STATES
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.helpers import compare_cluster_target
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.common import Mode
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.automatic_set import (
  AutomaticSet, StableMapLimit, auto_supported, read_map_evidence, resolve_auto_map,
)
from openpilot.common.gps import get_gps_location_service

ButtonType = car.CarState.ButtonEvent.Type
SpeedLimitAssistState = custom.LongitudinalPlanSP.SpeedLimit.AssistState

CRUISE_BUTTON_TIMER = {ButtonType.decelCruise: 0, ButtonType.accelCruise: 0,
                       ButtonType.setCruise: 0, ButtonType.resumeCruise: 0,
                       ButtonType.cancel: 0, ButtonType.mainCruise: 0}

V_CRUISE_MIN = 8
V_CRUISE_MAX = 145
V_CRUISE_UNSET = 255


def update_manual_button_timers(CS: car.CarState, button_timers: dict[car.CarState.ButtonEvent.Type, int]) -> None:
  # increment timer for buttons still pressed
  for k in button_timers:
    if button_timers[k] > 0:
      button_timers[k] += 1

  for b in CS.buttonEvents:
    if b.type.raw in button_timers:
      # Start/end timer and store current state on change of button pressed
      button_timers[b.type.raw] = 1 if b.pressed else 0


class VCruiseHelperSP:
  def __init__(self, CP: structs.CarParams, CP_SP: structs.CarParamsSP) -> None:
    self.CP = CP
    self.CP_SP = CP_SP
    self.v_cruise_kph = V_CRUISE_UNSET
    self.v_cruise_cluster_kph = V_CRUISE_UNSET
    self.params = Params()
    self.v_cruise_min = 0
    self.enabled_prev = False
    self.auto_set = AutomaticSet()
    self.auto_button_timers = dict.fromkeys(CRUISE_BUTTON_TIMER, 0)
    self.speed_limit_mode = self.params.get("SpeedLimitMode", return_default=True)
    self.mode_read_at = 0.
    self.auto_target = None
    self.auto_control_ok = False
    self.auto_params_valid = True
    self.auto_map = StableMapLimit()
    self.auto_gps_service = get_gps_location_service(self.params)
    self.auto_offset_type = self.params.get("SpeedLimitOffsetType", return_default=True)
    self.auto_offset_value = self.params.get("SpeedLimitValueOffset", return_default=True)

    self.custom_acc_enabled = self.params.get_bool("CustomAccIncrementsEnabled")
    self.short_increment = self.params.get("CustomAccShortPressIncrement", return_default=True)
    self.long_increment = self.params.get("CustomAccLongPressIncrement", return_default=True)

    self.enable_button_timers = CRUISE_BUTTON_TIMER

    # Speed Limit Assist
    self.sla_state = SpeedLimitAssistState.disabled
    self.prev_sla_state = SpeedLimitAssistState.disabled
    self.has_speed_limit = False
    self.speed_limit_final_last = 0.
    self.speed_limit_final_last_kph = 0.
    self.prev_speed_limit_final_last_kph = 0.
    self.req_plus = False
    self.req_minus = False

  def read_custom_set_speed_params(self) -> None:
    self.custom_acc_enabled = self.params.get_bool("CustomAccIncrementsEnabled")
    self.short_increment = self.params.get("CustomAccShortPressIncrement", return_default=True)
    self.long_increment = self.params.get("CustomAccLongPressIncrement", return_default=True)

  def update_v_cruise_delta(self, long_press: bool, v_cruise_delta: float) -> tuple[bool, float]:
    if not self.custom_acc_enabled:
      v_cruise_delta = v_cruise_delta * (5 if long_press else 1)
      return long_press, v_cruise_delta

    # Apply user-specified multipliers to the base increment
    short_increment = np.clip(self.short_increment, 1, 10)
    long_increment = np.clip(self.long_increment, 1, 10)

    actual_increment = long_increment if long_press else short_increment
    round_to_nearest = actual_increment in (5, 10)
    v_cruise_delta = v_cruise_delta * actual_increment

    return round_to_nearest, v_cruise_delta

  def get_minimum_set_speed(self, is_metric: bool) -> None:
    if self.CP_SP.pcmCruiseSpeed:
      self.v_cruise_min = V_CRUISE_MIN
      return

    self.v_cruise_min = get_minimum_set_speed(is_metric)

  def update_enabled_state(self, CS: car.CarState, enabled: bool) -> bool:
    # special enabled state for non pcmCruiseSpeed, unchanged for non pcmCruise
    if not self.CP_SP.pcmCruiseSpeed:
      update_manual_button_timers(CS, self.enable_button_timers)
      button_pressed = any(self.enable_button_timers[k] > 0 for k in self.enable_button_timers)

      if enabled and not self.enabled_prev:
        self.enabled_prev = not button_pressed
        enabled = False
      elif not enabled:
        self.enabled_prev = enabled

      return enabled and self.enabled_prev

    return enabled

  def update_speed_limit_assist(self, is_metric, LP_SP: custom.LongitudinalPlanSP,
                                *, plan_fresh=False, control_fresh=False, long_active=False, override=True, map_sm=None) -> None:
    now = time.monotonic()
    # Optional input failures must not reuse a target or interrupt driver takeover.
    self.auto_target = None
    self.auto_control_ok = False
    if now - self.mode_read_at >= 0.5:
      self.mode_read_at = now
      try:
        mode = self.params.get("SpeedLimitMode", return_default=True)
        offset_type = self.params.get("SpeedLimitOffsetType", return_default=True)
        offset_value = self.params.get("SpeedLimitValueOffset", return_default=True)
        if (type(mode) is not int or mode not in range(5) or type(offset_type) is not int or offset_type not in range(3)
            or type(offset_value) not in (int, float) or not math.isfinite(offset_value)):
          raise ValueError("Invalid speed-limit settings")
      except (OSError, RuntimeError, ValueError, OverflowError):
        self.auto_params_valid = False
      else:
        self.speed_limit_mode, self.auto_offset_type, self.auto_offset_value = mode, offset_type, offset_value
        self.auto_params_valid = True
    if not self.auto_params_valid:
      self.auto_map.reset()
      self.auto_evidence = None
      self.auto_evidence_read_at = 0.
      self.sla_state = SpeedLimitAssistState.disabled
      self.has_speed_limit = self.req_plus = self.req_minus = False
      return
    if self.speed_limit_mode == Mode.automatic and map_sm is not None:
      # Read the small SHM sidecar at 10 Hz; it binds a limit to mapd's input fix.
      if now - getattr(self, 'auto_evidence_read_at', 0.) >= 0.1:
        self.auto_evidence = read_map_evidence()
        self.auto_evidence_read_at = now
      target = resolve_auto_map(self.auto_map, map_sm, self.auto_gps_service, now,
                                self.auto_offset_type, self.auto_offset_value, is_metric,
                                getattr(self, 'auto_evidence', None))
      self.auto_target = target * CV.MS_TO_KPH if target is not None else None
    else:
      self.auto_map.reset()
    self.auto_control_ok = (plan_fresh and control_fresh and long_active and not override
                            and not LP_SP.speedLimit.assist.enabled)
    resolver = LP_SP.speedLimit.resolver
    self.has_speed_limit = resolver.speedLimitValid or resolver.speedLimitLastValid
    self.speed_limit_final_last = LP_SP.speedLimit.resolver.speedLimitFinalLast
    self.speed_limit_final_last_kph = self.speed_limit_final_last * CV.MS_TO_KPH
    self.sla_state = (SpeedLimitAssistState.disabled if self.speed_limit_mode == Mode.automatic
                      else LP_SP.speedLimit.assist.state)
    self.req_plus, self.req_minus = compare_cluster_target(self.v_cruise_cluster_kph * CV.KPH_TO_MS,
                                                           self.speed_limit_final_last, is_metric)

  @property
  def update_speed_limit_final_last_changed(self) -> bool:
    return self.has_speed_limit and bool(self.speed_limit_final_last_kph != self.prev_speed_limit_final_last_kph)

  def update_speed_limit_assist_pre_active_confirmed(self, button_type: car.CarState.ButtonEvent.Type) -> bool:
    if self.speed_limit_mode == Mode.automatic:
      return False
    if self.sla_state == SpeedLimitAssistState.preActive or self.prev_sla_state == SpeedLimitAssistState.preActive:
      if button_type == ButtonType.decelCruise and self.req_minus:
        return True
      if button_type == ButtonType.accelCruise and self.req_plus:
        return True

    return False

  def update_automatic_set(self, CS, enabled: bool) -> None:
    # Track held buttons independently of the native pcmCruiseSpeed path.
    update_manual_button_timers(CS, self.auto_button_timers)
    manual = [b for b in CS.buttonEvents if b.type.raw in CRUISE_BUTTON_TIMER]
    held = any(self.auto_button_timers.values())
    target = self.auto_set.update(
      now=time.monotonic(), selected=self.speed_limit_mode == Mode.automatic,
      supported=auto_supported(self.CP), enabled=enabled,
      available=CS.cruiseState.available, control_ok=self.auto_control_ok and CS.canValid and not CS.canTimeout,
      pedal=CS.gasPressed or CS.brakePressed, manual_event=bool(manual),
      manual_press=any(b.pressed for b in manual),
      cancel=any(b.type == ButtonType.cancel for b in manual), held=held,
      target=self.auto_target, current=self.v_cruise_kph, minimum=self.v_cruise_min,
    )
    if target is not None:
      self.v_cruise_kph = target

  def update_speed_limit_assist_v_cruise_non_pcm(self) -> None:
    if self.sla_state in SLA_ACTIVE_STATES and (self.prev_sla_state not in SLA_ACTIVE_STATES or
                                                self.update_speed_limit_final_last_changed):
      self.v_cruise_kph = np.clip(round(self.speed_limit_final_last_kph, 1), self.v_cruise_min, V_CRUISE_MAX)

    self.prev_sla_state = self.sla_state
    self.prev_speed_limit_final_last_kph = self.speed_limit_final_last_kph
