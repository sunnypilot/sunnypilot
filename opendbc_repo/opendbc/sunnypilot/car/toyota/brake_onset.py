"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math
import numpy as np

ONSET_T_BP = [0.0, 0.15, 0.6]  # s
# Speed schedule of the brake onset. Below 10 km/h (creep follow: the lead moves a little, the car catches up and
# stops again) the Altis PCM bites hard on a modest request (route 000000ed 04:05:41: output -0.42 -> -1.25 m/s^2,
# 1400 N; five ACC re-stops on 10-03/04 all -0.9..-1.25), so at creep speeds the onset uses the same numbers as the
# engage schedule (driver 2026-10-04 "yes, apply it"): 0.5 m/s^3 for 0.2 s, stock by 0.7 s; from 20 km/h the normal
# 1.0 m/s^3 for 0.1 s, stock by 0.4 s (driver 2026-10-03), interpolated between.
# Driver 2026-10-04 after route 000000f2: "the brake after creeping forward again improved but is still not soft
# enough, softer again" -> below 10 km/h 0.3 m/s^3 for 0.3 s (-0.09 m/s^2 at 0.3 s), stock by 0.9 s.
# Driver 2026-10-05: "at 50 km/h the brake still feels heavy and there was plenty of distance; every brake should start
# extremely light, and if that needs distance, start earlier" -> the creep-speed numbers (0.3 m/s^3 for 0.3 s, stock
# by 0.9 s) now apply at every speed up to 60 km/h, fading to the highway onset (1.0 m/s^3, 0.1 s, stock by 0.4 s) at
# 80 km/h, which stays as it was. The planner's light-onset margin (long_mpc) supplies the extra distance.
# Driver 2026-10-05, same drive: "at 40-50 km/h the build from light to firm is still not smooth, a bit abrupt" -> the
# jerk the onset ramps UP TO is also scheduled: 2.0 m/s^3 up to 60 km/h (was the stock 4.0 from 0.9 s on), stock at 80.
ONSET_V_BP = [16.7, 22.2]  # m/s (60, 80 km/h)
ONSET_T1_V = [0.3, 0.1]
ONSET_T3_V = [0.9, 0.4]
ONSET_J1_V = [0.3, 1.0]  # m/s^3 during the first phase
ONSET_J3_V = [2.0, 4.0]  # m/s^3 the ramp ends at (the shaper never exceeds the stock limit)
ONSET_J_DOWN = [1.0, 1.0, 4.0]  # m/s^3 (reference shape; the first two entries follow ONSET_J1_V)
# Engaging ACC (SET-) while creeping up to a lead (driver 2026-10-04: "the car used to brake hard the moment I press
# SET-; the first ~0.2 s must be a light touch, then blend into the decel the speed needs"). Route 000000ee 11:48:07:
# engaged at 9 km/h 4 m behind a 4 km/h lead, the request went 0 -> -0.42 in 0.2 s and -1.6 by 0.8 s, the car hit
# -2.7 m/s^2 (3280 N). While the engage window is open the down jerk is capped on time SINCE ENGAGING: 0.5 m/s^3 for
# the first 0.2 s (-0.1 m/s^2 at 0.2 s), then rising to stock by 0.7 s; the planner's full request still arrives, just
# later. The normal onset schedule applies on top (the stricter of the two wins).
ENGAGE_BRAKE_T_BP = [0.0, 0.2, 0.7]  # s since engaging
ENGAGE_BRAKE_J_DOWN = [0.5, 0.5, 4.0]  # m/s^3
# Owner 2026-10-06: only a plan beyond -3.0 (a genuine emergency) bypasses the soft onset; -2.0 .. -3.0 keep it (at
# 40 km/h -2.5 is reached slowly in ~1.8 s). History: -1.5 until 2026-10-03, -2.0, then -3.5 (= never) on 2026-10-05.
HARD_BRAKE_ACCEL = -3.0
URGENT_T = 0.1  # s
URGENT_J = 1.0  # m/s^3
URGENT_T_RAMP = 0.1  # s


# Creep-follow gas release, with the creep-follow stop (see
# stopping_controller.py). Route 0000010d 23:56:59: after a +0.5 launch the plan turned to braking within 0.2 s, but the
# soft onset above treated the drop from +0.5 as the start of a brake (0.3 m/s^3) and the command stayed positive for
# ~0.7 s while the car kept accelerating into a 2 m gap; then the brake bit 0 -> 1640 N. Taking away gas is not
# braking: below CREEP_GAS_V the positive part of the command is now taken away at the stock rate; the soft onset
# starts from zero, where the braking starts.
CREEP_GAS_V = 8.0 / 3.6  # m/s


