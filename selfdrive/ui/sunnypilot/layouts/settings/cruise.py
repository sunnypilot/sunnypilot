from openpilot.system.ui.lib.scroller import Scroller
from openpilot.system.ui.lib.widget import Widget
from openpilot.system.ui.sunnypilot.lib.list_view import option_item
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

    current_gap = int(self._params.get("CustomAccLongPressIncrement", encoding="utf8") or "3")

    items = [
      option_item(
        title="Option Control Test",
        description="This is but a test",
        min_value=1,
        max_value=4,
        initial_value=current_gap,
        value_change_step=1,
        on_value_changed=on_gap_change
      )
    ]
    return items

  def _render(self, rect):
    self._scroller.render(rect)
