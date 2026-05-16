"""
Copyright (c) 2021-, rav4kumar, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from collections import deque
from dataclasses import dataclass

import numpy as np

from cereal import log
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL


LongPersonality = log.LongitudinalPersonality
PERSONALITY_OPTIONS = [LongPersonality.relaxed, LongPersonality.standard, LongPersonality.aggressive]


PERSONALITY_BASE  = {LongPersonality.relaxed: 1.85, LongPersonality.standard: 1.55, LongPersonality.aggressive: 1.30}
PERSONALITY_FLOOR = {LongPersonality.relaxed: 1.65, LongPersonality.standard: 1.35, LongPersonality.aggressive: 1.10}
PERSONALITY_CEIL  = {LongPersonality.relaxed: 2.55, LongPersonality.standard: 2.15, LongPersonality.aggressive: 1.75}

JERK_WINDOW_FRAMES = 400
JERK_DELTA_MAX     = 0.18
JERK_SIGMA_FLOOR   = 1.5
JERK_SIGMA_SCALE   = 4.0

CUTIN_DELTA          = 0.22
CUTIN_DECAY_FRAMES   = 160
CUTIN_CONFIRM_FRAMES = 2

CLOSING_VREL_MAX      = -2.0
CLOSING_VREL_DEADBAND = -0.2
CLOSING_DELTA_MAX     = 0.18

ALEAD_DECEL_MAX      = -1.2
ALEAD_DECEL_DEADBAND = -0.15
ALEAD_DELTA_MAX      = 0.32

ATAU_RESET      = 1.5
ATAU_DELTA_MAX  = 0.18
ATAU_GATE_ALEAD = -0.1

# Lead-flicker modifier: when radar lead state oscillates (status flips,
# dRel jumps from track-id churn), widen t_follow so MPC has buffer to
# coast through the noise instead of brake/release ringing. We cannot
# smooth what MPC sees in radarState from sunnypilot, but we can reduce
# its reactivity by holding a wider follow gap during instability.
FLICKER_WINDOW_FRAMES = max(1, int(round(1.0 / DT_MDL)))  # 1.0s @ 20Hz = 20
FLICKER_FLIPS_DEADBAND = 2     # status flips in window below this = no delta
FLICKER_FLIPS_MAX      = 6     # saturate flips contribution here
FLICKER_DREL_JUMP_M    = 4.0   # dRel delta between frames signaling track churn
FLICKER_JUMPS_MAX      = 4     # saturate dRel-jumps contribution here
FLICKER_DELTA_MAX      = 0.25  # max t_follow delta added under full flicker

RATE_UP_BP   = [0.0, 20.0]
RATE_UP_V    = [0.65, 0.45]
RATE_DOWN_BP = [0.0, 10.0, 25.0]
RATE_DOWN_V  = [0.06, 0.10, 0.18]

LOW_SPEED_SCALE_BP = [0.0, 3.0, 7.0, 12.0]
LOW_SPEED_SCALE_V  = [0.22, 0.48, 0.78, 1.00]

HEADWAY_BOOST_V_MIN = 3.0
HEADWAY_BOOST_T     = 3.0

PERSONALITY_CHANGE_COOLDOWN_S = 2.0
LEAD_LOST_GRACE_FRAMES = 14
PARAM_REFRESH_FRAMES = max(1, int(1.0 / DT_MDL))

SPEED_SCALE_RISE_TAU = 0.15
SPEED_SCALE_FALL_TAU = 0.5


@dataclass
class ModifierDeltas:
  jerk: float = 0.0
  cutin: float = 0.0
  closing: float = 0.0
  alead: float = 0.0
  atau: float = 0.0
  flicker: float = 0.0

  @property
  def total(self) -> float:
    return self.jerk + self.cutin + max(self.alead, self.closing) + self.atau + self.flicker


class FollowDistanceController:
  def __init__(self):
    self.params = Params()
    self._frame = 0
    self._first = True

    val = self.params.get('LongitudinalPersonality')
    self._personality = val if val is not None else LongPersonality.standard
    self._enabled = self.params.get_bool('DynamicFollow')

    self._t_follow = PERSONALITY_BASE[self._personality]
    self._cooldown = 0
    self._cooldown_frames = int(PERSONALITY_CHANGE_COOLDOWN_S / DT_MDL)

    self._alead_history: deque[float] = deque(maxlen=JERK_WINDOW_FRAMES)
    self._jerk_history: deque[float] = deque(maxlen=JERK_WINDOW_FRAMES)
    self._status_history: deque[bool] = deque(maxlen=FLICKER_WINDOW_FRAMES)
    self._drel_jumps: deque[bool] = deque(maxlen=FLICKER_WINDOW_FRAMES)

    self._prev_lead = False
    self._prev_drel = 0.0
    self._cutin_frames = 0
    self._cutin_confirm = 0
    self._lead_grace = 0
    self._last_lead_target: float | None = None

    self._dbg = ModifierDeltas()
    self._smoothed_speed_scale = 1.0
    self.dbg_speed_scale = 1.0

  def is_enabled(self) -> bool:
    return self._enabled

  def set_enabled(self, enabled: bool):
    self._enabled = bool(enabled)
    self.params.put_bool('DynamicFollow', self._enabled)

  def toggle(self) -> bool:
    self.set_enabled(not self._enabled)
    return self._enabled

  @property
  def personality(self) -> int:
    return self._personality

  def get_personality(self) -> int:
    return int(self._personality)

  def set_personality(self, personality: int):
    if personality not in PERSONALITY_OPTIONS:
      return
    self._personality = personality
    self.params.put('LongitudinalPersonality', personality)
    self._cooldown = self._cooldown_frames
    self._reset_history()

  def cycle_personality(self) -> int:
    idx = PERSONALITY_OPTIONS.index(self._personality)
    self.set_personality(PERSONALITY_OPTIONS[(idx + 1) % len(PERSONALITY_OPTIONS)])
    return int(self._personality)

  def reset(self):
    self._personality = LongPersonality.standard
    self.params.put('LongitudinalPersonality', LongPersonality.standard)
    self._frame = 0
    self._first = True
    self._t_follow = PERSONALITY_BASE[LongPersonality.standard]
    self._cooldown = 0
    self._smoothed_speed_scale = 1.0
    self._reset_history()

  def update(self):
    self._frame += 1
    if self._cooldown > 0:
      self._cooldown -= 1

    if self._frame % PARAM_REFRESH_FRAMES == 0:
      val = self.params.get('LongitudinalPersonality')
      new_p = val if val is not None else LongPersonality.standard
      if new_p != self._personality:
        self._personality = new_p
        self._cooldown = self._cooldown_frames
        self._reset_history()
      self._enabled = self.params.get_bool('DynamicFollow')

  def get_follow_distance_multiplier(self, v_ego: float, radarstate=None) -> float:
    v_ego = max(0.0, v_ego)
    lead = radarstate.leadOne if (radarstate is not None and radarstate.leadOne.status) else None

    target_scale = self._compute_speed_scale(v_ego, lead)
    tau = SPEED_SCALE_RISE_TAU if target_scale >= self._smoothed_speed_scale else SPEED_SCALE_FALL_TAU
    alpha = DT_MDL / (tau + DT_MDL)
    self._smoothed_speed_scale += alpha * (target_scale - self._smoothed_speed_scale)
    self.dbg_speed_scale = self._smoothed_speed_scale

    target = self._compute_target(v_ego, lead)

    if self._first:
      self._t_follow = target
      self._smoothed_speed_scale = target_scale
      self._first = False
      return float(self._t_follow * self._smoothed_speed_scale)

    rate_up   = float(np.interp(v_ego, RATE_UP_BP,   RATE_UP_V))   * DT_MDL
    rate_down = float(np.interp(v_ego, RATE_DOWN_BP, RATE_DOWN_V)) * DT_MDL

    if self._cooldown > 0:
      step = rate_up
      self._t_follow = float(np.clip(target, self._t_follow - step, self._t_follow + step))
    else:
      step = rate_up if target > self._t_follow else rate_down
      self._t_follow = float(np.clip(target, self._t_follow - step, self._t_follow + step))

    return float(self._t_follow * self._smoothed_speed_scale)

  @property
  def current_t_follow(self) -> float:
    return self._t_follow

  @property
  def dbg_jerk_delta(self) -> float:
    return self._dbg.jerk

  @property
  def dbg_cutin_delta(self) -> float:
    return self._dbg.cutin

  @property
  def dbg_closing_delta(self) -> float:
    return self._dbg.closing

  @property
  def dbg_alead_delta(self) -> float:
    return self._dbg.alead

  @property
  def dbg_atau_delta(self) -> float:
    return self._dbg.atau

  @property
  def dbg_flicker_delta(self) -> float:
    return self._dbg.flicker

  def _reset_history(self):
    self._alead_history.clear()
    self._jerk_history.clear()
    self._status_history.clear()
    self._drel_jumps.clear()
    self._cutin_frames = 0
    self._cutin_confirm = 0
    self._prev_lead = False
    self._prev_drel = 0.0
    self._lead_grace = 0
    self._last_lead_target = None
    self._dbg = ModifierDeltas()

  def _compute_target(self, v_ego: float, lead) -> float:
    base = PERSONALITY_BASE[self._personality]
    floor = PERSONALITY_FLOOR[self._personality]
    ceil = PERSONALITY_CEIL[self._personality]

    if lead is None:
      self._lead_grace = max(0, self._lead_grace - 1)
      if self._lead_grace == 0:
        self._on_no_lead()
        self._last_lead_target = None
        self._dbg = ModifierDeltas()
        return float(np.clip(base, floor, ceil))
      if self._last_lead_target is not None:
        return self._last_lead_target
      return float(np.clip(base, floor, ceil))

    self._lead_grace = LEAD_LOST_GRACE_FRAMES

    a_lead = float(lead.aLeadK)
    a_tau = float(lead.aLeadTau)
    v_rel = float(lead.vLead) - v_ego
    d_rel = float(lead.dRel)
    status = bool(lead.status)

    self._update_history(a_lead, status, d_rel)

    self._dbg = ModifierDeltas(
      jerk    = self._mod_jerk(),
      cutin   = self._mod_cutin(),
      closing = self._mod_closing(v_rel),
      alead   = self._mod_alead(a_lead),
      atau    = self._mod_atau(a_tau, a_lead),
      flicker = self._mod_flicker(),
    )

    self._prev_lead = status
    self._prev_drel = d_rel

    target = float(np.clip(base + self._dbg.total, floor, ceil))
    self._last_lead_target = target
    return target

  def _on_no_lead(self):
    self._prev_lead = False
    self._prev_drel = 0.0
    self._cutin_frames = 0
    self._cutin_confirm = 0
    self._alead_history.clear()
    self._jerk_history.clear()
    self._status_history.clear()
    self._drel_jumps.clear()

  def _update_history(self, a_lead: float, status: bool, d_rel: float):
    if self._alead_history:
      self._jerk_history.append(abs((a_lead - self._alead_history[-1]) / DT_MDL))
    self._alead_history.append(a_lead)

    self._status_history.append(status)
    self._drel_jumps.append(self._prev_lead and status and abs(self._prev_drel - d_rel) > FLICKER_DREL_JUMP_M)

    is_new_lead = status and not self._prev_lead
    is_drel_jump = status and self._prev_lead and (self._prev_drel - d_rel) > 3.0

    if is_new_lead:
      self._cutin_confirm = 0
      self._cutin_frames = CUTIN_DECAY_FRAMES
    elif is_drel_jump:
      self._cutin_confirm += 1
      if self._cutin_confirm >= CUTIN_CONFIRM_FRAMES:
        self._cutin_frames = CUTIN_DECAY_FRAMES
    else:
      self._cutin_confirm = 0

    if self._cutin_frames > 0:
      self._cutin_frames -= 1

  def _compute_speed_scale(self, v_ego: float, lead) -> float:
    base = float(np.interp(v_ego, LOW_SPEED_SCALE_BP, LOW_SPEED_SCALE_V))
    if lead is None or v_ego < HEADWAY_BOOST_V_MIN:
      return base
    d_rel = float(lead.dRel)
    a_lead = float(lead.aLeadK)
    if d_rel <= 0.0 or a_lead > 0.1:
      return base
    t_hw = d_rel / v_ego
    if t_hw >= HEADWAY_BOOST_T:
      return base
    boost = float(np.interp(t_hw, [0.0, HEADWAY_BOOST_T], [1.0, base]))
    return max(base, boost)

  def _mod_jerk(self) -> float:
    if len(self._jerk_history) < 10:
      return 0.0
    sigma = float(np.std(self._jerk_history))
    sigma_eff = max(0.0, sigma - JERK_SIGMA_FLOOR)
    return JERK_DELTA_MAX * float(np.clip(sigma_eff / JERK_SIGMA_SCALE, 0.0, 1.0))

  def _mod_cutin(self) -> float:
    return CUTIN_DELTA * (self._cutin_frames / CUTIN_DECAY_FRAMES)

  def _mod_closing(self, v_rel: float) -> float:
    if v_rel >= CLOSING_VREL_DEADBAND:
      return 0.0
    span = CLOSING_VREL_MAX - CLOSING_VREL_DEADBAND
    return CLOSING_DELTA_MAX * float(np.clip((v_rel - CLOSING_VREL_DEADBAND) / span, 0.0, 1.0))

  def _mod_alead(self, a_lead: float) -> float:
    if a_lead >= ALEAD_DECEL_DEADBAND:
      return 0.0
    span = ALEAD_DECEL_MAX - ALEAD_DECEL_DEADBAND
    return ALEAD_DELTA_MAX * float(np.clip((a_lead - ALEAD_DECEL_DEADBAND) / span, 0.0, 1.0))

  def _mod_atau(self, a_tau: float, a_lead: float) -> float:
    if a_lead >= ATAU_GATE_ALEAD:
      return 0.0
    return ATAU_DELTA_MAX * float(np.clip(a_tau / ATAU_RESET, 0.0, 1.0))

  def _mod_flicker(self) -> float:
    if len(self._status_history) < FLICKER_WINDOW_FRAMES // 2:
      return 0.0
    flips = sum(1 for i in range(1, len(self._status_history))
                if self._status_history[i] != self._status_history[i-1])
    jumps = sum(1 for j in self._drel_jumps if j)
    flips_score = float(np.clip((flips - FLICKER_FLIPS_DEADBAND) /
                                max(1, FLICKER_FLIPS_MAX - FLICKER_FLIPS_DEADBAND), 0.0, 1.0))
    jumps_score = float(np.clip(jumps / FLICKER_JUMPS_MAX, 0.0, 1.0))
    return FLICKER_DELTA_MAX * max(flips_score, jumps_score)
