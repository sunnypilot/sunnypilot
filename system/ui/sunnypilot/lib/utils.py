"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.system.ui.sunnypilot.widgets.list_view import ButtonActionSP


class NoElideButtonAction(ButtonActionSP):
  def get_width_hint(self):
    return super().get_width_hint() + 1
