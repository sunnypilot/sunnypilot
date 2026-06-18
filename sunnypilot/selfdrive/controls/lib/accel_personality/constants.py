"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import custom

AccelerationPersonality = custom.LongitudinalPlanSP.AccelerationPersonality
ECO = AccelerationPersonality.eco
NORMAL = AccelerationPersonality.normal
SPORT = AccelerationPersonality.sport

PERSONALITY_MIN = min(AccelerationPersonality.schema.enumerants.values())
PERSONALITY_MAX = max(AccelerationPersonality.schema.enumerants.values())

# Accel ceiling. NORMAL is stock so a disabled controller (forced to NORMAL) is stock.
# This is the POSITIVE-accel upper clip + its upward slew rate. It is the launch/cruise-accel side and
# is independent of braking (which is the lower clip + the convex/SMOOTH_DECEL shaper) -- tuning it does
# NOT change the gentle-brake goals. ECO launch (v=0) matches stock + stock rise rate so take-off from
# a stop is prompt (no honking); only the 25/40 m/s cruise points stay gentle.
A_CRUISE_MAX_BP = [0., 14., 25., 40.]
STOCK_A_CRUISE_MAX_V = [1.6, 0.7, 0.2, 0.08]
STOCK_RISE_RATE = 0.05
A_CRUISE_MAX_V = {
  ECO:    [1.60, 0.60, 0.13, 0.05],   # stock launch (v=0), gentle cruise (25/40)
  NORMAL: STOCK_A_CRUISE_MAX_V,
  SPORT:  [1.90, 1.30, 0.60, 0.25],
}
RISE_RATE = {ECO: 0.05, NORMAL: STOCK_RISE_RATE, SPORT: 0.06}   # ECO rise = stock so launch ramps promptly

# Early soft braking: predicted brake need (m/s^2) -> early decel target (m/s^2).
SMOOTH_DECEL_BP = [0.0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4]
SMOOTH_DECEL_V = {
  ECO:    [0.00, -0.02, -0.05, -0.10, -0.25, -0.40, -0.60],
  #ECO:    [0.00, -0.08, -0.20, -0.30, -0.40, -0.70, -0.80],
  NORMAL: [0.00, -0.13, -0.30, -0.55, -0.84, -1.12, -1.40],
  SPORT:  [0.00, -0.17, -0.40, -0.72, -1.05, -1.35, -1.65],
}
BRAKE_DEEPENING_JERK = {ECO: 0.5, NORMAL: 0.8, SPORT: 1.0}
BRAKE_RELEASE_JERK = 2.0
ACCEL_RISE_JERK = {ECO: 0.7, NORMAL: 1.2, SPORT: 1.6}

SMOOTH_DECEL_LOOKAHEAD_T = 3.0
MIN_SMOOTH_BRAKE_NEED = 0.2
HARD_BRAKE_TARGET_ACCEL = -1.5
HARD_BRAKE_NEED = 2.6

# Below this ego speed the shaper stands down (full stock decel). Softening the creep-to-stop makes the
# car brake less -> coast farther -> halt too close to a stopped lead (~1.3 m). Stock decel below this
# speed stops at the proper gap; sub-3 m/s braking is gentle anyway. Onset shaping applies above it.
STOP_APPROACH_VEGO = 3.0       # m/s

# --- Convex brake-onset shaper (param-gated; ECO/SPORT only, NORMAL = stock passthrough) ---
# The grabby bite is the raw MPC plan: stock deepening uses a CONSTANT jerk (integrates to a LINEAR
# accel ramp) and min(slewed,raw) lets the deep raw plan win, so the bite passes through untouched.
# Fix: jerk-limit the deepening with a DEPTH-PROPORTIONAL jerk
#   jerk(a) = ONSET_JERK0 + ONSET_JERK_GAIN * abs(a_current),  capped at ONSET_JERK_MAX
# At the bite (a~0) the jerk is ONSET_JERK0 (gentle); it grows with decel depth, so the decel magnitude
# follows da/dt = j0 + k*a  =>  a(t) = (j0/k)*(exp(k*t) - 1) -- the exponential-growth reference. The
# output is never deeper than the plan (only ever softer-or-equal during the bite) and converges to it.
# No velocity-debt feedback: it carried stale state across closely-spaced stop-and-go brakes and
# over-braked the next onset (verified). NORMAL omitted -> shaper never runs.
ONSET_JERK0 = {ECO: 0.15, SPORT: 0.25}        # m/s^3  initial gentle jerk at the bite (target band 0.15-0.25)
ONSET_JERK_GAIN = {ECO: 0.9, SPORT: 1.5}      # 1/s    depth-proportional growth rate k (lowered: gentler jerk-build = smoother decel, less "jerky")

# Bounded softening: the gentle bite lags the plan (brakes shallower) at the very start. To keep the
# softening modest (so it never feels like "no brakes"), an INSTANTANEOUS-gap catch-up adds jerk when
# realized lags the plan by more than ONSET_GAP_SOFT, hard-capped at ONSET_JERK_MAX. This uses the
# current accel gap only (no integrated state) so nothing carries across closely-spaced brakes. Steady
# softening then settles near ONSET_GAP_SOFT; the hard cap keeps the catch from ever being a grab.
ONSET_GAP_SOFT = {ECO: 0.30, SPORT: 0.25}     # m/s^2  tolerated shallower-than-plan gap before catch-up
ONSET_GAP_GAIN = {ECO: 4.0, SPORT: 5.0}       # 1/s    extra jerk per m/s^2 of gap beyond ONSET_GAP_SOFT
ONSET_JERK_MAX = {ECO: 1.1, SPORT: 1.4}       # m/s^3  hard ceiling on convex-path jerk (lowered: smoother catch-up)
# Fast hand-back: once the plan leaves the gentle zone (no longer armed) but a soft gap is still open,
# close it at this FIRM jerk so the output catches the plan BEFORE braking gets firm -> no late-brake lag
# into the [-1.5,-1.0] band. Jerk-limited (not a snap), and never deeper than the plan, so not a grab.
ONSET_HANDBACK_JERK = {ECO: 2.2, SPORT: 3.0}  # m/s^3  gap-close rate (lowered: gentler hand-back = less jounce/jerk)

# Arm gates (conservative). Only shape genuinely gentle onsets; firm/deep onsets fall to the stock
# never-weaker slew (they SHOULD bite). Two independent safety layers against late braking: (1) the
# PREDICTIVE brake_need gate declines to start a gentle bite when a firmer brake is seen within 3s, so
# we don't soften ahead of one; (2) the fast hand-back (ONSET_HANDBACK_JERK) closes any open soft gap
# before the plan reaches firm braking. Together: 0 firm-band ([-1.5,-1.0]) lag on the verified windows.
SOFT_ONSET_MAX_BRAKE_NEED = 0.9               # do NOT soften if a firmer brake is predicted within 3s
SOFT_ONSET_MAX_INSTANT_ACCEL = -0.7           # m/s^2  stop softening (fast hand-back) once raw is this deep
# Sticky re-arm: once an onset goes firm (instantaneously too deep) it latches OFF; require this many
# consecutive released/flat frames before a NEW soft window may open, so lead/SnG jitter cannot re-arm
# the bite every few hundred ms (flicker guard). Controller runs at the model rate (DT_MDL = 0.05 s).
SOFT_ONSET_REARM_FRAMES = 10                  # frames (~0.5 s at 20 Hz model rate) of release before re-arm
