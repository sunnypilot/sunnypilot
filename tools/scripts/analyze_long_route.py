#!/usr/bin/env python3
"""
Longitudinal-control post-drive analysis.

Pulls a comma route via tools.lib.LogReader, extracts ego accel + lead state +
controls plan, and reports the metrics that matter for the smoothness goal:
peak felt jerk, hard-brake events, gas/brake zero-crossings (rubber band),
lead status flicker, late-brake detections.

Reads `longitudinalPlanSP` when present (fork plan with SLA/DEC/SCC overrides
applied) and falls back to upstream `longitudinalPlan` otherwise.

Run:
  python3 tools/scripts/analyze_long_route.py <route> [<route> ...]
  python3 tools/scripts/analyze_long_route.py --budget <route>   # exit nonzero on violation

Auth first if private:
  python3 tools/lib/auth.py
"""
import argparse
import sys
from collections import defaultdict

import numpy as np

from openpilot.tools.lib.logreader import LogReader


HARD_BRAKE_THRESHOLD = -2.0   # m/s²
PEAK_JERK_THRESHOLD = 1.5     # m/s³ flag threshold
ZERO_CROSS_BAND = 0.20        # m/s² ± band for rubber-band detection
LATE_BRAKE_LAG_S = 0.6        # s — ego decel lag behind lead decel

CITY_V_MAX = 12.0             # m/s — stop-n-go regime
HIGHWAY_V_MIN = 18.0          # m/s

# Per-minute budgets used by --budget. Conservative starting values; tighten
# as tuning improves. Any single violation across reported routes => exit 1.
BUDGET = {
  'hard_brakes_per_min':    0.5,
  'jerk_p95':               1.5,   # m/s³
  'late_brake_clusters_per_min': 0.1,
  'rubber_band_per_min':    2.0,
  'lead_flips_per_min':     6.0,
}


def load_series(route: str):
  ts: dict[str, list[tuple[float, dict]]] = defaultdict(list)
  for msg in LogReader(route):
    t = msg.logMonoTime / 1e9
    w = msg.which()
    if w == 'carState':
      cs = msg.carState
      ts['carState'].append((t, {'vEgo': cs.vEgo, 'aEgo': cs.aEgo,
                                 'gasPressed': cs.gasPressed, 'brakePressed': cs.brakePressed,
                                 'cruiseEnabled': cs.cruiseState.enabled,
                                 'standstill': cs.standstill,
                                 'cruiseStandstill': cs.cruiseState.standstill}))
    elif w == 'carControl':
      cc = msg.carControl
      lcs_raw = cc.actuators.longControlState
      lcs_map = {'off': 0, 'pid': 1, 'stopping': 2, 'starting': 3}
      lcs_int = lcs_map.get(str(lcs_raw), -1)
      ts['carControl'].append((t, {'accel': cc.actuators.accel,
                                   'longActive': cc.longActive,
                                   'longControlState': lcs_int}))
    elif w == 'radarState':
      lo = msg.radarState.leadOne
      ts['radarState'].append((t, {'status': lo.status, 'dRel': lo.dRel,
                                   'vLead': lo.vLead, 'vRel': lo.vRel,
                                   'aLeadK': lo.aLeadK, 'aLeadTau': lo.aLeadTau}))
    elif w == 'longitudinalPlan':
      lp = msg.longitudinalPlan
      ts['longitudinalPlan'].append((t, {'aTarget': lp.aTarget,
                                         'shouldStop': lp.shouldStop}))
    elif w == 'longitudinalPlanSP':
      lp = msg.longitudinalPlanSP
      # SP plan has aTarget but no shouldStop — controller reads upstream
      # longitudinalPlan.shouldStop; don't fabricate a shouldStop column here.
      ts['longitudinalPlanSP'].append((t, {'aTarget': lp.aTarget}))
  return ts


