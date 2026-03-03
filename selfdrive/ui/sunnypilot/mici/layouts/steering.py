"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""


from cereal import car
from openpilot.selfdrive.ui.mici.widgets.button import (
  BigButton, BigParamControl, BigParamOption, BigMultiParamToggle,
)
from openpilot.selfdrive.ui.sunnypilot.mici.layouts._nav import make_sub_view
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.mads.helpers import MadsSteeringModeOnBrake, mads_limited_settings
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets.scroller import NavScroller

MADS_STEERING_MODE_LABELS = ["remain", "pause", "disengage"]


def _bb(val: bool) -> str:
  return "on" if val else "off"


def _speed_unit():
  return "km/h" if ui_state.is_metric else "mph"


# ---------------------------------------------------------------------------
# MADS sub-panel items
# ---------------------------------------------------------------------------
def _build_mads_items():
  main_cruise = BigParamControl("main cruise toggle", "MadsMainCruiseAllowed")
  unified = BigParamControl("unified engagement", "MadsUnifiedEngagementMode")
  steering_mode = BigMultiParamToggle(
    "steering on brake", "MadsSteeringMode",
    MADS_STEERING_MODE_LABELS,
  )
  return [main_cruise, unified, steering_mode], main_cruise, unified, steering_mode


# ---------------------------------------------------------------------------
# Lane Change sub-panel items
# ---------------------------------------------------------------------------
def _build_lane_change_items():
  auto_lc = BigParamControl("auto lane change", "AutoLaneChangeTimer")
  bsm_delay = BigParamControl("bsm delay", "AutoLaneChangeBsmDelay")
  return [auto_lc, bsm_delay], auto_lc, bsm_delay


# ---------------------------------------------------------------------------
# Blinker sub-panel items
# ---------------------------------------------------------------------------
def _build_blinker_items():
  toggle = BigParamControl("enable blinker pause", "BlinkerPauseLateralControl")
  speed = BigParamOption(
    "blinker speed", "BlinkerMinLateralControlSpeed",
    min_value=0, max_value=255, value_change_step=5,
    label_callback=lambda v: f"{v} {_speed_unit()}",
    picker_unit=_speed_unit,
  )
  delay = BigParamOption(
    "blinker delay", "BlinkerLateralReengageDelay",
    min_value=0, max_value=10,
    label_callback=lambda v: f"{v} seconds",
    picker_unit="seconds",
  )
  return [toggle, speed, delay], toggle, speed, delay


# ---------------------------------------------------------------------------
# Torque sub-panel items
# ---------------------------------------------------------------------------
def _build_self_tune_items():
  self_tune = BigParamControl("enable self-tune", "LiveTorqueParamsToggle")
  relaxed = BigParamControl("less restrict", "LiveTorqueParamsRelaxedToggle")
  return [self_tune, relaxed], self_tune, relaxed


def _build_custom_tune_items():
  custom_tune = BigParamControl("enable custom tuning", "CustomTorqueParams")
  manual_rt = BigParamControl("manual realtime", "TorqueParamsOverrideEnabled")
  lat_accel = BigParamOption(
    "lat accel", "TorqueParamsOverrideLatAccelFactor",
    min_value=1, max_value=500,
    label_callback=lambda x: f"{x / 100} m/s\u00b2",
    picker_label_callback=lambda x: f"{x / 100}",
    float_param=True,
    picker_unit="m/s\u00b2",
  )
  friction = BigParamOption(
    "friction", "TorqueParamsOverrideFriction",
    min_value=1, max_value=100,
    label_callback=lambda x: f"{x / 100}",
    float_param=True,
  )
  return [custom_tune, manual_rt, lat_accel, friction], \
    custom_tune, manual_rt, lat_accel, friction


