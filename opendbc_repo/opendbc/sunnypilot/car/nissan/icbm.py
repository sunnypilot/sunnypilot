"""
Copyright (c) 2021-, sunnypilot, downquark7, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections import deque
from enum import IntEnum

from opendbc.car import DT_CTRL, structs
from opendbc.car.can_definitions import CanData
from opendbc.sunnypilot.car.intelligent_cruise_button_management_interface_base import IntelligentCruiseButtonManagementInterfaceBase
from opendbc.sunnypilot.car.nissan.nissancan_ext import create_cruise_throttle_msg

SendButtonState = structs.IntelligentCruiseButtonManagement.SendButtonState

BUTTONS = {
  SendButtonState.increase: "RES_BUTTON",
  SendButtonState.decrease: "SET_BUTTON",
}

# Driver presses swallowed while ICBM owns CRUISE_THROTTLE, replayed afterward
REPLAY_BUTTONS = ("PROPILOT_BUTTON", "FOLLOW_DISTANCE_BUTTON", "SET_BUTTON", "RES_BUTTON")


class ButtonSendState(IntEnum):
  IDLE = 0
  RELEASE = 1
  PRESS = 2


class IntelligentCruiseButtonManagementInterface(IntelligentCruiseButtonManagementInterfaceBase):
  def __init__(self, CP, CP_SP):
    super().__init__(CP, CP_SP)
    self.button_send_state = ButtonSendState.IDLE
    self.queued_buttons = deque()
    self.prev_buttons = dict.fromkeys(REPLAY_BUTTONS, False)

  def reset(self):
    self.button_send_state = ButtonSendState.IDLE
    self.queued_buttons.clear()
    self.last_button_frame = self.frame

  def update(self, CS, CC_SP, packer, frame, last_button_frame, pcm_cancel_cmd) -> list[CanData]:
    self.CC_SP = CC_SP
    self.ICBM = CC_SP.intelligentCruiseButtonManagement
    self.frame = frame
    self.last_button_frame = last_button_frame

    buttons = {b: CS.cruise_throttle_msg[b] for b in REPLAY_BUTTONS}
    pressed = [b for b in REPLAY_BUTTONS if buttons[b] and not self.prev_buttons[b]]
    self.prev_buttons = buttons

    send_button = None
    # Drop pending presses on cancel or disengage so nothing can resume cruise afterward
    if pcm_cancel_cmd or CS.cruise_throttle_msg["CANCEL_BUTTON"] or not CS.out.cruiseState.enabled:
      self.reset()
      if pcm_cancel_cmd:
        send_button = "CANCEL_BUTTON"

    else:
      if self.button_send_state == ButtonSendState.IDLE and (self.queued_buttons or self.ICBM.sendButton != SendButtonState.none):
        self.button_send_state = ButtonSendState.RELEASE

      if self.button_send_state != ButtonSendState.IDLE:
        self.queued_buttons.extend(pressed)

      # Send no button, giving the car time to adjust the set speed
      if self.button_send_state == ButtonSendState.RELEASE:
        send_button = "NO_BUTTON_PRESSED"
        if (self.frame - self.last_button_frame) * DT_CTRL >= 0.06:
          if not self.queued_buttons and self.ICBM.sendButton != SendButtonState.none:
            self.queued_buttons.append(BUTTONS[self.ICBM.sendButton])
          if self.queued_buttons:
            self.button_send_state = ButtonSendState.PRESS
            self.last_button_frame = self.frame
          # Hold release until the driver lets go, so a swallowed press is not passed through again
          elif not any(buttons.values()):
            self.button_send_state = ButtonSendState.IDLE

      elif self.button_send_state == ButtonSendState.PRESS:
        send_button = self.queued_buttons[0]
        if (self.frame - self.last_button_frame) * DT_CTRL >= 0.06:
          self.queued_buttons.popleft()
          self.button_send_state = ButtonSendState.RELEASE
          self.last_button_frame = self.frame

    return [create_cruise_throttle_msg(packer, self.CP.carFingerprint, CS.cruise_throttle_msg, self.frame, send_button)]
