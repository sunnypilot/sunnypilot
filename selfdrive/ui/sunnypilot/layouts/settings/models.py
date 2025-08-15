from openpilot.system.ui.sunnypilot.lib.list_view import button_item_sp, toggle_item_sp
from openpilot.system.ui.widgets.scroller import Scroller
from openpilot.system.ui.widgets import Widget
from openpilot.common.params import Params


class ModelsLayout(Widget):
  def __init__(self):
    super().__init__()

    self._params = Params()
    items = self._init_items()
    self._scroller = Scroller(items, line_separator=True, spacing=0)

  def _init_items(self):
    items = [
      button_item_sp("Current Model", "SELECT", callback=self._on_model_select),
      toggle_item_sp("Live Learning Steer Delay"),
    ]
    return items

  def _render(self, rect):
    self._scroller.render(rect)

  def _on_model_select(self):
    return
