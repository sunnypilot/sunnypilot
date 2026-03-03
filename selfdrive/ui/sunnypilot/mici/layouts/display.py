"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""


from openpilot.selfdrive.ui.mici.widgets.button import BigParamOption
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.display import ONROAD_BRIGHTNESS_TIMER_VALUES, OnroadBrightness
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.widgets.scroller import NavScroller


def _timer_picker_unit():
  raw = ui_state.params.get("OnroadScreenOffTimer", return_default=True) or 0
  mapped = ONROAD_BRIGHTNESS_TIMER_VALUES.get(raw, raw)
  return "seconds" if mapped < 60 else "minutes"


def _brightness_label(val):
  if val == OnroadBrightness.AUTO:
    return "auto"
  if val == OnroadBrightness.AUTO_DARK:
    return "auto (dark)"
  if val == OnroadBrightness.SCREEN_OFF:
    return "screen off"
  return f"{(val - 2) * 5}%"


def _brightness_picker_label(val):
  if val == OnroadBrightness.AUTO:
    return "auto"
  if val == OnroadBrightness.AUTO_DARK:
    return "auto\n(dark)"
  if val == OnroadBrightness.SCREEN_OFF:
    return "0\n(off)"
  return str((val - 2) * 5)


def _timer_label(val):
  if val < 60:
    return f"{val} second{'s' if val != 1 else ''}"
  mins = int(val / 60)
  return f"{mins} minute{'s' if mins != 1 else ''}"


def _timer_picker_label(val):
  if val < 60:
    return str(val)
  return str(int(val / 60))


def _timeout_label(val):
  if not val:
    return "default"
  return f"{val} seconds"


class DisplayLayoutMici(NavScroller):
  def __init__(self):
    super().__init__()

    self._brightness = BigParamOption(
      "brightness", "OnroadScreenOffBrightness",
      min_value=0, max_value=22,
      label_callback=_brightness_label,
      picker_label_callback=_brightness_picker_label,
      picker_unit="%",
      picker_item_width=140,
    )
    self._brightness_timer = BigParamOption(
      "brightness delay", "OnroadScreenOffTimer",
      min_value=0, max_value=11,
      value_map=ONROAD_BRIGHTNESS_TIMER_VALUES,
      label_callback=_timer_label,
      picker_label_callback=_timer_picker_label,
      picker_unit=_timer_picker_unit,
    )
    self._ui_timeout = BigParamOption(
      "ui timeout", "InteractivityTimeout",
      min_value=0, max_value=120, value_change_step=10,
      label_callback=_timeout_label,
      picker_label_callback=lambda v: "default" if not v else str(v),
      picker_unit="seconds",
    )

    self._scroller.add_widgets([self._brightness, self._brightness_timer, self._ui_timeout])

  def _update_state(self):
    super()._update_state()
    self._brightness.refresh()
    self._brightness_timer.refresh()
    self._ui_timeout.refresh()

    brightness_val = ui_state.params.get("OnroadScreenOffBrightness", return_default=True)
    self._brightness_timer.set_enabled(
      brightness_val not in (OnroadBrightness.AUTO, OnroadBrightness.AUTO_DARK)
    )
