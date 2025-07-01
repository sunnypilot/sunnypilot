from openpilot.system.ui.lib.scroller import Scroller
from openpilot.system.ui.lib.widget import Widget
from openpilot.common.params import Params


class SteeringLayout(Widget):
  def __init__(self):
    super().__init__()

    self._params = Params()
    items = self._init_items()
    self._scroller = Scroller(items, line_separator=True, spacing=0)

  def _init_items(self):
    items = [

    ]
    return items

  def _render(self, rect):
    self._scroller.render(rect)
