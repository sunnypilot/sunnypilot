#!/usr/bin/env python3
"""
Longitudinal control sim harness.

Acceptance gate for the three personality controllers:
  - sunnypilot/selfdrive/controls/lib/accel_personality/accel_controller.py
  - sunnypilot/selfdrive/controls/lib/dynamic_personality/dynamic_follow.py
  - sunnypilot/selfdrive/controls/lib/distant_lead.py

Each scenario encodes a real driver-felt failure mode (rubber band, late brake,
gas/brake stop-n-go, carsick spike) as concrete pass/fail metrics on the
controller outputs (a_min, a_max, t_follow, distant-track override).

Run:
  python3 tools/scripts/long_sim.py
"""
import sys
import types
from dataclasses import dataclass, field
from collections.abc import Callable

import numpy as np


# ── Stub openpilot.common.params before any controller import ─────────────────
# Avoids requiring a built params_pyx (Cython) for harness use.
class _StubParams:
  _store: dict = {}

  def __init__(self, *_a, **_k):
    pass

  def get(self, key, *_a, **_kw):
    return self._store.get(key)

  def put(self, key, val):
    self._store[key] = val

  def put_nonblocking(self, key, val):
    self._store[key] = val

  def get_bool(self, key, *_a, **_kw):
    return bool(self._store.get(key, False))

  def put_bool(self, key, val):
    self._store[key] = bool(val)

  def remove(self, key):
    self._store.pop(key, None)


_stub_mod = types.ModuleType('openpilot.common.params')
_stub_mod.Params = _StubParams
_stub_mod.ParamKeyFlag = type('ParamKeyFlag', (), {})
_stub_mod.ParamKeyType = type('ParamKeyType', (), {})
_stub_mod.UnknownKeyName = type('UnknownKeyName', (Exception,), {})
sys.modules['openpilot.common.params'] = _stub_mod
sys.modules['openpilot.common.params_pyx'] = _stub_mod

from openpilot.common.realtime import DT_MDL


# ── Mock cereal-style structs ─────────────────────────────────────────────────

@dataclass
class MockLead:
  status: bool = False
  dRel: float = 0.0
  yRel: float = 0.0
  vLead: float = 0.0
  vRel: float = 0.0
  aLeadK: float = 0.0
  aLeadTau: float = 0.0
  vLeadK: float = 0.0


@dataclass
class MockRadarState:
  leadOne: MockLead = field(default_factory=MockLead)


@dataclass
class MockCarState:
  vCruise: float = 100.0


@dataclass
class MockSm:
  store: dict = field(default_factory=dict)

  def __getitem__(self, k):
    return self.store[k]


@dataclass
class MockTrack:
  trackId: int = 0
  dRel: float = 0.0
  yRel: float = 0.0
  vLead: float = 0.0
  vLeadK: float = 0.0
  vRel: float = 0.0


@dataclass
class MockLaneLine:
  x: list[float] = field(default_factory=lambda: list(np.linspace(0, 100, 33)))
  y: list[float] = field(default_factory=lambda: [1.85] * 33)


@dataclass
class MockPosition:
  x: list[float] = field(default_factory=lambda: list(np.linspace(0, 100, 33)))


@dataclass
class MockModelV2:
  position: MockPosition = field(default_factory=MockPosition)
  laneLines: list[MockLaneLine] = field(default_factory=list)


def make_model_with_lanes(width: float = 1.85, horizon: float = 100.0) -> MockModelV2:
  # modelV2 lane-line y uses positive-right convention; tracks use positive-left
  # (distant_lead.py reconciles via -track.yRel). Mock matches modelV2.
  m = MockModelV2()
  xs = list(np.linspace(0, horizon, 33))
  m.position.x = xs
  left = MockLaneLine(x=xs, y=[-width] * 33)
  right = MockLaneLine(x=xs, y=[ width] * 33)
  m.laneLines = [MockLaneLine(), left, right, MockLaneLine()]
  return m


def make_sm(v_cruise_kph: float = 100.0) -> MockSm:
  return MockSm(store={'carState': MockCarState(vCruise=v_cruise_kph)})


def make_rs(status: bool, dRel: float, vLead: float,
            aLeadK: float = 0.0, aLeadTau: float = 0.0,
            v_ego: float = 0.0) -> MockRadarState:
  rs = MockRadarState()
  rs.leadOne.status = status
  rs.leadOne.dRel = dRel
  rs.leadOne.vLead = vLead
  rs.leadOne.aLeadK = aLeadK
  rs.leadOne.aLeadTau = aLeadTau
  rs.leadOne.vRel = vLead - v_ego
  return rs


