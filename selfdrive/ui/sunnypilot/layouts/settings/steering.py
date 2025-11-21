from enum import IntEnum
import pyray as rl

from openpilot.selfdrive.ui.sunnypilot.ui_state import ui_state_sp
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, simple_button_item_sp, option_item_sp
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller, LineSeparator
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
    )
    self._mads_settings_button = simple_button_item_sp(
      button_text=lambda: tr("Customize MADS"),
      button_width=600
    )
    self._lane_change_settings_button = simple_button_item_sp(
      button_text=lambda: tr("Customize Lane Change"),
      button_width=800
    )
    self._blinker_control_toggle = toggle_item_sp(
      param="BlinkerPauseLateralControl",
      description=lambda: tr("Pause lateral control with blinker when traveling below the desired speed selected."),
      title=lambda: tr("Pause Lateral Control with Blinker"),
    )
    self._blinker_control_options = option_item_sp(
      param="BlinkerMinLateralControlSpeed",
      title=lambda: tr("Minimum Speed to Pause Lateral Control"),
      min_value=0,
      max_value=255,
      value_change_step=5,
      description="",
      label_callback=lambda speed: f'{speed} {"km/h" if ui_state_sp.is_metric else "mph"}'
    )
    self._torque_control_toggle = toggle_item_sp(
      param="EnforceTorqueControl",
      title=lambda: tr("Enforce Torque Lateral Control"),
      description=lambda: tr("Enable this to enforce sunnypilot to steer with Torque lateral control."),
    )
    self._torque_customization_button = simple_button_item_sp(
      button_text=lambda: tr("Customize Torque Params"),
      button_width=850
    )
    self._nnlc_toggle = toggle_item_sp(
      param="NeuralNetworkLateralControl",
      title=lambda: tr("Neural Network Lateral Control (NNLC)"),
      description=""
    )

    items = [
      self._mads_toggle,
      self._mads_settings_button,
      LineSeparator(),
      self._lane_change_settings_button,
      LineSeparator(),
      self._blinker_control_toggle,
      self._blinker_control_options,
      LineSeparator(),
      self._torque_control_toggle,
      self._torque_customization_button,
      LineSeparator(),
      self._nnlc_toggle
    ]
    return items

  def _update_state(self):
    super()._update_state()
    self._mads_toggle.action_item.set_enabled(ui_state_sp.is_offroad())
    self._mads_settings_button.action_item.set_enabled(ui_state_sp.is_offroad())
    self._mads_settings_button.set_visible(self._mads_toggle.action_item.get_state())
    self._blinker_control_options.set_visible(self._blinker_control_toggle.action_item.get_state())
    self._torque_customization_button.set_visible(self._torque_control_toggle.action_item.get_state())


  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    # subtract button
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40,
                                rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()
