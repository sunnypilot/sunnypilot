from enum import IntEnum

from opendbc.car.structs import car


class CustomButtonAction(IntEnum):
  NONE = 0
  BOOKMARK = 1
  QUIET_MODE = 2


def handle_custom_button(sm, params, bookmark_callback):
  if not sm.updated['carState']:
    return

  custom_pressed = any(be.type == car.CarState.ButtonEvent.Type.altButton2 and be.pressed
                       for be in sm['carState'].buttonEvents)
  if not custom_pressed:
    return

  action = CustomButtonAction(params.get('SteeringCustomButtonMapping', return_default=True))
  if action == CustomButtonAction.BOOKMARK:
    bookmark_callback()
  elif action == CustomButtonAction.QUIET_MODE:
    params.put_bool('QuietMode', not params.get_bool('QuietMode'))
