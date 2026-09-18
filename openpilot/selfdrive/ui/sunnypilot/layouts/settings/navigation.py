"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.common.params import Params
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.widgets import Widget


class NavigationLayout(Widget):
  def __init__(self):
    super().__init__()

    self._params = Params()
    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=True, spacing=0)

  def _initialize_items(self):
    items = [

    ]
    return items

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
