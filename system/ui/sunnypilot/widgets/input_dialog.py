"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections.abc import Callable

from openpilot.common.params import Params
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets import DialogResult
from openpilot.system.ui.widgets.keyboard import Keyboard


class InputDialogSP:
  def __init__(self, title: str, sub_title: str | None = None, current_text: str = "", param: str | None = None,
               callback: Callable[[DialogResult, str], None] | None = None,
               min_text_size: int = 0, password_mode: bool = False):
    self.callback = callback
    self.current_text = current_text
    self.keyboard = Keyboard(max_text_size=255, min_text_size=min_text_size, password_mode=password_mode)
    self.param = param
    self._params = Params()
    self.sub_title = sub_title
    self.title = title

  def show(self):
    self.keyboard.reset(min_text_size=self.keyboard._min_text_size)
    if self.sub_title:
      self.keyboard.set_title(self.title, self.sub_title)
    else:
      self.keyboard.set_title(self.title)
    self.keyboard.set_text(self.current_text)

    def internal_callback(result: DialogResult):
      text = self.keyboard.text if result == DialogResult.CONFIRM else ""
      if result == DialogResult.CONFIRM and self.param:
        self._params.put(self.param, text)
      if self.callback:
        self.callback(result, text)

    gui_app.set_modal_overlay(self.keyboard, internal_callback)
