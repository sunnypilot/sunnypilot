"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import car
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
from openpilot.sunnypilot.mads.helpers import MadsSteeringModeOnBrake, get_mads_limited_brands
from openpilot.system.ui.lib.application import gui_app

MADS_STEERING_MODE_LABELS = [tr("remain"), tr("pause"), tr("disengage")]


def _on_off(val: bool) -> str:
  return "on" if val else "off"


class SteeringLayoutMici(NavScroller):
  """Steering settings: MADS, lane change, blinker pause, torque control, NNLC.

  Sub-panels are pre-built NavScrollers pushed onto the nav stack via link_sub_panel.
  See CruiseLayoutMici for the transition tracking pattern explanation.
  """

  def __init__(self):
    super().__init__()

    # Transition tracking — None means first frame (triggers cleanup like False→False would)
    self._prev_torque_allowed: bool | None = None
    self._prev_mads_limited: bool | None = None
    self._prev_self_tune_on: bool | None = None

    # --- Main view items ---
    self._mads_settings_btn = BigButtonSP(tr("mads"))
    self._lane_change_btn = BigButtonSP(tr("lane change"))
    self._blinker_settings_btn = BigButtonSP(tr("blinker pause"))
    self._torque_settings_btn = BigButtonSP(tr("torque control"))
    self._nnlc_toggle = BigParamControl(tr("nnlc"), "NeuralNetworkLateralControl")

    for btn in [self._mads_settings_btn, self._lane_change_btn, self._blinker_settings_btn, self._torque_settings_btn]:
      btn.set_subtitle_font_size(24)

    self._scroller.add_widgets([
      self._mads_settings_btn, self._lane_change_btn,
      self._blinker_settings_btn, self._torque_settings_btn,
      self._nnlc_toggle,
    ])

    # --- MADS sub-panel ---
    self._mads_toggle = BigParamControl(tr("enable mads"), "Mads")
    self._mads_main_cruise = BigParamControl(tr("main cruise toggle"), "MadsMainCruiseAllowed")
    self._mads_unified = BigParamControl(tr("unified engagement"), "MadsUnifiedEngagementMode")
    self._mads_steering = BigMultiParamToggleSP(tr("steering on brake"), "MadsSteeringMode", MADS_STEERING_MODE_LABELS)
    self._mads_view = self._mads_settings_btn.link_sub_panel([self._mads_toggle, self._mads_main_cruise, self._mads_unified, self._mads_steering])

    # --- Lane change sub-panel ---
    self._lc_timer = BigParamControl(tr("auto lane change"), "AutoLaneChangeTimer")
    self._lc_bsm = BigParamControl(tr("bsm delay"), "AutoLaneChangeBsmDelay")
    self._lc_view = self._lane_change_btn.link_sub_panel([self._lc_timer, self._lc_bsm])

    # --- Blinker sub-panel ---
    self._blinker_toggle = BigParamControl(tr("enable blinker pause"), "BlinkerPauseLateralControl")
    self._blinker_speed = BigParamOption(tr("blinker speed"), "BlinkerMinLateralControlSpeed",
                                         min_value=0, max_value=255, value_change_step=5,
                                         label_callback=lambda v: f"{v} {speed_unit()}", picker_unit=speed_unit)
    self._blinker_delay = BigParamOption(tr("blinker delay"), "BlinkerLateralReengageDelay",
                                         min_value=0, max_value=10,
                                         label_callback=lambda v: f"{v} " + tr("seconds"), picker_unit=tr("seconds"))
    self._blinker_view = self._blinker_settings_btn.link_sub_panel([self._blinker_toggle, self._blinker_speed, self._blinker_delay])

    # --- Torque sub-panel ---
    self._torque_toggle = BigParamControl(tr("enable torque control"), "EnforceTorqueControl")

    self._tq_self_tune_btn = BigButtonSP(tr("self tune"))
    self._tq_self_tune_btn.set_subtitle_font_size(24)
    self._tq_self_tune = BigParamControl(tr("enable self-tune"), "LiveTorqueParamsToggle")
    self._tq_relaxed = BigParamControl(tr("less restrict"), "LiveTorqueParamsRelaxedToggle")
    self._tq_speed_dep = BigParamControl(tr("speed dependent"), "SpeedDependentTorqueToggle")
    self._tq_self_tune_view = self._tq_self_tune_btn.link_sub_panel([self._tq_self_tune, self._tq_relaxed, self._tq_speed_dep])

    self._tq_custom_btn = BigButtonSP(tr("custom tune"))
    self._tq_custom_btn.set_subtitle_font_size(24)
    self._tq_custom = BigParamControl(tr("enable custom tuning"), "CustomTorqueParams")
    self._tq_manual_rt = BigParamControl(tr("manual realtime"), "TorqueParamsOverrideEnabled")
    self._tq_lat_accel = BigParamOption(tr("lat accel"), "TorqueParamsOverrideLatAccelFactor",
                                        min_value=1, max_value=500, label_callback=lambda x: f"{x / 100} m/s\u00b2",
                                        picker_label_callback=lambda x: f"{x / 100}", float_param=True, picker_unit="m/s\u00b2")
    self._tq_friction = BigParamOption(tr("friction"), "TorqueParamsOverrideFriction",
                                       min_value=1, max_value=100, label_callback=lambda x: f"{x / 100}",
                                       picker_label_callback=lambda x: f"{x / 100}", float_param=True)
    self._tq_custom_view = self._tq_custom_btn.link_sub_panel([self._tq_custom, self._tq_manual_rt, self._tq_lat_accel, self._tq_friction])

    self._tq_items_rest = [self._tq_self_tune_btn, self._tq_custom_btn]
    self._tq_view = self._torque_settings_btn.link_sub_panel([self._torque_toggle] + self._tq_items_rest)

  # --- Main view state ---
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
      self._mads_settings_btn.set_disabled()
    else:
      cruise = _on_off(ui_state.params.get_bool("MadsMainCruiseAllowed"))
      unified = _on_off(ui_state.params.get_bool("MadsUnifiedEngagementMode"))
      steer_idx = ui_state.params.get("MadsSteeringMode", return_default=True) or 0
      steer_mode = MADS_STEERING_MODE_LABELS[min(steer_idx, len(MADS_STEERING_MODE_LABELS) - 1)]
      self._mads_settings_btn.set_badges([(tr("enabled"), "on"), (tr("main-cruise"), cruise), (tr("unified"), unified), (steer_mode, "on")])

    blinker_on = ui_state.params.get_bool("BlinkerPauseLateralControl")
    if not blinker_on:
      self._blinker_settings_btn.set_disabled()
    else:
      speed_val = ui_state.params.get("BlinkerMinLateralControlSpeed", return_default=True) or 0
      delay_val = ui_state.params.get("BlinkerLateralReengageDelay", return_default=True) or 0
      self._blinker_settings_btn.set_badges([(tr("enabled"), "on"), (tr("pause"), f"{speed_val}{speed_unit()}"), (tr("delay"), f"{delay_val}s")])

    lc_auto = _on_off(ui_state.params.get_bool("AutoLaneChangeTimer"))
    lc_bsm = _on_off(ui_state.params.get_bool("AutoLaneChangeBsmDelay"))
    if lc_auto == "off" and lc_bsm == "off":
      self._lane_change_btn.set_disabled()
    else:
      self._lane_change_btn.set_badges([(tr("auto"), lc_auto), (tr("bsm-delay"), lc_bsm)])

    enforce_torque = ui_state.params.get_bool("EnforceTorqueControl")
    self_tune_on = ui_state.params.get_bool("LiveTorqueParamsToggle")
    custom_on = ui_state.params.get_bool("CustomTorqueParams")

    self._torque_settings_btn.set_enabled(torque_allowed)
    if not enforce_torque:
      self._torque_settings_btn.set_disabled()
    else:
      self._torque_settings_btn.set_badges([(tr("enabled"), "on"), (tr("self-tune"), _on_off(self_tune_on)), (tr("custom-tuning"), _on_off(custom_on))])
    self._nnlc_toggle.set_enabled(torque_allowed and offroad and not enforce_torque)

    # --- Sub-panel state (skipped when not visible) ---
    self._update_mads_state()
    self._update_lane_change_state()
    self._update_blinker_state()
    self._update_torque_state(torque_allowed, enforce_torque, self_tune_on, custom_on)

  # --- MADS sub-panel ---
  def _update_mads_state(self):
    # Transition tracking — force safe defaults for MADS-limited brands (rivian, tesla w/o vehicle bus)
    is_mads_limited = ui_state.CP is not None and ui_state.CP_SP is not None and get_mads_limited_brands(ui_state.CP, ui_state.CP_SP)
    if is_mads_limited and self._prev_mads_limited is not True:
      ui_state.params.remove("MadsMainCruiseAllowed")
      ui_state.params.put_bool("MadsUnifiedEngagementMode", True)
      ui_state.params.put("MadsSteeringMode", MadsSteeringModeOnBrake.DISENGAGE)
    self._prev_mads_limited = is_mads_limited

    if not gui_app.widget_in_stack(self._mads_view):
      return
    self._mads_toggle.refresh()
    self._mads_main_cruise.refresh()
    self._mads_unified.refresh()
    self._mads_steering.refresh()

    mads_on = ui_state.params.get_bool("Mads")
    self._mads_toggle.set_enabled(ui_state.is_offroad())
    if is_mads_limited:
      self._mads_main_cruise.set_enabled(False)
      self._mads_unified.set_enabled(False)
      self._mads_steering.set_enabled(False)
    else:
      self._mads_main_cruise.set_enabled(mads_on)
      self._mads_unified.set_enabled(mads_on)
      self._mads_steering.set_enabled(mads_on)

  # --- Lane change sub-panel ---
  def _update_lane_change_state(self):
    if not gui_app.widget_in_stack(self._lc_view):
      return
    self._lc_timer.refresh()
    self._lc_bsm.refresh()
    self._lc_bsm.set_enabled(ui_state.CP is not None and ui_state.CP.enableBsm)

  # --- Blinker sub-panel ---
  def _update_blinker_state(self):
    if not gui_app.widget_in_stack(self._blinker_view):
      return
    self._blinker_toggle.refresh()
    self._blinker_speed.refresh()
    self._blinker_delay.refresh()
    self._blinker_speed.set_enabled(lambda: self._blinker_toggle._checked)
    self._blinker_delay.set_enabled(lambda: self._blinker_toggle._checked)

  # --- Torque sub-panel ---
  def _update_torque_state(self, torque_allowed: bool, enforce_torque: bool, self_tune_on: bool, custom_on: bool):
    if not self_tune_on and self._prev_self_tune_on is not False:
      ui_state.params.remove("LiveTorqueParamsRelaxedToggle")
    self._prev_self_tune_on = self_tune_on

    if not gui_app.widget_in_stack(self._tq_view):
      return

    self._torque_toggle.refresh()
    nnlc = ui_state.params.get_bool("NeuralNetworkLateralControl")
    offroad = ui_state.is_offroad()
    self._torque_toggle.set_enabled(torque_allowed and offroad and not nnlc)

    for item in self._tq_items_rest:
      item.set_enabled(enforce_torque)
      item.set_active(enforce_torque)

    if not self_tune_on:
      self._tq_self_tune_btn.set_disabled()
    else:
      self._tq_self_tune_btn.set_badges([(tr("enabled"), "on"), (tr("less-restrict"), _on_off(ui_state.params.get_bool("LiveTorqueParamsRelaxedToggle"))),
                                          (tr("speed-dependent"), _on_off(ui_state.params.get_bool("SpeedDependentTorqueToggle")))])

    if not custom_on:
      self._tq_custom_btn.set_disabled()
    else:
      manual_rt = _on_off(ui_state.params.get_bool("TorqueParamsOverrideEnabled"))
      lat_val = int(ui_state.params.get("TorqueParamsOverrideLatAccelFactor", return_default=True) or 1) / 100
      fric_val = int(ui_state.params.get("TorqueParamsOverrideFriction", return_default=True) or 1) / 100
      self._tq_custom_btn.set_badges([(tr("enabled"), "on"), (tr("realtime"), manual_rt), (f"{lat_val}m/s\u00b2", "on"), (str(fric_val), "on")])

    # Nested sub-panels — lambda enables same-frame toggle responsiveness (see button.py docstring)
    if gui_app.widget_in_stack(self._tq_self_tune_view):
      self._tq_self_tune.refresh()
      self._tq_relaxed.refresh()
      self._tq_speed_dep.refresh()
      self._tq_self_tune.set_enabled(offroad)
      self._tq_relaxed.set_enabled(lambda: self._tq_self_tune._checked)
      self._tq_speed_dep.set_enabled(lambda: self._tq_self_tune._checked)

    if gui_app.widget_in_stack(self._tq_custom_view):
      self._tq_custom.refresh()
      self._tq_manual_rt.refresh()
      self._tq_lat_accel.refresh()
      self._tq_friction.refresh()
      self._tq_custom.set_enabled(offroad)
      self._tq_manual_rt.set_enabled(lambda: self._tq_custom._checked)
      self._tq_lat_accel.set_enabled(lambda: self._tq_custom._checked)
      self._tq_friction.set_enabled(lambda: self._tq_custom._checked)
