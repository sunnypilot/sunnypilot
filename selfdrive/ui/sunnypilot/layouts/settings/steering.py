from enum import IntEnum
import pyray as rl

from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, button_item_sp
from openpilot.system.ui.widgets.list_view import button_item
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller import Scroller, LineSeparator
from openpilot.system.ui.widgets import Widget
from openpilot.common.params import Params

class PanelType(IntEnum):
  STEERING = 0
  MADS = 1
  LANE_CHANGE = 2
  TORQUE_CONTROL = 3
  PAUSE_BLINKER = 4

class SteeringLayout(Widget):
  def __init__(self):
    super().__init__()

    self._params = Params()
    self._current_panel = PanelType.STEERING
    self._back_button = NavButton(tr("Back"))

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  def _initialize_items(self):
    self._mads_toggle = toggle_item_sp(
      param="Mads",
      title=lambda: tr("Modular Assistive Driving System (MADS)"),
      description=lambda: tr("Enable the beloved MADS feature. " +
                             "Disable toggle to revert back to stock sunnypilot engagement/disengagement."),
      callback=lambda state: self._mads_settings_button.set_visible(state)
    )
    self._mads_settings_button = button_item_sp(
      title=lambda: tr("Customize MADS Settings"),
      button_text=lambda: tr("MADS"),
    )
    self._mads_settings_button.set_visible(False)
    items = [
      self._mads_toggle,
      self._mads_settings_button,
      LineSeparator(),
    ]
    return items

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    # subtract button
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40,
                                rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()
