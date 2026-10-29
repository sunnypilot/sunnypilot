"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.mici.layouts.main import MiciMainLayout
from openpilot.selfdrive.ui.sunnypilot.custom_button import CustomButton, CustomButtonAction
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets import Widget


class MiciMainLayoutSP(MiciMainLayout):
  def __init__(self):
    super().__init__()
    self._custom_button = CustomButton({
      CustomButtonAction.BOOKMARK: self._on_bookmark_clicked,
      CustomButtonAction.CYCLE_UI: self._cycle_ui,
    })

  def _render(self, rect):
    self._custom_button.update()
    super()._render(rect)

  def _show_layout(self, layout: Widget):
    if gui_app.widget_in_stack(self._onboarding_window):
      return
    gui_app.pop_widgets_to(self, lambda: self._scroll_to(layout))

  def _layout_visible(self, layout: Widget) -> bool:
    return abs(layout.rect.x - self._rect.x) < self._rect.width / 2

  def _cycle_ui(self):
    if gui_app.widget_in_stack(self._settings_layout):
      self._show_layout(self._onroad_layout)
    elif gui_app.get_active_widget() is self and self._layout_visible(self._home_layout):
      gui_app.push_widget(self._settings_layout)
    else:
      self._show_layout(self._home_layout)
