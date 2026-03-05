"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""



from openpilot.selfdrive.ui.mici.widgets.button import (
  BigButton,
  BigMultiParamToggle,
  BigParamControl,
  BigParamOption,
)
from openpilot.selfdrive.ui.sunnypilot.mici.layouts._nav import make_sub_view
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets.scroller import NavScroller

SL_MODE_LABELS = ["off", "info", "warn", "assist"]
SL_SOURCE_LABELS = ["car", "map", "car-first", "map-first", "combined"]
ACC_LONG_PRESS_MAP = {1: 1, 2: 5, 3: 10}


def _speed_unit():
  return "km/h" if ui_state.is_metric else "mph"


# ---------------------------------------------------------------------------
# Speed Limit sub-panel items
# ---------------------------------------------------------------------------
def _offset_unit():
  t = int(ui_state.params.get("SpeedLimitOffsetType", return_default=True))
  if t == 2:
    return "%"
  if t == 1:
    return _speed_unit()
  return ""


def _offset_label(value):
  unit = _offset_unit()
  return f"{value}{unit}" if unit else "none"


def _build_speed_limit_items():
  mode = BigMultiParamToggle(
    "speed limit mode",
    "SpeedLimitMode",
    SL_MODE_LABELS,
  )
  source = BigMultiParamToggle(
    "speed limit source",
    "SpeedLimitPolicy",
    SL_SOURCE_LABELS,
  )
  offset_type = BigMultiParamToggle(
    "offset type",
    "SpeedLimitOffsetType",
    ["none", "fixed", "%"],
  )

  offset_value = BigParamOption(
    "offset value",
    "SpeedLimitValueOffset",
    min_value=-30,
    max_value=30,
    label_callback=_offset_label,
    picker_unit=_offset_unit,
  )
  return [mode, source, offset_type, offset_value], mode, source, offset_type, offset_value


# ---------------------------------------------------------------------------
# Custom ACC sub-panel items
# ---------------------------------------------------------------------------
def _build_custom_acc_items():
  toggle = BigParamControl("enable custom increments", "CustomAccIncrementsEnabled")

  def _speed_label(v):
    return f"{v} {_speed_unit()}"
  short_press = BigParamOption(
    "short press",
    "CustomAccShortPressIncrement",
    min_value=1,
    max_value=10,
    label_callback=_speed_label,
    picker_unit=_speed_unit,
  )
  long_press = BigParamOption(
    "long press",
    "CustomAccLongPressIncrement",
    min_value=1,
    max_value=3,
    value_map=ACC_LONG_PRESS_MAP,
    label_callback=_speed_label,
    picker_unit=_speed_unit,
  )
  return [toggle, short_press, long_press], toggle, short_press, long_press