# ── Metric helpers ────────────────────────────────────────────────────────────

def jerk(series: list[float], dt: float = DT_MDL) -> float:
  if len(series) < 2:
    return 0.0
  return float(np.max(np.abs(np.diff(series)) / dt))


def reversals(series: list[float], min_delta: float = 0.02) -> int:
  if len(series) < 3:
    return 0
  d = np.diff(series)
  s = np.sign(d)
  count = 0
  for i in range(1, len(s)):
    if s[i] * s[i - 1] < 0 and abs(d[i]) > min_delta:
      count += 1
  return count


def settled_time(series: list[float], target: float, tol: float, dt: float = DT_MDL) -> float:
  arr = np.asarray(series)
  for i in range(len(arr) - 1, -1, -1):
    if abs(arr[i] - target) > tol:
      return (i + 1) * dt
  return 0.0


# ── Sim runners ───────────────────────────────────────────────────────────────

def run_envelope_scenario(name: str, duration_s: float,
                          gen: Callable[[int], tuple[float, MockLead | None]],
                          checks: dict[str, tuple[Callable[[float], bool], str]],
                          v_cruise_kph: float = 100.0,
                          personality_long: int | None = None,
                          personality_accel: int | None = None) -> bool:
  from openpilot.sunnypilot.selfdrive.controls.lib.accel_personality.accel_controller import (
    AccelPersonalityController, AccelPersonality
  )
  from openpilot.sunnypilot.selfdrive.controls.lib.dynamic_personality.dynamic_follow import (
    FollowDistanceController, LongPersonality
  )

  ac = AccelPersonalityController()
  ac.set_enabled(True)
  if personality_accel is None:
    personality_accel = AccelPersonality.normal
  ac.set_accel_personality(personality_accel)
  df = FollowDistanceController()
  df.set_enabled(True)
  if personality_long is None:
    personality_long = LongPersonality.standard
  df.set_personality(personality_long)
  sm = make_sm(v_cruise_kph)

  a_min_h, a_max_h, tf_h, v_h = [], [], [], []
  n = int(duration_s / DT_MDL)
  for f in range(n):
    v_ego, lead = gen(f)
    rs = make_rs(
      status=bool(lead and lead.status),
      dRel=lead.dRel if lead else 0.0,
      vLead=lead.vLead if lead else 0.0,
      aLeadK=lead.aLeadK if lead else 0.0,
      aLeadTau=lead.aLeadTau if lead else 0.0,
      v_ego=v_ego,
    )
    ac.update(sm)
    df.update()
    a_min, a_max = ac.get_accel_limits(v_ego)
    tf = df.get_follow_distance_multiplier(v_ego, rs)
    a_min_h.append(a_min)
    a_max_h.append(a_max)
    tf_h.append(tf)
    v_h.append(v_ego)

  # Rise time: frames from baseline to peak (proxy for cut-in / brake response speed)
  baseline_tf = tf_h[0]
  peak_tf = max(tf_h)
  rise_threshold = baseline_tf + 0.5 * (peak_tf - baseline_tf)
  rise_frame = next((i for i, v in enumerate(tf_h) if v >= rise_threshold), len(tf_h) - 1)
  rise_time_s = rise_frame * DT_MDL

  metrics = {
    'a_min_jerk': jerk(a_min_h),
    'a_max_jerk': jerk(a_max_h),
    't_follow_jerk': jerk(tf_h),
    't_follow_reversals': float(reversals(tf_h)),
    'a_min_floor': float(min(a_min_h)),
    'a_max_ceil': float(max(a_max_h)),
    't_follow_min': float(min(tf_h)),
    't_follow_max': float(max(tf_h)),
    't_follow_settle_s': settled_time(tf_h, tf_h[-1], 0.05),
    't_follow_rise_s': rise_time_s,
  }

  print(f"\n[{name}]")
  for k, v in metrics.items():
    print(f"  {k:24s} = {v:.4f}")
  ok_all = True
  for key, (pred, doc) in checks.items():
    val = metrics[key]
    ok = pred(val)
    if not ok:
      ok_all = False
    tag = 'PASS' if ok else 'FAIL'
    print(f"  [{tag}] {key} {doc}")
  return ok_all


