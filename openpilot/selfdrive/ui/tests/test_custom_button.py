from types import SimpleNamespace
from unittest.mock import Mock

from opendbc.car.structs import car

from openpilot.selfdrive.ui.sunnypilot.custom_button import CustomButtonAction, handle_custom_button


def test_custom_button_actions():
  params = Mock()
  press = SimpleNamespace(carState=SimpleNamespace(buttonEvents=[SimpleNamespace(
      type=car.CarState.ButtonEvent.Type.altButton2,
      pressed=True,
    )]))
  messages = [press, SimpleNamespace(carState=SimpleNamespace(buttonEvents=[])), press]
  callbacks = {action: Mock() for action in CustomButtonAction if action != CustomButtonAction.NONE}

  for action, callback in callbacks.items():
    params.get.return_value = action
    handle_custom_button(messages, params, callbacks)
    assert callback.call_count == 2
