from enum import IntEnum

from opendbc.car.structs import car


class CustomButtonAction(IntEnum):
  NONE = 0
  BOOKMARK = 1
  CYCLE_UI = 3


def handle_custom_button(messages, params, callbacks):
  for msg in messages:
    custom_pressed = any(be.type == car.CarState.ButtonEvent.Type.altButton2 and be.pressed
                         for be in msg.carState.buttonEvents)
    if custom_pressed:
      action = CustomButtonAction(params.get('CustomButtonAction', return_default=True))
      if callback := callbacks.get(action):
        callback()
