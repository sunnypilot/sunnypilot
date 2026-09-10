"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from openpilot.selfdrive.ui.mici.widgets.button import BigParamControl
from openpilot.selfdrive.ui.sunnypilot.mici.widgets.button import (
  BigButtonSP,
  BigMultiParamToggleSP,
  BigParamOption,
  speed_unit,
)
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets.scroller import NavScroller
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app

SL_MODE_LABELS = [tr("off"), tr("info"), tr("warn"), tr("assist")]
SL_SOURCE_LABELS = [tr("car"), tr("map"), tr("car-first"), tr("map-first"), tr("combined")]
SL_MODE_OFF = 0
SL_MODE_WARN = 2
SL_MODE_ASSIST = 3
ACC_LONG_PRESS_MAP = {1: 1, 2: 5, 3: 10}


def _offset_unit():
  t = int(ui_state.params.get("SpeedLimitOffsetType", return_default=True))
  if t == 2:
    return "%"
  if t == 1:
    return speed_unit()
  return ""


def _offset_label(value):
  unit = _offset_unit()
  return f"{value}{unit}" if unit else tr("none")


class CruiseLayoutMici(NavScroller):
  """Cruise settings: ICBM, DEC, SCC, custom ACC increments, speed limit assist.

  State gating pattern:
    - _update_state runs every frame, reads params and enables/disables widgets
    - _prev_* fields track state transitions (None → first frame, True → False = cleanup)
    - Params are only removed on True→False transitions to avoid per-frame disk writes
    - has_icbm is computed from toggle state directly to avoid 5s update_params delay
  """

  def __init__(self):
    super().__init__()

    self._prev_icbm_available: bool | None = None
    self._prev_has_long_or_icbm: bool | None = None
    self._prev_sla_available: bool | None = None

    # --- Main view items ---
    self._icbm_toggle = BigParamControl(tr("intelligent cruise button management"), "IntelligentCruiseButtonManagement")
    self._dec_toggle = BigParamControl(tr("dynamic experimental control"), "DynamicExperimentalControl")
    self._scc_v_toggle = BigParamControl(tr("smart cruise vision"), "SmartCruiseControlVision")
    self._scc_m_toggle = BigParamControl(tr("smart cruise map"), "SmartCruiseControlMap")
    self._custom_acc_btn = BigButtonSP(tr("custom increments"))
    self._speed_limit_btn = BigButtonSP(tr("speed limit"))

    for btn in [self._custom_acc_btn, self._speed_limit_btn]:
      btn.set_subtitle_font_size(24)

    self._scroller.add_widgets([
      self._icbm_toggle, self._dec_toggle,
      self._scc_v_toggle, self._scc_m_toggle,
      self._custom_acc_btn, self._speed_limit_btn,
    ])

    # --- Custom ACC sub-panel ---
    self._custom_acc_toggle = BigParamControl(tr("enable custom increments"), "CustomAccIncrementsEnabled")

    def _speed_label(v):
      return f"{v} {speed_unit()}"
    self._acc_short = BigParamOption(tr("short press"), "CustomAccShortPressIncrement",
                                     min_value=1, max_value=10, label_callback=_speed_label, picker_unit=speed_unit)
    self._acc_long = BigParamOption(tr("long press"), "CustomAccLongPressIncrement",
                                    min_value=1, max_value=3, value_map=ACC_LONG_PRESS_MAP,
                                    label_callback=_speed_label, picker_unit=speed_unit)
    self._acc_view = self._custom_acc_btn.link_sub_panel([self._custom_acc_toggle, self._acc_short, self._acc_long])

    # --- Speed limit sub-panel ---
    self._sl_mode = BigMultiParamToggleSP(tr("speed limit mode"), "SpeedLimitMode", SL_MODE_LABELS)
    self._sl_source = BigMultiParamToggleSP(tr("source"), "SpeedLimitPolicy", SL_SOURCE_LABELS)
    self._sl_offset_type = BigMultiParamToggleSP(tr("offset type"), "SpeedLimitOffsetType", [tr("none"), tr("fixed"), "%"])
    self._sl_offset_value = BigParamOption(tr("offset value"), "SpeedLimitValueOffset",
                                           min_value=-30, max_value=30, label_callback=_offset_label, picker_unit=_offset_unit)
    self._sl_view = self._speed_limit_btn.link_sub_panel([self._sl_mode, self._sl_source, self._sl_offset_type, self._sl_offset_value])

  # --- Main view state ---
  def _update_state(self):
    super()._update_state()

    self._icbm_toggle.refresh()
    self._dec_toggle.refresh()
    self._scc_v_toggle.refresh()
    self._scc_m_toggle.refresh()

    cp_ready = ui_state.CP is not None and ui_state.CP_SP is not None
    has_long = cp_ready and ui_state.has_longitudinal_control
    offroad = ui_state.is_offroad()
    icbm_available = cp_ready and ui_state.CP_SP.intelligentCruiseButtonManagementAvailable and not has_long
    # Compute from toggle state directly — avoids 5s update_params delay
    has_icbm = icbm_available and self._icbm_toggle._checked

    self._icbm_toggle.set_enabled(icbm_available and offroad)
    self._dec_toggle.set_enabled(has_long)
    self._scc_v_toggle.set_enabled(has_long or has_icbm)
    self._scc_m_toggle.set_enabled(has_long or has_icbm)
    self._custom_acc_btn.set_enabled(((has_long and not ui_state.CP.pcmCruise) or has_icbm) and offroad if cp_ready else False)

    # Transition tracking — only remove params on True→False transitions
    if not icbm_available and self._prev_icbm_available is not False:
      ui_state.params.remove("IntelligentCruiseButtonManagement")
    self._prev_icbm_available = icbm_available

    has_long_or_icbm = has_long or has_icbm
    if not has_long_or_icbm and self._prev_has_long_or_icbm is not False:
      ui_state.params.remove("CustomAccIncrementsEnabled")
      ui_state.params.remove("DynamicExperimentalControl")
      ui_state.params.remove("SmartCruiseControlVision")
      ui_state.params.remove("SmartCruiseControlMap")
    self._prev_has_long_or_icbm = has_long_or_icbm

    # Custom ACC button subtitle
    acc_on = ui_state.params.get_bool("CustomAccIncrementsEnabled")
    if not acc_on:
      self._custom_acc_btn.set_disabled()
    else:
      unit = speed_unit()
      short_val = ui_state.params.get("CustomAccShortPressIncrement", return_default=True) or 1
      long_raw = ui_state.params.get("CustomAccLongPressIncrement", return_default=True) or 1
      long_val = ACC_LONG_PRESS_MAP.get(long_raw, long_raw)
      self._custom_acc_btn.set_badges([(f"{short_val}{unit}", "on"), (f"{long_val}{unit}", "on")])

    # Speed limit button subtitle
    sl_mode_idx = ui_state.params.get("SpeedLimitMode", return_default=True) or 0
    sl_mode = SL_MODE_LABELS[min(sl_mode_idx, len(SL_MODE_LABELS) - 1)]
    offset_type = ui_state.params.get("SpeedLimitOffsetType", return_default=True)
    if sl_mode_idx == SL_MODE_OFF:
      self._speed_limit_btn.set_disabled()
    else:
      sl_source_idx = ui_state.params.get("SpeedLimitPolicy", return_default=True) or 0
      sl_source = SL_SOURCE_LABELS[min(sl_source_idx, len(SL_SOURCE_LABELS) - 1)]
      sl_offset_val = ui_state.params.get("SpeedLimitValueOffset", return_default=True) or 0
      unit = "%" if offset_type == 2 else (speed_unit() if offset_type == 1 else "")
      badges = [(sl_mode, "on"), (sl_source, "on")]
      if unit:
        sign = "+" if sl_offset_val > 0 else ""
        badges.append((f"{sign}{sl_offset_val}{unit}", "on"))
      self._speed_limit_btn.set_badges(badges)

    # --- Sub-panel state (skipped when not visible) ---
    self._update_custom_acc_state()
    self._update_speed_limit_state(cp_ready, has_long, has_icbm, offset_type)

  # --- Custom ACC sub-panel ---
  def _update_custom_acc_state(self):
    if not gui_app.widget_in_stack(self._acc_view):
      return
    self._custom_acc_toggle.refresh()
    self._acc_short.refresh()
    self._acc_long.refresh()
    self._custom_acc_toggle.set_enabled(self._custom_acc_btn.enabled)
    # Lambda: short/long respond same-frame when toggle is tapped (see button.py docstring)
    self._acc_short.set_enabled(lambda: self._custom_acc_btn.enabled and self._custom_acc_toggle._checked)
    self._acc_long.set_enabled(lambda: self._custom_acc_btn.enabled and self._custom_acc_toggle._checked)

  # --- Speed limit sub-panel ---
  def _update_speed_limit_state(self, cp_ready: bool, has_long: bool, has_icbm: bool, offset_type: int):
    # SLA availability gating (must always run)
    sla_available = False
    if cp_ready:
      brand = ui_state.CP.brand
      sla_disallow_in_release = brand == "tesla" and ui_state.is_sp_release
      sla_always_disallow = brand == "rivian"
      sla_available = (has_long or has_icbm) and not sla_disallow_in_release and not sla_always_disallow

    # Downgrade "assist" to "warning" when unavailable — only on transition
    if not sla_available and self._prev_sla_available is not False:
      sl_mode_idx = ui_state.params.get("SpeedLimitMode", return_default=True) or 0
      if sl_mode_idx == SL_MODE_ASSIST:
        ui_state.params.put("SpeedLimitMode", SL_MODE_WARN)
    self._prev_sla_available = sla_available

    if not gui_app.widget_in_stack(self._sl_view):
      return
    self._sl_mode.refresh()
    self._sl_source.refresh()
    self._sl_offset_type.refresh()
    self._sl_mode.set_enabled(True)
    self._sl_source.set_enabled(True)
    self._sl_offset_type.set_enabled(True)
    self._sl_offset_value.set_enabled(offset_type != 0)  # 0 = off/none
    self._sl_offset_value.refresh()
