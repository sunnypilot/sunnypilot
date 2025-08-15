from openpilot.system.ui.widgets.scroller import Scroller
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.sunnypilot.lib.list_view import option_item_sp
from openpilot.common.params import Params


class CruiseLayout(Widget):
  def __init__(self):
    super().__init__()

    self._params = Params()
    items = self._init_items()
    self._scroller = Scroller(items, line_separator=True, spacing=0)

  def _init_items(self):
    def on_gap_change(value: int):
      self._params.put("CustomAccLongPressIncrement", str(value))

    current_gap = int(self._params.get("CustomAccLongPressIncrement", return_default = True) or "3")

    items = [
    ]
    return items

  def _render(self, rect):
    self._scroller.render(rect)
