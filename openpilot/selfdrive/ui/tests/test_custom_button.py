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
  params.get_bool.return_value = False
  sm = FakeSubMaster({
    'carState': SimpleNamespace(buttonEvents=[SimpleNamespace(
      type=car.CarState.ButtonEvent.Type.altButton2,
      pressed=True,
    )]),
  })
  bookmark_callback = Mock()

  params.get.return_value = CustomButtonAction.BOOKMARK
  handle_custom_button(sm, params, bookmark_callback)
  bookmark_callback.assert_called_once()

  params.get.return_value = CustomButtonAction.QUIET_MODE
  handle_custom_button(sm, params, bookmark_callback)
  params.put_bool.assert_called_once_with('QuietMode', True)
