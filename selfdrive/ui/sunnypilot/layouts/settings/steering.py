"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from enum import IntEnum

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, simple_button_item_sp, option_item_sp
from openpilot.system.ui.widgets.scroller_tici import Scroller, LineSeparator
from openpilot.system.ui.widgets import Widget
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.steering_sub_layouts.lane_change_settings import LaneChangeSettingsLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.steering_sub_layouts.mads_settings import MadsSettingsLayout
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.steering_sub_layouts.torque_settings import TorqueSettingsLayout


class PanelType(IntEnum):
  STEERING = 0
  MADS = 1
  LANE_CHANGE = 2
  TORQUE_CONTROL = 3

class SteeringLayout(Widget):
  def __init__(self):
    super().__init__()

    self._current_panel = PanelType.STEERING
    self._lane_change_settings_layout = LaneChangeSettingsLayout(lambda: self._set_current_panel(PanelType.STEERING))
    self._mads_settings_layout = MadsSettingsLayout(lambda: self._set_current_panel(PanelType.STEERING))
    self._torque_control_layout = TorqueSettingsLayout(lambda: self._set_current_panel(PanelType.STEERING))

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
      button_width=600,
      callback=lambda: self._set_current_panel(PanelType.MADS)
    )
    self._lane_change_settings_button = simple_button_item_sp(
      button_text=lambda: tr("Customize Lane Change"),
      button_width=800,
      callback=lambda: self._set_current_panel(PanelType.LANE_CHANGE)
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
      label_callback=lambda speed: f'{speed} {"km/h" if ui_state.is_metric else "mph"}'
    )
    self._torque_control_toggle = toggle_item_sp(
      param="EnforceTorqueControl",
      title=lambda: tr("Enforce Torque Lateral Control"),
      description=lambda: tr("Enable this to enforce sunnypilot to steer with Torque lateral control."),
    )
    self._torque_customization_button = simple_button_item_sp(
      button_text=lambda: tr("Customize Torque Params"),
      button_width=850,
      callback=lambda: self._set_current_panel(PanelType.TORQUE_CONTROL)
    )
    self._nnlc_toggle = toggle_item_sp(
      param="NeuralNetworkLateralControl",
      title=lambda: tr("Neural Network Lateral Control (NNLC)"),
      description=""
    )

    items = [
      self._lane_change_settings_button,
      LineSeparator(),
      self._mads_toggle,
      self._mads_settings_button,
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

  def _set_current_panel(self, panel: PanelType):
    self._current_panel = panel

  def _update_state(self):
    super()._update_state()
    self._mads_toggle.action_item.set_enabled(ui_state.is_offroad())
    self._mads_settings_button.action_item.set_enabled(ui_state.is_offroad())
    self._mads_settings_button.set_visible(self._mads_toggle.action_item.get_state())
    self._blinker_control_options.set_visible(self._blinker_control_toggle.action_item.get_state())
    self._torque_customization_button.set_visible(self._torque_control_toggle.action_item.get_state())


  def _render(self, rect):
    if self._current_panel == PanelType.LANE_CHANGE:
      self._lane_change_settings_layout.render(rect)
    elif self._current_panel == PanelType.MADS:
      self._mads_settings_layout.render(rect)
    elif self._current_panel == PanelType.TORQUE_CONTROL:
      self._torque_control_layout.render(rect)
    else:
      self._scroller.render(rect)

  def show_event(self):
    self._set_current_panel(PanelType.STEERING)
    self._scroller.show_event()