# Friction entry (hybrid). Owner 2026-10-09: "no heavy-press jolt at the start of a brake - this is what I most want
# gone; even -2.6 is fine if it is reached smoothly". On this hybrid the first ~-0.6 m/s^2 of a brake is regen; past it
# the PCM brings in the friction brake (BRAKE 0xA6 BRAKE_FORCE), and how hard that bites depends on how fast the
# command is moving at that moment. 27 engaged onsets with a friction entry, routes 00000109-00000119 (onset_bite.py):
#   command rate at friction entry -1.91 / -1.05 / -0.44 m/s^3 -> delivered jerk -3.70 / -2.22 / -1.22 m/s^3,
#   friction force rate 3067 / 1067 / 533 N/s (r = 0.78; gap command-delivered at entry r = 0.80).
# The onset schedule above opens to 2.0 m/s^3 by 0.9 s - right when the friction usually enters (median 0.9 s), e.g.
# route 00000119 09:23:02 (46 km/h, lead braking to a stop): command -0.9 -> -1.66 smoothly, the car sat at the regen
# limit (-0.55), then the friction came in 680 -> 1520 N and the car went -0.76 -> -1.98 m/s^2 in 0.5 s.
# So while the command is more than ENTRY_GAP beyond what the car delivers and the friction force is still below
# ENTRY_FORCE_N, the command moves at most ENTRY_J: the friction enters slowly and the car catches up. After the entry
# (force established or ENTRY_T_MAX) the command closes the remaining gap at CATCHUP_J, then the normal limits apply.
# Not for FCW / urgent (< HARD_BRAKE_ACCEL) requests, below ENTRY_V_MIN (creep follow has its own onset), or without
# measurements (a_ego None).
ENTRY_GAP = 0.25        # m/s^2 the command may lead the delivered decel before the entry limit applies
ENTRY_FORCE_N = 600.0   # N: friction established
ENTRY_J = 0.5           # m/s^3 while the friction enters
ENTRY_T_MAX = 1.0       # s per brake onset
CATCHUP_J = 1.5         # m/s^3 after the entry until the command reaches the request
ENTRY_V_MIN = 10.0 / 3.6  # m/s


