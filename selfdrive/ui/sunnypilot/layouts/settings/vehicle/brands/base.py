"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import abc
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.sunnypilot.widgets.list_view import ToggleActionSP, MultipleButtonActionSP
from openpilot.system.ui.sunnypilot.widgets.option_control import OptionControlSP


class BrandSettings(abc.ABC):
  def __init__(self):
    self.items = []

  @abc.abstractmethod
  def update_settings(self) -> None:
    """Update the settings based on the current vehicle brand."""

  def update_toggles(self) -> None:
    for item in self.items:
      if not item.action_item:
        continue

      action = item.action_item
      if isinstance(action, ToggleActionSP) and action.toggle.param_key:
        action.set_state(ui_state.params.get_bool(action.toggle.param_key))
      elif isinstance(action, MultipleButtonActionSP) and action.param_key:
        action.selected_button = int(ui_state.params.get(action.param_key, return_default=True))
      elif isinstance(action, OptionControlSP) and action.param_key:
        action.current_value = int(ui_state.params.get(action.param_key, return_default=True))
