"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math
import time

import pyray as rl

from openpilot.selfdrive.ui.mici.layouts.home import MiciHomeLayout
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import FontWeight
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets.icon_widget import IconWidget
from openpilot.system.ui.widgets.label import UnifiedLabel, gui_label

METERS_PER_MILE = 1609.344
METERS_PER_KILOMETER = 1000.0
SUMMARY_DURATION_SECONDS = 10.0
SUMMARY_WAIT_SECONDS = 3.0


def _nonnegative_float(value) -> float:
  try:
    return max(0.0, float(value))
  except (TypeError, ValueError):
    return 0.0


class MiciHomeLayoutSP(MiciHomeLayout):
  def __init__(self):
    super().__init__()
    self._openpilot_label = UnifiedLabel("sunnypilot", font_size=88, font_weight=FontWeight.AUDIOWIDE, max_width=480, wrap_text=False)
    self._egpu_icon_default = IconWidget("icons_mici/egpu.png", (50, 37))
    self._egpu_icon_default.set_visible(False)
    self._egpu_icon_orange = IconWidget("icons_mici/egpu_orange.png", (50, 37))
    self._egpu_icon_orange.set_visible(False)
    gray_idx = self._status_bar_layout.widgets.index(self._egpu_icon_gray)
    self._status_bar_layout.widgets.insert(gray_idx + 1, self._egpu_icon_default)
    self._status_bar_layout.widgets.insert(gray_idx + 2, self._egpu_icon_orange)
    initial_summary = ui_state.params.get("LastDriveAssistedDrivingSummary", return_default=True) or {}
    self._last_summary_id = initial_summary.get("id", 0)
    self._summary_wait_until = 0.0
    self._summary_visible_until = 0.0
    self._drive_summary = {}

  def request_drive_summary(self) -> None:
    self._summary_wait_until = time.monotonic() + SUMMARY_WAIT_SECONDS

  def _render(self, _: rl.Rectangle) -> None:
    super()._render(_)
    now = time.monotonic()
    if now < self._summary_wait_until:
      summary = ui_state.params.get("LastDriveAssistedDrivingSummary", return_default=True) or {}
      summary_id = summary.get("id", 0)
      if summary_id and summary_id != self._last_summary_id:
        self._last_summary_id = summary_id
        distances = summary.get("distancesMeters", {})
        enabled = ui_state.params.get_bool("AssistedDrivingMilestonesEnabled")
        if enabled and any(_nonnegative_float(distances.get(category, 0.0)) > 0.0 for category in ("mads", "fullAssist")):
          self._drive_summary = summary
          self._summary_visible_until = now + SUMMARY_DURATION_SECONDS
        self._summary_wait_until = 0.0

    if now < self._summary_visible_until:
      self._draw_drive_summary(_)

  def _draw_drive_summary(self, rect: rl.Rectangle) -> None:
    distances = self._drive_summary.get("distancesMeters", {})
    metric = self._drive_summary.get("unit") == "metric"
    meters_per_unit = METERS_PER_KILOMETER if metric else METERS_PER_MILE
    unit = "KM" if metric else "MI"
    mads = _nonnegative_float(distances.get("mads", 0.0)) / meters_per_unit
    full_assist = _nonnegative_float(distances.get("fullAssist", 0.0)) / meters_per_unit

    rl.draw_rectangle_rec(rect, rl.Color(0, 0, 0, 235))
    gui_label(rl.Rectangle(rect.x, rect.y + 14, rect.width, 52), tr("DRIVE COMPLETE"), 42,
              font_weight=FontWeight.SEMI_BOLD, alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER)
    gui_label(rl.Rectangle(rect.x + 20, rect.y + 78, rect.width / 2 - 30, 42), tr("MADS"), 28,
              color=rl.Color(255, 255, 255, 184), alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER)
    gui_label(rl.Rectangle(rect.x + rect.width / 2 + 10, rect.y + 78, rect.width / 2 - 30, 42), tr("FULL ASSIST"), 28,
              color=rl.Color(255, 255, 255, 184), alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER)
    gui_label(rl.Rectangle(rect.x + 20, rect.y + 116, rect.width / 2 - 30, 72), f"{mads:.1f} {unit}", 48,
              font_weight=FontWeight.DISPLAY, alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER)
    gui_label(rl.Rectangle(rect.x + rect.width / 2 + 10, rect.y + 116, rect.width / 2 - 30, 72), f"{full_assist:.1f} {unit}", 48,
              font_weight=FontWeight.DISPLAY, alignment=rl.GuiTextAlignment.TEXT_ALIGN_CENTER)

  def _set_egpu_visibility(self):
    chestnut = ui_state.sm["deviceState"].chestnutPresent
    if not chestnut:
      self._egpu_icon.set_visible(False)
      self._egpu_icon_default.set_visible(False)
      self._egpu_icon_orange.set_visible(False)
      self._egpu_icon_gray.set_visible(False)
      return

    big_model_selected = ui_state.usbgpu_compiled or ui_state.model_runner_tinygrad
    big_model_failed = ui_state.started and ui_state.big_model_failed
    loading = ui_state.usbgpu_loading or (big_model_selected and ui_state.started and ui_state.usbgpu_active is None)

    if loading:
      self._egpu_icon_default._opacity = 0.35 + 0.65 * (0.5 - 0.5 * math.cos(rl.get_time() * 6.0))
      self._egpu_icon_default.set_visible(True)
      self._egpu_icon.set_visible(False)
      self._egpu_icon_orange.set_visible(False)
      self._egpu_icon_gray.set_visible(False)
    else:
      self._egpu_icon_default.set_visible(False)
      self._egpu_icon.set_visible(big_model_selected and not big_model_failed)
      self._egpu_icon_orange.set_visible(big_model_selected and big_model_failed)
      self._egpu_icon_gray.set_visible(not big_model_selected)