class BrakeOnsetShaper:
  def __init__(self, dt: float, stock_down_jerk: float):
    self.dt = dt
    self.stock_down_jerk = stock_down_jerk
    self.t_onset = 0.0
    self.t_entry = 0.0      # time spent limited by the friction entry in this brake
    self.catchup = False    # after an entry: close the gap gently
    self.friction_in = False

  def reset(self) -> None:
    self.t_onset = 0.0
    self.t_entry = 0.0
    self.catchup = False
    self.friction_in = False

  def friction_entry_step(self, accel_request: float, prev_accel: float, v_ego: float, a_ego: float | None,
                          brake_force: float) -> float | None:
    """largest down step (> 0, m/s^2 per step) while the friction brake enters, None = no limit"""
    if a_ego is None or v_ego < ENTRY_V_MIN or prev_accel > -0.1:
      self.t_entry, self.catchup, self.friction_in = 0.0, False, False
      return None
    if math.isfinite(brake_force) and brake_force >= ENTRY_FORCE_N:
      self.friction_in = True
    if accel_request >= prev_accel:
      self.catchup = False
      return None
    leading = prev_accel - a_ego < -ENTRY_GAP
    if leading and not self.friction_in and self.t_entry < ENTRY_T_MAX:
      self.t_entry += self.dt
      self.catchup = True
      return ENTRY_J * self.dt
    if self.catchup:
      return CATCHUP_J * self.dt
    return None

  @staticmethod
  def schedule_t(v_ego: float) -> list[float]:
    t1 = float(np.interp(v_ego, ONSET_V_BP, ONSET_T1_V))
    t3 = float(np.interp(v_ego, ONSET_V_BP, ONSET_T3_V))
    return [0.0, t1, t3]

  @staticmethod
  def schedule_j(v_ego: float) -> list[float]:
    j1 = float(np.interp(v_ego, ONSET_V_BP, ONSET_J1_V))
    j3 = float(np.interp(v_ego, ONSET_V_BP, ONSET_J3_V))
    return [j1, j1, j3]

  def down_step(self, accel_request: float, prev_accel: float, bypass: bool = False, v_ego: float = 30.0,
                urgent: bool = False, t_engaged: float | None = None, a_ego: float | None = None,
                brake_force: float = float('nan')) -> float:
    if bypass:
      self.t_onset = 0.0
      self.t_entry, self.catchup = 0.0, False
      return -self.stock_down_jerk * self.dt
    entry = None if urgent else self.friction_entry_step(accel_request, prev_accel, v_ego, a_ego, brake_force)
    step = self._down_step(accel_request, prev_accel, v_ego, urgent, t_engaged)
    return step if entry is None else -min(-step, entry)

  def _down_step(self, accel_request: float, prev_accel: float, v_ego: float, urgent: bool,
                 t_engaged: float | None) -> float:
    if prev_accel > 0.0 and v_ego < CREEP_GAS_V and accel_request < prev_accel:
      self.t_onset = 0.0
      return -min(self.stock_down_jerk * self.dt, prev_accel - max(accel_request, 0.0))

    if urgent:
      t_bp, j_bp = [0.0, URGENT_T, URGENT_T + max(URGENT_T_RAMP, self.dt)], [URGENT_J, URGENT_J, self.stock_down_jerk]
    else:
      t_bp, j_bp = self.schedule_t(v_ego), self.schedule_j(v_ego)
    gentlest_step = -ONSET_J_DOWN[0] * self.dt
    onset = (accel_request - prev_accel) < gentlest_step - 1e-9
    if onset:
      j_down = float(np.interp(self.t_onset, t_bp, j_bp))
      self.t_onset = min(self.t_onset + self.dt, t_bp[-1])
    else:
      j_down = self.stock_down_jerk
      self.t_onset = max(self.t_onset - self.dt, 0.0)
    if t_engaged is not None and t_engaged < ENGAGE_BRAKE_T_BP[-1]:
      j_down = min(j_down, float(np.interp(t_engaged, ENGAGE_BRAKE_T_BP, ENGAGE_BRAKE_J_DOWN)))
    return -min(j_down, self.stock_down_jerk) * self.dt

  def is_urgent(self, accel_request: float, fcw: bool) -> bool:
    return fcw or accel_request < HARD_BRAKE_ACCEL

ENGAGE_T_BP = [0.0, 0.1, 0.6]  # s; the window is still used to keep the soft BRAKE onset for a hard request after engaging
# Driver 2026-10-04: "if Kumar's base added a soft start again, remove it - I want an immediate response, not a lurch,
# following the eco/normal/sport profile". The gas-side engage ramp (0.25 -> 0.6 -> 4.0 m/s^3 over 0.6 s) is gone:
# the up jerk after engaging is the stock windup limit; the accel profile sets how much.
ENGAGE_J_UP = [4.0, 4.0, 4.0]  # m/s^3
# Resume while moving. Owner 2026-10-08: "when resuming the
# speed (RES), can the first 0.4 s accelerate more gently?". Routes 0000010e-00000112, eight RES engagements at 15-61
# km/h: the car was coasting at -0.3..-0.5 m/s^2 (regen), the command started from 0 and reached +0.3..+0.5 within
# 0.4-0.6 s, so in the first 0.4 s the regen vanished AND the gas came in (aEgo -0.43 -> +0.19 in 0.4 s at 23:09:07,
# +0.12 -> +0.64 in 0.6 s at 17:43:01, ~1.5-2 m/s^3). Now, when engaging above RESUME_V_MIN, the command starts from
# the coasting decel (aEgo, clipped to RESUME_START_MIN..0) instead of 0, and rises at RESUME_J_UP: 0.6 m/s^3 for the
# first 0.4 s, opening to the stock limit by 0.8 s. Replays of the logged plans: the command meets the stock one by
# 0.6-0.8 s, identical afterwards (the eco/normal/sport profile is untouched). Standstill launches are not affected.
RESUME_V_MIN = 15.0 / 3.6  # m/s
RESUME_T_BP = [0.0, 0.4, 0.8]  # s since engaging
RESUME_J_UP = [0.6, 0.6, 4.0]  # m/s^3
RESUME_START_MIN = -0.6  # m/s^2
RESUME_EDGE_T = 0.5  # s: the engagement must follow the cruise switching on (not a gas-override release)


