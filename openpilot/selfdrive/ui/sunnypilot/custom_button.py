from enum import IntEnum

from opendbc.car.structs import car


class CustomButtonAction(IntEnum):
  NONE = 0
  BOOKMARK = 1
  QUIET_MODE = 2
  ONROAD = 3
  HOME = 4
  SETTINGS = 5


def handle_custom_button(sm, params, callbacks):
  if not sm.updated['carState']:
    return

  custom_pressed = any(be.type == car.CarState.ButtonEvent.Type.altButton2 and be.pressed
                       for be in sm['carState'].buttonEvents)
  if not custom_pressed:
    return

  action = CustomButtonAction(params.get('CustomButtonAction', return_default=True))
  if callback := callbacks.get(action):
    callback()