def run_distant_lead_scenario(name: str, duration_s: float,
                              gen: Callable[[int], tuple[float, dict[int, MockTrack], MockModelV2, float, bool]],
                              expect_track_id: int | None,
                              expect_within_s: float = 1.0) -> bool:
  from openpilot.sunnypilot.selfdrive.controls.lib.distant_lead import DistantLeadDetector

  det = DistantLeadDetector()
  n = int(duration_s / DT_MDL)
  detected_at: float | None = None
  detected_id: int | None = None
  for f in range(n):
    v_ego, tracks, model_data, lead_one_drel, lead_one_status = gen(f)
    chosen = det.detect(tracks, model_data, v_ego, lead_one_drel, lead_one_status)
    if chosen is not None and detected_at is None:
      detected_at = f * DT_MDL
      detected_id = chosen.trackId
  print(f"\n[{name}]")
  print(f"  detected_at_s = {detected_at}")
  print(f"  detected_id   = {detected_id}")
  ok = True
  if expect_track_id is None:
    if detected_id is not None:
      print(f"  [FAIL] expected no detection, got id={detected_id}")
      ok = False
    else:
      print("  [PASS] no detection (as expected)")
  else:
    if detected_id != expect_track_id:
      print(f"  [FAIL] expected id={expect_track_id}, got {detected_id}")
      ok = False
    elif detected_at is None or detected_at > expect_within_s:
      print(f"  [FAIL] detected too late: {detected_at}s > {expect_within_s}s")
      ok = False
    else:
      print(f"  [PASS] id={detected_id} at {detected_at:.2f}s")
  return ok


# ── Scenarios ─────────────────────────────────────────────────────────────────

def scn_steady_follow():
  def g(f):
    v_ego = 25.0
    lead = MockLead(status=True, dRel=v_ego * 1.4 + 6.0, vLead=25.0, aLeadK=0.0, aLeadTau=0.0)
    return v_ego, lead
  return g


def scn_brake_release():
  def g(f):
    t = f * DT_MDL
    v_ego = 25.0
    if t < 1.0:
      a_lead, v_lead = 0.0, 25.0
    elif t < 3.0:
      a_lead = -2.0
      v_lead = max(15.0, 25.0 - 2.0 * (t - 1.0))
    else:
      a_lead, v_lead = 0.0, 21.0
    d_rel = max(5.0, 30.0 + (v_lead - v_ego) * (t - 1.0 if t > 1.0 else 0))
    tau = 1.5 if a_lead < -0.3 else 0.0
    lead = MockLead(status=True, dRel=d_rel, vLead=v_lead, aLeadK=a_lead, aLeadTau=tau)
    return v_ego, lead
  return g


def scn_cutin():
  def g(f):
    t = f * DT_MDL
    v_ego = 25.0
    if t < 1.0:
      return v_ego, MockLead(status=False)
    return v_ego, MockLead(status=True, dRel=15.0, vLead=23.0, aLeadK=0.0, aLeadTau=0.0)
  return g