class EngageOnsetShaper:
  def __init__(self, dt: float, stock_up_jerk: float):
    self.dt = dt
    self.stock_up_jerk = stock_up_jerk
    self.t_engaged: float | None = None
    self.resume = False
    self.cruise_on_t = 1e9  # s since the PCM cruise went from off to on (RES / SET)
    self.prev_cruise = False

  def reset(self) -> None:
    self.t_engaged = None
    self.resume = False

  def cruise_state(self, cruise_enabled: bool) -> None:
    """called every frame: tracks RES / SET (cruise off -> on), so a gas-override release is not a resume"""
    self.cruise_on_t = 0.0 if (cruise_enabled and not self.prev_cruise) else self.cruise_on_t + self.dt
    self.prev_cruise = cruise_enabled

  def start_accel(self, prev_accel: float, a_ego: float, v_ego: float) -> float:
    """on the first engaged frame of a resume while moving, the command starts from the coasting decel"""
    if self.t_engaged is None and v_ego > RESUME_V_MIN and self.cruise_on_t < RESUME_EDGE_T:
      self.resume = True
      return float(np.clip(a_ego, RESUME_START_MIN, 0.0))
    return prev_accel

  @property
  def in_engage_window(self) -> bool:
    return self.t_engaged is None or self.t_engaged < ENGAGE_T_BP[-1]

  @property
  def t_since_engage(self) -> float | None:
    """seconds since engaging while the engage brake schedule still applies, else None"""
    t = 0.0 if self.t_engaged is None else self.t_engaged
    return t if t < ENGAGE_BRAKE_T_BP[-1] else None

  def up_step(self, active: bool) -> float:
    if not active:
      self.t_engaged = None
      return self.stock_up_jerk * self.dt
    if self.t_engaged is None:
      self.t_engaged = 0.0
    else:
      self.t_engaged += self.dt
    if self.resume:
      if self.t_engaged < RESUME_T_BP[-1]:
        return min(float(np.interp(self.t_engaged, RESUME_T_BP, RESUME_J_UP)), self.stock_up_jerk) * self.dt
      self.resume = False
    if self.t_engaged >= ENGAGE_T_BP[-1]:
      return self.stock_up_jerk * self.dt
    j_up = float(np.interp(self.t_engaged, ENGAGE_T_BP, ENGAGE_J_UP))
    return min(j_up, self.stock_up_jerk) * self.dt

