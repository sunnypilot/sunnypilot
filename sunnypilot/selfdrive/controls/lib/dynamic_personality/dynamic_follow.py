"""
Copyright (c) 2021-, rav4kumar, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import log
import numpy as np
from collections import deque
from openpilot.common.realtime import DT_MDL
from openpilot.common.params import Params

LongPersonality = log.LongitudinalPersonality

PERSONALITY_BASE = {
  LongPersonality.relaxed:    1.75,
  LongPersonality.standard:   1.45,
  LongPersonality.aggressive: 1.25,
}

PERSONALITY_FLOOR = {
  LongPersonality.relaxed:    1.5,
  LongPersonality.standard:   1.2,
  LongPersonality.aggressive: 1.0,
}
PERSONALITY_CEILING = {
  LongPersonality.relaxed:    2.4,
  LongPersonality.standard:   2.0,
  LongPersonality.aggressive: 1.6,
}

JERK_WINDOW_FRAMES = 400   # ~20s at DT_MDL=0.05
JERK_DELTA_MAX     = 0.12  # sec added at max jerk volatility
JERK_SIGMA_SCALE   = 5.0   # m/s³ sigma to full delta

CUTIN_DELTA        = 0.10  # sec added on cut-in event
CUTIN_DECAY_FRAMES = 100   # ~5s decay

CLOSING_VREL_SCALE = -2.0  # m/s — vRel at which closing delta is maxed
CLOSING_DELTA_MAX  = 0.08  # sec

# High aLeadTau means MPC lead extrapolation decays fast — uncertain future.
# Radar resets tau to ~1.5 at brake onset; sustained braking drives tau→0.
# delta = ATAU_DELTA_MAX * (tau / ATAU_TAU_RESET): max at onset, smoothly falls to 0 as MPC calibrates.
# Gate on a_lead<-0.3 so modifier only fires during active braking.
ATAU_TAU_RESET = 1.5   # radar's reset value when |aLeadK| < 0.5 — used as normalization denominator
ATAU_DELTA_MAX = 0.08  # sec

# aLeadK-based delta: fires earlier than vRel closing delta
ALEAD_DECEL_SCALE = -1.0   # m/s² — aLeadK at which alead delta is maxed
ALEAD_DELTA_MAX   = 0.10   # sec

# Speed-dependent rate limits.
# Rate-up: fast at low speed for quick stop-and-go response, gentler at highway to avoid jerk.
# Rate-down: SLOW at low speed so t_follow stays elevated between repeated stop-and-go braking
#   events — keeps gap larger going into the next event → softer repeat braking.
#   Fast at highway so t_follow clears cleanly after sparse events → no rubber band.
T_FOLLOW_RATE_UP_BP   = [0.0, 20.0]        # m/s
T_FOLLOW_RATE_UP_V    = [0.42, 0.25]        # sec/sec
T_FOLLOW_RATE_DOWN_BP = [0.0, 10.0, 25.0]  # m/s
T_FOLLOW_RATE_DOWN_V  = [0.10, 0.16, 0.30]  # sec/sec

# Low-speed t_follow scaling for stop-and-go.
# MPC safe_dist = v²/(2*COMFORT_BRAKE) + t_follow*v + STOP_DIST.  At low speed the
# stopping-distance term already dominates; the t_follow component adds unnecessary
# gap requirement on top, forcing hard brakes when actual gap is urban-normal.
# Scaling reduces t_follow contribution at city speeds without changing internal tracking.
LOW_SPEED_SCALE_BP = [0.0, 3.0, 7.0, 12.0]  # m/s
LOW_SPEED_SCALE_V  = [0.15, 0.28, 0.62, 1.00]

# Dynamic headway scale: when time headway (dRel/v_ego) drops below HEADWAY_SCALE_S,
# boost speed_scale toward 1.0 so MPC feels safe_dist pressure at v=4-6 m/s
# (where stopping distance is small) rather than waiting until v=8-12 (hard brake).
# Gated on a_lead ≤ 0.1: when lead is accelerating away from stop, gap will naturally
# grow — don't apply boost or the car can't follow from a standing start.
HEADWAY_SCALE_V_MIN = 3.0   # m/s — below this allow crawl from stop unrestricted
HEADWAY_SCALE_S     = 2.5   # sec time-headway threshold that triggers boost

PERSONALITY_CHANGE_COOLDOWN_S = 2.0

# Grace period before clearing history on lead loss.
# Radar leadOne flips on/off at ~100% sub-1s rate due to prob threshold jitter.
# Without grace, every flip triggers _update_no_lead() → history reset → t_follow oscillation.
LEAD_LOST_GRACE_FRAMES = 10  # ~0.5s at DT_MDL=0.05


class FollowDistanceController:
  def __init__(self):
    self.params = Params()
    self._poll_frame = 0

    val = self.params.get('LongitudinalPersonality')
    self._personality = val if val is not None else LongPersonality.standard
    self._enabled = self.params.get_bool('DynamicFollow')

    self.current_t_follow = PERSONALITY_BASE[self._personality]
    self.first_run = True
    self.personality_change_cooldown = 0
    self.personality_cooldown_frames = int(PERSONALITY_CHANGE_COOLDOWN_S / DT_MDL)
    self._alead_history: deque[float] = deque(maxlen=JERK_WINDOW_FRAMES)
    self._jerk_history: deque[float] = deque(maxlen=JERK_WINDOW_FRAMES)
    self._prev_lead_status = False
    self._prev_drel = 0.0
    self._cutin_frames_remaining = 0
    self._cutin_confirm = 0  # consecutive frames of closure >3m before triggering
    self._lead_lost_grace = 0  # countdown frames before clearing history after lead loss
    self._last_lead_target: float | None = None  # last target computed with lead present

    self.dbg_jerk_delta    = 0.0
    self.dbg_cutin_delta   = 0.0
    self.dbg_closing_delta = 0.0
    self.dbg_atau_delta    = 0.0
    self.dbg_alead_delta   = 0.0
    self.dbg_speed_scale   = 1.0

  def is_enabled(self) -> bool:
    return self._enabled

  def set_enabled(self, enabled: bool):
    self._enabled = enabled
    self.params.put_bool('DynamicFollow', enabled)

  def toggle(self) -> bool:
    self.set_enabled(not self._enabled)
    return self._enabled

  @property
  def personality(self) -> int:
    return self._personality

  def get_personality(self) -> int:
    return int(self._personality)

  def set_personality(self, personality: int):
    if personality not in [LongPersonality.relaxed, LongPersonality.standard, LongPersonality.aggressive]:
      return
    self._personality = personality
    self.params.put('LongitudinalPersonality', personality)
    self.personality_change_cooldown = self.personality_cooldown_frames
    self._reset_history()

  def cycle_personality(self) -> int:
    personalities = [LongPersonality.relaxed, LongPersonality.standard, LongPersonality.aggressive]
    idx = personalities.index(self._personality)
    self.set_personality(personalities[(idx + 1) % len(personalities)])
    return int(self._personality)

  def get_follow_distance_multiplier(self, v_ego: float, radarstate=None) -> float:
    v_ego = max(0.0, v_ego)
    lead = radarstate.leadOne if (radarstate is not None and radarstate.leadOne.status) else None
    speed_scale = self._compute_speed_scale(v_ego, lead)
    self.dbg_speed_scale = speed_scale

    target = self._compute_target(v_ego, lead)

    if self.first_run:
      self.current_t_follow = target
      self.first_run = False
      return float(self.current_t_follow * speed_scale)

    rate_up   = float(np.interp(v_ego, T_FOLLOW_RATE_UP_BP,   T_FOLLOW_RATE_UP_V))   * DT_MDL
    rate_down = float(np.interp(v_ego, T_FOLLOW_RATE_DOWN_BP, T_FOLLOW_RATE_DOWN_V)) * DT_MDL

    if self.personality_change_cooldown > 0:
      self.current_t_follow = float(np.clip(target, self.current_t_follow - rate_up, self.current_t_follow + rate_up))
      return float(self.current_t_follow * speed_scale)

    rate = rate_up if target > self.current_t_follow else rate_down
    self.current_t_follow = float(np.clip(target, self.current_t_follow - rate, self.current_t_follow + rate))
    return float(self.current_t_follow * speed_scale)

  def reset(self):
    self._personality = LongPersonality.standard
    self.params.put('LongitudinalPersonality', LongPersonality.standard)
    self._poll_frame = 0
    self.current_t_follow = PERSONALITY_BASE[LongPersonality.standard]
    self.first_run = True
    self.personality_change_cooldown = 0
    self._reset_history()

  def update(self):
    self._poll_frame += 1
    if self.personality_change_cooldown > 0:
      self.personality_change_cooldown -= 1

    if self._poll_frame % max(1, int(1.0 / DT_MDL)) == 0:
      val = self.params.get('LongitudinalPersonality')
      new_personality = val if val is not None else LongPersonality.standard
      if new_personality != self._personality:
        self._personality = new_personality
        self.personality_change_cooldown = self.personality_cooldown_frames
        self._reset_history()
      self._enabled = self.params.get_bool('DynamicFollow')

  def _reset_history(self):
    self._alead_history.clear()
    self._jerk_history.clear()
    self._cutin_frames_remaining = 0
    self._cutin_confirm = 0
    self._prev_lead_status = False
    self._lead_lost_grace = 0
    self._last_lead_target = None

  def _compute_target(self, v_ego: float, lead) -> float:
    base = PERSONALITY_BASE[self._personality]
    floor = PERSONALITY_FLOOR[self._personality]
    ceil  = PERSONALITY_CEILING[self._personality]

    if lead is None:
      self._lead_lost_grace = max(0, self._lead_lost_grace - 1)
      if self._lead_lost_grace == 0:
        self._update_no_lead()
        self._last_lead_target = None
        return float(np.clip(base, floor, ceil))
      # Within grace: hold last lead-based target so current_t_follow doesn't chase base
      if self._last_lead_target is not None:
        return self._last_lead_target
      return float(np.clip(base, floor, ceil))

    self._lead_lost_grace = LEAD_LOST_GRACE_FRAMES

    a_lead = float(lead.aLeadK)
    a_tau  = float(lead.aLeadTau)
    v_rel  = float(lead.vLead) - v_ego
    d_rel  = float(lead.dRel)
    status = bool(lead.status)

    self._update_history(a_lead, v_rel, status, d_rel)

    delta = 0.0
    delta += self._mod_jerk_volatility()
    delta += self._mod_cutin()
    # alead and closing both fire on same braking event — take max to avoid double-counting
    delta += max(self._mod_alead(a_lead), self._mod_closing(v_rel))
    delta += self._mod_atau(a_tau, a_lead)

    self._prev_lead_status = status
    self._prev_drel = d_rel

    result = float(np.clip(base + delta, floor, ceil))
    self._last_lead_target = result
    return result

  def _update_no_lead(self):
    self._prev_lead_status = False
    self._prev_drel = 0.0
    self._cutin_frames_remaining = 0
    self._cutin_confirm = 0
    self._alead_history.clear()
    self._jerk_history.clear()

  def _update_history(self, a_lead: float, v_rel: float, status: bool, d_rel: float):
    if self._alead_history:
      self._jerk_history.append(abs((a_lead - self._alead_history[-1]) / DT_MDL))
    self._alead_history.append(a_lead)

    # New lead: trigger immediately (genuine appearance)
    # Sudden dRel jump: require 2 consecutive frames to reject single-frame radar jitter
    is_new_lead = status and not self._prev_lead_status
    is_closing_jump = status and self._prev_lead_status and (self._prev_drel - d_rel) > 3.0

    if is_new_lead:
      self._cutin_confirm = 0
      self._cutin_frames_remaining = CUTIN_DECAY_FRAMES
    elif is_closing_jump:
      self._cutin_confirm += 1
      if self._cutin_confirm >= 2:
        self._cutin_frames_remaining = CUTIN_DECAY_FRAMES
    else:
      self._cutin_confirm = 0

    if self._cutin_frames_remaining > 0:
      self._cutin_frames_remaining -= 1

  def _compute_speed_scale(self, v_ego: float, lead) -> float:
    base = float(np.interp(v_ego, LOW_SPEED_SCALE_BP, LOW_SPEED_SCALE_V))
    if lead is None or v_ego < HEADWAY_SCALE_V_MIN:
      return base
    d_rel  = float(lead.dRel)
    a_lead = float(lead.aLeadK)
    if d_rel <= 0.0 or a_lead > 0.1:
      # Lead accelerating away  gap will grow naturally; don't restrict takeover from stop
      return base
    t_hw = d_rel / v_ego
    if t_hw >= HEADWAY_SCALE_S:
      return base
    # Boost scale from base toward 1.0 as headway tightens below threshold
    boost = float(np.interp(t_hw, [0.0, HEADWAY_SCALE_S], [1.0, base]))
    return max(base, boost)

  def _mod_jerk_volatility(self) -> float:
    if len(self._jerk_history) < 10:
      self.dbg_jerk_delta = 0.0
      return 0.0
    sigma = float(np.std(self._jerk_history))
    delta = JERK_DELTA_MAX * float(np.clip(sigma / JERK_SIGMA_SCALE, 0.0, 1.0))
    self.dbg_jerk_delta = delta
    return delta

  def _mod_cutin(self) -> float:
    frac = self._cutin_frames_remaining / CUTIN_DECAY_FRAMES
    delta = CUTIN_DELTA * frac
    self.dbg_cutin_delta = delta
    return delta

  def _mod_alead(self, a_lead: float) -> float:
    ratio = float(np.clip(a_lead / ALEAD_DECEL_SCALE, 0.0, 1.0))
    delta = ALEAD_DELTA_MAX * ratio
    self.dbg_alead_delta = delta
    return delta

  def _mod_closing(self, v_rel: float) -> float:
    ratio = float(np.clip(v_rel / CLOSING_VREL_SCALE, 0.0, 1.0))
    delta = CLOSING_DELTA_MAX * ratio
    self.dbg_closing_delta = delta
    return delta

  def _mod_atau(self, a_tau: float, a_lead: float = 0.0) -> float:
    if a_lead >= -0.3:
      self.dbg_atau_delta = 0.0
      return 0.0
    # Smooth proportional decay: max at onset (tau=1.5), zero when fully calibrated (tau=0)
    ratio = float(np.clip(a_tau / ATAU_TAU_RESET, 0.0, 1.0))
    delta = ATAU_DELTA_MAX * ratio
    self.dbg_atau_delta = delta
    return delta
