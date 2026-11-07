"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.layouts.settings.initial_cruise_speed import get_speed_options, set_initial_cruise_speed
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import ListItemSP
from openpilot.system.ui.sunnypilot.widgets.option_control import OptionControlSP


class InitialCruiseSpeedControlSP(OptionControlSP):
  """Upstream's initial max speed stepper in the sunnypilot option style. Indexes the upstream option list,
  which is in display units; the param stays in km/h."""
  def __init__(self):
    self._options, idx = get_speed_options()
    super().__init__("InitialCruiseSpeedKph", 0, len(self._options) - 1)
    self.current_value = idx

  def refresh(self):
    self._options, self.current_value = get_speed_options()
    self.max_value = len(self._options) - 1

  def set_value(self, value: int):
    if not (self.min_value <= value <= self.max_value) or value == self.current_value:
      return
    self.current_value = value
    set_initial_cruise_speed(self._options[value])

  def get_displayed_value(self) -> str:
    return f"{self._options[self.current_value]} " + (tr("km/h") if ui_state.is_metric else tr("mph"))


def initial_cruise_speed_item_sp(**kwargs) -> ListItemSP:
  """Stock row in the sunnypilot option layout: title on top, control below, like option_item_sp."""
  return ListItemSP(inline=False, **kwargs)