# Hard-brake overshoot limit (owner 2026-10-06, route 00000100 19:41:42-45: the lead braked from 44 km/h at -3.3 m/s^2;
# openpilot asked for -3.49 at most, but the PCM with the hybrid's regen delivered -4.3 m/s^2 for 0.8 s (BRAKE_FORCE
# 4880 N), ~30% more than asked - the last, heaviest part of the "sudden brake" feel. The stock PID only lifted the
# command ~0.3 above the request.) Once the request is a hard brake, the car's own deceleration is watched: when it
# runs OVERSHOOT_DEADBAND past the request (predicted a moment ahead, as the PID does), the command is lifted by
# OVERSHOOT_GAIN times the excess, at most OVERSHOOT_MAX, so the car settles near what openpilot asked for. The request
# itself is never weakened: the limit only takes back braking the car delivered ON TOP of it (an MPC replay of 19:41
# with the asked-for -3.5 ends 4.9 m behind the stopped lead). It never lifts the command above OVERSHOOT_CMD_CEIL.
OVERSHOOT_ACTIVE_ACCEL = -2.5  # m/s^2: the limit works only while the request is harder than this
OVERSHOOT_DEADBAND = 0.2  # m/s^2 of overshoot that is left alone
OVERSHOOT_GAIN = 0.8
OVERSHOOT_MAX = 1.0  # m/s^2 largest lift
OVERSHOOT_RATE_UP = 3.0  # m/s^3 how fast the lift may grow
OVERSHOOT_RATE_DOWN = 2.0  # m/s^3 how fast it is given back (also when the hard request ends)
OVERSHOOT_CMD_CEIL = -1.5  # m/s^2: the lifted command always stays a firm brake
# Moderate band - Corolla Altis Hybrid only (owner 2026-10-07, route 0000010e 17:38:41: "at 50 km/h the braking started
# soft, but the speed dropped too fast, still a bit fierce"). A stopped queue appeared 74 m ahead after a lane change;
# openpilot asked for at most -1.60 m/s^2, the car delivered -1.82..-1.95 (regen on top). Routes 00000100..0000010e:
# above 20 km/h the Altis delivers 0.1-0.4 m/s^2 more than a -1.0..-2.0 request (e.g. 0000010d 15-25 km/h: asked
# -1.68, got -2.05). So above OVERSHOOT_MOD_V the limit also works for requests harder than OVERSHOOT_MOD_ACCEL, with
# a smaller deadband, and the lifted command never gets lighter than OVERSHOOT_MOD_KEEP of the command (the request
# is never weakened by more than a quarter). The hard band above is unchanged for every car.
OVERSHOOT_MOD_ACCEL = -1.0  # m/s^2
OVERSHOOT_MOD_V = 12.0 / 3.6  # m/s (0000010d 23:54:58: asked -1.72 at 17-23 km/h, delivered -1.96..-2.19)
OVERSHOOT_MOD_DEADBAND = 0.15  # m/s^2
OVERSHOOT_MOD_KEEP = 0.75
# The moderate band works as a slow trim, not a fast limiter: a replay of 17:38:36-38 with the hard band's logic
# (predicted aEgo, 3.0 / 2.0 m/s^3) pulsed the command by 0.2-0.3 m/s^2 for 0.2 s at a time on the noisy aEgo (-1.2 ..
# -1.8 at a steady request), and the stock PID was already lifting the command (-1.6 asked, ~-1.1 sent). So the band
# uses the overshoot of the measured aEgo, low-passed over OVERSHOOT_MOD_TAU, and moves at OVERSHOOT_MOD_RATE.
# Relaxed personality only (owner 2026-10-08). A process_replay of 14 Aggressive-mode segments (routes fe/100/101/104/
# 107/109) found the band acting mostly in CLOSE following: 0000109 23:19:44, lead 16 m away and still braking, request
# -1.99/-1.75 at 26-21 km/h, the car delivered -2.73/-2.27 and the band lifted the command by up to 0.35 - taking away a
# margin the close gap needs (open loop, no planner reaction: +6 m travelled). Tonight's Relaxed drives (routes
# 00000112-00000116) never triggered it. Owner: "keep D in Relaxed". The carcontroller passes
# hud_control.leadDistanceBars == 3 (controlsd: personality + 1; relaxed = 2 -> 3 bars).
# OFF since 2026-10-08 (owner: "so D never acted in Relaxed last night? then switch it off and try"): routes
# 00000112-00000116 never triggered it, and in Aggressive close following it removes margin. Kept in the code; set True
# to bring it back (Relaxed only).
OVERSHOOT_MOD_ENABLED = False
OVERSHOOT_MOD_TAU = 0.5  # s
OVERSHOOT_MOD_RATE = 0.5  # m/s^3


class BrakeOvershootLimiter:
  def __init__(self, dt: float, moderate: bool = False):
    self.dt = dt
    self.moderate = moderate  # also the moderate band (OVERSHOOT_MOD_*)
    self.lift = 0.0
    self.in_moderate = False
    self.mod_excess = 0.0

  def reset(self) -> None:
    self.lift = 0.0
    self.in_moderate = False
    self.mod_excess = 0.0

  def update(self, accel_request: float, a_ego_future: float, active: bool = True, v_ego: float = 0.0,
             a_ego: float | None = None, moderate_allowed: bool = True) -> float:
    """returns the lift (>= 0, m/s^2) to add to the command"""
    target = 0.0
    hard = accel_request < OVERSHOOT_ACTIVE_ACCEL
    self.in_moderate = (self.moderate and moderate_allowed and not hard and accel_request < OVERSHOOT_MOD_ACCEL and
                        v_ego > OVERSHOOT_MOD_V)
    if self.in_moderate:
      measured = a_ego_future if a_ego is None else a_ego
      alpha = self.dt / (OVERSHOOT_MOD_TAU + self.dt)
      self.mod_excess += alpha * ((accel_request - measured) - self.mod_excess)
    else:
      self.mod_excess = 0.0
    if active and hard:
      excess = accel_request - a_ego_future - OVERSHOOT_DEADBAND  # > 0: decelerating harder than asked
      target = float(np.clip(OVERSHOOT_GAIN * excess, 0.0, OVERSHOOT_MAX))
    elif active and self.in_moderate:
      target = float(np.clip(OVERSHOOT_GAIN * (self.mod_excess - OVERSHOOT_MOD_DEADBAND), 0.0, OVERSHOOT_MAX))
    if self.in_moderate and not hard:
      step = OVERSHOOT_MOD_RATE * self.dt
      self.lift = float(np.clip(target, self.lift - step, self.lift + step))
    else:
      self.lift = float(np.clip(target, self.lift - OVERSHOOT_RATE_DOWN * self.dt, self.lift + OVERSHOOT_RATE_UP * self.dt))
    return self.lift

  def apply(self, accel_cmd: float) -> float:
    if self.lift <= 0.0:
      return accel_cmd
    ceiling = OVERSHOOT_MOD_KEEP * accel_cmd if self.in_moderate else OVERSHOOT_CMD_CEIL
    return min(accel_cmd + self.lift, max(accel_cmd, ceiling))


