from collections.abc import Callable
from enum import Enum

import pyray as rl

from openpilot.selfdrive.ui.sunnypilot.ui_state import ui_state_sp
from openpilot.system.ui.lib.multilang import tr, tr_noop
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, simple_button_item_sp, option_item_sp
from openpilot.system.ui.widgets.network import NavButton
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.widgets import Widget
from system.ui.sunnypilot.widgets.list_view import multiple_button_item_sp

MADS_STEERING_MODE_OPTIONS = [
  (tr("Remain Active"), tr_noop("Remain Active: ALC will remain active when the brake pedal is pressed.")),
  (tr("Pause"), tr_noop("Pause: ALC will pause when the brake pedal is pressed.")),
  (tr("Disengage"),tr_noop("Disengage: ALC will disengage when the brake pedal is pressed."))
]

class MadsSettingsLayout(Widget):
  def __init__(self, back_btn_callback: Callable):
    super().__init__()
    self._back_button = NavButton(tr("Back"))
    self._back_button.set_click_callback(back_btn_callback)
    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=True, spacing=0)

  def _initialize_items(self):
    self._main_cruise_toggle = toggle_item_sp(
      title=lambda: tr("Toggle with Main Cruise"),
      description="",
      param="MadsMainCruiseAllowed",
    )
    self._unified_engagement_toggle = toggle_item_sp(
      title=lambda: tr("Unified Engagement Mode (UEM)"),
      description="",
      param="MadsUnifiedEngagementMode"
    )
    self._steering_mode = multiple_button_item_sp(
      param="MadsSteeringMode",
      title=lambda: tr("Steering Mode on Brake Pedal"),
      description="",
      buttons=[opt[0] for opt in MADS_STEERING_MODE_OPTIONS],
      inline=False,
      button_width=350
    )

    items = [
      self._main_cruise_toggle,
      self._unified_engagement_toggle,
      self._steering_mode,
    ]
    return items

  def _update_state(self):
    super()._update_state()

  def _render(self, rect):
    self._back_button.set_position(self._rect.x, self._rect.y + 20)
    self._back_button.render()
    # subtract button
    content_rect = rl.Rectangle(rect.x, rect.y + self._back_button.rect.height + 40,
                                rect.width, rect.height - self._back_button.rect.height - 40)
    self._scroller.render(content_rect)

  def show_event(self):
    self._scroller.show_event()

  def _mads_limited_settings(self) -> bool:
    if ui_state_sp.CP and ui_state_sp.CP.brand == "Rivian":
      return True
    elif ui_state_sp.CP and ui_state_sp.CP.brand == "Tesla":
      return not ui_state_sp.CP_SP.flags() & 1  # 1 == TeslaFlagsSP.HAS_VEHICLE_BUS
    return False

  def _update_toggles(self):
    if self._mads_limited_settings():
      ui_state_sp.params.remove("MadsMainCruiseAllowed")
      ui_state_sp.params.put_bool("MadsUnifiedEngagementMode", True)
      ui_state_sp.params.put("MadsSteeringMode", "Disengage")
