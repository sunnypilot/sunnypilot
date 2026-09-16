"""Compare Ford feedback variants on recorded references and frozen vehicle motion.

Input: extract.py route.npz/model_paths.npz/metadata.json directories. This checks
command continuity and overrides; it does not predict a changed wheel response.
Both controllers receive the logged selected curvature. Recorded-command agreement
is expected only for routes driven with the selected baseline and fixed 7 m C0.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import numpy as np

from opendbc.car.vehicle_model import VehicleModel
from openpilot.selfdrive.controls.lib.ford_model_action import FordModelActionController
from tools.ford_pscm_lab.model_action_replay import WireCheck, sample, table


def replay(source, destination, baseline_class, provenance, *, delay_intake=None):
  meta = json.loads((source/'metadata.json').read_text())
  with np.load(source/'route.npz') as z:
    r = {k: table(z, k) for k in ('controls', 'cs', 'cc', 'path', 'params', 'pscm', 'model')}
  with np.load(source/'model_paths.npz') as z:
    paths = z['paths']
    path_ns = z['ns']
  c = r['controls']
  t = c['t']
  delays = np.zeros(len(t))
  if delay_intake is not None:
    with np.load(delay_intake) as z:
      stream = z['delay']
    # Match controlsd's lateralDelay message plus its imported modeld constant.
    source_tree = ast.parse(Path('openpilot/selfdrive/modeld/modeld.py').read_text())
    smoothing = next(ast.literal_eval(n.value) for n in source_tree.body
                     if isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == 'LAT_SMOOTH_SECONDS')
    delays = sample({'t': stream[:, 0], 'value': stream[:, 3]}, t)['value'] + smoothing
    delays[t < stream[0, 0]] = smoothing
  cs, pa, ps = [sample(r[k], t) for k in ('cs', 'params', 'pscm')]
  cc, sent = [sample(r[k], t, nearest=True) for k in ('cc', 'path')]
  mi = np.clip(np.searchsorted(path_ns, c['model_ns']), 0, len(path_ns)-1)
  exact = path_ns[mi] == c['model_ns']
  models = [SimpleNamespace(position=SimpleNamespace(x=p[0], y=p[1]), orientation=SimpleNamespace(z=p[2])) for p in paths]
  car = meta['car'][0]
  cp = SimpleNamespace(**{k: car[k] for k in ('mass', 'wheelbase', 'centerToFront', 'steerRatioRear', 'tireStiffnessFront', 'tireStiffnessRear')},
                       steerRatio=car['steer_ratio'], rotationalInertia=0.)
  vm = VehicleModel(cp)
  cores = [baseline_class(), FordModelActionController()]
  zero_delay = FordModelActionController() if delay_intake is not None else None
  wire = WireCheck()
  names = ['t', 'active', 'valid', 'speed', 'pressed', 'raw_torque', 'pscm_override', 'limit',
           'old_c0', 'new_c0', 'old_c1', 'new_c1', 'old_i', 'new_i', 'old_feedback', 'new_feedback',
           'recorded_c0', 'recorded_c1', 'latched_angle_error', 'model_ns', 'desired_angle',
           'desired', 'measured', 'old_reference', 'new_reference', 'feedback_delay', 'old_c0_p', 'new_c0_p', 'old_c1_p', 'new_c1_p']
  rows = np.zeros((len(t), len(names)))
  for i, now in enumerate(t):
    vm.update_params(max(pa['stiffness'][i], .1), max(pa['steer_ratio'][i], .1))
    scale = vm.get_steer_from_curvature(1., cs['speed'][i], 0.)/(cp.steerRatio*cp.wheelbase)
    error = c['desired'][i]-c['measured'][i]
    if abs(error) > 1e-5:
      scale = -np.radians(c['desired_angle'][i]-c['actual_angle'][i])/error/(cp.steerRatio*cp.wheelbase)
    status = SimpleNamespace(valid=bool(ps['valid'][i] and ps['status_valid'][i]), canMonoTime=round(ps['stamp'][i]*1e9),
                             limit=int(ps['limit'][i]), lateralState=int(ps['lateral_state'][i]), denied=bool(ps['denied'][i]))
    active = bool(cc['active'][i])
    valid = bool(c['valid'][i] and cs['valid'][i] and cs['can_valid'][i] and pa['valid'][i] and exact[i])
    commands = []
    inputs = {'current_curvature': c['measured'][i], 'speed': cs['speed'][i], 'yaw_rate': cs['yaw'][i], 'now': now, 'measurement_time': cs['t'][i],
              'model_time': c['model_ns'][i]*1e-9, 'reference_time': c['model_ns'][i]*1e-9,
              'active': active, 'valid': valid, 'driver_pressed': bool(cs['pressed'][i]), 'driver_torque': cs['torque'][i],
              'pscm_status': status, 'curvature_scale': scale}
    for variant, core in enumerate(cores):
      delay_args = {'lat_delay': delays[i]} if variant == 1 and delay_intake is not None else {}
      command = core.update(models[mi[i]], c['desired'][i], **inputs, **delay_args)
      assert abs(command.path_offset) <= 5.1100001 and abs(command.path_angle) <= .5000001
      assert command.curvature == command.curvature_rate == 0.
      if command.valid and (cs['pressed'][i] or (status.valid and -.005 <= now-ps['stamp'][i] <= .15 and status.limit == 3)):
        assert not core.diagnostics['feedback_enabled']
        assert core.core.correction == core.core.proportional == core.core.offset_proportional == 0.
      commands.append(command)
    assert commands[0].valid == commands[1].valid
    if zero_delay is not None:
      assert zero_delay.update(models[mi[i]], c['desired'][i], **inputs, lat_delay=0.) == commands[0]
      assert zero_delay.core.correction == cores[0].core.correction
      for key in ('heading_feedforward', 'offset_overflow', 'driver_override', 'feedback_enabled', 'pscm_limited'):
        assert cores[0].diagnostics.get(key) == cores[1].diagnostics.get(key)
    if i % 10 == 0:
      wire.check(commands[1])
    old, new = commands
    rows[i] = [now-meta['t0'], active, new.valid, cs['speed'][i], cs['pressed'][i], cs['torque'][i], status.limit == 3, status.limit == 2,
               old.path_offset, new.path_offset, old.path_angle, new.path_angle, cores[0].core.correction, cores[1].core.correction,
               cores[0].diagnostics.get('feedback_enabled', False), cores[1].diagnostics.get('feedback_enabled', False),
               sent['c0'][i], sent['c1'][i], abs(cs['angle'][i]-c['actual_angle'][i]), c['model_ns'][i], c['desired_angle'][i],
               c['desired'][i], c['measured'][i], cores[0].core.feedback_curvature, cores[1].core.feedback_curvature,
               cores[1].diagnostics.get('feedback_delay', 0.), cores[0].core.offset_proportional, cores[1].core.offset_proportional,
               cores[0].core.proportional, cores[1].core.proportional]
  a = dict(zip(names, rows.T, strict=True))
  live = a['valid'].astype(bool)
  consecutive = live[1:] & live[:-1] & (np.diff(t) < .03)
  low = consecutive & (a['speed'][1:] < 15*.44704)
  raw_crossing = (consecutive & (abs(a['raw_torque'][:-1]) <= 1.) & (abs(a['raw_torque'][1:]) > 1.)
                  & ~a['pressed'][:-1].astype(bool) & ~a['pressed'][1:].astype(bool)
                  & ~a['pscm_override'][:-1].astype(bool) & ~a['pscm_override'][1:].astype(bool)
                  & (np.diff(a['model_ns']) == 0) & (abs(np.diff(a['desired_angle'])) < .1))
  metrics = {'cycles': len(t), 'wire_checks': wire.count,
             'zero_delay_matches_baseline': True if zero_delay is not None else None,
             'feedback_delay_requested_min_median_max': np.quantile(delays, [0., .5, 1.]).tolist(),
             'feedback_delay_used_min_median_max': np.quantile(a['feedback_delay'][live], [0., .5, 1.]).tolist(),
             'baseline_recorded_error_p50_p95_p99_max': {
               k: np.quantile(abs(a['old_'+k][live]-a['recorded_'+k][live]), [.5, .95, .99, 1]).tolist() for k in ('c0', 'c1')},
             'latched_angle_match_fraction': float(np.mean(a['latched_angle_error'][live] < 1e-4)),
             'command_changes': {k: np.quantile(abs(a['new_'+k][live]-a['old_'+k][live]), [.5, .95, .99, 1]).tolist() for k in ('c0', 'c1')},
             'variants': {}}
  for name in ('old', 'new'):
    metrics['variants'][name] = {
      'feedback_switches_active': int(np.count_nonzero(np.diff(a[name+'_feedback'])[consecutive])),
      'feedback_switches_low_speed': int(np.count_nonzero(np.diff(a[name+'_feedback'])[low])),
      'low_speed_c0_steps_over_025m': int(np.count_nonzero(abs(np.diff(a[name+'_c0'])[low]) > .250001)),
      'low_speed_c1_steps_over_005rad': int(np.count_nonzero(abs(np.diff(a[name+'_c1'])[low]) > .050001)),
      'low_speed_step_p99': {k: float(np.quantile(abs(np.diff(a[name+'_'+k])[low]), .99)) for k in ('c0', 'c1')},
      'raw_crossing_c0_steps_over_025m': int(np.count_nonzero(abs(np.diff(a[name+'_c0'])[raw_crossing]) > .250001)),
      'c0_bound_active_s': float(np.sum(np.minimum(np.diff(t, append=t[-1]+.01), .03)[live & (abs(a[name+'_c0']) >= 5.105)])),
      'c1_bound_active_s': float(np.sum(np.minimum(np.diff(t, append=t[-1]+.01), .03)[live & (abs(a[name+'_c1']) >= .49975)])),
    }
  # Baseline agreement is reported rather than hidden: control publication time
  # approximates the core's call time, and retained-message service checks are unavailable.
  metrics['method'] = __doc__
  metrics['provenance'] = provenance
  metrics['sources_sha256'] = {str(source/k): hashlib.sha256((source/k).read_bytes()).hexdigest() for k in ('route.npz', 'model_paths.npz', 'metadata.json')}
  if delay_intake is not None:
    metrics['sources_sha256'][str(delay_intake)] = hashlib.sha256(delay_intake.read_bytes()).hexdigest()
  destination.mkdir(parents=True, exist_ok=True)
  np.savez_compressed(destination/'commands.npz', names=names, rows=rows)
  (destination/'report.json').write_text(json.dumps(metrics, indent=2)+'\n')
  return metrics


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--source', type=Path, required=True)
  parser.add_argument('--output', type=Path, required=True)
  parser.add_argument('--baseline', default='4900c0a40c87c72000b7168a6cf4fe6dd98ea6d0')
  parser.add_argument('--delay-intake', type=Path, help='intake.npz with logged lateralDelay; requires a baseline with identical gains and driver gating')
  args = parser.parse_args()
  revision = subprocess.check_output(['git', 'rev-parse', f'{args.baseline}^{{commit}}'], text=True).strip()
  controller_path = 'openpilot/selfdrive/controls/lib/ford_model_action.py'
  code = subprocess.check_output(['git', 'show', f'{revision}:{controller_path}'], text=True)
  namespace = {'__name__': 'recorded_ford_controller'}
  exec(compile(code, '<recorded_ford_controller>', 'exec'), namespace)
  provenance = {'baseline_commit': revision, 'baseline_controller_sha256': hashlib.sha256(code.encode()).hexdigest(),
                'candidate_controller_sha256': hashlib.sha256(Path(controller_path).read_bytes()).hexdigest(),
                'fixed_c0_distance_m': 7.}
  result = replay(args.source, args.output, namespace['FordModelActionController'], provenance, delay_intake=args.delay_intake)
  print(json.dumps({k: v for k, v in result.items() if k != 'sources_sha256'}, indent=2))