# Low-speed regen hand-over feed-forward. History: route 0000010d 23:54:58-23:55:03 - between 20 and 9 km/h the car cut its own
# friction brake (BRAKE 0xA6 BRAKE_FORCE 1640 -> 440 N) and delivered ~70% of the request, felt as "brakes, goes light,
# brakes again". A feedback compensation (shortfall x 0.8 past a 0.2 deadband, 1.0 m/s^3) was the first fix; its
# first drive, route 0000010e 2026-10-07, showed it acting only in 0.1-0.25 m/s^2 pulses that never filled the gap
# (owner: "the stops are sometimes soft, sometimes still not smooth; several stops still braked twice").
# Measured on routes 00000100..0000010e (engaged stops, request / delivered, m/s^2): the request eases smoothly, but the
# delivered decel DIPS at 15-9 km/h (10e: -0.84 asked, -0.61 delivered; 109: -0.87 / -0.69; 107: -1.04 / -0.81) and
# comes back ON TOP of the request at 7-1 km/h (10e: -0.47 / -0.60; 109: -0.54 / -0.80), the second part pushed by the
# PID integrator that wound up during the dip (command - request -0.10..-0.17 there). So, instead of feedback:
#  - a FEED-FORWARD extra brake by speed, the measured dip: HANDOVER_EXTRA_MAX (or HANDOVER_EXTRA_FRAC of a lighter
#    request) at 10-14 km/h, fading to 0 at 6 and 17 km/h, changing at HANDOVER_RATE, only while braking harder than
#    HANDOVER_MIN_REQUEST;
#  - below PID_HOLD_V, while the request brakes, the PID integrator is frozen and bled toward zero (a positive
#    integral, left over from a launch, faster), so the catch-up no longer adds braking at the end of the stop.
# Expected delivered decel on 10e (by speed band 15-12/12-9/9-7/7-5/5-3/3-1 km/h): -0.86/-0.81/-0.75/-0.75/-0.63/-0.48,
# continuous easing, instead of -0.66/-0.61/-0.75/-0.75/-0.71/-0.60.
HANDOVER_V_BP = [6.0 / 3.6, 8.0 / 3.6, 10.0 / 3.6, 14.0 / 3.6, 17.0 / 3.6]  # m/s
HANDOVER_V_W = [0.0, 0.5, 1.0, 1.0, 0.0]
HANDOVER_MIN_REQUEST = -0.3  # m/s^2
HANDOVER_EXTRA_MAX = 0.2  # m/s^2
HANDOVER_EXTRA_FRAC = 0.25  # of the request, for lighter requests
HANDOVER_RATE = 1.0  # m/s^3
# The dip is a moderate-brake effect: at a firm request the regen gives MORE, not less (0000010d 15-12 km/h: asked
# -1.46, delivered -1.72), so the extra fades out between these requests (full at -1.0 and lighter, none at -1.5).
HANDOVER_REQ_BP = [-1.5, -1.0]  # m/s^2
HANDOVER_REQ_W = [0.0, 1.0]
# Owner 2026-10-10 (route 0000011c 00:19:10, Aggressive stop 1.6 m behind the lead): "the end of the stop slides too
# much, the last two metres feel too light". With the PID held below PID_HOLD_V nothing makes up the under-delivery
# below the hand-over band; asked / delivered by band (m/s^2), three stops of 11c (00:18:07 / 00:19:10 / 00:20:58):
#   8-7 km/h -0.75/-0.62  -0.89/-0.58  -0.77/-0.54     6-5 km/h -0.63/-0.45  -0.75/-0.50  -0.66/-0.49
#   5-4 km/h -0.60/-0.40  -0.67/-0.28  -0.64/-0.35     4-3 km/h -0.58/-0.62  -0.62/-0.45  -0.61/-0.57
#   3-2 km/h on target or above. Brake force 650-850 N at 6-4 km/h, below what beats the hybrid creep torque.
# So a second, low-speed feed-forward: LOW_EXTRA at LOW_EXTRA_V_BP (0.25 at 5-6.5 km/h, gone by 3 km/h, led by about
# 0.5 km/h for the ~0.3 s actuator lag), added to the hand-over extra, same request gate and rate.
LOW_EXTRA_V_BP = [3.0 / 3.6, 4.0 / 3.6, 5.0 / 3.6, 6.5 / 3.6, 8.5 / 3.6]  # m/s
LOW_EXTRA = [0.0, 0.15, 0.25, 0.25, 0.0]  # m/s^2
PID_HOLD_V = 9.0 / 3.6  # m/s
PID_BLEED_NEG = 0.5  # m/s^2 per s: a braking integral fades this fast
PID_BLEED_POS = 2.0  # m/s^2 per s: a gas integral (left from the launch) fades this fast

