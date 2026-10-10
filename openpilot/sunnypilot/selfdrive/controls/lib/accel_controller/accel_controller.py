"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np

from openpilot.cereal import custom
from openpilot.common.params import Params
from openpilot.sunnypilot import get_sanitize_int_param

AccelProfile = custom.LongitudinalPlanSP.AccelController.Profile

MAX_ACCEL_BREAKPOINTS = [0., 3., 12,  24., 36.]  # m/s
MAX_ACCEL_PROFILES = {
  AccelProfile.eco:    [1.75, 1.50, 0.40, 0.15, 0.12],
  AccelProfile.normal: [1.95, 1.80, 0.70, 0.36, 0.25],
  AccelProfile.sport:  [2.00, 2.00, 1.20, 0.70, 0.50],
}
# Eco while the hybrid's engine is OFF (battery-first mode, ported from tncr18): keep wheel power m*a*v + road load under
# the ~11-14 kW at which a Corolla hybrid starts its engine (30 Corolla Cross rlogs, threshold not SOC dependent):
# 60 km/h 0.25, 70 km/h 0.16, 80 km/h 0.12. Launch values are the Altis eco ones. Once the engine runs there is nothing
# to save, so the normal eco line takes over until it stops again.
ECO_ENGINE_OFF_BP = [0., 3., 12., 16.67, 19.44, 22.22, 24., 36.]  # m/s
# The first two rows follow the eco line above: battery-first may never launch harder than eco. They still held the
# pre-retune eco values (1.85 / 1.55) in the source this was ported from, which put engine-off above eco at 0-3 m/s.
ECO_ENGINE_OFF_MAX_ACCEL = [1.75, 1.50, 0.35, 0.25, 0.16, 0.12, 0.08, 0.06]
# Cruise deceleration to a lowered set speed (no lead). Normal/sport: one CONSTANT decel latched when the gap opens
# (gap / response time, never gentler than CRUISE_DECEL_ACCEL) and held, so the car slows on a straight line instead of
# the proportional gap/time law, which braked hardest at the start and dragged a long tail; more presses = firmer.
# Eco (driver request 2026-09-25/26): never hurry to the new set speed however far it is or however many presses.
# Above 70 km/h: pure coasting - the target decel IS the planner's pitch-aware coast accel (get_coast_accel), so the
# PCM neither adds throttle nor regen; the speed table above 70 is only the fallback when no coast value is given
# (road-load estimate of a 1500 kg Corolla Cross: -0.22 at 70, -0.30 at 90, -0.40 at 120). Below 60 km/h -0.40
# (regen), blended into coasting between 60 and 70 as the speed falls. Whether -0.40 is too firm is for the road test.
CRUISE_DECEL_RESPONSE_TIME = {  # seconds to close the gap (normal/sport)
  AccelProfile.normal: 3.5,
  AccelProfile.sport: 3.0,
}
CRUISE_DECEL_ACCEL = {  # m/s^2; gentlest constant decel (normal/sport)
  AccelProfile.normal: -0.50,
  AccelProfile.sport: -0.65,
}
ECO_CRUISE_DECEL_BP = [0., 16.67, 19.44, 25.0, 33.3]   # m/s (0, 60, 70, 90, 120 km/h)
ECO_CRUISE_DECEL_V = [-0.40, -0.40, -0.22, -0.30, -0.40]  # m/s^2; the >= 70 km/h part is only the FALLBACK coast estimate
ECO_COAST_BLEND_BP = [16.67, 19.44]  # m/s: -0.40 at 60 km/h blends into pure coasting by 70 km/h
ECO_COAST_MIN, ECO_COAST_MAX = -1.2, -0.05  # m/s^2; sanity clip on the planner's pitch-aware coast accel
# Eco lead pull-away boost (driver 2026-10-01 night): below 80 km/h, when a detected lead is pulling away (gap opening),
# eco may accelerate a little harder for a while so the car keeps up, eased in and out; with no lead nothing changes.
# The boost scales with how fast the gap opens, fades out from 70 to 80 km/h, and never lifts eco above the normal line.
ECO_BOOST_DV_BP = [0.3, 2.5]     # m/s, lead speed minus ego speed
ECO_BOOST_V = [0.0, 0.35]        # m/s^2 added to the eco limit
ECO_BOOST_FADE_BP = [19.44, 22.22]  # m/s (70 -> 80 km/h): full -> none
ECO_BOOST_D_MAX = 80.0           # m, only a lead this close counts
ECO_BOOST_PROB_MIN = 0.5
ECO_BOOST_RISE = 0.25            # m/s^3, how fast the boost builds
ECO_BOOST_FALL = 0.5             # m/s^3, how fast it fades
ECO_BOOST_DT = 0.05              # s, planner step
CRUISE_DECEL_TAPER_TIME = 1.0  # s; inside |decel| * this of the target the decel eases off proportionally (no overshoot)


