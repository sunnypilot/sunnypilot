"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from collections.abc import Sequence

import numpy as np

from cereal import messaging
from opendbc.car import structs
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.sunnypilot import get_sanitize_int_param
from openpilot.sunnypilot.selfdrive.controls.lib.accel_personality.constants import \
  NORMAL, PERSONALITY_MIN, PERSONALITY_MAX, A_CRUISE_MAX_BP, A_CRUISE_MAX_V, RISE_RATE, SMOOTH_DECEL_BP, \
  SMOOTH_DECEL_V, BRAKE_DEEPENING_JERK, BRAKE_RELEASE_JERK, ACCEL_RISE_JERK, SMOOTH_DECEL_LOOKAHEAD_T, \
  MIN_SMOOTH_BRAKE_NEED, HARD_BRAKE_TARGET_ACCEL, HARD_BRAKE_NEED, STOP_APPROACH_VEGO, \
  ONSET_JERK0, ONSET_JERK_GAIN, ONSET_GAP_SOFT, ONSET_GAP_GAIN, ONSET_JERK_MAX, ONSET_HANDBACK_JERK, \
  SOFT_ONSET_MAX_BRAKE_NEED, SOFT_ONSET_MAX_INSTANT_ACCEL, SOFT_ONSET_REARM_FRAMES

_ZERO_ACCEL_EPS = 1e-6