class BrakeHandoverFeedforward:
  def __init__(self, dt: float):
    self.dt = dt
    self.extra = 0.0

  def reset(self) -> None:
    self.extra = 0.0

  def update(self, accel_request: float, v_ego: float, active: bool = True) -> float:
    """returns the extra braking (>= 0, m/s^2) to subtract from the command"""
    target = 0.0
    if active and accel_request < HANDOVER_MIN_REQUEST:
      w = float(np.interp(v_ego, HANDOVER_V_BP, HANDOVER_V_W)) * float(np.interp(accel_request, HANDOVER_REQ_BP, HANDOVER_REQ_W))
      target = w * min(HANDOVER_EXTRA_MAX, HANDOVER_EXTRA_FRAC * -accel_request)
      target += float(np.interp(v_ego, LOW_EXTRA_V_BP, LOW_EXTRA)) * float(np.interp(accel_request, HANDOVER_REQ_BP, HANDOVER_REQ_W))
    step = HANDOVER_RATE * self.dt
    self.extra = float(np.clip(target, self.extra - step, self.extra + step))
    return self.extra

  def apply(self, accel_cmd: float) -> float:
    return accel_cmd - self.extra

  def condition_pid(self, pid, accel_request: float, v_ego: float) -> bool:
    """below PID_HOLD_V while braking: bleed the integrator toward zero; returns True = freeze it this step"""
    if v_ego >= PID_HOLD_V or accel_request >= 0.0:
      return False
    if pid.i > 0.0:
      pid.i = max(0.0, pid.i - PID_BLEED_POS * self.dt)
    else:
      pid.i = min(0.0, pid.i + PID_BLEED_NEG * self.dt)
    return True


class BrakeCommandCorrections:
  """tnpb2 corrections to the final braking command."""
  def __init__(self, dt: float):
    self.overshoot = BrakeOvershootLimiter(dt, moderate=OVERSHOOT_MOD_ENABLED)
    self.handover = BrakeHandoverFeedforward(dt)

  def reset(self) -> None:
    self.overshoot.reset()
    self.handover.reset()

  def apply(self, accel_cmd: float, accel_request: float, a_ego_future: float, v_ego: float, stopping: bool, fcw: bool,
            a_ego: float | None = None, relaxed: bool = True) -> float:
    # take back braking the car delivers beyond a hard request (never under FCW); the moderate band only in Relaxed
    self.overshoot.update(accel_request, a_ego_future, active=not stopping and not fcw, v_ego=v_ego, a_ego=a_ego,
                          moderate_allowed=relaxed)
    accel_cmd = self.overshoot.apply(accel_cmd)
    # feed-forward the braking the car does not deliver in the low-speed regen hand-over
    self.handover.update(accel_request, v_ego, active=not fcw)
    return self.handover.apply(accel_cmd)

  def condition_pid(self, pid, accel_request: float, v_ego: float) -> bool:
    """called before the stock PID update; True = freeze the integrator this step"""
    return self.handover.condition_pid(pid, accel_request, v_ego)
