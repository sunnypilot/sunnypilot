"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import car


def get_set_point(is_metric: bool) -> float:
  return 30 if is_metric else 20


def speed_hysteresis(controller, speed: float, speed_steady: float, hyst: float) -> float:
  if speed > speed_steady + hyst:
    speed_steady = speed - hyst
  elif speed < speed_steady - hyst:
    speed_steady = speed + hyst

  controller.speed_steady = speed

  return speed_steady


def update_manual_button_timers(CS: car.CarState, button_timers: dict[car.CarState.ButtonEvent.Type, int]) -> None:
  # increment timer for buttons still pressed
  for k in button_timers:
    if button_timers[k] > 0:
      button_timers[k] += 1

  for b in CS.buttonEvents:
    if b.type.raw in button_timers:
      # Start/end timer and store current state on change of button pressed
      button_timers[b.type.raw] = 1 if b.pressed else 0