def to_arrays(rows, t0: float | None = None):
  """Build aligned numpy arrays for a topic. If t0 is given, all topics share
  the same time origin so cross-topic plots align (carState, carControl,
  longitudinalPlan can have different first-msg times)."""
  if not rows:
    return None
  ts = np.array([r[0] for r in rows])
  ts -= (t0 if t0 is not None else ts[0])
  keys = rows[0][1].keys()
  data = {k: np.array([float(r[1][k]) for r in rows]) for k in keys}
  data['t'] = ts
  return data


def common_t0(ts: dict) -> float:
  """Pick the earliest first-msg time across all topics so they share a clock."""
  origins = [rows[0][0] for rows in ts.values() if rows]
  return min(origins) if origins else 0.0


def regime_mask(v_ego: np.ndarray) -> dict[str, np.ndarray]:
  return {
    'city':    v_ego < CITY_V_MAX,
    'highway': v_ego >= HIGHWAY_V_MIN,
    'all':     np.ones_like(v_ego, dtype=bool),
  }


def jerk_series(a: np.ndarray, t: np.ndarray, glitch_clip: float = 12.0) -> np.ndarray:
  if len(a) < 2:
    return np.zeros_like(a)
  dt = np.diff(t)
  dt[dt <= 0] = np.median(dt[dt > 0]) if np.any(dt > 0) else 0.05
  j = np.diff(a) / dt
  j = np.clip(j, -glitch_clip, glitch_clip)
  return np.concatenate([[0.0], j])


def count_zero_crossings(a: np.ndarray, band: float) -> int:
  s = np.sign(a)
  s[np.abs(a) < band] = 0
  s_nz = s[s != 0]
  if len(s_nz) < 2:
    return 0
  return int(np.sum(np.abs(np.diff(s_nz)) > 1.5))


def cluster_events(times: np.ndarray, gap_s: float = 5.0) -> list[tuple[float, float]]:
  if len(times) == 0:
    return []
  out = [(times[0], times[0])]
  for t in times[1:]:
    s, e = out[-1]
    if t - e <= gap_s:
      out[-1] = (s, t)
    else:
      out.append((t, t))
  return out


def detect_late_brakes(rs, cs, controls):
  """Flag only when lead is close + braking hard + ego unresponsive.
  Avoids false positives where lead is far enough that no brake is required."""
  if rs is None or controls is None:
    return []
  cs_t = cs['t']
  cs_a = cs['aEgo']
  cs_v = cs['vEgo']
  rs_t = rs['t']
  rs_a = rs['aLeadK']
  rs_drel = rs['dRel']
  rs_status = rs['status'].astype(bool)
  late = []
  for i in range(1, len(rs_t)):
    if not rs_status[i] or rs_a[i] > -2.0:
      continue
    j_v = np.searchsorted(cs_t, rs_t[i])
    j_v = min(j_v, len(cs_v) - 1)
    v_ego = max(cs_v[j_v], 1.0)
    t_hw = rs_drel[i] / v_ego
    if t_hw > 4.0:
      continue
    j_ego = min(np.searchsorted(cs_t, rs_t[i] + LATE_BRAKE_LAG_S), len(cs_a) - 1)
    if cs_a[j_ego] > -0.3:
      late.append((rs_t[i], rs_a[i], cs_a[j_ego]))
  return late


