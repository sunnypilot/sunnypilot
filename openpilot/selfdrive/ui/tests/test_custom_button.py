from types import SimpleNamespace
from unittest.mock import Mock

from opendbc.car.structs import car

from openpilot.selfdrive.ui.layouts import main


class FakeSubMaster:
  def __init__(self, messages):
    self.messages = messages
    self.updated = {'carState': True}

  def __getitem__(self, key):
    return self.messages[key]


def test_custom_button_actions(monkeypatch):
  params = Mock()
  params.get_bool.return_value = False
  sm = FakeSubMaster({
    'carState': SimpleNamespace(buttonEvents=[SimpleNamespace(
      type=car.CarState.ButtonEvent.Type.altButton2,
      pressed=True,
    )]),
  })
  monkeypatch.setattr(main, 'ui_state', SimpleNamespace(sm=sm, params=params))

  layout = main.MainLayout.__new__(main.MainLayout)
  layout._on_bookmark_clicked = Mock()

  params.get.return_value = main.CustomButtonAction.BOOKMARK
  layout._handle_custom_button()
  layout._on_bookmark_clicked.assert_called_once()

  params.get.return_value = main.CustomButtonAction.QUIET_MODE
  layout._handle_custom_button()
  params.put_bool.assert_called_once_with('QuietMode', True)
