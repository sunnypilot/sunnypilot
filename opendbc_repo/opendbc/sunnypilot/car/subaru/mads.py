"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from enum import StrEnum
from opendbc.car import Bus, structs

from opendbc.car.subaru.values import SubaruFlags
from opendbc.sunnypilot.mads_base import MadsCarStateBase
from opendbc.can.parser import CANParser

ButtonType = structs.CarState.ButtonEvent.Type


class MadsCarState(MadsCarStateBase):
  def __init__(self, CP: structs.CarParams, CP_SP: structs.CarParamsSP):
    super().__init__(CP, CP_SP)
    self._prev_lkas_raw = None
    self._initial_applied = False

  @staticmethod
  def create_lkas_button_events(cur_btn: int, prev_btn: int,
                                buttons_dict: dict[int, structs.CarState.ButtonEvent.Type]) -> list[structs.CarState.ButtonEvent]:
    events: list[structs.CarState.ButtonEvent] = []

    if cur_btn == prev_btn:
      return events

    state_changes = [
      {"pressed": prev_btn != cur_btn and cur_btn != 2 and not (prev_btn == 2 and cur_btn == 1)},
      {"pressed": prev_btn != cur_btn and cur_btn == 2 and cur_btn != 1},
    ]

    for change in state_changes:
      if change["pressed"]:
        events.append(structs.CarState.ButtonEvent(pressed=change["pressed"],
                                                   type=buttons_dict.get(cur_btn, ButtonType.unknown)))
    return events

  def update_mads(self, ret: structs.CarState, can_parsers: dict[StrEnum, CANParser]) -> None:
    cp_cam = can_parsers[Bus.cam]

    self.prev_lkas_button = self.lkas_button
    if self.CP.flags & SubaruFlags.PREGLOBAL:
      # Pre-global Subarus don't have ES_LKAS_State. The LKAS button
      # state is in ES_DashStatus byte4 bit6 as a latching toggle (0/1).
      lkas_state = int(cp_cam.vl["ES_DashStatus"]["LKAS_State"])
      if self._prev_lkas_raw is None:
        # First read: record state, wait for cruise to be available
        self._prev_lkas_raw = lkas_state
        self.lkas_button = 0
      elif not self._initial_applied:
        # Track LKAS changes during boot (user may press button early)
        self._prev_lkas_raw = lkas_state
        if ret.cruiseState.available:
          # Cruise is ready. Apply current LKAS state to auto-enable
          # MADS if LKAS was left on, matching the dash indicator.
          self.lkas_button = lkas_state
          self._initial_applied = True
        else:
          self.lkas_button = 0
      else:
        # Normal operation: convert latching toggle to pulse so
        # create_lkas_button_events sees 0->1->0 per press.
        if lkas_state != self._prev_lkas_raw:
          self.lkas_button = 1
        else:
          self.lkas_button = 0
        self._prev_lkas_raw = lkas_state
    else:
      self.lkas_button = cp_cam.vl["ES_LKAS_State"]["LKAS_Dash_State"]

    ret.buttonEvents = self.create_lkas_button_events(self.lkas_button, self.prev_lkas_button, {1: ButtonType.lkas})