def scn_micro_brake_stop_and_go():
  def g(f):
    t = f * DT_MDL
    v_ego = 5.0
    phase = (t // 2) % 2
    if phase == 0:
      a_lead, v_lead = -1.0, 4.0
    else:
      a_lead, v_lead = 0.5, 6.0
    lead = MockLead(status=True, dRel=12.0, vLead=v_lead, aLeadK=a_lead, aLeadTau=1.0 if a_lead < -0.3 else 0.0)
    return v_ego, lead
  return g


def scn_cruise_approach_no_lead():
  def g(f):
    v_ego = 22.0
    return v_ego, MockLead(status=False)
  return g


def scn_hard_lead_decel_advisor():
  """Advisor's scenario: ego 25 m/s, lead 30m, lead drops 0→-3 m/s²"""
  def g(f):
    t = f * DT_MDL
    v_ego = 25.0
    if t < 1.0:
      a_lead, v_lead = 0.0, 25.0
    else:
      a_lead = -3.0
      v_lead = max(0.0, 25.0 - 3.0 * (t - 1.0))
    d_rel = max(2.0, 30.0 + (v_lead - v_ego) * (t - 1.0 if t > 1.0 else 0))
    tau = 1.5 if a_lead < -0.3 else 0.0
    lead = MockLead(status=True, dRel=d_rel, vLead=v_lead, aLeadK=a_lead, aLeadTau=tau)
    return v_ego, lead
  return g


def scn_radar_noise_steady():
  """Steady follow with realistic radar noise: vLead ±0.5 m/s, aLeadK ±0.3 m/s².
  Tests whether modifiers fire on noise alone (would cause rubber band)."""
  rng = np.random.default_rng(42)

  def g(f):
    v_ego = 25.0
    v_lead_noise = float(rng.normal(0.0, 0.4))
    a_lead_noise = float(rng.normal(0.0, 0.25))
    lead = MockLead(
      status=True,
      dRel=35.0 + float(rng.normal(0.0, 0.3)),
      vLead=25.0 + v_lead_noise,
      aLeadK=a_lead_noise,
      aLeadTau=0.0,
    )
    return v_ego, lead
  return g


def scn_v_ego_sweep():
  """Linear v_ego ramp 0→30 m/s over 30s, no lead. Exercises a_min/a_max curves."""
  def g(f):
    t = f * DT_MDL
    v_ego = min(30.0, t)
    return v_ego, MockLead(status=False)
  return g


def scn_coast_deadband_at_cruise():
  """v_ego held at v_cruise (27.78 m/s = 100 km/h). Bounds should compress."""
  def g(f):
    v_ego = 27.78
    return v_ego, MockLead(status=False)
  return g


def scn_lead_flicker():
  """leadOne status flips on/off every other frame. Grace must hold t_follow."""
  def g(f):
    v_ego = 22.0
    status = (f % 2 == 0)
    return v_ego, MockLead(status=status, dRel=30.0, vLead=22.0, aLeadK=0.0)
  return g


def scn_highway_hard_cutin():
  """Ego 30 m/s, lead appears at 8m vRel=-5 m/s — worst-case cut-in."""
  def g(f):
    t = f * DT_MDL
    v_ego = 30.0
    if t < 0.5:
      return v_ego, MockLead(status=False)
    return v_ego, MockLead(status=True, dRel=8.0, vLead=25.0, aLeadK=-1.0, aLeadTau=1.5)
  return g


def scn_distant_lead_in_lane():
  """Track at 50m in lane, leadOne at 100m (or absent)"""
  model = make_model_with_lanes(width=1.85, horizon=120.0)

  def g(f):
    v_ego = 20.0
    track = MockTrack(trackId=42, dRel=50.0, yRel=0.2, vLead=18.0, vLeadK=18.0, vRel=-2.0)
    tracks = {42: track}
    return v_ego, tracks, model, 100.0, True
  return g


def scn_distant_lead_out_of_lane():
  """Track at 50m but yRel=2.5m (out of lane) — should NOT promote"""
  model = make_model_with_lanes(width=1.85, horizon=120.0)

  def g(f):
    v_ego = 20.0
    track = MockTrack(trackId=99, dRel=50.0, yRel=2.5, vLead=18.0, vLeadK=18.0, vRel=-2.0)
    tracks = {99: track}
    return v_ego, tracks, model, 100.0, True
  return g


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> int:
  failures = 0

  if True:
    # Steady follow — no oscillation, no drift
    if not run_envelope_scenario(
      'steady_follow', 30.0, scn_steady_follow(),
      checks={
        't_follow_jerk':      (lambda x: x < 0.20,  '< 0.20 s/s²'),
        'a_min_jerk':         (lambda x: x < 1.50,  '< 1.50 m/s³'),
        'a_max_jerk':         (lambda x: x < 1.50,  '< 1.50 m/s³'),
        't_follow_reversals': (lambda x: x <= 4.0,  '≤ 4 reversals (no rubber band)'),
      },
    ):
      failures += 1

    # Brake → release — no rubber band on recovery
    if not run_envelope_scenario(
      'brake_release', 8.0, scn_brake_release(),
      checks={
        't_follow_max':       (lambda x: x > 1.55,  'rises above base on brake'),
        't_follow_jerk':      (lambda x: x < 1.0,   '< 1.0 s/s²'),
        't_follow_reversals': (lambda x: x <= 5.0,  '≤ 5 reversals'),
      },
    ):
      failures += 1

    # Cut-in — quick response, capped
    if not run_envelope_scenario(
      'cutin', 6.0, scn_cutin(),
      checks={
        't_follow_max':       (lambda x: 1.55 < x < 2.50, 'rises on cut-in & capped at ceiling'),
        't_follow_jerk':      (lambda x: x < 1.5,         '< 1.5 s/s²'),
      },
    ):
      failures += 1

    # Stop-and-go — no gas/brake oscillation, t_follow stable
    if not run_envelope_scenario(
      'micro_brake_stop_n_go', 12.0, scn_micro_brake_stop_and_go(),
      checks={
        't_follow_jerk':      (lambda x: x < 1.0,   '< 1.0 s/s²'),
        't_follow_reversals': (lambda x: x <= 8.0,  '≤ 8 reversals'),
        'a_min_jerk':         (lambda x: x < 1.5,   '< 1.5 m/s³'),
      },
    ):
      failures += 1

    # Cruise approach (no lead) — smooth envelope
    if not run_envelope_scenario(
      'cruise_approach', 8.0, scn_cruise_approach_no_lead(),
      checks={
        'a_min_jerk':  (lambda x: x < 1.0, '< 1.0 m/s³'),
        'a_max_jerk':  (lambda x: x < 1.0, '< 1.0 m/s³'),
      },
    ):
      failures += 1

    # Advisor's hard-lead-decel scenario
    if not run_envelope_scenario(
      'hard_lead_decel_advisor', 6.0, scn_hard_lead_decel_advisor(),
      checks={
        't_follow_max':  (lambda x: x > 1.55, 't_follow rises'),
        't_follow_jerk': (lambda x: x < 1.5,  '< 1.5 s/s²'),
        'a_min_jerk':    (lambda x: x < 2.0,  '< 2.0 m/s³ envelope tighten'),
      },
    ):
      failures += 1

    # Radar noise on steady follow — modifiers should not ratchet t_follow up
    if not run_envelope_scenario(
      'radar_noise_steady', 30.0, scn_radar_noise_steady(),
      checks={
        # Base 1.55 + ≤0.15s drift acceptable (ε ≈ 0.10s with floor + deadbands)
        't_follow_max':       (lambda x: x < 1.70, 't_follow stays close to base under noise'),
        't_follow_reversals': (lambda x: x < 20,   '< 20 reversals over 30s'),
      },
    ):
      failures += 1

    # Variable v_ego sweep — a_min/a_max smooth across speeds
    if not run_envelope_scenario(
      'v_ego_sweep_no_lead', 30.0, scn_v_ego_sweep(),
      checks={
        'a_min_jerk':  (lambda x: x < 1.5, '< 1.5 m/s³ across speed sweep'),
        'a_max_jerk':  (lambda x: x < 1.0, '< 1.0 m/s³ across speed sweep'),
      },
    ):
      failures += 1

    # Coast deadband activation — bounds compress near v_cruise
    if not run_envelope_scenario(
      'coast_deadband', 4.0, scn_coast_deadband_at_cruise(),
      v_cruise_kph=100.0,
      checks={
        'a_min_floor': (lambda x: x > -0.3, 'a_min compresses to coast drag near cruise'),
        'a_max_ceil':  (lambda x: x < 0.10, 'a_max compresses to ~0.05 near cruise'),
      },
    ):
      failures += 1

    # Lead flicker — grace must hold t_follow stable
    if not run_envelope_scenario(
      'lead_flicker', 4.0, scn_lead_flicker(),
      checks={
        't_follow_jerk':      (lambda x: x < 0.5, '< 0.5 s/s² (grace holds through flicker)'),
        't_follow_reversals': (lambda x: x < 8,   '< 8 reversals (no rubber band)'),
      },
    ):
      failures += 1

    # Highway hard cut-in — worst-case. Rise time critical (must not be delayed).
    if not run_envelope_scenario(
      'highway_hard_cutin', 6.0, scn_highway_hard_cutin(),
      v_cruise_kph=110.0,
      checks={
        't_follow_max':    (lambda x: x > 1.65, 't_follow rises sharply on cut-in'),
        't_follow_jerk':   (lambda x: x < 1.5,  '< 1.5 s/s²'),
        'a_min_jerk':      (lambda x: x < 4.0,  '< 4 m/s³ envelope tighten (bounded by tighten rate)'),
        # Includes 0.5s pre-cutin baseline + chase. Real chase budget ~0.55s.
        't_follow_rise_s': (lambda x: x < 1.5,  'rise to half-peak < 1.5s (no smoothing delay)'),
      },
    ):
      failures += 1

    # Distant lead — in-lane track promoted
    if not run_distant_lead_scenario(
      'distant_lead_in_lane', 2.0, scn_distant_lead_in_lane(),
      expect_track_id=42, expect_within_s=1.0,
    ):
      failures += 1

    # Distant lead — out-of-lane rejected
    if not run_distant_lead_scenario(
      'distant_lead_out_of_lane_reject', 2.0, scn_distant_lead_out_of_lane(),
      expect_track_id=None,
    ):
      failures += 1

  print(f"\n=== {'ALL PASS' if failures == 0 else f'{failures} SCENARIO(S) FAILED'} ===")
  return 0 if failures == 0 else 1


if __name__ == '__main__':
  sys.exit(main())