class AccelController:
  def __init__(self):
    self.params = Params()
    self._cruise_decel: float | None = None
    self._cruise_decel_target: float | None = None
    self._boost = 0.0
    self.update()

  def update(self) -> None:
    self._profile = get_sanitize_int_param("AccelPersonality", AccelProfile.eco, AccelProfile.sport, self.params)
    self._enabled = self.params.get_bool("AccelPersonalityEnabled")

  @property
  def profile(self) -> int:
    return self._profile

  def is_enabled(self) -> bool:
    return self._enabled

  def get_max_accel(self, v_ego: float, engine_off: bool = False, lead=None) -> float:
    if engine_off and self._profile == AccelProfile.eco:
      base = float(np.interp(max(0.0, v_ego), ECO_ENGINE_OFF_BP, ECO_ENGINE_OFF_MAX_ACCEL))
    else:
      base = float(np.interp(max(0.0, v_ego), MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[self._profile]))
    if self._profile != AccelProfile.eco:
      self._boost = 0.0
      return base
    return base + self._eco_lead_boost(v_ego, base, lead)

  def _eco_lead_boost(self, v_ego: float, base: float, lead) -> float:
    target = 0.0
    if lead is not None and lead.present and lead.modelProb > ECO_BOOST_PROB_MIN and lead.dRel < ECO_BOOST_D_MAX:
      target = float(np.interp(lead.vLead - v_ego, ECO_BOOST_DV_BP, ECO_BOOST_V))
      target *= float(np.interp(v_ego, ECO_BOOST_FADE_BP, [1.0, 0.0]))
      normal = float(np.interp(max(0.0, v_ego), MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[AccelProfile.normal]))
      target = float(np.clip(target, 0.0, max(normal - base, 0.0)))
    step = (ECO_BOOST_RISE if target > self._boost else ECO_BOOST_FALL) * ECO_BOOST_DT
    self._boost = float(np.clip(target, self._boost - step, self._boost + step))
    return self._boost

  def get_cruise_target(self, v_ego: float, v_target: float, accel_coast: float | None = None) -> float:
    if not np.isfinite(v_target) or v_target <= 0.0 or v_target >= v_ego:
      self._cruise_decel = None
      self._cruise_decel_target = None
      return v_target

    target_delta = v_target - v_ego
    if self._profile == AccelProfile.eco:
      # speed-scheduled, independent of the gap and of how many presses opened it
      decel = float(np.interp(v_ego, ECO_CRUISE_DECEL_BP, ECO_CRUISE_DECEL_V))
      if accel_coast is not None and np.isfinite(accel_coast) and accel_coast < 0.0:
        # >= 70 km/h: coast exactly (pitch-aware); 60-70 km/h: blend from the low-speed value into coasting
        coast = float(np.clip(accel_coast, ECO_COAST_MIN, ECO_COAST_MAX))
        w = float(np.interp(v_ego, ECO_COAST_BLEND_BP, [0.0, 1.0]))
        decel = (1.0 - w) * ECO_CRUISE_DECEL_V[1] + w * coast
    else:
      if self._cruise_decel is None or self._cruise_decel_target != v_target:
        # a new (or changed) gap: latch one constant decel for this episode
        self._cruise_decel = min(CRUISE_DECEL_ACCEL[self._profile], target_delta / CRUISE_DECEL_RESPONSE_TIME[self._profile])
        self._cruise_decel_target = v_target
      decel = self._cruise_decel

    # taper only once the target is close (both terms are negative; max = the gentler one) so the speed lands cleanly
    decel = max(decel, target_delta / CRUISE_DECEL_TAPER_TIME)
    return float(v_ego + decel)
