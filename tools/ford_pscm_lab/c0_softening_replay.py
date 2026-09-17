"""Replay C0 softening against v21 on frozen recorded motion, not a PSCM model."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import numpy as np

from opendbc.car.vehicle_model import VehicleModel
from openpilot.selfdrive.controls.lib.ford_model_action import FordModelActionController
from tools.ford_pscm_lab.model_action_replay import WireCheck, sample, table


BASELINE = 'ed9c44f57584b5f033f79db6331e21b9b3e0ad55'
CONTROLLER = 'openpilot/selfdrive/controls/lib/ford_model_action.py'


def replay(source, intake, archive, destination):
  meta = json.loads((source/'metadata.json').read_text())
  with np.load(source/'route.npz') as z:
    r = {k: table(z, k) for k in ('controls', 'cs', 'cc', 'path', 'params', 'pscm')}
  with np.load(source/'model_paths.npz') as z:
    paths, path_ns = z['paths'], z['ns']
  with np.load(intake) as z:
    delay = z['delay']
  with np.load(archive) as z:
    archived = dict(zip(z['names'], z['rows'].T, strict=True))
  baseline_source = subprocess.check_output(['git', 'show', f'{BASELINE}:{CONTROLLER}'], text=True)
  namespace = {'__name__': 'v21_ford_controller'}
  exec(compile(baseline_source, '<v21_ford_controller>', 'exec'), namespace)
  old, new = namespace['FordModelActionController'](), FordModelActionController()
  c, cp = r['controls'], meta['car'][0]
  q = c['t']
  cs, pa, ps = [sample(r[k], q) for k in ('cs', 'params', 'pscm')]
  cc, sent = [sample(r[k], q, nearest=True) for k in ('cc', 'path')]
  mi = np.clip(np.searchsorted(path_ns, c['model_ns']), 0, len(path_ns)-1)
  exact = path_ns[mi] == c['model_ns']
  models = [SimpleNamespace(position=SimpleNamespace(x=p[0], y=p[1]), orientation=SimpleNamespace(z=p[2])) for p in paths]
  delays = sample({'t': delay[:, 0], 'value': delay[:, 3]}, q)['value']
  delays[q < delay[0, 0]] = 0.
  params = SimpleNamespace(**{k: cp[k] for k in ('mass', 'wheelbase', 'centerToFront', 'steerRatioRear', 'tireStiffnessFront', 'tireStiffnessRear')},
                           steerRatio=cp['steer_ratio'], rotationalInertia=0.)
  vm = VehicleModel(params)
  wire = WireCheck()
  names = ['t', 'valid', 'speed', 'desired', 'measured', 'reference', 'target_angle', 'actual_angle',
           'old_c0', 'new_c0', 'old_p', 'new_p', 'c1', 'c1_p', 'i', 'feedback', 'pressed', 'torque', 'pscm_limit',
           'recorded_c0', 'recorded_c1']
  rows = np.zeros((len(q), len(names)))
  for i, now in enumerate(q):
    vm.update_params(max(pa['stiffness'][i], .1), max(pa['steer_ratio'][i], .1))
    scale = vm.get_steer_from_curvature(1., cs['speed'][i], 0.)/(params.steerRatio*params.wheelbase)
    error = c['desired'][i]-c['measured'][i]
    if abs(error) > 1e-5:
      scale = -np.radians(c['desired_angle'][i]-c['actual_angle'][i])/error/(params.steerRatio*params.wheelbase)
    status = SimpleNamespace(valid=bool(ps['valid'][i] and ps['status_valid'][i]), canMonoTime=round(ps['stamp'][i]*1e9),
                             limit=int(ps['limit'][i]), lateralState=int(ps['lateral_state'][i]), denied=bool(ps['denied'][i]))
    args = {'current_curvature': c['measured'][i], 'speed': cs['speed'][i], 'yaw_rate': cs['yaw'][i], 'now': now,
            'measurement_time': cs['t'][i], 'model_time': c['model_ns'][i]*1e-9, 'reference_time': c['model_ns'][i]*1e-9,
            'active': bool(cc['active'][i]), 'valid': bool(c['valid'][i] and cs['valid'][i] and cs['can_valid'][i] and pa['valid'][i] and exact[i]),
            'driver_pressed': bool(cs['pressed'][i]), 'driver_torque': cs['torque'][i], 'pscm_status': status,
            'curvature_scale': scale, 'lat_delay': delays[i]}
    before, after = [core.update(models[mi[i]], c['desired'][i], **args) for core in (old, new)]
    assert before.valid == after.valid
    assert before.path_angle == after.path_angle and old.core.correction == new.core.correction
    assert old.core.proportional == new.core.proportional and old.core.feedback_curvature == new.core.feedback_curvature
    assert old.core.offset_proportional == new.core.offset_proportional_linear
    assert abs(new.core.offset_proportional) <= abs(old.core.offset_proportional)+1e-12
    assert new.core.offset_proportional*old.core.offset_proportional >= 0.
    assert abs(new.core.offset_proportional-old.core.offset_proportional) <= .125000001
    assert abs(before.path_offset-after.path_offset) <= .130000001
    assert abs(after.path_offset) <= 5.110000001 and abs(after.path_angle) <= .500000001
    assert after.curvature == after.curvature_rate == 0.
    for key in ('feedback_enabled', 'driver_override', 'pscm_limited', 'heading_feedforward', 'offset_overflow', 'feedback_delay'):
      assert old.diagnostics.get(key) == new.diagnostics.get(key)
    assert before.path_offset == archived['new_c0'][i] and before.path_angle == archived['new_c1'][i]
    assert old.core.correction == archived['new_i'][i]
    if not new.diagnostics.get('feedback_enabled', False):
      assert new.core.offset_proportional == new.core.proportional == new.core.correction == 0.
      assert before == after
    if i % 10 == 0:
      wire.check(after)
    rows[i] = [now-meta['t0'], after.valid, cs['speed'][i], c['desired'][i], c['measured'][i], new.core.feedback_curvature,
               c['desired_angle'][i], c['actual_angle'][i], before.path_offset, after.path_offset,
               old.core.offset_proportional, new.core.offset_proportional, after.path_angle, new.core.proportional, new.core.correction,
               new.diagnostics.get('feedback_enabled', False), cs['pressed'][i], cs['torque'][i], ps['limit'][i], sent['c0'][i], sent['c1'][i]]
  a = dict(zip(names, rows.T, strict=True))
  valid = a['valid'].astype(bool)
  dt = np.minimum(np.diff(a['t'], append=a['t'][-1]+.01), .03)
  paired = valid[1:] & valid[:-1] & (np.diff(a['t']) < .03)
  metrics = {'cycles': len(q), 'wire_checks': wire.count, 'baseline_matches_archived_v21_exactly': True,
             'c1_integral_reference_arbitration_equal_every_cycle': True,
             'P_reduction_p50_p95_p99_max_m': np.quantile(abs(a['old_p'][valid]-a['new_p'][valid]), [.5, .95, .99, 1]).tolist(),
             'C0_change_p50_p95_p99_max_m': np.quantile(abs(a['old_c0'][valid]-a['new_c0'][valid]), [.5, .95, .99, 1]).tolist(),
             'variants': {}, 'baseline_commit': BASELINE, 'method': __doc__}
  for prefix in ('old', 'new'):
    metrics['variants'][prefix] = {'c0_step_p95_p99_max': np.quantile(abs(np.diff(a[prefix+'_c0'])[paired]), [.95, .99, 1]).tolist(),
                                  'c0_bound_seconds': float(dt[valid & (abs(a[prefix+'_c0']) >= 5.105)].sum())}
  metrics['controller_sha256'] = hashlib.sha256(Path(CONTROLLER).read_bytes()).hexdigest()
  metrics['source_sha256'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in [source/'route.npz', source/'model_paths.npz', intake, archive]}
  destination.mkdir(parents=True, exist_ok=True)
  np.savez_compressed(destination/'commands.npz', names=names, rows=rows)
  (destination/'report.json').write_text(json.dumps(metrics, indent=2)+'\n')
  return {k: v for k, v in metrics.items() if k != 'source_sha256'}


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--source', type=Path, required=True)
  parser.add_argument('--delay-intake', type=Path, required=True)
  parser.add_argument('--archive', type=Path, required=True, help='Archived v21 commands.npz for an exact baseline check')
  parser.add_argument('--output', type=Path, required=True)
  args = parser.parse_args()
  print(json.dumps(replay(args.source, args.delay_intake, args.archive, args.output), indent=2))