# ===========================================================================
# Main Cruise Layout
# ===========================================================================
class CruiseLayoutMici(NavScroller):
  def __init__(self):
    super().__init__()

    # Transition tracking to avoid per-frame disk writes
    self._prev_icbm_available: bool | None = None
    self._prev_has_long_or_icbm: bool | None = None
    self._prev_sla_available: bool | None = None

    # --- Main view items ---
    self._icbm_toggle = BigParamControl("intelligent cruise button management", "IntelligentCruiseButtonManagement",
                                       toggle_callback=lambda _: ui_state.update_params())
    self._dec_toggle = BigParamControl("dynamic experimental control", "DynamicExperimentalControl")
    self._scc_v_toggle = BigParamControl("smart cruise vision", "SmartCruiseControlVision")
    self._scc_m_toggle = BigParamControl("smart cruise map", "SmartCruiseControlMap")
    self._custom_acc_btn = BigButton("btn increments")
    self._speed_limit_btn = BigButton("speed limit")

    for btn in [self._custom_acc_btn, self._speed_limit_btn]:
      btn.set_subtitle_font_size(24)

    self._scroller.add_widgets(
      [
        self._icbm_toggle,
        self._dec_toggle,
        self._scc_v_toggle,
        self._scc_m_toggle,
        self._custom_acc_btn,
        self._speed_limit_btn,
      ]
    )

    # --- Custom ACC sub-panel ---
    self._acc_items, self._custom_acc_toggle, self._acc_short, self._acc_long = _build_custom_acc_items()

    # --- Speed limit sub-panel ---
    self._sl_items, self._sl_mode, self._sl_source, self._sl_offset_type, self._sl_offset_value = _build_speed_limit_items()

    # Pre-build sub-view NavScrollers
    self._acc_view = make_sub_view(self._acc_items)
    self._sl_view = make_sub_view(self._sl_items)

    self._custom_acc_btn.set_click_callback(lambda: gui_app.push_widget(self._acc_view))
    self._speed_limit_btn.set_click_callback(lambda: gui_app.push_widget(self._sl_view))

  # --- State gating ---
  def _update_state(self):
    super()._update_state()

    self._icbm_toggle.refresh()
    self._dec_toggle.refresh()
    self._scc_v_toggle.refresh()
    self._scc_m_toggle.refresh()

    has_long = False
    has_icbm = False
    icbm_available = False

    if ui_state.CP is not None and ui_state.CP_SP is not None:
      has_icbm = ui_state.has_icbm
      has_long = ui_state.has_longitudinal_control
      icbm_available = ui_state.CP_SP.intelligentCruiseButtonManagementAvailable and not has_long

      if icbm_available:
        self._icbm_toggle.set_enabled(ui_state.is_offroad())
      else:
        self._icbm_toggle.set_enabled(False)

      if has_long or has_icbm:
        offroad = ui_state.is_offroad()
        self._custom_acc_btn.set_enabled(((has_long and not ui_state.CP.pcmCruise) or has_icbm) and offroad)
        self._dec_toggle.set_enabled(has_long)
        self._scc_v_toggle.set_enabled(True)
        self._scc_m_toggle.set_enabled(True)
      else:
        self._custom_acc_btn.set_enabled(False)
        self._dec_toggle.set_enabled(False)
        self._scc_v_toggle.set_enabled(False)
        self._scc_m_toggle.set_enabled(False)
    else:
      self._icbm_toggle.set_enabled(False)
      self._custom_acc_btn.set_enabled(False)
      self._dec_toggle.set_enabled(False)
      self._scc_v_toggle.set_enabled(False)
      self._scc_m_toggle.set_enabled(False)

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
      self._custom_acc_btn.set_value("off")
    else:
      unit = _speed_unit()
      short_val = ui_state.params.get("CustomAccShortPressIncrement", return_default=True) or 1
      long_raw = ui_state.params.get("CustomAccLongPressIncrement", return_default=True) or 1
      long_val = ACC_LONG_PRESS_MAP.get(long_raw, long_raw)
      self._custom_acc_btn.set_badges(
        [
          ("enabled", "on"),
          ("short", f"{short_val}{unit}"),
          ("long", f"{long_val}{unit}"),
        ]
      )

    # Speed limit button subtitle
    sl_mode_idx = ui_state.params.get("SpeedLimitMode", return_default=True) or 0
    sl_mode = SL_MODE_LABELS[min(sl_mode_idx, len(SL_MODE_LABELS) - 1)]
    if sl_mode == "off":
      self._speed_limit_btn.set_value("off")
    else:
      sl_source_idx = ui_state.params.get("SpeedLimitPolicy", return_default=True) or 0
      sl_source = SL_SOURCE_LABELS[min(sl_source_idx, len(SL_SOURCE_LABELS) - 1)]
      sl_offset_val = ui_state.params.get("SpeedLimitValueOffset", return_default=True) or 0
      sl_offset = _offset_label(sl_offset_val)
      self._speed_limit_btn.set_badges(
        [
          (sl_mode, "on"),
          (sl_source, "on"),
          ("offset", sl_offset),
        ]
      )

    # Sub-panel state
    self._update_custom_acc_state()
    self._update_speed_limit_state()

  def _update_custom_acc_state(self):
    self._custom_acc_toggle.refresh()
    self._acc_short.refresh()
    self._acc_long.refresh()

    acc_enabled = self._custom_acc_btn.enabled
    self._custom_acc_toggle.set_enabled(acc_enabled)
    self._acc_short.set_enabled(lambda: acc_enabled and self._custom_acc_toggle.is_checked)
    self._acc_long.set_enabled(lambda: acc_enabled and self._custom_acc_toggle.is_checked)

  def _update_speed_limit_state(self):
    self._sl_mode.refresh()
    self._sl_source.refresh()
    self._sl_offset_type.refresh()

    # SLA availability gating — "assist" mode requires specific conditions
    sla_available = False
    if ui_state.CP is not None and ui_state.CP_SP is not None:
      brand = ui_state.CP.brand
      has_long = ui_state.has_longitudinal_control
      has_icbm = ui_state.has_icbm
      sla_disallow_in_release = brand == "tesla" and ui_state.is_sp_release
      sla_always_disallow = brand == "rivian"
      sla_available = (has_long or has_icbm) and not sla_disallow_in_release and not sla_always_disallow

    # Downgrade "assist" to "warning" when unavailable — only on transition
    if not sla_available and self._prev_sla_available is not False:
      sl_mode_idx = ui_state.params.get("SpeedLimitMode", return_default=True) or 0
      if sl_mode_idx == SL_MODE_LABELS.index("assist"):
        ui_state.params.put("SpeedLimitMode", SL_MODE_LABELS.index("warn"))
        self._sl_mode.refresh()
    self._prev_sla_available = sla_available

    self._sl_mode.set_enabled(True)
    self._sl_source.set_enabled(True)
    self._sl_offset_type.set_enabled(True)

    offset_type = ui_state.params.get("SpeedLimitOffsetType", return_default=True)
    self._sl_offset_value.set_enabled(offset_type != 0)  # 0 = off/none
    self._sl_offset_value.refresh()
