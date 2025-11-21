from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp
from openpilot.system.ui.widgets.scroller import Scroller
from openpilot.system.ui.widgets import Widget
from openpilot.common.params import Params


class DisplayLayout(Widget):
  def __init__(self):
    super().__init__()

    self._params = Params()
    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=True, spacing=0)

  def _initialize_items(self):
    self._onroad_brightness_toggle = toggle_item_sp(
      param="OnroadScreenOffControl",
      title=tr("Onroad Screen: Reduced Brightness"),
      description=tr("Turn off device screen or reduce brightness after driving starts. " +
         "It automatically brightens again when screen is touched or a visible alert is displayed."),
    )
    items = [
      self._onroad_brightness_toggle,
    ]
    return items

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
