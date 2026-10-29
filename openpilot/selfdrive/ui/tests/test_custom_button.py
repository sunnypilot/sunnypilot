from types import SimpleNamespace
from unittest.mock import Mock

from openpilot.common.test import OpenpilotTestCase
import openpilot.selfdrive.ui.sunnypilot.custom_button as custom_button
from openpilot.selfdrive.ui.sunnypilot.custom_button import ALT_BUTTON_2_BIT, CustomButton, CustomButtonAction


def make_ui_state(monkeypatch, action, has_custom_button=True):
  state = SimpleNamespace(started=True, has_custom_button=has_custom_button, params=Mock(),
                          sm={"selfdriveStateSP": SimpleNamespace(buttonsReleaseToggle=0)})
  state.params.get.return_value = action
  monkeypatch.setattr(custom_button, "ui_state", state)
  return state


def run(button, state, toggles):
  for toggle in toggles:
    state.sm["selfdriveStateSP"].buttonsReleaseToggle = toggle
    button.update()


class TestCustomButton(OpenpilotTestCase):
  def test_actions_on_release(self, monkeypatch):
    for action in (CustomButtonAction.BOOKMARK, CustomButtonAction.CYCLE_UI):
      state = make_ui_state(monkeypatch, action)
      callbacks = {a: Mock() for a in (CustomButtonAction.BOOKMARK, CustomButtonAction.CYCLE_UI)}
      # first read seeds, then two releases of altButton2 and one of another button
      run(CustomButton(callbacks), state, [0, 1 << ALT_BUTTON_2_BIT, 1 << ALT_BUTTON_2_BIT, 0, 0b1])
      assert callbacks[action].call_count == 2
      assert sum(cb.call_count for cb in callbacks.values()) == 2


  def test_no_action_when_unavailable_or_unknown(self, monkeypatch):
    callback = Mock()
    state = make_ui_state(monkeypatch, 2)  # removed option value
    run(CustomButton({CustomButtonAction.BOOKMARK: callback}), state, [0, 1 << ALT_BUTTON_2_BIT])

    state = make_ui_state(monkeypatch, CustomButtonAction.BOOKMARK, has_custom_button=False)
    run(CustomButton({CustomButtonAction.BOOKMARK: callback}), state, [0, 1 << ALT_BUTTON_2_BIT])

    state = make_ui_state(monkeypatch, CustomButtonAction.BOOKMARK)
    run(CustomButton({CustomButtonAction.BOOKMARK: callback}), state, [1 << ALT_BUTTON_2_BIT])  # stale toggle on first read
    assert callback.call_count == 0
