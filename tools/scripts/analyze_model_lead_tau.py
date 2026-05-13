#!/usr/bin/env python3
"""
Premise check for "use model lead trajectory to bias aLeadTau".

For each frame where radar shows hard lead brake (aLeadK < BRAKE_A), look back
into the model's predicted lead trajectory (modelV2.leadsV3[0].a at t=2s, 4s)
to see if the model was already predicting the brake earlier.

Output is one row per detected brake event:
  t_event   aLeadK   best_model_a[1]_in_lookback   lead_time_s   verdict

Aggregate verdict at end: signal_score = fraction of events where model led
radar by >= LEAD_TIME_THRESHOLD with a[1]/a[2] <= MODEL_BRAKE_A.

Run:
  python3 tools/scripts/analyze_model_lead_tau.py <route> [<route> ...]

Auth first if private:
  python3 tools/lib/auth.py
"""
import argparse
import sys
from collections import defaultdict

import numpy as np

from openpilot.tools.lib.logreader import LogReader


BRAKE_A = -1.5            # m/s² — radar-confirmed lead braking event threshold
MODEL_BRAKE_A = -1.0      # m/s² — model considered predicting brake at horizon
LOOKBACK_S = 3.0          # how far back to search model predictions
LEAD_TIME_THRESHOLD = 0.5 # min seconds model must lead radar to count as signal
MIN_PROB = 0.5            # ignore low-prob model leads


def load_series(route: str):
  ts: dict[str, list] = defaultdict(list)
  for msg in LogReader(route):
    t = msg.logMonoTime / 1e9
    w = msg.which()
    if w == 'radarState':
      lo = msg.radarState.leadOne
      ts['radarState'].append((t, {
        'status': bool(lo.status),
        'aLeadK': float(lo.aLeadK),
        'aLeadTau': float(lo.aLeadTau),
        'dRel': float(lo.dRel),
      }))
    elif w == 'modelV2':
      if len(msg.modelV2.leadsV3) == 0:
        continue
      lead0 = msg.modelV2.leadsV3[0]
      ts['modelV2'].append((t, {
        'prob': float(lead0.prob),
        'a': np.array(lead0.a, dtype=np.float32),       # len 6 at [0,2,4,6,8,10] s
        'v': np.array(lead0.v, dtype=np.float32),
        'x': np.array(lead0.x, dtype=np.float32),
      }))
    elif w == 'carState':
      cs = msg.carState
      ts['carState'].append((t, {'vEgo': float(cs.vEgo), 'aEgo': float(cs.aEgo)}))
  return ts


