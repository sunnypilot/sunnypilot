"""
Dynamic Acceleration Boost (DAB)
================================

Standalone implementation moved from `longitudinal_planner.py` to simplify the
planner file and enable reuse.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import json
import os
import time

import numpy as np

from cereal import log
from opendbc.car.interfaces import ACCEL_MAX
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.controls.lib.drive_helpers import CONTROL_N
from openpilot.selfdrive.modeld.constants import ModelConstants

# -----------------------------------------------------------------------------
# Tunable parameters (identical to original helper)
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Aggressive yet smooth tuning values
#   • shorter headway / follow distance (similar feel to Tesla FSD)
#   • faster take-off from stand-still
#   • less slowdown for gentle highway curves, still reacts to tight back-road
#     bends.
#   • slightly snappier boost response with a bit more filtering removed.
# -----------------------------------------------------------------------------

# Lead-vehicle gating ---------------------------------------------------------
# Headway factor: bigger → keeps more distance.  Reduce to ~0.6 s for a more
# natural 1-car-length gap at 70 mph.
# Phase-2: shorten desired time-headway so we sit closer to the lead car
# (≈0.35 s maps to ~1-car gap at 70 mph which feels natural yet safe)
# Phase-5 tune: slightly shorter headway to close gaps quicker without
# feeling overly aggressive. This still leaves a comfortable margin at
# highway speeds while encouraging a more natural following distance.
# Desired following headway by personality. Larger values increase following distance:
#   - Aggressive: Prioritizes quicker response and closer following.
#   - Standard: Balanced approach for everyday driving.
#   - Relaxed: Prioritizes smoother, more distant following.
# Base time headway by following distance setting. An additional
# small speed based extension is added dynamically.
HEADWAY_TIME_BASE = {
  log.LongitudinalPersonality.aggressive: 0.55, # Closer following, quicker reaction
  log.LongitudinalPersonality.standard: 0.65, # Balanced following distance
  log.LongitudinalPersonality.relaxed: 0.9,   # More distant and smoother following
}
HEADWAY_TIME_SPEED_DELTA = 0.2  # extra at ~30 m/s
# Default for backward compatibility when personality isn't specified
LEAD_HEADWAY_TIME = HEADWAY_TIME_BASE[log.LongitudinalPersonality.standard]
# Minimum absolute distance we always try to preserve in metres.
LEAD_DISTANCE_MIN = 4.0  # [m]
# Logistic slope.  Slightly steeper so the boost ramps down more decisively
# once we get too close, but otherwise stays at 1 quickly.
# Slightly steeper transition so the helper keeps working until we are
# definitively too close.
# Gentler slope so the helper stays engaged until we're much closer to
# the lead. This avoids prematurely backing off when a slower car is far
# ahead yet still prevents oscillations once the gap closes.
LEAD_DISTANCE_K = 0.35  # 1 / m

# Relative-speed / time-to-collision gating ----------------------------------
# TTC thresholds (time-to-collision) ------------------------------------------
# Time-to-collision gating (unchanged)
TTC_HARD = 1.0  # [s]  below this, kill boost immediately
# Allow boost to stay active a bit longer when closing in on a slower
# vehicle.
TTC_SOFT = 5.5  # [s]  above this, don't reduce boost

# Time-to-slow (TTS) gating ----------------------------------------------------
# The 'hard' threshold scales with the user's chosen following-distance
# personality:
#   aggressive → 1.5 s
#   standard   → 2.0 s
#   relaxed    → 2.5 s

TTS_HARD_RELAXED = 2.0  # [s]
TTS_HARD_STANDARD = 1.5  # [s]
TTS_HARD_AGGRESSIVE = 1.0  # [s]

# Maintain the same margin between *hard* and *soft* thresholds that the
# original logic used (≈2.5 s).
TTS_DELTA_SOFT =  4.0 # [s]
# *TTS_SOFT* will be computed dynamically.

# Curvature gating -----------------------------------------------------------
# Tight back-road curves should tame the helper, but gentle highway bends (with
# large radii) should not.  Keep the midpoint a bit higher so that we only
# start attenuating once lateral accel exceeds ~1.6 m/s².
CURV_A_HALF = 1.8  # [m/s²]
CURV_K = 20.0

# Additional *instant-curve* gate based purely on geometric curvature (κ).
# This differentiates between tight back-road corners (κ ≳ 0.004) and gentle
# highway bends, independent of speed.
# κ-based gate – focus on geometric curvature so that we catch low-speed but
# tight (<200 m radius) corners.
# Tune κ-based instant curvature gate so its output aligns with empirical
# observations:
#   • ≥0.70 ⇒ dead-straight
#   • ≈0.55 ⇒ mild bend just becoming visible
#   • ≤0.45 ⇒ definitely turning
# The logistic parameters below satisfy those targets for typical κ values
# seen in the model stream.
#
# ( see: gate = 1 / (1 + exp(K * (κ - HALF))) )

CURV_KAPPA_HALF = 0.004  # [1/m] – centre point (gate = 0.5)
CURV_KAPPA_K = 600.0  # slope – steeper drop-off around the threshold

# -----------------------------------------------------------------------------
# New *curviness*-based gate ----------------------------------------------------
#
# Instead of attenuating the helper based on instantaneous lateral acceleration
# (v²·κ) we now leverage the already-computed *curviness* debug metric which
# represents the **maximum absolute curvature** along the ~50 m model horizon
# scaled by 1000 for easier interpretation.
#
#   curviness = κ_max · 1000   ⟹   κ_max = curviness / 1000
#
# The logistic gate below starts reducing the helper once the metric exceeds
# ≈ 7 (moderate corner) and rapidly approaches zero for values above ≈ 14
# (tight back-road bend).  These numbers map well to the on-screen UI scale
# (0-10 ≈ straight/gentle highway; 10-25 ≈ moderate; 25+ ≈ tight).
#
# The slope (CURVINESS_K) was chosen so that the gate is ~0.98 at 0, 0.5 at 7
# and ~0.02 at 14, closely mirroring the behaviour of the original lat-acc gate
# but in the more intuitive *curviness* domain.
# -----------------------------------------------------------------------------

# New RMS-based curviness tuning values.  RMS tends to be ~30-40 % lower than
# max-kappa×1000, so adjust the half-point for a more forgiving response on
# slight bends and long highway curves. The gate now tolerates moderate
# curviness before attenuating boost.
CURVINESS_HALF = 4.7  # lower half-point to anticipate curves earlier (Tuned from 4.5)
CURVINESS_K = 0.65  # logistic slope (Tuned from 0.7)

# Control dynamics -----------------------------------------------------------
# Shorter time-constant for critically damped accel helper → quicker response.
# Phase-1: make the critically-damped helper a touch slower so accel
# builds more progressively.
# Phase-1: slower helper time-constant for smoother acceleration response.
# Reduced time-constant for quicker acceleration response, varying by personality.
TAU_MIN_BY_PERSONALITY = {
  log.LongitudinalPersonality.aggressive: 0.9,  # [s] Quicker response
  log.LongitudinalPersonality.standard: 1.1,    # [s] Balanced response
  log.LongitudinalPersonality.relaxed: 1.3,     # [s] Smoother, gradual response
}
TAU_SPAN = 0.7  # [s]

# Extra helper gain for stronger (yet still capped) boost.
# Helper gain – lowered a bit so boost feels less like a "rocket-ship" yet
# still provides meaningful assistance.
# Slightly gentler acceleration boost
# Phase-1: lower raw helper gain for gentler peak acceleration
# Increased gain for quicker low-speed response, balanced for overall smoothness.
# Helper gain now varies by personality for distinct acceleration feel.
HELPER_GAIN_BY_PERSONALITY = {
  log.LongitudinalPersonality.aggressive: 0.30, # More responsive acceleration
  log.LongitudinalPersonality.standard: 0.26,   # Balanced acceleration
  log.LongitudinalPersonality.relaxed: 0.22,    # Gentler acceleration
}

# Filtering constants.  Lower alpha = less filtering / quicker reaction.
# Additional filtering to damp oscillations
# Lower alphas → less filtering → snappier response without overshoot.
# HELPER_LPF_ALPHA_HIGH increased for smoother high-speed boost.
# LPF alphas now vary by personality for tailored smoothness and responsiveness.
HELPER_LPF_ALPHA_HIGH_BY_PERSONALITY = {
  log.LongitudinalPersonality.aggressive: 0.80, # Less filtering for responsiveness
  log.LongitudinalPersonality.standard: 0.85,   # Balanced filtering
  log.LongitudinalPersonality.relaxed: 0.90,    # More filtering for smoothness
}
HELPER_LPF_ALPHA_LOW_BY_PERSONALITY = {
  log.LongitudinalPersonality.aggressive: 0.55, # Less filtering
  log.LongitudinalPersonality.standard: 0.60,   # Balanced filtering
  log.LongitudinalPersonality.relaxed: 0.65,    # More filtering
}

# Clear-road metric low-pass – make it follow quicker too.
CLEAR_ROAD_LPF_ALPHA = 0.75

# -----------------------------------------------------------------------------
# Scaling factors to temper aggression when there's *no* lead vehicle.
# -----------------------------------------------------------------------------

# How much the helper weight is allowed to drop at high speed when road is clear
# and there's no lead. 0 = keep full aggressiveness, 1 = completely disable.
# Drop less boost at high speed (0.6 instead of 0.7)
# Phase-3: retain a bit more eagerness even with no lead vehicle
NO_LEAD_WEIGHT_DROP = 0.10  # maintain more boost at high speed

# Minimum scaling so we never turn the boost fully off.
# Phase-3: allow slightly lower floor so highway cruising feels steadier
NO_LEAD_WEIGHT_MIN = 0.40  # higher minimum weight to maintain boost

# Base minimum helper weight to protect against false-positive low clear_road
# (e.g. due to curvature noise).
MIN_BASE_WEIGHT = 0.20

# Additional overshoot allowance when following a distant lead.  A larger
# velocity margin lets the car close very large gaps more assertively.
CATCHUP_V_REL_EXTRA = 2.0  # [m/s] - increased for closer following

# Distance beyond the desired following gap at which the helper begins to
# aggressively pull forward.  The catch-up weight scales with the extra
# distance up to this value.
CATCHUP_DIST_MAX = 12.0 # [m]

# -----------------------------------------------------------------------------
# Phase-4: jerk limiting -------------------------------------------------------
# -----------------------------------------------------------------------------
# Limit the *change* in commanded acceleration (jerk) so the boost feels smooth
# at high speeds.  We apply a simple speed-dependent cap expressed in m/s³.  In
# practice the planner runs at 20 Hz (dt ≈0.05 s) so we convert the per-second
# jerk limit to a per-cycle delta-accel threshold.

# Break-points in m/s.  17.9 m/s ≈ 40 mph.
JERK_LIMIT_BP = [0.0, 17.9, 30.0]  # [m/s]
# Allowed jerk (|da/dt|) at the corresponding speeds → lower at high speed.
# Increased low-speed jerk for faster take-off, moderate mid-speed, and smooth high-speed.
# Jerk limits now vary by personality.
JERK_LIMIT_VALS_BY_PERSONALITY = {
  log.LongitudinalPersonality.aggressive: [2.2, 1.2, 0.7],  # [m/s³] More responsive
  log.LongitudinalPersonality.standard:   [2.0, 1.0, 0.6],  # [m/s³] Balanced
  log.LongitudinalPersonality.relaxed:    [1.8, 0.8, 0.5],  # [m/s³] Smoother
}


# Above this speed, ignore E2E slowdowns when no radar lead is detected
# Speed threshold above which model slowdowns may be considered phantom.
# Use exact 50 mph (22.35 m/s) to avoid gating at slightly lower speeds.
PHANTOM_BRAKE_SPEED = 22.35  # m/s (50 mph)
# Difference in acceleration between planner and model required to treat
# the model braking as phantom.  Slightly higher to avoid spurious
# activation from small planner/model discrepancies.
PHANTOM_BRAKE_THRESHOLD = 0.25  # m/s^2
# Duration that planner output overrides mild model braking once phantom
# deceleration is detected.  Shortened so the override is brief.
PHANTOM_BRAKE_TIME = 0.3  # s

# Gate for far-away slow radar leads. If radar detects a vehicle far ahead
# moving much slower than us, disable the helper to avoid accelerating into
# a potential stopped car or traffic queue.
SLOW_RADAR_DIST = 70.0        # minimum distance to check for slow lead [m]
SLOW_RADAR_SPEED_DELTA = 10.0 # relative speed threshold to disable DAB [m/s]

CONTROL_N_T_IDX = ModelConstants.T_IDXS[:CONTROL_N]

# Maximum forward distance (in metres) to consider when computing the *curviness*
# metric.  Shortening the horizon from 50  m to 35  m makes the value react
# slightly earlier when exiting a turn, better matching the instantaneous
# steering feel without compromising anticipation on winding roads.
CURVINESS_FWD_DIST = 50.0  # longer horizon to better anticipate curves


@dataclass
class LeadData:
  """Simplified lead representation for sensor fusion."""

  status: bool
  dRel: float = 0.0
  vRel: float = 0.0
  vLead: float = 0.0


@dataclass
class CurvatureData:
  """Model-derived curvature inputs."""

  desired: float
  x: Sequence[float]
  y: Sequence[float]
  yaw_rate: Sequence[float]
  speeds: Sequence[float]


@dataclass
class DabInputs:
  v_ego: float
  a_ego: float
  v_set: float
  output_a_target: float
  output_a_mpc: float
  output_a_e2e: float
  v_desired: Sequence[float]
  allow_throttle: bool
  radar_lead: LeadData
  model_lead: LeadData
  curvature: CurvatureData
  personality: log.LongitudinalPersonality


@dataclass
class DabOutputs:
  a_final: float
  clear_road: float
  a_helper: float
  weight: float
  lead_car_gate: float
  tts_gate: float
  curv_gate: float
  phantom_brake_gate: float
  slow_radar_gate: float


class DynamicAccelerationBoost:
  """Compute dynamic acceleration boost.

  Returns `(a_final, clear_road, a_helper, weight)` matching the original
  interface.
  """

  def __init__(self) -> None:
    self._helper_a_lpf: float = 0.0
    self._clear_road_lpf: float = 0.0
    self._curviness: float = 0.0  # scaled κ for UI/debug

    self._params = Params()

    # Additional smoothing state to dampen high-speed oscillations
    self._weight_lpf: float = 0.0
    # Smoothed catch-up weight to avoid rapid toggling when closing on a lead
    self._catchup_lpf: float = 0.0

    # Phase-4: previous acceleration for jerk limiting
    self._prev_a_final: float = 0.0

    # Gate toggles ----------------------------------------------------
    self._gate_phantom: bool = True
    self._gate_lead: bool = True
    self._gate_tts: bool = True
    self._gate_curv: bool = True
    # Disable helper when a far-away radar lead is moving much slower
    self._gate_slow_radar: bool = True
    self._last_gate_check: float = 0.0
    self._phantom_time: float = 0.0
    self._last_debug_print_time: float = 0.0


  # ------------------------------------------------------------------
  # Properties
  # ------------------------------------------------------------------

  @property
  def curviness(self) -> float:
    """Return the latest *curviness* metric (κ_max · 1000).

    The value corresponds to the maximum absolute curvature along the
    predicted path (≈50 m) scaled up for readability.  Values:
      0-10  → almost straight road
      10-25 → gentle highway bend
      25-50 → moderate corner
      50+   → tight back-road curve"""
    return self._curviness

  def _debug_print(self, message: str) -> None:
    """Print debug messages at most once per second."""
    now = time.monotonic()
    if now - self._last_debug_print_time >= 1.0:
      print(f"[DAB DEBUG] {message}")
      self._last_debug_print_time = now

  def _apply_jerk_limit(self, accel: float, v_ego: float, personality: log.LongitudinalPersonality) -> float:
    """Limit jerk based on vehicle speed and personality, then update previous accel."""
    self._debug_print(f"_apply_jerk_limit: input accel={accel:.2f}, v_ego={v_ego:.2f}, personality={personality}")
    jerk_vals = JERK_LIMIT_VALS_BY_PERSONALITY.get(personality, JERK_LIMIT_VALS_BY_PERSONALITY[log.LongitudinalPersonality.standard])
    jerk_limit = float(np.interp(v_ego, JERK_LIMIT_BP, jerk_vals))
    max_delta = jerk_limit * DT_MDL

    delta = accel - self._prev_a_final
    self._debug_print(f"_apply_jerk_limit: jerk_limit={jerk_limit:.2f}, max_delta={max_delta:.4f}, delta={delta:.4f}, prev_a_final={self._prev_a_final:.2f}")

    if delta > max_delta:
      accel = self._prev_a_final + max_delta
      self._debug_print(f"_apply_jerk_limit: positive jerk limited, new accel={accel:.2f}")
    elif delta < -max_delta:
      accel = self._prev_a_final - max_delta
      self._debug_print(f"_apply_jerk_limit: negative jerk limited, new accel={accel:.2f}")

    self._prev_a_final = accel
    return accel

  def _headway_time(self, personality: log.LongitudinalPersonality, v_ego: float) -> float:
    """Return dynamic time headway based on personality and speed."""
    base = HEADWAY_TIME_BASE.get(personality, LEAD_HEADWAY_TIME)
    speed_extra = np.interp(v_ego, [0.0, 30.0], [0.0, HEADWAY_TIME_SPEED_DELTA])
    return base + speed_extra

  # ------------------------------------------------------------------
  # Internal helpers
  # ------------------------------------------------------------------


  def _update_gate_toggles(self) -> None:
    """Refresh gate toggles from Params."""
    now = time.monotonic()
    if now - self._last_gate_check > 1.0:
      self._last_gate_check = now
      try:
        self._gate_phantom = self._params.get_bool("DABPhantomGate")
        self._gate_lead = self._params.get_bool("DABLeadGate")
        self._gate_tts = self._params.get_bool("DABTTSGate")
        self._gate_curv = self._params.get_bool("DABCurvGate")
        self._gate_slow_radar = self._params.get_bool("DABSlowLeadGate")
      except Exception:
        pass

  def _phantom_brake_gate(self, inputs: DabInputs) -> float:
    """Return base acceleration target accounting for phantom brakes.

    This helper is currently unused since phantom brake overrides are disabled.
    """
    self._debug_print(f"_phantom_brake_gate called with e2e={inputs.output_a_e2e:.2f}, mpc={inputs.output_a_mpc:.2f}")
    """
    fused_lead = self._fused_lead(inputs.radar_lead, inputs.model_lead)
    if self._gate_phantom and inputs.v_ego > PHANTOM_BRAKE_SPEED and not fused_lead.status:
      diff = inputs.output_a_e2e - inputs.output_a_mpc
      phantom = diff < -PHANTOM_BRAKE_THRESHOLD
      self._debug_print(f"_phantom_brake_gate: v_ego={inputs.v_ego:.2f}, fused_lead_status={fused_lead.status}, diff={diff:.2f}, phantom={phantom}")
      if phantom:
        self._phantom_time += DT_MDL
      else:
        self._phantom_time = 0.0
      self._debug_print(f"_phantom_brake_gate: phantom_time={self._phantom_time:.2f}")

      if phantom and self._phantom_time < PHANTOM_BRAKE_TIME and inputs.output_a_e2e > -0.5:
        self._debug_print(f"_phantom_brake_gate: overriding with mpc output: {inputs.output_a_mpc:.2f}")
        return inputs.output_a_mpc
      self._debug_print(f"_phantom_brake_gate: returning min(mpc, e2e): {min(inputs.output_a_mpc, inputs.output_a_e2e):.2f}")
      return min(inputs.output_a_mpc, inputs.output_a_e2e)
    else:
      self._phantom_time = 0.0
      self._debug_print(f"_phantom_brake_gate: condition not met or gate disabled, returning min(mpc, e2e): {min(inputs.output_a_mpc, inputs.output_a_e2e):.2f}")
      return min(inputs.output_a_mpc, inputs.output_a_e2e)
    """
    self._debug_print(f"_phantom_brake_gate: returning e2e output: {inputs.output_a_e2e:.2f} (phantom logic bypassed)")
    return inputs.output_a_e2e

  def _fused_lead(self, radar_lead: LeadData, model_lead: LeadData) -> LeadData:
    """Return fused lead from radar and model."""
    if radar_lead.status and model_lead.status:
      d_rel = 0.5 * (radar_lead.dRel + model_lead.dRel)
      v_rel = 0.5 * (radar_lead.vRel + model_lead.vRel)
      v_lead = 0.5 * (radar_lead.vLead + model_lead.vLead)
      return LeadData(True, d_rel, v_rel, v_lead)
    elif radar_lead.status:
      return radar_lead
    elif model_lead.status:
      return model_lead
    else:
      return LeadData(False)

  def _lead_car_gate(self, inputs: DabInputs) -> float:
    """Compute gate based on lead-car distance and relative speed."""
    lead = self._fused_lead(inputs.radar_lead, inputs.model_lead)
    if self._gate_lead and lead.status:
      d_rel = float(lead.dRel)
      v_rel = float(lead.vRel)

      headway = self._headway_time(inputs.personality, inputs.v_ego)
      smoothing_dist = max(LEAD_DISTANCE_MIN, inputs.v_ego * headway)
      dist_gate = 1.0 / (1.0 + np.exp(-LEAD_DISTANCE_K * (d_rel - smoothing_dist)))

      if v_rel < -0.1:
        ttc = d_rel / max(0.1, -v_rel)
      else:
        ttc = float('inf')

      if ttc <= TTC_HARD:
        ttc_gate = 0.0
      elif ttc >= TTC_SOFT:
        ttc_gate = 1.0
      else:
        ttc_gate = (ttc - TTC_HARD) / (TTC_SOFT - TTC_HARD)

      return dist_gate * ttc_gate
    return 1.0

  def _tts_gate(self, inputs: DabInputs) -> float:
    """Gate based on predicted slowdown horizon."""
    personality = inputs.personality

    if personality == log.LongitudinalPersonality.aggressive:
      TTS_HARD = TTS_HARD_AGGRESSIVE
    elif personality == log.LongitudinalPersonality.relaxed:
      TTS_HARD = TTS_HARD_RELAXED
    else:
      TTS_HARD = TTS_HARD_STANDARD

    TTS_SOFT = TTS_HARD + TTS_DELTA_SOFT

    v_now = inputs.v_desired[0] if len(inputs.v_desired) else inputs.v_ego
    slow_thresh = max(0.0, v_now - 2.0)

    tts = float('inf')
    for t, v in zip(CONTROL_N_T_IDX, inputs.v_desired, strict=True):
      if v < slow_thresh:
        tts = t
        break

    if self._gate_tts:
      if tts <= TTS_HARD:
        return 0.0
      elif tts >= TTS_SOFT:
        return 1.0
      else:
        return (tts - TTS_HARD) / (TTS_SOFT - TTS_HARD)
    return 1.0

  def _curvature_metrics(self, inputs: DabInputs) -> tuple[float, float, float]:
    """Return (curviness, kappa_now, a_lat) from model curvature."""
    a_lat = 0.0
    kappa_max = 0.0
    _kappa_sq_accum = 0.0
    _kappa_count = 0

    def _update_metrics(kappa: float, speed: float) -> None:
      nonlocal a_lat, kappa_max, _kappa_sq_accum, _kappa_count
      abs_k = abs(kappa)
      a_lat = max(a_lat, abs_k * speed**2)
      kappa_max = max(kappa_max, abs_k)
      _kappa_sq_accum += abs_k**2
      _kappa_count += 1

    try:
      xs = np.asarray(inputs.curvature.x)
      ys = np.asarray(inputs.curvature.y)
      yaw_rates = np.asarray(inputs.curvature.yaw_rate)
      speeds_path = np.asarray(inputs.curvature.speeds)

      n = min(len(xs), len(ys), len(yaw_rates), len(speeds_path))

      if n >= 3:
        MAX_FWD_DIST = CURVINESS_FWD_DIST
        idxs = np.arange(1, n - 1)
        ahead = xs[idxs + 1] <= MAX_FWD_DIST
        if not np.all(ahead):
          idxs = idxs[:np.argmax(~ahead)]

        if idxs.size:
          v_here = np.maximum(0.1, speeds_path[idxs])
          kappa_yaw = yaw_rates[idxs] / v_here
          abs_k = np.abs(kappa_yaw)
          a_lat = max(a_lat, float(np.max(abs_k * v_here**2)))
          kappa_max = max(kappa_max, float(np.max(abs_k)))
          _kappa_sq_accum += float(np.sum(abs_k**2))
          _kappa_count += int(abs_k.size)

          x1 = xs[idxs - 1]
          x2 = xs[idxs]
          x3 = xs[idxs + 1]
          y1 = ys[idxs - 1]
          y2 = ys[idxs]
          y3 = ys[idxs + 1]

          a = np.hypot(x2 - x1, y2 - y1)
          b = np.hypot(x3 - x2, y3 - y2)
          c = np.hypot(x1 - x3, y1 - y3)

          valid = (a >= 1e-4) & (b >= 1e-4) & (c >= 1e-4)
          if np.any(valid):
            area = 0.5 * ((x2[valid] - x1[valid]) * (y3[valid] - y1[valid]) - (y2[valid] - y1[valid]) * (x3[valid] - x1[valid]))
            kappa_geo = np.abs(2.0 * area) / (a[valid] * b[valid] * c[valid])
            a_lat = max(a_lat, float(np.max(kappa_geo * v_here[valid]**2)))
            kappa_max = max(kappa_max, float(np.max(kappa_geo)))
            _kappa_sq_accum += float(np.sum(kappa_geo**2))
            _kappa_count += int(np.count_nonzero(valid))

      if kappa_max == 0.0:
        curv_immediate = float(inputs.curvature.desired)
        kappa_max = abs(curv_immediate)
        a_lat = abs(curv_immediate) * inputs.v_ego**2

    except Exception:
      try:
        curv_immediate = float(inputs.curvature.desired)
        kappa_max = abs(curv_immediate)
        a_lat = abs(curv_immediate) * inputs.v_ego**2
      except Exception:
        kappa_max = 0.0
        a_lat = 0.0

    if _kappa_count > 0:
      curv_rms = (_kappa_sq_accum / _kappa_count) ** 0.5
      self._curviness = curv_rms * 1000.0
    else:
      self._curviness = kappa_max * 1000.0

    try:
      kappa_now = abs(float(inputs.curvature.desired))
    except Exception:
      kappa_now = 0.0

    return self._curviness, kappa_now, a_lat

  def _curvature_gate(self, curviness: float, kappa_now: float, v_ego: float) -> float:
    """Return combined curvature gate."""
    self._debug_print(f"_curvature_gate: curviness={curviness:.2f}, kappa_now={kappa_now:.4f}, v_ego={v_ego:.2f}")
    # Disable curve check at low speeds
    if v_ego < 15.0:
      self._debug_print(f"_curvature_gate: v_ego ({v_ego:.2f} m/s) < 15.0 m/s, curve check disabled, returning 1.0")
      return 1.0

    kappa_gate = 1.0 / (1.0 + np.exp(CURV_KAPPA_K * (kappa_now - CURV_KAPPA_HALF)))
    curviness_gate = 1.0 / (1.0 + np.exp(CURVINESS_K * (curviness - CURVINESS_HALF)))
    _curv_gate_raw = min(curviness_gate, kappa_gate)
    self._debug_print(f"_curvature_gate: kappa_gate={kappa_gate:.2f}, curviness_gate={curviness_gate:.2f}, raw_gate={_curv_gate_raw:.2f}")

    if self._gate_curv:
      speed_kmh = v_ego * 3.6
      hi_thr = 0.55
      lo_thr = 0.45

      if speed_kmh > 70.0:
        relax = min(1.0, (speed_kmh - 70.0) / 40.0)
        hi_thr -= 0.10 * relax
        lo_thr -= 0.10 * relax

      if _curv_gate_raw >= hi_thr:
        return 1.0
      elif _curv_gate_raw <= lo_thr:
        return 0.0
      else:
        return (_curv_gate_raw - lo_thr) / (hi_thr - lo_thr)
    self._debug_print(f"_curvature_gate: gate_curv disabled or condition not met, returning 1.0")
    return 1.0

  def _slow_radar_gate(self, radar_lead: LeadData, v_ego: float) -> float:
    """Disable boost if a far radar lead is moving much slower."""
    self._debug_print(f"_slow_radar_gate: radar_status={radar_lead.status}, dRel={radar_lead.dRel:.1f}, vLead={radar_lead.vLead:.1f}, v_ego={v_ego:.1f}")
    if self._gate_slow_radar and radar_lead.status and v_ego > 5.0:
      if radar_lead.dRel >= SLOW_RADAR_DIST:
        if (v_ego - radar_lead.vLead) >= SLOW_RADAR_SPEED_DELTA:
          self._debug_print(f"_slow_radar_gate: SLOW RADAR DETECTED, returning 0.0")
          return 0.0
    self._debug_print(f"_slow_radar_gate: returning 1.0")
    return 1.0

  def _helper_accel(self, inputs: DabInputs, clear_road: float, lead: LeadData) -> float:
    """Compute critically-damped helper acceleration based on personality."""
    self._debug_print(f"_helper_accel: clear_road={clear_road:.2f}, lead_status={lead.status}, v_ego={inputs.v_ego:.2f}, a_ego={inputs.a_ego:.2f}, v_set={inputs.v_set:.2f}, personality={inputs.personality}")
    v_lead_safe = float(lead.vLead) if lead.status else 99_999.0
    if lead.status:
      headway = self._headway_time(inputs.personality, inputs.v_ego)
      desired_dist = max(LEAD_DISTANCE_MIN, inputs.v_ego * headway)
      extra_dist = max(0.0, lead.dRel - desired_dist)
      v_overshoot = 0.0
      if extra_dist > 1.0:
        overshoot_scale = float(np.interp(inputs.v_ego, [0.0, 20.0, 33.0],
                                          [1.2, 1.0, 0.6]))
        v_overshoot = CATCHUP_V_REL_EXTRA * overshoot_scale
      v_target = min(inputs.v_set, v_lead_safe + v_overshoot)
      self._debug_print(f"_helper_accel (lead): headway={headway:.2f}, desired_dist={desired_dist:.1f}, extra_dist={extra_dist:.1f}, v_overshoot={v_overshoot:.2f}, v_target={v_target:.2f}")
    else:
      v_target = inputs.v_set
      self._debug_print(f"_helper_accel (no lead): v_target={v_target:.2f}")
    v_err = max(0.0, v_target - inputs.v_ego)

    tau_min = TAU_MIN_BY_PERSONALITY.get(inputs.personality, TAU_MIN_BY_PERSONALITY[log.LongitudinalPersonality.standard])
    tau = tau_min + TAU_SPAN * (1.0 - clear_road)
    a_des = (2.0 * v_err / tau) - (inputs.a_ego / tau)
    helper_gain = HELPER_GAIN_BY_PERSONALITY.get(inputs.personality, HELPER_GAIN_BY_PERSONALITY[log.LongitudinalPersonality.standard])
    helper_a = float(np.clip(a_des * helper_gain, 0.0, ACCEL_MAX))
    self._debug_print(f"_helper_accel: v_err={v_err:.2f}, tau={tau:.2f} (tau_min={tau_min:.2f}), a_des={a_des:.2f}, helper_gain={helper_gain:.2f}, helper_a_final={helper_a:.2f}")
    return helper_a

  def _blend_result(self, base_target: float, a_helper: float, weight: float, v_ego: float, personality: log.LongitudinalPersonality) -> float:
    """Blend helper with planner and apply smoothing & jerk limit based on personality."""
    self._debug_print(f"_blend_result: base_target={base_target:.2f}, a_helper={a_helper:.2f}, weight={weight:.2f}, v_ego={v_ego:.2f}, personality={personality}")
    w_alpha = float(np.interp(v_ego, [0.0, 20.0, 30.0], [0.60, 0.75, 0.85]))
    self._weight_lpf = w_alpha * self._weight_lpf + (1.0 - w_alpha) * weight
    if self._weight_lpf > weight + 0.1:
      self._weight_lpf = weight + 0.1
    self._weight_lpf = max(0.0, min(self._weight_lpf, 1.0))
    self._debug_print(f"_blend_result: w_alpha={w_alpha:.2f}, _weight_lpf={self._weight_lpf:.2f} (prev_weight_lpf was implicitly used)")

    alpha_low = HELPER_LPF_ALPHA_LOW_BY_PERSONALITY.get(personality, HELPER_LPF_ALPHA_LOW_BY_PERSONALITY[log.LongitudinalPersonality.standard])
    alpha_high = HELPER_LPF_ALPHA_HIGH_BY_PERSONALITY.get(personality, HELPER_LPF_ALPHA_HIGH_BY_PERSONALITY[log.LongitudinalPersonality.standard])
    alpha = float(np.interp(v_ego, [0.0, 20.0, 30.0], [alpha_low, 0.8, alpha_high])) # Using 0.8 as mid-point, consistent with previous logic
    self._helper_a_lpf = alpha * self._helper_a_lpf + (1.0 - alpha) * a_helper
    self._debug_print(f"_blend_result: alpha={alpha:.2f} (low={alpha_low:.2f}, high={alpha_high:.2f}), _helper_a_lpf={self._helper_a_lpf:.2f} (prev_helper_a_lpf was implicitly used)")

    a_final = self._weight_lpf * self._helper_a_lpf + (1.0 - self._weight_lpf) * base_target
    self._debug_print(f"_blend_result: a_final_before_jerk_limit={a_final:.2f}")
    return self._apply_jerk_limit(a_final, v_ego, personality)

  def compute(self, sm, inputs: DabInputs) -> DabOutputs:
    """Return Dynamic Acceleration Boost for the given inputs."""
    self._debug_print(f"compute called. inputs: {inputs}")

    if not inputs.allow_throttle:
      self._debug_print("compute: allow_throttle is False, returning early.")
      return DabOutputs(
        a_final=inputs.output_a_e2e,
        clear_road=0.0,
        a_helper=0.0,
        weight=0.0,
        lead_car_gate=0.0,
        tts_gate=0.0,
        curv_gate=0.0,
        phantom_brake_gate=0.0,
        slow_radar_gate=0.0,
      )

    self._update_gate_toggles()

    # Skip phantom brake overrides and simply use the lower acceleration target
    base_target = self._phantom_brake_gate(inputs) #min(inputs.output_a_mpc, inputs.output_a_e2e)
    self._debug_print(f"compute: base_target={base_target:.2f}")

    lead_gate = self._lead_car_gate(inputs)
    self._debug_print(f"compute: lead_gate={lead_gate:.2f}")
    tts_gate = self._tts_gate(inputs)
    self._debug_print(f"compute: tts_gate={tts_gate:.2f}")

    curviness, kappa_now, a_lat_val = self._curvature_metrics(inputs)
    self._debug_print(f"compute: curviness={curviness:.2f}, kappa_now={kappa_now:.4f}, a_lat_val={a_lat_val:.2f}")
    curv_gate = self._curvature_gate(curviness, kappa_now, inputs.v_ego)
    self._debug_print(f"compute: curv_gate={curv_gate:.2f}")

    slow_gate = self._slow_radar_gate(inputs.radar_lead, inputs.v_ego)
    self._debug_print(f"compute: slow_gate={slow_gate:.2f}")

    clear_road_raw = lead_gate * tts_gate * curv_gate * slow_gate
    self._debug_print(f"compute: clear_road_raw={clear_road_raw:.2f} (prev_clear_road_lpf={self._clear_road_lpf:.2f})")
    self._clear_road_lpf = CLEAR_ROAD_LPF_ALPHA * self._clear_road_lpf + (1.0 - CLEAR_ROAD_LPF_ALPHA) * clear_road_raw
    clear_road = self._clear_road_lpf
    self._debug_print(f"compute: clear_road (LPF)={clear_road:.2f}")


    lead = self._fused_lead(inputs.radar_lead, inputs.model_lead)
    a_helper = self._helper_accel(inputs, clear_road, lead)
    self._debug_print(f"compute: a_helper={a_helper:.2f}")

    if base_target < -0.05 or clear_road < 1e-3:
      weight = 0.0
      self._debug_print(f"compute: weight set to 0 (base_target={base_target:.2f} or clear_road={clear_road:.3f})")
    else:
      WEIGHT_EXP = 1.5
      weight = clear_road ** WEIGHT_EXP
      self._debug_print(f"compute: initial weight={weight:.2f} (clear_road={clear_road:.2f})")

    self._debug_print(f"compute: (before catchup) weight={weight:.2f}, _catchup_lpf={self._catchup_lpf:.2f}")
    if lead.status:
      d_rel = float(lead.dRel)
      headway = self._headway_time(inputs.personality, inputs.v_ego)
      desired_dist = max(LEAD_DISTANCE_MIN, inputs.v_ego * headway)
      extra_dist = max(0.0, d_rel - desired_dist)
      if extra_dist > 1.0 and base_target >= 0.0 and inputs.output_a_target >= 0.0:
        dist_factor = min(extra_dist / CATCHUP_DIST_MAX, 1.0)
        speed_clip = float(np.interp(inputs.v_ego, [0.0, 20.0, 33.0],
                                     [1.0, 0.9, 0.7]))
        catchup_target = (0.5 + 0.4 * dist_factor) * speed_clip
        self._catchup_lpf = 0.85 * self._catchup_lpf + 0.15 * catchup_target
      else:
        # Decay smoothing state when catchup no longer warranted
        self._catchup_lpf *= 0.85
        self._debug_print(f"compute (lead status, no catchup): _catchup_lpf decayed to {self._catchup_lpf:.2f}")
    else:
      # Gradually fade any residual catch-up weight when no lead is present
      self._catchup_lpf *= 0.85
      self._debug_print(f"compute (no lead status): _catchup_lpf decayed to {self._catchup_lpf:.2f}")

    weight = max(weight, self._catchup_lpf)
    self._debug_print(f"compute: weight after max(weight, _catchup_lpf)={weight:.2f}")

    if not lead.status and weight > 0.0:
      speed_scale = 1.0 - NO_LEAD_WEIGHT_DROP * min(inputs.v_ego, 30.0) / 30.0
      speed_scale = max(NO_LEAD_WEIGHT_MIN, speed_scale)
      self._debug_print(f"compute (no lead, weight > 0): speed_scale={speed_scale:.2f}, original weight={weight:.2f}")
      weight *= speed_scale
      self._debug_print(f"compute (no lead, weight > 0): weight after speed_scale={weight:.2f}")

    if inputs.output_a_target < -0.1:
      self._debug_print(f"compute (output_a_target < -0.1): original weight={weight:.2f}")
      weight *= 0.5
      self._debug_print(f"compute (output_a_target < -0.1): weight halved to {weight:.2f}")

    if weight < MIN_BASE_WEIGHT and inputs.v_ego < 15.0:
      self._debug_print(f"compute (weight < MIN_BASE_WEIGHT and v_ego < 15): original weight={weight:.2f}")
      weight = MIN_BASE_WEIGHT
      self._debug_print(f"compute (weight < MIN_BASE_WEIGHT and v_ego < 15): weight set to MIN_BASE_WEIGHT {weight:.2f}")

    a_final = self._blend_result(base_target, a_helper, weight, inputs.v_ego, inputs.personality)
    self._debug_print(f"compute: a_final after _blend_result={a_final:.2f}")

    outputs = DabOutputs(
      a_final=a_final,
      clear_road=clear_road,
      a_helper=a_helper,
      weight=weight,
      lead_car_gate=lead_gate,
      tts_gate=tts_gate,
      curv_gate=curv_gate,
      phantom_brake_gate=base_target, # Renamed from phantom_brake_gate to base_target for clarity
      slow_radar_gate=slow_gate,
    )
    self._debug_print(f"compute: final outputs: {outputs}")
    return outputs