class AccelController:
  def __init__(self, CP: structs.CarParams, mpc, params=None):
    self._CP = CP
    self._mpc = mpc
    self._params = params or Params()
    self._frame = 0
    self._enabled = self._params.get_bool("AccelPersonalityEnabled")
    self._personality = NORMAL
    self._v_ego = 0.0
    self._last_target_accel = 0.0
    self._brake_need = 0.0
    self._decel_target = 0.0
    self._smooth_active = False
    self._bypassed = False
    # convex brake-onset shaper state
    self._onset_latched = False # sticky: True once an onset goes firm -> no re-soften until sustained release
    self._onset_release = 0     # consecutive non-deepening frames (sticky re-arm debounce)
    self._soft_active = False   # True iff the convex shaper governed this frame's output (bypasses min(.,raw))
    self._soft_episode = False  # True while a soft onset is open (incl. closing its gap) -> own deepening, no snap
    self._read_params()

  def _read_params(self) -> None:
    self._enabled = self._params.get_bool("AccelPersonalityEnabled")
    if not self._enabled:
      self._personality = NORMAL
      return
    self._personality = get_sanitize_int_param("AccelPersonality", PERSONALITY_MIN, PERSONALITY_MAX, self._params)

  def update(self, sm: messaging.SubMaster) -> None:
    if self._frame % int(1. / DT_MDL) == 0:
      self._read_params()
    self._v_ego = sm['carState'].vEgo
    self._frame += 1

  def get_max_accel(self, v_ego: float) -> float:
    return float(np.interp(v_ego, A_CRUISE_MAX_BP, A_CRUISE_MAX_V[self._personality]))

  def get_rise_rate(self) -> float:
    return RISE_RATE[self._personality]

  def get_decel_target(self, brake_need: float) -> float:
    return float(np.interp(max(0.0, float(brake_need)), SMOOTH_DECEL_BP, SMOOTH_DECEL_V[self._personality]))

  def smooth_target_accel(self, raw_target_accel: float, accel_trajectory: Sequence[float], t_idxs: Sequence[float],
                          should_stop: bool, reset: bool = False, stock_brake: bool = False) -> float:
    raw_target_accel = float(raw_target_accel)
    self._brake_need = self._compute_brake_need(raw_target_accel, accel_trajectory, t_idxs)
    self._decel_target = 0.0
    self._soft_active = False
    # convex shaper runs ONLY when enabled and personality != NORMAL (off==stock, NORMAL==stock).
    # Single source of truth: when it cannot run, hard-reset all shaper state so nothing leaks across
    # a param toggle (SPORT->NORMAL / enable->disable) or a bypass interlude.
    convex_on = self._enabled and self._personality != NORMAL
    if not convex_on:
      self._reset_onset()

    # disabled, reset, or blended/e2e braking: hand straight to the plan
    if reset or not self._enabled or (stock_brake and (raw_target_accel < 0.0 or self._brake_need >= MIN_SMOOTH_BRAKE_NEED)):
      self._bypassed = False
      return self._passthrough(raw_target_accel)

    self._bypassed = self._emergency_bypass(raw_target_accel, should_stop)
    if self._bypassed:
      self._reset_onset()
      return self._passthrough(raw_target_accel)

    # Low-speed creep-to-stop: stand down (incl. the brake_need-driven front-load, which softens even
    # when raw~0). Softening the final approach to a stopped lead makes the car brake less -> coast
    # farther -> halt too close (~1.3 m). Hand full stock decel through so it stops at the proper gap.
    # Onset shaping still applies above STOP_APPROACH_VEGO.
    if self._v_ego < STOP_APPROACH_VEGO:
      self._reset_onset()
      return self._passthrough(raw_target_accel)

    if self._brake_need < MIN_SMOOTH_BRAKE_NEED:
      self._smooth_active = False
      slewed = self._slew(raw_target_accel)
      if self._soft_active:
        return self._finalize(slewed)
      return self._finalize(min(slewed, raw_target_accel) if raw_target_accel < 0.0 else slewed)

    # front-load a gentle early brake, never weaker than the plan (unless the convex onset is active)
    self._smooth_active = True
    self._decel_target = self.get_decel_target(self._brake_need)
    slewed = self._slew(min(raw_target_accel, self._decel_target))
    if self._soft_active:
      return self._finalize(slewed)
    return self._finalize(min(slewed, raw_target_accel))

  def _compute_brake_need(self, raw_target_accel: float, accel_trajectory: Sequence[float], t_idxs: Sequence[float]) -> float:
    min_accel = float(raw_target_accel)
    for accel, t in zip(accel_trajectory, t_idxs, strict=False):
      if float(t) <= SMOOTH_DECEL_LOOKAHEAD_T:
        min_accel = min(min_accel, float(accel))
    return max(0.0, -min_accel)

  def _emergency_bypass(self, raw_target_accel: float, should_stop: bool) -> bool:
    return (self._mpc.crash_cnt > 0 or should_stop or
            raw_target_accel <= HARD_BRAKE_TARGET_ACCEL or self._brake_need >= HARD_BRAKE_NEED)

  def _slew(self, target_accel: float) -> float:
    target_accel = float(target_accel)
    p = self._personality
    jmax = BRAKE_DEEPENING_JERK[p]
    deepening = target_accel <= self._last_target_accel
    if not deepening:
      # genuine release / coast: close any soft episode, advance the re-arm debounce, unlatch after a
      # sustained release.
      self._soft_episode = False
      self._onset_release += 1
      if self._onset_release >= SOFT_ONSET_REARM_FRAMES:
        self._onset_latched = False
      return self._slew_up(target_accel)
    self._onset_release = 0
    # NORMAL (and disabled, forced to NORMAL) -> stock constant-jerk linear deepening, byte-exact.
    if p == NORMAL:
      return self._clean_accel(max(target_accel, self._last_target_accel - jmax * DT_MDL))
    return self._slew_convex(target_accel, jmax)

  def _onset_soft_armed(self, target_accel: float) -> bool:
    # Gentle non-emergency onset. Armed from the FIRST deepening tick (no brake_need lower gate, so the
    # gentle bite lands on the actual onset, not after the plan has already deepened). Two upper gates
    # keep it off firm/deep braking: the 3s-lookahead brake_need ceiling AND the instantaneous raw depth.
    return (self._enabled and self._personality != NORMAL and
            0.0 < self._brake_need < SOFT_ONSET_MAX_BRAKE_NEED and
            target_accel > SOFT_ONSET_MAX_INSTANT_ACCEL)

  def _slew_convex(self, target_accel: float, jmax: float) -> float:
    # target_accel is the effective plan to track (raw, or min(raw, decel_target) on the smooth branch).
    p = self._personality
    last = self._last_target_accel
    soft_armed = self._onset_soft_armed(target_accel)
    armed = soft_armed and not self._onset_latched
    gap = max(0.0, last - target_accel)   # m/s^2 currently shallower than the plan (last,target both <=0)
    if not armed:
      # entered the firm/deep zone: latch off any further (re)arming for this event.
      if soft_armed:
        self._onset_latched = True
      # NEVER start softening a fresh firm brake.
      if not (self._soft_episode and gap > _ZERO_ACCEL_EPS):
        self._soft_episode = False
        return self._clean_accel(max(target_accel, last - jmax * DT_MDL))   # stock; caller does min(.,raw)
      # Plan left the gentle zone but a soft gap is still open: close it FAST (firm, jerk-limited so it
      # is not a snap) so the output catches the plan before braking gets firm -> no late-brake lag.
      out = max(last - ONSET_HANDBACK_JERK[p] * DT_MDL, target_accel)
      if out <= target_accel + _ZERO_ACCEL_EPS:
        self._soft_episode = False
      self._soft_active = True
      return self._clean_accel(out)
    self._soft_episode = True
    # Depth-proportional convex jerk: gentle ONSET_JERK0 at the bite (a~0), growing with current decel
    # depth. da/dt = j0 + k*a integrates to a(t) = (j0/k)*(exp(k*t)-1), the exponential-growth profile.
    jerk = ONSET_JERK0[p] + ONSET_JERK_GAIN[p] * abs(last)
    # Instantaneous-gap catch-up (stateless): once realized lags the plan by more than ONSET_GAP_SOFT,
    # add bounded jerk so the softening can't run away and the gap-close is never a snap; hard-capped at
    # ONSET_JERK_MAX so even the catch (while still gentle/armed) is never a grab.
    jerk = min(jerk + ONSET_GAP_GAIN[p] * max(0.0, gap - ONSET_GAP_SOFT[p]), ONSET_JERK_MAX[p])
    out = max(last - jerk * DT_MDL, target_accel)   # never deeper than the plan -> only softer-or-equal
    if out <= target_accel + _ZERO_ACCEL_EPS:       # gap closed -> episode complete
      self._soft_episode = False
    self._soft_active = True
    return self._clean_accel(out)

  def _reset_onset(self) -> None:
    self._onset_latched = False
    self._onset_release = 0
    self._soft_active = False
    self._soft_episode = False

  def _slew_up(self, target_accel: float) -> float:
    if self._last_target_accel < 0.0:
      released = min(target_accel, self._last_target_accel + BRAKE_RELEASE_JERK * DT_MDL)
      if released <= 0.0:
        return self._clean_accel(released)
      return self._clean_accel(min(target_accel, ACCEL_RISE_JERK[self._personality] * DT_MDL))
    step = ACCEL_RISE_JERK[self._personality] * DT_MDL
    return self._clean_accel(min(target_accel, self._last_target_accel + step))

  def _passthrough(self, target_accel: float) -> float:
    self._smooth_active = False
    self._soft_active = False
    return self._finalize(target_accel)

  def _finalize(self, target_accel: float) -> float:
    target_accel = self._clean_accel(target_accel)
    self._last_target_accel = target_accel
    return target_accel

  @staticmethod
  def _clean_accel(accel: float) -> float:
    accel = float(accel)
    return 0.0 if abs(accel) < _ZERO_ACCEL_EPS else accel

  def enabled(self) -> bool:
    return self._enabled

  def personality(self):
    return self._personality

  def max_accel(self) -> float:
    return self.get_max_accel(self._v_ego)

  def brake_need(self) -> float:
    return self._brake_need

  def decel_target(self) -> float:
    return self._decel_target

  def smooth_active(self) -> bool:
    return self._smooth_active

  def bypassed(self) -> bool:
    return self._bypassed