def report(name: str, ts: dict) -> dict:
  """Print the route summary; return per-minute metrics for budget gating."""
  t0 = common_t0(ts)
  cs = to_arrays(ts.get('carState', []), t0)
  ctl = to_arrays(ts.get('carControl', []), t0)
  rs = to_arrays(ts.get('radarState', []), t0)
  # Prefer fork plan (SLA/DEC/SCC overrides applied) when present
  lp_sp = to_arrays(ts.get('longitudinalPlanSP', []), t0)
  lp_up = to_arrays(ts.get('longitudinalPlan', []), t0)
  lp = lp_sp if lp_sp is not None else lp_up
  plan_source = 'longitudinalPlanSP' if lp_sp is not None else ('longitudinalPlan' if lp_up is not None else 'none')

  metrics: dict[str, float] = {
    'duration_s': 0.0,
    'hard_brakes': 0,
    'jerk_p95': 0.0,
    'late_brake_clusters': 0,
    'rubber_band': 0,
    'lead_flips': 0,
  }

  print(f"\n══════ {name} ══════")
  if cs is None:
    print("  no carState — empty route")
    return metrics

  duration_s = float(cs['t'][-1])
  metrics['duration_s'] = duration_s
  engaged = cs['cruiseEnabled'].astype(bool)
  v = cs['vEgo']
  a = cs['aEgo']
  j = jerk_series(a, cs['t'])

  print(f"  duration:        {duration_s:.1f} s")
  print(f"  plan source:     {plan_source}")
  print(f"  engaged frac:    {float(np.mean(engaged)):.2%}")
  print(f"  v_ego mean:      {float(np.mean(v[engaged])) if engaged.any() else 0:.2f} m/s")

  regimes = regime_mask(v)
  for tag in ('all', 'city', 'highway'):
    mask = regimes[tag] & engaged
    if mask.sum() < 10:
      continue
    a_m = a[mask]
    j_m = j[mask]
    hard_idx = np.where(a_m < HARD_BRAKE_THRESHOLD)[0]
    hard_t = cs['t'][mask][hard_idx] if hard_idx.size else np.array([])
    hard_clusters = cluster_events(hard_t)
    print(f"\n  -- regime: {tag} ({mask.sum()*0.01:.0f}s engaged) --")
    print(f"    aEgo  range:        {float(np.min(a_m)):+.2f} .. {float(np.max(a_m)):+.2f} m/s²")
    print(f"    aEgo  p95/p05:      {float(np.percentile(a_m, 95)):+.2f} / {float(np.percentile(a_m, 5)):+.2f} m/s²")
    j_p95 = float(np.percentile(np.abs(j_m), 95))
    j_max = float(np.max(np.abs(j_m)))
    print(f"    |jerk| p95:         {j_p95:.2f} m/s³")
    print(f"    |jerk| max:         {j_max:.2f} m/s³"
          + (" ⚠" if j_max > PEAK_JERK_THRESHOLD else ""))
    print(f"    hard brake events:  {len(hard_clusters)} (thresh {HARD_BRAKE_THRESHOLD} m/s²)")
    if tag == 'all':
      metrics['hard_brakes'] = len(hard_clusters)
      metrics['jerk_p95'] = j_p95
      metrics['rubber_band'] = count_zero_crossings(a_m, ZERO_CROSS_BAND)
      for s, e in hard_clusters[:8]:
        idx = np.where((cs['t'] >= s) & (cs['t'] <= e))[0]
        if idx.size:
          worst = idx[np.argmin(a[idx])]
          print(f"      t={cs['t'][worst]:7.1f}s  aEgo={a[worst]:+.2f} m/s²  v={v[worst]:.1f} m/s")
    print(f"    rubber-band cross:  {count_zero_crossings(a_m, ZERO_CROSS_BAND)}"
          + f" zero-crossings in ±{ZERO_CROSS_BAND} band")

  if rs is not None:
    flicker = int(np.sum(np.diff(rs['status'].astype(int)) != 0))
    metrics['lead_flips'] = flicker
    print(f"\n  lead status flips:   {flicker} over {duration_s:.0f}s"
          + f" ({flicker / max(duration_s, 1):.2f}/s)")
    if engaged.any():
      late = detect_late_brakes(rs, cs, ctl)
      late_ts = np.array([e[0] for e in late])
      late_clusters = cluster_events(late_ts)
      metrics['late_brake_clusters'] = len(late_clusters)
      print(f"  late-brake clusters: {len(late_clusters)} (lead a < -1.5 m/s², ego >-0.5 m/s² {LATE_BRAKE_LAG_S}s later)")
      for s, e in late_clusters[:8]:
        relevant = [(t, la, ea) for t, la, ea in late if s <= t <= e]
        worst = min(relevant, key=lambda x: x[1])
        print(f"    t={worst[0]:7.1f}s  lead a={worst[1]:+.2f}  ego a@+{LATE_BRAKE_LAG_S}s={worst[2]:+.2f}")

  if ctl is not None and engaged.any():
    a_cmd = ctl['accel']
    active = ctl['longActive'].astype(bool)
    if active.sum() > 10:
      print(f"\n  carControl.accel |jerk| p95:  {float(np.percentile(np.abs(jerk_series(a_cmd[active], ctl['t'][active])), 95)):.2f} m/s³")
      print(f"  carControl.accel rubber band: {count_zero_crossings(a_cmd[active], ZERO_CROSS_BAND)} zero-crossings")

      # Planner-vs-actuator gap detector (commit 542c1f692b regression signature):
      # planner aTarget mild while actuator accel saturated for >=N consecutive frames.
      if lp is not None and lp['t'].size:
        idx = np.clip(np.searchsorted(lp['t'], ctl['t']), 0, len(lp['t']) - 1)
        plan_aligned = lp['aTarget'][idx]
        gap_mask = active & (ctl['accel'] < -3.0) & (plan_aligned > -1.0)
        if gap_mask.sum() > 5:
          print(f"  planner-vs-actuator gap: {int(gap_mask.sum())} frames where actuator<-3 m/s² while plan>-1")

  if lp is not None:
    lp_a = lp['aTarget']
    print(f"  longPlan |jerk| p95: {float(np.percentile(np.abs(jerk_series(lp_a, lp['t'])), 95)):.2f} m/s³ ({plan_source})")

  return metrics


