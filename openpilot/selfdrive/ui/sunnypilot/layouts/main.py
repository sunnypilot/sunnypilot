"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.layouts.main import MainLayout, MainState
from openpilot.selfdrive.ui.sunnypilot.custom_button import CustomButton, CustomButtonAction


class MainLayoutSP(MainLayout):
  def __init__(self):
    super().__init__()
    self._custom_button = CustomButton({
      CustomButtonAction.BOOKMARK: self._on_bookmark_clicked,
      CustomButtonAction.CYCLE_UI: self._cycle_ui,
    })

  def _render(self, rect):
    self._custom_button.update()
    super()._render(rect)

  def _cycle_ui(self):
    if self._current_mode == MainState.ONROAD and not self._sidebar.is_visible:
      self._sidebar.set_visible(True)
    elif self._current_mode == MainState.SETTINGS:
      self._set_mode_for_state()
    else:
      self._on_settings_clicked()
