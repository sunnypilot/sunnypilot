"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import car, custom
import numpy as np
from opendbc.car import structs
from openpilot.common.params import Params
from openpilot.selfdrive.car.cruise import VCruiseHelper, IMPERIAL_INCREMENT, CRUISE_LONG_PRESS, CRUISE_NEAREST_FUNC, CV, V_CRUISE_MIN, V_CRUISE_MAX, CRUISE_INTERVAL_SIGN

ButtonType = car.CarState.ButtonEvent.Type
EventNameSP = custom.OnroadEventSP.EventName

DISTANCE_LONG_PRESS = 50


class CruiseHelper:
  def __init__(self, CP: structs.CarParams):
    self.CP = CP
    self.params = Params()

    self.button_frame_counts = {ButtonType.gapAdjustCruise: 0}
    self._experimental_mode = False
    self.experimental_mode_switched = False

  def update(self, CS, events, experimental_mode) -> None:
    if self.CP.openpilotLongitudinalControl:
      if CS.cruiseState.available:
        self.update_button_frame_counts(CS)

        # toggle experimental mode once on distance button hold
        self.update_experimental_mode(events, experimental_mode)

  def update_button_frame_counts(self, CS) -> None:
    for button in self.button_frame_counts:
      if self.button_frame_counts[button] > 0:
        self.button_frame_counts[button] += 1

    for button_event in CS.buttonEvents:
      button = button_event.type.raw
      if button in self.button_frame_counts:
        self.button_frame_counts[button] = int(button_event.pressed)

  def update_experimental_mode(self, events, experimental_mode) -> None:
    if self.button_frame_counts[ButtonType.gapAdjustCruise] >= DISTANCE_LONG_PRESS and not self.experimental_mode_switched:
      self._experimental_mode = not experimental_mode
      self.params.put_bool_nonblocking("ExperimentalMode", self._experimental_mode)
      events.add(EventNameSP.experimentalModeSwitched)
      self.experimental_mode_switched = True


class VCruiseHelperSP(VCruiseHelper):

  def __init__(self, CP: structs.CarParams) -> None:
    super().__init__(CP)
    self.params = Params()

  def _update_v_cruise_non_pcm(self, CS: car.CarState, enabled: bool, is_metric: bool) -> None:
    if not enabled:
      return

    long_press = False
    button_type = None

    for b in CS.buttonEvents:
      if b.type.raw in self.button_timers and not b.pressed:
        if self.button_timers[b.type.raw] > CRUISE_LONG_PRESS:
          return  # end long press
        button_type = b.type.raw
        break
    else:
      for k, timer in self.button_timers.items():
        if timer and timer % CRUISE_LONG_PRESS == 0:
          button_type = k
          long_press = True
          break

    if button_type is None:
      return

    # Don't adjust speed when pressing resume to exit standstill
    cruise_standstill = self.button_change_states[button_type]["standstill"] or CS.cruiseState.standstill
    if button_type == ButtonType.accelCruise and cruise_standstill:
      return

    # Don't adjust speed if we've enabled since the button was depressed (some ports enable on rising edge)
    if not self.button_change_states[button_type]["enabled"]:
      return

    self.v_cruise_kph = self.adjust_cruise_speed(button_type, long_press, is_metric)

    # If set is pressed while overriding, clip cruise speed to minimum of vEgo
    if CS.gasPressed and button_type in (ButtonType.decelCruise, ButtonType.setCruise):
      self.v_cruise_kph = max(self.v_cruise_kph, CS.vEgo * CV.MS_TO_KPH)

    self.v_cruise_kph = np.clip(round(self.v_cruise_kph, 1), V_CRUISE_MIN, V_CRUISE_MAX)

  def adjust_cruise_speed(self, button_type: ButtonType, long_press: bool, is_metric: bool) -> float:
    """
    Adjust cruise control speed based on button inputs with customizable increments.
    Parameters:
    - button_type: Type of button pressed (affects direction and rounding)
    - long_press: Whether button is being held down
    - is_metric: Check if the system is using metric units
    """
    # Base increment value based on unit system
    base_increment = 1. if is_metric else IMPERIAL_INCREMENT

    try:
      custom_enabled = self.params.get_bool("CustomAccIncrementsEnabled")
      short_increment = int(self.params.get("CustomAccShortPressIncrement"))
      long_increment = int(self.params.get("CustomAccLongPressIncrement"))

      # Apply the user-specified multipliers to the base increment if custom enabled
      short_increment = short_increment if custom_enabled and 1 <= short_increment <= 10 else 1
      long_increment = long_increment if custom_enabled and 1 <= long_increment <= 10 else 10 if is_metric else 5

    except Exception:
      short_increment = 1
      long_increment = 10 if is_metric else 5

    # Determine which increment to use based on press type
    adjusted_delta = long_increment if long_press else short_increment
    v_cruise = self.v_cruise_kph / base_increment

    # Check if we need to align to interval boundaries
    if adjusted_delta in [5, 10] and v_cruise % adjusted_delta != 0:
      rounded_value = CRUISE_NEAREST_FUNC[button_type](v_cruise / adjusted_delta)
      v_cruise = rounded_value * adjusted_delta
    else:
      direction = CRUISE_INTERVAL_SIGN[button_type]  # +1 or -1 based on button type
      v_cruise += adjusted_delta * direction

    self.v_cruise_kph = v_cruise * base_increment
    return self.v_cruise_kph
