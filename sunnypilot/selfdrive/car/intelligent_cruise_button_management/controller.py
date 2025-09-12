"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import car, custom
from openpilot.common.constants import CV
from openpilot.common.params import Params
from openpilot.common.realtime import DT_CTRL
from openpilot.sunnypilot.selfdrive.car.intelligent_cruise_button_management.helpers import get_set_point, \
  speed_hysteresis, update_manual_button_timers

ButtonType = car.CarState.ButtonEvent.Type
State = custom.IntelligentCruiseButtonManagement.IntelligentCruiseButtonManagementState
SendButtonState = custom.IntelligentCruiseButtonManagement.SendButtonState

SendCan = tuple[int, bytes, int]

INACTIVE_TIMER = 0.4
RESET_COUNT = 5
HOLD_TIME = 7


class IntelligentCruiseButtonManagement:
  def __init__(self, CP, CP_SP):
    self.CP = CP
    self.CP_SP = CP_SP

    self.v_target = 0
    self.v_cruise_cluster = 0
    self.v_cruise_min = 0
    self.cruise_button = SendButtonState.none
    self.state = State.inactive
    self.button_count = 0
    self.pre_active_timer = 0

    self.is_ready = False
    self.is_ready_prev = False
    self.speed_steady = 0
    self.is_metric = False

    self.cruise_buttons = {ButtonType.decelCruise: 0, ButtonType.accelCruise: 0,
                           ButtonType.setCruise: 0, ButtonType.resumeCruise: 0}

  def update_calculations(self, CS: car.CarState, CC: car.CarControl) -> None:
    v_cruise_kph = CC.vCruise
    v_cruise = v_cruise_kph * CV.KPH_TO_MS
    self.v_cruise_min = get_set_point(self.is_metric)
    self.v_cruise_cluster = round(CS.cruiseState.speed * (CV.MS_TO_KPH if self.is_metric else CV.MS_TO_MPH))

    v_targets = {'cruise': CC.vCruise}

    source = min(v_targets, key=v_targets.get)

    v_target = speed_hysteresis(self, v_targets[source], self.speed_steady, 1.5 * (CV.KPH_TO_MS if self.is_metric else CV.MPH_TO_MS))
    v_target = min(v_target, v_cruise)
    v_target = round(v_target * (CV.MS_TO_KPH if self.is_metric else CV.MS_TO_MPH))

    self.v_target = v_target

  def update_state_machine(self):
    self.pre_active_timer = max(0, self.pre_active_timer - 1)

    # HOLDING, ACCELERATING, DECELERATING, PRE_ACTIVE
    if self.state != State.inactive:
      if not self.is_ready:
        self.button_count = 0
        self.state = State.inactive

      else:
        # PRE_ACTIVE
        if self.state == State.preActive:
          if self.v_target > self.v_cruise_cluster:
            self.state = State.increasing
          elif self.v_target < self.v_cruise_cluster and self.v_cruise_cluster > self.v_cruise_min:
            self.state = State.decreasing
          else:
            self.state = State.holding

        # HOLDING
        elif self.state == State.holding:
          self.button_count += 1
          if self.button_count >= HOLD_TIME:
            self.button_count = 0
            self.state = State.preActive

        # ACCELERATING
        elif self.state == State.increasing:
          self.button_count += 1
          if self.v_target <= self.v_cruise_cluster or self.button_count > RESET_COUNT:
            self.button_count = 0
            self.state = State.holding

        # DECELERATING
        elif self.state == State.decreasing:
          self.button_count += 1
          if self.v_target >= self.v_cruise_cluster or self.v_cruise_cluster <= self.v_cruise_min or self.button_count > RESET_COUNT:
            self.button_count = 0
            self.state = State.holding

    # INACTIVE
    elif self.state == State.inactive:
      if self.is_ready:
        if not self.is_ready_prev:
          self.pre_active_timer = int(INACTIVE_TIMER / DT_CTRL)

        elif self.pre_active_timer <= 0:
          self.state = State.preActive

  def update_readiness(self, CS: car.CarState, CC: car.CarControl) -> None:
    update_manual_button_timers(CS, self.cruise_buttons)
    ready = CS.cruiseState.enabled and not CC.cruiseControl.cancel and not CC.cruiseControl.resume
    button_pressed = any(self.cruise_buttons[k] > 0 for k in self.cruise_buttons)

    self.is_ready = ready and not button_pressed

  def run(self, CS: car.CarState, CC: car.CarControl, is_metric: bool):
    if self.CP_SP.pcmCruiseSpeed:
      return

    self.is_metric = is_metric

    self.update_calculations(CS, CC)
    self.update_readiness(CS, CC)
    self.update_state_machine()

    self.is_ready_prev = self.is_ready
