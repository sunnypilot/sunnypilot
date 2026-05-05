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
CLOSING_DELTA_MAX  = 0.12  # sec

# High aLeadTau means MPC lead extrapolation decays fast — uncertain future
ATAU_HIGH      = 2.0   # tau threshold
ATAU_DELTA_MAX = 0.05  # sec

# aLeadK-based delta: fires earlier than vRel closing delta
ALEAD_DECEL_SCALE = -1.0   # m/s² — aLeadK at which alead delta is maxed
ALEAD_DELTA_MAX   = 0.15   # sec

# Asymmetric rate limits — fast up on danger, slow down on relax
T_FOLLOW_RATE_UP   = 0.45  # sec/sec — gentle snap toward danger; avoids lead noise ratcheting
T_FOLLOW_RATE_DOWN = 0.12  # sec/sec — moderate decay; holds space after brake events but recovers fast enough MPC doesn't hunt

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
    target = self._compute_target(v_ego, lead)

    if self.first_run:
      self.current_t_follow = target
      self.first_run = False
      return float(self.current_t_follow)

    if self.personality_change_cooldown > 0:
      # Fast converge to new personality base on cooldown
      rate = T_FOLLOW_RATE_UP * DT_MDL
      self.current_t_follow = float(np.clip(target, self.current_t_follow - rate, self.current_t_follow + rate))
      return float(self.current_t_follow)

    if target > self.current_t_follow:
      rate = T_FOLLOW_RATE_UP * DT_MDL    # snap up fast — gap increasing needed (danger)
    else:
      rate = T_FOLLOW_RATE_DOWN * DT_MDL  # ease back slow — no rush to reduce gap

    self.current_t_follow = float(np.clip(target, self.current_t_follow - rate, self.current_t_follow + rate))
    return float(self.current_t_follow)

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
    delta += self._mod_atau(a_tau)

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

  def _mod_atau(self, a_tau: float) -> float:
    ratio = float(np.clip((a_tau - ATAU_HIGH) / ATAU_HIGH, 0.0, 1.0))
    delta = ATAU_DELTA_MAX * ratio
    self.dbg_atau_delta = delta
    return delta
