"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets import DialogResult
from openpilot.system.ui.widgets.html_render import HtmlModal


class HtmlModalSP(HtmlModal):
  def __init__(self, file_path=None, text=None, callback=None):
    super().__init__(file_path=file_path, text=text)
    self._callback = callback
    self._dialog_result = DialogResult.NO_ACTION
    self._ok_button._click_callback = self._on_ok_clicked

  def _on_ok_clicked(self):
    self._dialog_result = DialogResult.CONFIRM
    gui_app.set_modal_overlay(None)

    if self._callback:
      self._callback(self._dialog_result)

  def reset(self):
    self._dialog_result = DialogResult.NO_ACTION
