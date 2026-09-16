"""Reference-only sensitivity check; the selected default also has full command replay."""
import argparse
import json
from pathlib import Path

import numpy as np

from openpilot.selfdrive.controls.lib.drive_helpers import clip_curvature
from tools.ford_pscm_lab.geometry_action_hybrid import GeometryActionHybrid
from tools.ford_pscm_lab.hybrid_reference_replay import load_route, sustained


def quantiles(values):
  return np.quantile(values, [.1, .5, .95, 1.]).tolist() if values else None


def run(label, root):
  d = load_route(label)
  with np.load(root/label/'commands.npz') as z:
    a = dict(zip(z['names'], z['rows'].T, strict=True))
  with np.load(Path('.cache/ford_routes158_159')/f'{label}_fullrate_aligned.npz') as z:
    scale = z['angle_scale']
    np.testing.assert_allclose(z['t'], a['t'])
  events = json.loads((root/label/'report.json').read_text())['events']
  t, live = a['t'], a['valid'].astype(bool)
  consecutive = live[1:] & live[:-1] & (np.diff(t) < .03)
  results = []
  curves = {'t': t}
  for start in [.006, .01, .015]:
    for power in [1., 2., 4., 8.]:
      h = GeometryActionHybrid(start, 2*start, power)
      selected = 0.
      curve = np.zeros(len(t))
      weights = np.zeros(len(t))
      for i in range(len(t)):
        target = h.update(float(d.action[i]), float(d.geometry[i]), active=bool(d.active[i] and d.valid[i]))
        selected, _ = clip_curvature(d.cs['speed'][i], selected, target if d.active[i] else d.c['measured'][i], d.pa['roll'][i])
        curve[i] = a['action_angle'][i]+scale[i]*(selected-a['action_reference'][i])
        weights[i] = h.weight
      if start == .01 and power == 2.:
        np.testing.assert_allclose(curve[live], a['hybrid_angle'][live], atol=1e-5)
      retained, entry_leads, exit_delays = [], [], []
      unavailable_release = unavailable_entry = 0
      details = []
      for e in events:
        sign = 1 if e['direction'] == 'left' else -1
        window = live & (t >= e['window'][0]) & (t <= e['window'][1])
        build = window & (t <= e['action_peak_t'])
        release = window & (t >= e['action_peak_t'])
        extra = sign*(a['geometry_angle']-a['action_angle'])
        assist = build & (extra > 5.) & (sign*a['action_angle'] > 0.) & (sign*a['geometry_angle'] > 50.)
        keep = float(np.sum(sign*(curve-a['action_angle'])[assist])/np.sum(extra[assist])) if assist.any() else None
        if keep is not None:
          retained.append(keep)
        entry = sustained(t, build & (sign*curve >= 50.))
        end = sustained(t, release & (sign*curve < 25.))
        action_entry, action_exit = [e['variants']['action'][k] for k in ('entry_50_s', 'release_25_s')]
        if action_entry is not None:
          if entry is None:
            unavailable_entry += 1
          else:
            entry_leads.append(action_entry-entry)
        if action_exit is not None:
          if end is None:
            unavailable_release += 1
          else:
            exit_delays.append(end-action_exit)
        details.append({'id': e['id'], 'retained': keep, 'entry': entry, 'release': end})
      key = f'{start:.3f}_p{power:.0f}'
      curves[key] = curve
      results.append({'start': start, 'full': 2*start, 'power': power,
                      'geometry_entry_extra_retained_p10_p50_p95_max': quantiles(retained),
                      'entry_lead_vs_action_s_p10_p50_p95_max': quantiles(entry_leads),
                      'release_later_than_action_s_p10_p50_p95_max': quantiles(exit_delays),
                      'unavailable_entry_when_action_has_one': unavailable_entry,
                      'unavailable_release_when_action_has_one': unavailable_release,
                      'target_steps_over_20deg': int((abs(np.diff(curve)[consecutive]) > 20.).sum()),
                      'events': details})
  np.savez_compressed(root/label/'sweep_curves.npz', **curves)
  (root/label/'sweep.json').write_text(json.dumps(results, indent=2, allow_nan=False)+'\n')
  print(json.dumps({'route': label, 'settings': len(results)}), flush=True)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--route', choices=['15a', '15b'], required=True)
  parser.add_argument('--output', type=Path, default=Path('.cache/ford_hybrid'))
  args = parser.parse_args()
  run(args.route, args.output)