def check_budget(name: str, metrics: dict, budget: dict) -> list[str]:
  """Return list of violation strings; empty list = pass."""
  dur = max(metrics['duration_s'], 1.0)
  per_min = lambda x: 60.0 * x / dur  # noqa: E731
  violations = []
  if per_min(metrics['hard_brakes']) > budget['hard_brakes_per_min']:
    violations.append(f"hard_brakes {per_min(metrics['hard_brakes']):.2f}/min > {budget['hard_brakes_per_min']}/min")
  if metrics['jerk_p95'] > budget['jerk_p95']:
    violations.append(f"jerk_p95 {metrics['jerk_p95']:.2f} > {budget['jerk_p95']} m/s³")
  if per_min(metrics['late_brake_clusters']) > budget['late_brake_clusters_per_min']:
    violations.append(f"late_brake_clusters {per_min(metrics['late_brake_clusters']):.2f}/min > {budget['late_brake_clusters_per_min']}/min")
  if per_min(metrics['rubber_band']) > budget['rubber_band_per_min']:
    violations.append(f"rubber_band {per_min(metrics['rubber_band']):.2f}/min > {budget['rubber_band_per_min']}/min")
  if per_min(metrics['lead_flips']) > budget['lead_flips_per_min']:
    violations.append(f"lead_flips {per_min(metrics['lead_flips']):.2f}/min > {budget['lead_flips_per_min']}/min")
  return violations