def analyze(route: str, ts: dict) -> dict:
  rs = ts.get('radarState', [])
  md = ts.get('modelV2', [])
  cs = ts.get('carState', [])
  if not rs or not md:
    print(f"\n══════ {route} ══════ missing radarState or modelV2")
    return {'events': 0, 'led': 0, 'signal_score': 0.0}

  t0 = rs[0][0]
  rs_t = np.array([r[0] - t0 for r in rs])
  rs_a = np.array([r[1]['aLeadK'] for r in rs])
  rs_status = np.array([r[1]['status'] for r in rs])
  rs_drel = np.array([r[1]['dRel'] for r in rs])

  md_t = np.array([m[0] - t0 for m in md])
  md_a = np.stack([m[1]['a'] for m in md])      # (N, 6)
  md_prob = np.array([m[1]['prob'] for m in md])

  cs_t = np.array([c[0] - t0 for c in cs]) if cs else np.array([0.0])
  cs_v = np.array([c[1]['vEgo'] for c in cs]) if cs else np.array([0.0])

  events_raw = []
  for i in range(1, len(rs_t)):
    if not rs_status[i] or rs_a[i] > BRAKE_A:
      continue
    j_v = min(np.searchsorted(cs_t, rs_t[i]), len(cs_v) - 1)
    v_ego = max(cs_v[j_v], 1.0)
    if rs_drel[i] / v_ego > 4.0:
      continue
    events_raw.append((rs_t[i], rs_a[i], rs_drel[i]))

  events = []
  last_t = -1e9
  for ev_t, ev_a, ev_d in events_raw:
    if ev_t - last_t < 5.0:
      continue
    events.append((ev_t, ev_a, ev_d))
    last_t = ev_t

  led = 0
  lead_times: list[float] = []
  rows = []
  for ev_t, ev_a, ev_d in events:
    mask = (md_t >= ev_t - LOOKBACK_S) & (md_t < ev_t - 0.1) & (md_prob > MIN_PROB)
    if not np.any(mask):
      rows.append((ev_t, ev_a, np.nan, np.nan, np.nan, "no_model_window"))
      continue
    window_a = md_a[mask]              # (M, 6)
    window_t = md_t[mask]              # (M,)
    a1_min = float(window_a[:, 1].min())
    a2_min = float(window_a[:, 2].min())
    pred_idx_a1 = np.where(window_a[:, 1] <= MODEL_BRAKE_A)[0]
    pred_idx_a2 = np.where(window_a[:, 2] <= MODEL_BRAKE_A)[0]
    earliest_pred_window_t = np.inf
    if pred_idx_a1.size:
      earliest_pred_window_t = min(earliest_pred_window_t, float(window_t[pred_idx_a1[0]]))
    if pred_idx_a2.size:
      earliest_pred_window_t = min(earliest_pred_window_t, float(window_t[pred_idx_a2[0]]))
    lead_time = ev_t - earliest_pred_window_t if np.isfinite(earliest_pred_window_t) else 0.0
    if np.isfinite(earliest_pred_window_t) and (lead_time >= LEAD_TIME_THRESHOLD):
      led += 1
      lead_times.append(lead_time)
      verdict = "LED"
    else:
      verdict = "no_lead"
    rows.append((ev_t, ev_a, a1_min, a2_min, lead_time, verdict))

  print(f"\n══════ {route} ══════")
  print(f"  duration: {rs_t[-1]:.1f}s  events: {len(events)}  led: {led}  "
        f"signal_score: {led / max(len(events), 1):.2f}")
  if lead_times:
    lt = np.array(lead_times)
    print(f"  lead-time stats:  mean={lt.mean():.2f}s  median={np.median(lt):.2f}s  "
          f"p90={np.percentile(lt, 90):.2f}s  max={lt.max():.2f}s")
  print(f"  {'t_event':>8}  {'aLeadK':>7}  {'a[1]_min':>9}  {'a[2]_min':>9}  {'lead_s':>7}  verdict")
  for ev_t, ev_a, a1, a2, lt, verdict in rows:
    a1s = f"{a1:9.2f}" if not np.isnan(a1) else "      n/a"
    a2s = f"{a2:9.2f}" if not np.isnan(a2) else "      n/a"
    lts = f"{lt:7.2f}" if not np.isnan(lt) else "    n/a"
    print(f"  {ev_t:8.1f}  {ev_a:7.2f}  {a1s}  {a2s}  {lts}  {verdict}")

  return {
    'events': len(events),
    'led': led,
    'signal_score': led / max(len(events), 1),
    'lead_time_mean': float(np.mean(lead_times)) if lead_times else 0.0,
    'lead_time_p90': float(np.percentile(lead_times, 90)) if lead_times else 0.0,
  }


def main() -> int:
  ap = argparse.ArgumentParser()
  ap.add_argument('routes', nargs='+')
  args = ap.parse_args()

  totals = {'events': 0, 'led': 0, 'lt': []}
  for route in args.routes:
    ts = load_series(route)
    m = analyze(route, ts)
    totals['events'] += m['events']
    totals['led'] += m['led']
    if m['lead_time_mean'] > 0:
      totals['lt'].append(m['lead_time_mean'])

  print("\n══════ AGGREGATE ══════")
  if totals['events'] == 0:
    print("  no qualifying brake events across all routes")
    return 0
  score = totals['led'] / totals['events']
  print(f"  events: {totals['events']}  led: {totals['led']}  signal_score: {score:.2f}")
  if totals['lt']:
    print(f"  mean lead-time across routes: {np.mean(totals['lt']):.2f}s")
  print(f"  verdict: {'SIGNAL — proceed with hybrid' if score >= 0.4 else 'NO SIGNAL — skip hybrid, look elsewhere'}")
  return 0


if __name__ == '__main__':
  sys.exit(main())
