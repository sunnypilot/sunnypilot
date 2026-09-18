"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from collections.abc import Callable
from enum import IntEnum

import pyray as rl
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.cruise_sub_layouts.speed_limit_policy import SpeedLimitPolicyLayout
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.common import Mode as SpeedLimitMode
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.common import OffsetType as SpeedLimitOffsetType
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.sunnypilot.widgets import get_highlighted_description
from openpilot.system.ui.sunnypilot.widgets.list_view import multiple_button_item_sp, option_item_sp, simple_button_item_sp, LineSeparatorSP
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller

SPEED_LIMIT_MODE_BUTTONS = [tr("Off"), tr("Info"), tr("Warning"), tr("Assist")]
SPEED_LIMIT_OFFSET_TYPE_BUTTONS = [tr("None"), tr("Fixed"), tr("%")]

SPEED_LIMIT_MODE_DESCRIPTIONS = [
  tr("Off: Disables the Speed Limit functions."),
  tr("Information: Displays the current road's speed limit."),
  tr("Warning: Provides a warning when exceeding the current road's speed limit."),
  tr("Assist: Adjusts the vehicle's cruise speed based on the current road's speed limit when operating the +/- buttons."),
]

SPEED_LIMIT_OFFSET_DESCRIPTIONS = [
  tr("None: No Offset"),
  tr("Fixed: Adds a fixed offset [Speed Limit + Offset]"),
  tr("Percent: Adds a percent offset [Speed Limit + (Offset % Speed Limit)]"),
]


class PanelType(IntEnum):
  SETTINGS = 0
  POLICY = 1


class SpeedLimitSettingsLayout(Widget):
  def __init__(self, back_btn_callback: Callable):
    super().__init__()
    self._current_panel = PanelType.SETTINGS

    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)

    self._policy_layout = SpeedLimitPolicyLayout(lambda: self._set_current_panel(PanelType.SETTINGS))

    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=False, spacing=0)

  def _initialize_items(self):
    self._speed_limit_mode = multiple_button_item_sp(
      title=lambda: tr("Speed Limit"),
      description=self._get_mode_description,
      buttons=SPEED_LIMIT_MODE_BUTTONS,
      param="SpeedLimitMode",
      button_width=380,
    )

    self._source_button = simple_button_item_sp(
      button_text=lambda: tr("Customize Source"),
      button_width=720,
      callback=lambda: self._set_current_panel(PanelType.POLICY)
    )

    self._speed_limit_offset_type = multiple_button_item_sp(
      title=lambda: tr("Speed Limit Offset"),
      description="",
      buttons=SPEED_LIMIT_OFFSET_TYPE_BUTTONS,
      param="SpeedLimitOffsetType",
      button_width=450,
    )

    self._speed_limit_value_offset = option_item_sp(
      title="",
      param="SpeedLimitValueOffset",
      min_value=-30,
      max_value=30,
      description=self._get_offset_description,
      label_callback=self._get_offset_label,
    )

    items = [
      self._speed_limit_mode,
      LineSeparatorSP(40),
      self._source_button,
      LineSeparatorSP(40),
      self._speed_limit_offset_type,
      self._speed_limit_value_offset
    ]
    return items

  def _set_current_panel(self, panel: PanelType):
    self._current_panel = panel
    if panel == PanelType.POLICY:
      self._policy_layout.show_event()

  @staticmethod
  def _get_mode_description():
    return get_highlighted_description(ui_state.params, "SpeedLimitMode", SPEED_LIMIT_MODE_DESCRIPTIONS)

  @staticmethod
  def _get_offset_description():
    return get_highlighted_description(ui_state.params, "SpeedLimitOffsetType", SPEED_LIMIT_OFFSET_DESCRIPTIONS)

  @staticmethod
  def _get_offset_label(value):
    offset_type = int(ui_state.params.get("SpeedLimitOffsetType", return_default=True))
    unit = tr("km/h") if ui_state.is_metric else tr("mph")

    if offset_type == int(SpeedLimitOffsetType.percentage):
      return f"{value}%"
    elif offset_type == int(SpeedLimitOffsetType.fixed):
      return f"{value} {unit}"
    return str(value)

  def _update_state(self):
    super()._update_state()

    speed_limit_mode_param = ui_state.params.get("SpeedLimitMode", return_default=True)
    if ui_state.CP is not None and ui_state.CP_SP is not None:
      brand = ui_state.CP.brand
      has_long = ui_state.has_longitudinal_control
      has_icbm = ui_state.has_icbm

      """
          Speed Limit Assist is available when:
          - has_long or has_icbm, and
          - is not a release branch or not a disallowed brand, and
          - is not always disallwed
      """
      sla_disallow_in_release = brand == "tesla" and ui_state.is_sp_release
      sla_always_disallow = brand == "rivian"
      sla_available = (has_long or has_icbm) and not sla_disallow_in_release and not sla_always_disallow

      if not sla_available and speed_limit_mode_param == int(SpeedLimitMode.assist):
        ui_state.params.put("SpeedLimitMode", int(SpeedLimitMode.warning))

    else:
      sla_available = False

    if not sla_available:
      self._speed_limit_mode.action_item.set_enabled_buttons({
        int(SpeedLimitMode.off),
        int(SpeedLimitMode.information),
        int(SpeedLimitMode.warning),
      })
    else:
      self._speed_limit_mode.action_item.set_enabled_buttons(None)

    offset_type = ui_state.params.get("SpeedLimitOffsetType", return_default=True)
    self._speed_limit_value_offset.set_visible(offset_type != int(SpeedLimitOffsetType.off))

  def _render(self, rect):
    if self._current_panel == PanelType.POLICY:
      self._policy_layout.render(rect)
      return

    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()

    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40, rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._current_panel = PanelType.SETTINGS
    self._scroller.show_event()
    self._speed_limit_mode.show_description(True)

  def hide_event(self):
    self._current_panel = PanelType.SETTINGS
    self._scroller.hide_event()
