"""Compare explicit PI gains using production adapters and fixed recorded motion.

This checks command behavior, not counterfactual tracking or stability. Original
selected curvature is retained, including each route's original model/delay.
Service publication times proxy control execution time; full SubMaster state is
not logged. In particular, this is not exact process replay of historical cars.
"""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from openpilot.selfdrive.controls.lib import ford_model_action
from openpilot.selfdrive.controls.lib.ford_model_action import FordModelActionController
from tools.ford_pscm_lab.model_action_replay import WireCheck, sample, table


GAINS = (.50, .75)
DEFAULT_SETTINGS = tuple((kp, .25) for kp in GAINS)
DIAGNOSTICS = ('heading_feedforward', 'heading_proportional', 'heading_correction',
               'feedback_enabled', 'pscm_limited', 'driver_override', 'offset_overflow')


def describe(values, mask):
  values = values[mask]
  return {'mean': float(np.mean(values)), 'p95': float(np.quantile(values, .95)),
          'max': float(np.max(values))} if len(values) else None


def replay(route, output, settings=DEFAULT_SETTINGS):
  if len(settings) < 2 or any(len(pair) != 2 or not np.isfinite(pair).all() or min(pair) < 0. for pair in settings):
    raise ValueError('Provide at least two finite, nonnegative P:I pairs')
  label, source = route.split('=', 1)
  directory = Path(source).resolve()
  destination = output.resolve()/label
  if destination == directory or directory in destination.parents:
    raise ValueError('Output must preserve source extracts')
  raw = np.load(directory/'route.npz', allow_pickle=False)
  r = {key: table(raw, key) for key in ('controls', 'cs', 'cc', 'model', 'params', 'pscm', 'path')}
  metadata = json.loads((directory/'metadata.json').read_text())
  if ('maneuver' in raw and len(raw['maneuver'])) or any(
    f['counts'].get(service, 0) for f in metadata['files'] for service in ('lateralManeuverPlan', 'testJoystick')
  ):
    raise ValueError('This replay requires the recorded model-selected reference, without maneuver or joystick injection')
  geometry = np.load(directory/'model_paths.npz', allow_pickle=False)
  np.testing.assert_array_equal(geometry['ns'], r['model']['ns'])
  models = [SimpleNamespace(position=SimpleNamespace(x=p[0], y=p[1]), orientation=SimpleNamespace(z=p[2]))
            for p in geometry['paths']]
  c, t = r['controls'], r['controls']['t']
  cs, pa, ps = (sample(r[key], t) for key in ('cs', 'params', 'pscm'))
  # carControl is the same-cycle publication, never a future motion sample.
  cc = sample(r['cc'], t, nearest=True)
  mi = np.clip(np.searchsorted(r['model']['ns'], c['model_ns']), 0, len(models)-1)
  exact = r['model']['ns'][mi] == c['model_ns']
  health = (c['valid'].astype(bool) & cc['valid'].astype(bool) & cs['valid'].astype(bool)
            & cs['can_valid'].astype(bool) & pa['valid'].astype(bool) & exact
            & r['model']['valid'][mi].astype(bool) & (abs(cc['t']-t) < .005)
            & (t-pa['t'] >= 0.) & (t-pa['t'] <= .15))
  controllers = [FordModelActionController(proportional_gain=kp, integral_gain=ki, c0_time_based=False) for kp, ki in settings]
  commands = np.zeros((len(settings), len(t), 4))
  valid = np.zeros((len(settings), len(t)), bool)
  diagnostics = np.zeros((len(settings), len(t), len(DIAGNOSTICS)))
  reasons = [Counter() for _ in settings]
  wire = WireCheck()
  for i, now in enumerate(t):
    status = SimpleNamespace(valid=bool(ps['valid'][i] and ps['status_valid'][i]), canMonoTime=round(ps['stamp'][i]*1e9),
                             limit=int(ps['limit'][i]), lateralState=int(ps['lateral_state'][i]), denied=bool(ps['denied'][i]))
    kwargs = {'speed': cs['speed'][i], 'yaw_rate': cs['yaw'][i], 'now': now,
              'measurement_time': cs['t'][i], 'model_time': r['model']['t'][mi[i]],
              'reference_time': r['model']['t'][mi[i]], 'active': bool(cc['active'][i]), 'valid': bool(health[i]),
              'current_curvature': c['measured'][i], 'driver_pressed': bool(cs['pressed'][i]),
              'driver_torque': cs['torque'][i], 'pscm_status': status}
    for k, controller in enumerate(controllers):
      command = controller.update(models[mi[i]] if exact[i] else None, c['desired'][i], **kwargs)
      commands[k, i] = command.path_offset, command.path_angle, command.curvature, command.curvature_rate
      valid[k, i] = command.valid
      diagnostics[k, i] = [controller.diagnostics.get(name, 0.) for name in DIAGNOSTICS]
      reasons[k][controller.diagnostics['status']] += 1
      wire.check(command)
  assert np.isfinite(commands).all() and np.isfinite(diagnostics).all()
  assert (abs(commands[:, :, :2]) <= [5.1100001, .5000001]).all()
  assert (commands[:, :, 2:] == 0.).all() and (commands[~valid] == 0.).all()
  for k, (kp, _) in enumerate(settings):
    np.testing.assert_array_equal(valid[0], valid[k])
    np.testing.assert_array_equal(commands[0, :, 0], commands[k, :, 0])
    np.testing.assert_array_equal(diagnostics[0, :, [0, 3, 4, 5, 6]], diagnostics[k, :, [0, 3, 4, 5, 6]])
    expected_p = kp*np.maximum(7., cs['speed'])*(c['desired']-c['measured'])*diagnostics[k, :, 3]
    np.testing.assert_allclose(diagnostics[k, :, 1], expected_p, rtol=1e-12, atol=1e-12)
    assert (diagnostics[k, diagnostics[k, :, 3] == 0., 1:3] == 0.).all()
    assert reasons[0] == reasons[k]

  driver = (cs['pressed'] > 0.) | (abs(cs['torque']) > 1.) | ((ps['status_valid'] > 0) & (ps['limit'] == 3))
  bad = driver | ~valid[0] | (diagnostics[0, :, 3] == 0.)
  last_bad = np.maximum.accumulate(np.where(bad, t, -1e6))
  clean = ~bad & (t-last_bad >= 1.) & (cs['speed'] >= 3.*.44704)
  weights = np.minimum(np.diff(t, append=t[-1]+.01), .03)
  angle = abs(c['desired_angle'])
  # These labels describe the recorded error, not the candidate's response.
  behind = c['desired']*(c['desired']-c['measured']) > 0.
  derivative = np.r_[0., np.diff(abs(c['desired']))/np.maximum(np.diff(t), .002)]
  masks = {'all': clean, 'small_under_10deg': clean & (angle < 10.),
           'bend_10_to_45deg': clean & (angle >= 10.) & (angle < 45.),
           'turn_over_45deg': clean & (angle >= 45.),
           'turn_entry_behind': clean & (angle >= 45.) & behind & (derivative > 0.),
           'turn_releasing_excess_steering': clean & (angle >= 10.) & ~behind & (derivative < 0.)}
  change = commands[1, :, 1]-commands[0, :, 1]
  cohorts = {}
  for name, mask in masks.items():
    cohorts[name] = {'seconds': float(weights[mask].sum()), 'abs_c1_change': describe(abs(change), mask),
                     'settings': [{'kp': kp, 'ki': ki,
                                   'abs_c1_change_from_baseline': describe(abs(commands[k, :, 1]-commands[0, :, 1]), mask),
                                   'c1_bound_seconds': float(weights[mask & (abs(commands[k, :, 1]) >= .4995)].sum()),
                                   'abs_c1': describe(abs(commands[k, :, 1]), mask),
                                   'abs_integral': describe(abs(diagnostics[k, :, 2]), mask)} for k, (kp, ki) in enumerate(settings)]}
  paired = clean[1:] & clean[:-1]
  step = np.diff(commands[:, :, 1], axis=1)
  step_metrics = [{'kp': kp, 'ki': ki, 'abs_c1_per_cycle_change': describe(abs(step[k]), paired)} for k, (kp, ki) in enumerate(settings)]
  rec = sample(r['path'], t, nearest=True)
  rec_mask = clean & (rec['valid'] > 0) & (abs(rec['t']-t) < .005)
  baseline_comparison = {name: describe(abs(commands[0, :, idx]-rec[name]), rec_mask) for idx, name in enumerate(('c0', 'c1'))}
  sources = (directory/'route.npz', directory/'model_paths.npz', directory/'metadata.json',
             Path(__file__).resolve(), Path(ford_model_action.__file__).resolve())
  report = {'scope': __doc__, 'route': label, 'cycles': len(t), 'gains': [kp for kp, _ in settings],
            'settings': [{'kp': kp, 'ki': ki} for kp, ki in settings],
            'ki': settings[0][1] if len({ki for _, ki in settings}) == 1 else None,
            'can_round_trips': wire.count, 'validity_and_c0_and_gates_identical': True,
            'status_counts': dict(reasons[0]), 'cohorts': cohorts, 'per_cycle_changes': step_metrics,
            'baseline_difference_from_recorded_path': baseline_comparison,
            'baseline_comparison_note': 'Only meaningful for matching historical mapping/gains; adapter clock/health reconstruction is approximate.',
            'source_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
  destination.mkdir(parents=True, exist_ok=True)
  (destination/'report.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
  np.savez_compressed(destination/'commands.npz', t=t-metadata['t0'], commands=commands, valid=valid,
                      settings=np.array(settings),
                      diagnostics=diagnostics, diagnostic_names=DIAGNOSTICS, clean=clean,
                      driver=driver, speed=cs['speed'], desired=c['desired'], measured=c['measured'])
  return report


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--routes', nargs='+', required=True, help='label=extract-directory pairs')
  parser.add_argument('--output', type=Path, required=True)
  parser.add_argument('--workers', type=int, default=4)
  parser.add_argument('--settings', nargs='+', help='Explicit P:I pairs; defaults to 0.50:0.25 and 0.75:0.25')
  args = parser.parse_args()
  try:
    settings = tuple(tuple(float(v) for v in pair.split(':')) for pair in args.settings) if args.settings else DEFAULT_SETTINGS
    if len(settings) < 2 or any(len(pair) != 2 or not np.isfinite(pair).all() or min(pair) < 0. for pair in settings):
      raise ValueError
  except ValueError:
    parser.error('Settings require at least two finite, nonnegative P:I pairs')
  labels = [route.split('=', 1)[0] for route in args.routes]
  if len(set(labels)) != len(labels) or any(Path(label).name != label or label in ('.', '..') for label in labels):
    parser.error('Route labels must be unique directory names')
  with ProcessPoolExecutor(max_workers=args.workers) as pool:
    jobs = {pool.submit(replay, route, args.output, settings): route for route in args.routes}
    for job in as_completed(jobs):
      result = job.result()
      print(json.dumps({'route': result['route'], 'cycles': result['cycles'], 'can_round_trips': result['can_round_trips'],
                        'clean_seconds': result['cohorts']['all']['seconds']}), flush=True)