# ===========================================================================
# Main Steering Layout
# ===========================================================================
class SteeringLayoutMici(NavScroller):
  def __init__(self):
    super().__init__()

    # Transition tracking to avoid per-frame disk writes
    self._prev_torque_allowed: bool | None = None
    self._prev_mads_limited: bool | None = None
    self._prev_self_tune_on: bool | None = None

    # --- Main view items ---
    self._mads_settings_btn = BigButton("mads")
    self._lane_change_btn = BigButton("lane change")
    self._blinker_settings_btn = BigButton("blinker pause")
    self._torque_settings_btn = BigButton("torque control")

    self._nnlc_toggle = BigParamControl("nnlc", "NeuralNetworkLateralControl")

    for btn in [self._mads_settings_btn, self._lane_change_btn, self._blinker_settings_btn, self._torque_settings_btn]:
      btn.set_subtitle_font_size(24)

    self._scroller.add_widgets([
      self._mads_settings_btn,
      self._lane_change_btn,
      self._blinker_settings_btn,
      self._torque_settings_btn,
      self._nnlc_toggle,
    ])

    # --- Sub-panel items ---
    self._mads_toggle = BigParamControl("enable mads", "Mads")
    self._mads_items_rest, self._mads_main_cruise, self._mads_unified, self._mads_steering = _build_mads_items()
    self._mads_items = [self._mads_toggle] + self._mads_items_rest

    self._lc_items, self._lc_timer, self._lc_bsm = _build_lane_change_items()

    self._blinker_items, self._blinker_toggle, self._blinker_speed, self._blinker_delay = _build_blinker_items()

    self._torque_toggle = BigParamControl("enable torque control", "EnforceTorqueControl")

    # Self-tune subcategory
    self._tq_self_tune_btn = BigButton("self tune")
    self._tq_self_tune_btn.set_subtitle_font_size(24)
    self._tq_self_tune_items, self._tq_self_tune, self._tq_relaxed = _build_self_tune_items()

    # Custom tuning subcategory
    self._tq_custom_btn = BigButton("custom tune")
    self._tq_custom_btn.set_subtitle_font_size(24)
    self._tq_custom_items, self._tq_custom, self._tq_manual_rt, \
      self._tq_lat_accel, self._tq_friction = _build_custom_tune_items()

    self._tq_items_rest = [self._tq_self_tune_btn, self._tq_custom_btn]
    self._tq_items = [self._torque_toggle] + self._tq_items_rest

    # Pre-build sub-view NavScrollers (pushed onto nav stack on click)
    self._mads_view = make_sub_view(self._mads_items)
    self._lc_view = make_sub_view(self._lc_items)
    self._blinker_view = make_sub_view(self._blinker_items)
    self._tq_view = make_sub_view(self._tq_items)
    self._tq_self_tune_view = make_sub_view(self._tq_self_tune_items)
    self._tq_custom_view = make_sub_view(self._tq_custom_items)

    self._mads_settings_btn.set_click_callback(lambda: gui_app.push_widget(self._mads_view))
    self._lane_change_btn.set_click_callback(lambda: gui_app.push_widget(self._lc_view))
    self._blinker_settings_btn.set_click_callback(lambda: gui_app.push_widget(self._blinker_view))
    self._torque_settings_btn.set_click_callback(lambda: gui_app.push_widget(self._tq_view))
    self._tq_self_tune_btn.set_click_callback(lambda: gui_app.push_widget(self._tq_self_tune_view))
    self._tq_custom_btn.set_click_callback(lambda: gui_app.push_widget(self._tq_custom_view))

  # --- State gating ---
  def _update_state(self):
    super()._update_state()

    self._nnlc_toggle.refresh()

    torque_allowed = (ui_state.CP is not None and
                      ui_state.CP.steerControlType != car.CarParams.SteerControlType.angle)
    if not torque_allowed and self._prev_torque_allowed is not False:
      ui_state.params.remove("EnforceTorqueControl")
      ui_state.params.remove("NeuralNetworkLateralControl")
    self._prev_torque_allowed = torque_allowed

    mads_on = ui_state.params.get_bool("Mads")
    offroad = ui_state.is_offroad()
    self._mads_settings_btn.set_enabled(offroad)
    if not mads_on:
      self._mads_settings_btn.set_value("off")
    else:
      cruise = _bb(ui_state.params.get_bool("MadsMainCruiseAllowed"))
      unified = _bb(ui_state.params.get_bool("MadsUnifiedEngagementMode"))
      steer_idx = ui_state.params.get("MadsSteeringMode") or 0
      steer_mode = MADS_STEERING_MODE_LABELS[min(steer_idx, len(MADS_STEERING_MODE_LABELS) - 1)]
      self._mads_settings_btn.set_badges([
        ("enabled", "on"),
        ("main-cruise", cruise),
        ("unified", unified),
        (steer_mode, "on"),
      ])

    blinker_on = ui_state.params.get_bool("BlinkerPauseLateralControl")
    if not blinker_on:
      self._blinker_settings_btn.set_value("off")
    else:
      speed_val = ui_state.params.get("BlinkerMinLateralControlSpeed", return_default=True) or 0
      unit = _speed_unit()
      delay_val = ui_state.params.get("BlinkerLateralReengageDelay", return_default=True) or 0
      self._blinker_settings_btn.set_badges([
        ("enabled", "on"),
        ("pause", f"{speed_val}{unit}"),
        ("delay", f"{delay_val}s"),
      ])

    lc_auto = _bb(ui_state.params.get_bool("AutoLaneChangeTimer"))
    lc_bsm = _bb(ui_state.params.get_bool("AutoLaneChangeBsmDelay"))
    if lc_auto == "off" and lc_bsm == "off":
      self._lane_change_btn.set_value("off")
    else:
      self._lane_change_btn.set_badges([
        ("auto", lc_auto),
        ("bsm-delay", lc_bsm),
      ])

    enforce_torque = ui_state.params.get_bool("EnforceTorqueControl")
    self._torque_settings_btn.set_enabled(torque_allowed)
    if not enforce_torque:
      self._torque_settings_btn.set_value("off")
    else:
      self_tune = _bb(ui_state.params.get_bool("LiveTorqueParamsToggle"))
      custom = _bb(ui_state.params.get_bool("CustomTorqueParams"))
      self._torque_settings_btn.set_badges([
        ("enabled", "on"),
        ("self-tune", self_tune),
        ("custom-tuning", custom),
      ])
    self._nnlc_toggle.set_enabled(torque_allowed and offroad and not enforce_torque)

    # --- Sub-panel state ---
    self._update_mads_state()
    self._update_lane_change_state()
    self._update_blinker_state()
    self._update_torque_state(torque_allowed)

  def _update_mads_state(self):
    self._mads_toggle.refresh()
    self._mads_main_cruise.refresh()
    self._mads_unified.refresh()

    mads_on = ui_state.params.get_bool("Mads")
    offroad = ui_state.is_offroad()
    self._mads_toggle.set_enabled(offroad)

    is_mads_limited = mads_limited_settings(ui_state)
    if is_mads_limited:
      if self._prev_mads_limited is not True:
        ui_state.params.remove("MadsMainCruiseAllowed")
        ui_state.params.put_bool("MadsUnifiedEngagementMode", True)
        ui_state.params.put("MadsSteeringMode", MadsSteeringModeOnBrake.DISENGAGE)
        self._mads_steering.refresh()
        self._mads_main_cruise.refresh()
        self._mads_unified.refresh()
      self._mads_main_cruise.set_enabled(False)
      self._mads_unified.set_enabled(False)
      self._mads_steering.set_enabled(False)
    else:
      enabled = mads_on
      self._mads_main_cruise.set_enabled(enabled)
      self._mads_unified.set_enabled(enabled)
      self._mads_steering.set_enabled(enabled)
    self._prev_mads_limited = is_mads_limited

  def _update_lane_change_state(self):
    self._lc_timer.refresh()
    self._lc_bsm.refresh()
    enable_bsm = ui_state.CP is not None and ui_state.CP.enableBsm
    self._lc_bsm.set_enabled(enable_bsm)

  def _update_blinker_state(self):
    self._blinker_toggle.refresh()
    self._blinker_speed.refresh()
    self._blinker_delay.refresh()

    self._blinker_speed.set_enabled(lambda: self._blinker_toggle.is_checked)
    self._blinker_delay.set_enabled(lambda: self._blinker_toggle.is_checked)

  def _update_torque_state(self, torque_allowed: bool):
    self._torque_toggle.refresh()

    enforce_torque = ui_state.params.get_bool("EnforceTorqueControl")
    nnlc = ui_state.params.get_bool("NeuralNetworkLateralControl")
    offroad = ui_state.is_offroad()
    self._torque_toggle.set_enabled(torque_allowed and offroad and not nnlc)

    # Disable subcategory buttons when torque is off
    for item in self._tq_items_rest:
      item.set_enabled(enforce_torque)

    # Self-tune subcategory button summary
    self_tune_on = ui_state.params.get_bool("LiveTorqueParamsToggle")
    if not self_tune_on:
      self._tq_self_tune_btn.set_value("off")
      if self._prev_self_tune_on is not False:
        ui_state.params.remove("LiveTorqueParamsRelaxedToggle")
      self._prev_self_tune_on = False
    else:
      self._prev_self_tune_on = True
      relaxed = _bb(ui_state.params.get_bool("LiveTorqueParamsRelaxedToggle"))
      self._tq_self_tune_btn.set_badges([
        ("enabled", "on"),
        ("less-restrict", relaxed),
      ])

    # Custom tuning subcategory button summary
    custom_on = ui_state.params.get_bool("CustomTorqueParams")
    if not custom_on:
      self._tq_custom_btn.set_value("off")
    else:
      manual_rt = _bb(ui_state.params.get_bool("TorqueParamsOverrideEnabled"))
      lat_raw = ui_state.params.get("TorqueParamsOverrideLatAccelFactor", return_default=True) or 1
      fric_raw = ui_state.params.get("TorqueParamsOverrideFriction", return_default=True) or 1
      lat_val = int(lat_raw) / 100
      fric_val = int(fric_raw) / 100
      self._tq_custom_btn.set_badges([
        ("enabled", "on"),
        ("realtime", manual_rt),
        ("frc", str(fric_val)),
        ("lat", str(lat_val)),
      ])

    # Self-tune sub-panel state — use lambda so enabled evaluates at render time
    # (after the toggle processes the tap in the same frame)
    self._tq_self_tune.refresh()
    self._tq_relaxed.refresh()
    self._tq_self_tune.set_enabled(offroad)
    self._tq_relaxed.set_enabled(lambda: self._tq_self_tune.is_checked)

    # Custom tuning sub-panel state — same lambda pattern
    self._tq_custom.refresh()
    self._tq_manual_rt.refresh()
    self._tq_lat_accel.refresh()
    self._tq_friction.refresh()
    self._tq_custom.set_enabled(offroad)
    self._tq_manual_rt.set_enabled(lambda: self._tq_custom.is_checked)
    self._tq_lat_accel.set_enabled(lambda: self._tq_custom.is_checked)
    self._tq_friction.set_enabled(lambda: self._tq_custom.is_checked)
