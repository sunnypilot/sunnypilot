#!/usr/bin/env python3
"""
Longitudinal-control post-drive analysis.

Pulls a comma route via tools.lib.LogReader, extracts ego accel + lead state +
controls plan, and reports the metrics that matter for the smoothness goal:
peak felt jerk, hard-brake events, gas/brake zero-crossings (rubber band),
lead status flicker, late-brake detections.

Run:
  python3 tools/scripts/analyze_long_route.py <route> [<route> ...]

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


def load_series(route: str):
  ts: dict[str, list[tuple[float, dict]]] = defaultdict(list)
  for msg in LogReader(route):
    t = msg.logMonoTime / 1e9
    w = msg.which()
    if w == 'carState':
      cs = msg.carState
      ts['carState'].append((t, {'vEgo': cs.vEgo, 'aEgo': cs.aEgo,
                                 'gasPressed': cs.gasPressed, 'brakePressed': cs.brakePressed,
                                 'cruiseEnabled': cs.cruiseState.enabled}))
    elif w == 'carControl':
      cc = msg.carControl
      ts['carControl'].append((t, {'accel': cc.actuators.accel,
                                   'longActive': cc.longActive}))
    elif w == 'radarState':
      lo = msg.radarState.leadOne
      ts['radarState'].append((t, {'status': lo.status, 'dRel': lo.dRel,
                                   'vLead': lo.vLead, 'vRel': lo.vRel,
                                   'aLeadK': lo.aLeadK, 'aLeadTau': lo.aLeadTau}))
    elif w == 'longitudinalPlan':
      lp = msg.longitudinalPlan
      ts['longitudinalPlan'].append((t, {'aTarget': lp.aTarget}))
  return ts


def to_arrays(rows):
  if not rows:
    return None
  ts = np.array([r[0] for r in rows])
  ts -= ts[0]
  keys = rows[0][1].keys()
  data = {k: np.array([float(r[1][k]) for r in rows]) for k in keys}
  data['t'] = ts
  return data


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


def report(name: str, ts: dict):
  cs = to_arrays(ts.get('carState', []))
  ctl = to_arrays(ts.get('carControl', []))
  rs = to_arrays(ts.get('radarState', []))
  lp = to_arrays(ts.get('longitudinalPlan', []))

  print(f"\n══════ {name} ══════")
  if cs is None:
    print("  no carState — empty route")
    return

  duration_s = float(cs['t'][-1])
  engaged = cs['cruiseEnabled'].astype(bool)
  v = cs['vEgo']
  a = cs['aEgo']
  j = jerk_series(a, cs['t'])

  print(f"  duration:        {duration_s:.1f} s")
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
    print(f"    |jerk| p95:         {float(np.percentile(np.abs(j_m), 95)):.2f} m/s³")
    print(f"    |jerk| max:         {float(np.max(np.abs(j_m))):.2f} m/s³"
          + (" ⚠" if float(np.max(np.abs(j_m))) > PEAK_JERK_THRESHOLD else ""))
    print(f"    hard brake events:  {len(hard_clusters)} (thresh {HARD_BRAKE_THRESHOLD} m/s²)")
    if tag == 'all':
      for s, e in hard_clusters[:8]:
        idx = np.where((cs['t'] >= s) & (cs['t'] <= e))[0]
        if idx.size:
          worst = idx[np.argmin(a[idx])]
          print(f"      t={cs['t'][worst]:7.1f}s  aEgo={a[worst]:+.2f} m/s²  v={v[worst]:.1f} m/s")
    print(f"    rubber-band cross:  {count_zero_crossings(a_m, ZERO_CROSS_BAND)}"
          + f" zero-crossings in ±{ZERO_CROSS_BAND} band")

  if rs is not None:
    flicker = int(np.sum(np.diff(rs['status'].astype(int)) != 0))
    print(f"\n  lead status flips:   {flicker} over {duration_s:.0f}s "
          f"({flicker / max(duration_s, 1):.2f}/s)")
    if engaged.any():
      late = detect_late_brakes(rs, cs, ctl)
      late_ts = np.array([e[0] for e in late])
      late_clusters = cluster_events(late_ts)
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

  if lp is not None:
    lp_a = lp['aTarget']
    print(f"  longPlan |jerk| p95: {float(np.percentile(np.abs(jerk_series(lp_a, lp['t'])), 95)):.2f} m/s³")


def drill_event(name: str, ts: dict, event_t: float, window_s: float = 5.0):
  cs = to_arrays(ts.get('carState', []))
  cc = to_arrays(ts.get('carControl', []))
  rs = to_arrays(ts.get('radarState', []))
  lp = to_arrays(ts.get('longitudinalPlan', []))
  if cs is None:
    print(f"\n══════ DRILL {name} @ t={event_t:.1f}s ══════ no carState")
    return

  origin = cs['t'][0] if cs['t'].size else 0.0
  abs_event = event_t

  def slice_in(arr_t):
    return np.where((arr_t >= abs_event - window_s) & (arr_t <= abs_event + window_s))[0]

  cs_idx = slice_in(cs['t']) if cs is not None else np.array([], dtype=int)
  if not cs_idx.size:
    print(f"\n══════ DRILL @ t={event_t:.1f}s ══════ no data in window")
    return

  print(f"\n══════ DRILL @ t={event_t:.1f}s  (±{window_s:.0f}s) ══════")
  print(f"  cols: rel_t  v_ego  aEgo  | lead.st dRel vRel vLead aLeadK aLeadTau | aTgtPlan aCmd  | engaged")

  step = max(1, len(cs_idx) // 50)
  for i in cs_idx[::step]:
    t_rel = cs['t'][i] - abs_event
    line = f"  {t_rel:+5.2f}  {cs['vEgo'][i]:5.2f}  {cs['aEgo'][i]:+5.2f}  | "
    if rs is not None:
      j = np.searchsorted(rs['t'], cs['t'][i])
      j = min(j, len(rs['t']) - 1)
      line += (f"{int(rs['status'][j]):d}      {rs['dRel'][j]:5.1f} {rs['vRel'][j]:+5.2f} "
               f"{rs['vLead'][j]:5.2f} {rs['aLeadK'][j]:+5.2f} {rs['aLeadTau'][j]:4.2f} | ")
    else:
      line += "—                                       | "
    if lp is not None and lp['t'].size:
      k = np.searchsorted(lp['t'], cs['t'][i])
      k = min(k, len(lp['t']) - 1)
      line += f"{lp['aTarget'][k]:+5.2f}    "
    else:
      line += "—       "
    if cc is not None and cc['t'].size:
      k = np.searchsorted(cc['t'], cs['t'][i])
      k = min(k, len(cc['t']) - 1)
      line += f"{cc['accel'][k]:+5.2f}  | "
    else:
      line += "—     | "
    line += f"{int(cs['cruiseEnabled'][i]):d}"
    print(line)

  if rs is not None:
    flips = int(np.sum(np.diff(rs['status'][slice_in(rs['t'])].astype(int)) != 0))
    print(f"  -- lead status flips in window: {flips}")


def main() -> int:
  p = argparse.ArgumentParser()
  p.add_argument('routes', nargs='+', help='comma route IDs (e.g. abc.../00000099--xyz)')
  p.add_argument('--event', type=float, action='append', default=[],
                 help='drill into event at this absolute t (sec). repeat for multiple')
  p.add_argument('--window', type=float, default=5.0, help='drill window (sec) ±')
  args = p.parse_args()

  for r in args.routes:
    try:
      ts = load_series(r)
      report(r, ts)
      for ev_t in args.event:
        drill_event(r, ts, ev_t, args.window)
    except Exception as e:
      print(f"\n══════ {r} ══════")
      print(f"  ERROR: {type(e).__name__}: {e}")
  return 0


if __name__ == '__main__':
  sys.exit(main())