def drill_event(name: str, ts: dict, event_t: float, window_s: float = 5.0):
  # IMPORTANT: align all topics to a common t0 — different msgq services
  # publish their first message at different times (often >5s skew), so
  # if we don't share an origin, the aTarget/aCmd/cs columns will be misaligned.
  t0 = common_t0(ts)
  cs = to_arrays(ts.get('carState', []), t0)
  cc = to_arrays(ts.get('carControl', []), t0)
  rs = to_arrays(ts.get('radarState', []), t0)
  lp_sp = to_arrays(ts.get('longitudinalPlanSP', []), t0)
  lp_up = to_arrays(ts.get('longitudinalPlan', []), t0)
  # Controller uses upstream longitudinalPlan.shouldStop — show that, not SP's
  # (SP plan doesn't have shouldStop). Prefer upstream when both present so
  # aTarget+shouldStop+aCmd line up with what longcontrol.py actually sees.
  lp = lp_up if lp_up is not None else lp_sp
  if cs is None:
    print(f"\n══════ DRILL {name} @ t={event_t:.1f}s ══════ no carState")
    return

  abs_event = event_t

  def slice_in(arr_t):
    return np.where((arr_t >= abs_event - window_s) & (arr_t <= abs_event + window_s))[0]

  cs_idx = slice_in(cs['t']) if cs is not None else np.array([], dtype=int)
  if not cs_idx.size:
    print(f"\n══════ DRILL @ t={event_t:.1f}s ══════ no data in window")
    return

  print(f"\n══════ DRILL @ t={event_t:.1f}s  (±{window_s:.0f}s) ══════")
  print("  cols: rel_t  v_ego  aEgo  ss cSS  | lcs   aTgt  shStp aCmd  | lead.st dRel vRel vLead aLeadK aLeadTau | eng")
  print("    lcs: 0=off 1=pid 2=stopping 3=starting        ss=carState.standstill        cSS=cruiseState.standstill")

  # ~0.1s resolution: carState is 100 Hz, so step=10 ≈ 0.1s
  step = max(1, len(cs_idx) // max(int(window_s * 20), 50))  # ~20 rows/sec
  LCS_NAMES = {0: 'off', 1: 'pid ', 2: 'stop', 3: 'strt'}
  for i in cs_idx[::step]:
    t_rel = cs['t'][i] - abs_event
    ss = int(cs['standstill'][i]) if 'standstill' in cs else 0
    css = int(cs['cruiseStandstill'][i]) if 'cruiseStandstill' in cs else 0
    line = f"  {t_rel:+5.2f}  {cs['vEgo'][i]:5.2f}  {cs['aEgo'][i]:+5.2f}  {ss:d}  {css:d}  | "
    if cc is not None and cc['t'].size:
      k = np.searchsorted(cc['t'], cs['t'][i])
      k = min(k, len(cc['t']) - 1)
      lcs = int(cc['longControlState'][k]) if 'longControlState' in cc else 0
      line += f"{LCS_NAMES.get(lcs, '?'):4s} "
      if lp is not None and lp['t'].size:
        kp = np.searchsorted(lp['t'], cs['t'][i])
        kp = min(kp, len(lp['t']) - 1)
        ss_plan = int(lp['shouldStop'][kp]) if 'shouldStop' in lp else 0
        line += f"{lp['aTarget'][kp]:+5.2f}  {ss_plan:d}    "
      else:
        line += "—      —    "
      line += f"{cc['accel'][k]:+5.2f}  | "
    else:
      line += "—                          | "
    if rs is not None:
      j = np.searchsorted(rs['t'], cs['t'][i])
      j = min(j, len(rs['t']) - 1)
      line += (f"{int(rs['status'][j]):d}      {rs['dRel'][j]:5.1f} {rs['vRel'][j]:+5.2f}"
               + f" {rs['vLead'][j]:5.2f} {rs['aLeadK'][j]:+5.2f} {rs['aLeadTau'][j]:4.2f} | ")
    else:
      line += "—                                       | "
    line += f"{int(cs['cruiseEnabled'][i]):d}"
    print(line)

  if rs is not None:
    flips = int(np.sum(np.diff(rs['status'][slice_in(rs['t'])].astype(int)) != 0))
    print(f"  -- lead status flips in window: {flips}")

  # Transition detection: when does cruiseState.standstill, longControlState, and shouldStop flip?
  if 'cruiseStandstill' in cs:
    css_arr = cs['cruiseStandstill'][cs_idx].astype(int)
    css_t = cs['t'][cs_idx]
    diffs = np.where(np.diff(css_arr) != 0)[0]
    for d in diffs:
      print(f"  -- cruiseState.standstill {css_arr[d]}->{css_arr[d+1]} at t={css_t[d+1]:.2f}s "
            f"(rel {css_t[d+1]-abs_event:+.2f}s)")
  if 'standstill' in cs:
    ss_arr = cs['standstill'][cs_idx].astype(int)
    ss_t = cs['t'][cs_idx]
    diffs = np.where(np.diff(ss_arr) != 0)[0]
    for d in diffs:
      print(f"  -- carState.standstill   {ss_arr[d]}->{ss_arr[d+1]} at t={ss_t[d+1]:.2f}s "
            f"(rel {ss_t[d+1]-abs_event:+.2f}s)")
  if cc is not None and 'longControlState' in cc:
    cc_idx = slice_in(cc['t'])
    lcs_arr = cc['longControlState'][cc_idx].astype(int)
    cc_t = cc['t'][cc_idx]
    diffs = np.where(np.diff(lcs_arr) != 0)[0]
    for d in diffs:
      print(f"  -- longControlState     {LCS_NAMES.get(lcs_arr[d],'?')}->"
            f"{LCS_NAMES.get(lcs_arr[d+1],'?')} at t={cc_t[d+1]:.2f}s "
            f"(rel {cc_t[d+1]-abs_event:+.2f}s)")
  if lp is not None and 'shouldStop' in lp:
    lp_idx = slice_in(lp['t'])
    sh_arr = lp['shouldStop'][lp_idx].astype(int)
    lp_t = lp['t'][lp_idx]
    diffs = np.where(np.diff(sh_arr) != 0)[0]
    for d in diffs:
      print(f"  -- plan.shouldStop      {sh_arr[d]}->{sh_arr[d+1]} at t={lp_t[d+1]:.2f}s "
            f"(rel {lp_t[d+1]-abs_event:+.2f}s)")


def main() -> int:
  p = argparse.ArgumentParser()
  p.add_argument('routes', nargs='+', help='comma route IDs (e.g. abc.../00000099--xyz)')
  p.add_argument('--event', type=float, action='append', default=[],
                 help='drill into event at this absolute t (sec). repeat for multiple')
  p.add_argument('--window', type=float, default=5.0, help='drill window (sec) ±')
  p.add_argument('--budget', action='store_true',
                 help='exit nonzero on per-minute budget violation across reported routes')
  p.add_argument('--hard-brakes-per-min', type=float, default=BUDGET['hard_brakes_per_min'])
  p.add_argument('--jerk-p95', type=float, default=BUDGET['jerk_p95'])
  p.add_argument('--late-brake-clusters-per-min', type=float, default=BUDGET['late_brake_clusters_per_min'])
  p.add_argument('--rubber-band-per-min', type=float, default=BUDGET['rubber_band_per_min'])
  p.add_argument('--lead-flips-per-min', type=float, default=BUDGET['lead_flips_per_min'])
  args = p.parse_args()

  budget = {
    'hard_brakes_per_min': args.hard_brakes_per_min,
    'jerk_p95': args.jerk_p95,
    'late_brake_clusters_per_min': args.late_brake_clusters_per_min,
    'rubber_band_per_min': args.rubber_band_per_min,
    'lead_flips_per_min': args.lead_flips_per_min,
  }

  any_violation = False
  for r in args.routes:
    try:
      ts = load_series(r)
      metrics = report(r, ts)
      for ev_t in args.event:
        drill_event(r, ts, ev_t, args.window)
      if args.budget:
        v = check_budget(r, metrics, budget)
        if v:
          any_violation = True
          print(f"\n  ❌ BUDGET VIOLATION ({r}):")
          for line in v:
            print(f"     - {line}")
        else:
          print(f"\n  ✅ budget OK ({r})")
    except Exception as e:
      print(f"\n══════ {r} ══════")
      print(f"  ERROR: {type(e).__name__}: {e}")
      if args.budget:
        any_violation = True

  if args.budget and any_violation:
    print("\n>>> BUDGET FAILED — at least one route exceeded thresholds")
    return 1
  return 0


if __name__ == '__main__':
  sys.exit(main())
