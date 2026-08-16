from types import SimpleNamespace
from unittest.mock import Mock

from opendbc.car.structs import car

from openpilot.selfdrive.ui.sunnypilot.custom_button import CustomButtonAction, handle_custom_button


class FakeSubMaster:
  def __init__(self, messages):
    self.messages = messages
    self.updated = {'carState': True}

  def __getitem__(self, key):
    return self.messages[key]


def test_custom_button_actions():
  params = Mock()
  sm = FakeSubMaster({
    'carState': SimpleNamespace(buttonEvents=[SimpleNamespace(
      type=car.CarState.ButtonEvent.Type.altButton2,
      pressed=True,
    )]),
  })
  callbacks = {action: Mock() for action in CustomButtonAction if action != CustomButtonAction.NONE}

  for action, callback in callbacks.items():
    params.get.return_value = action
    handle_custom_button(sm, params, callbacks)
    callback.assert_called_once()
