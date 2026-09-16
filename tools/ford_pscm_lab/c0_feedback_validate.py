"""Replay C0 feedback against a baseline using frozen native-time Lightning measurements.

This checks software/CAN behavior, not the physical response to new commands.
Use cached route.npz, model_paths.npz and metadata.json from the rlog extractor.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import inspect
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from opendbc.car.vehicle_model import VehicleModel
from openpilot.selfdrive.controls.lib import ford_model_action
from tools.ford_pscm_lab.feedback_replay import original_controller
from tools.ford_pscm_lab.model_action_replay import WireCheck, sample, table


BASELINE = 'd425b3260b0785b22096d130702b54a2e0761c36'
SPECIAL = {'11c': 'ford_maneuver_11c/analysis', '125': 'ford_c0_response_124_125/route125',
           '146': 'ford_model_replay_146/full', '149': 'ford_route149/full', '151': 'ford_route151/full'}
ROUTES = ['a9', 'b9', '112', '113', '117', '11c', '125', '146', '149', '151']


def replay(label, output, baseline=BASELINE):
  source = Path('.cache')/SPECIAL.get(label, 'ford_route'+label)
  meta = json.loads((source/'metadata.json').read_text())
  with np.load(source/'route.npz') as z:
    r = {k: table(z, k) for k in ('controls', 'cs', 'cc', 'model', 'params', 'pscm')}
  with np.load(source/'model_paths.npz') as z:
    model_ns, paths = z['ns'], z['paths']
  reference = Path('.cache/ford_route112/metadata.json')
  car = {**json.loads(reference.read_text())['car'][0], **meta['car'][0]}
  assert car['fingerprint'] == 'FORD_F_150_LIGHTNING_MK1'
  cp = SimpleNamespace(**{k: car[k] for k in ('mass', 'wheelbase', 'centerToFront', 'steerRatioRear',
                                             'tireStiffnessFront', 'tireStiffnessRear')},
                       steerRatio=car['steer_ratio'], rotationalInertia=0.)
  vm = VehicleModel(cp)
  c, t = r['controls'], r['controls']['t']
  assert all(np.all(np.diff(s['t']) >= 0) for s in r.values())
  cs, pa, ps = [sample(r[k], t) for k in ('cs', 'params', 'pscm')]
  cc = sample(r['cc'], t, nearest=True)
  mi = np.clip(np.searchsorted(r['model']['ns'], c['model_ns']), 0, len(r['model']['ns'])-1)
  exact = r['model']['ns'][mi] == c['model_ns']
  np.testing.assert_array_equal(model_ns, r['model']['ns'])
  models = [SimpleNamespace(position=SimpleNamespace(x=p[0], y=p[1]), orientation=SimpleNamespace(z=p[2])) for p in paths]
  old, old_hash = original_controller(baseline)
  old_accepts_scale = 'curvature_scale' in inspect.signature(old.update).parameters
  new = ford_model_action.FordModelActionController()
  wire = WireCheck()
  names = ['t', 'valid', 'c0_old', 'c0_new', 'c1', 'offset_p', 'enabled', 'error_deg', 'target_deg', 'speed', 'curvature_scale']
  rows = np.zeros((len(t), len(names)))
  for i, now in enumerate(t):
    model_time = r['model']['t'][mi[i]]
    good_params = np.isfinite([pa['stiffness'][i], pa['steer_ratio'][i]]).all() and min(pa['stiffness'][i], pa['steer_ratio'][i]) > 0
    if good_params:
      vm.update_params(max(pa['stiffness'][i], .1), max(pa['steer_ratio'][i], .1))
    scale = vm.get_steer_from_curvature(1., cs['speed'][i], 0.)/(cp.steerRatio*cp.wheelbase)
    valid = bool(c['valid'][i] and cc['valid'][i] and cs['valid'][i] and cs['can_valid'][i] and good_params
                 and pa['valid'][i] and r['model']['valid'][mi[i]] and exact[i] and abs(cc['t'][i]-now) < .005
                 and 0 <= now-pa['t'][i] <= .15)
    status = SimpleNamespace(valid=bool(ps['valid'][i] and ps['status_valid'][i]), canMonoTime=round(ps['stamp'][i]*1e9),
                             limit=int(ps['limit'][i]), lateralState=int(ps['lateral_state'][i]), denied=bool(ps['denied'][i]))
    args = {'current_curvature': c['measured'][i], 'yaw_rate': cs['yaw'][i], 'speed': cs['speed'][i], 'now': now,
                'measurement_time': cs['t'][i], 'model_time': model_time, 'reference_time': model_time, 'active': bool(cc['active'][i]),
                'valid': valid, 'driver_pressed': bool(cs['pressed'][i]), 'driver_torque': cs['torque'][i], 'pscm_status': status}
    model = models[mi[i]] if exact[i] else None
    a = old.update(model, c['desired'][i], **args, **({'curvature_scale': scale} if old_accepts_scale else {}))
    b = new.update(model, c['desired'][i], curvature_scale=scale, **args)
    assert a.valid == b.valid
    assert a.path_angle == b.path_angle
    assert old.core.correction == new.core.correction
    assert old.core.proportional == new.core.proportional
    if hasattr(old.core, 'offset_proportional') and old.core.c0_proportional_gain > 0.:
      assert np.isclose(new.core.offset_proportional, old.core.offset_proportional *
                        new.core.c0_proportional_gain / old.core.c0_proportional_gain, rtol=1e-12, atol=1e-12)
    assert abs(b.path_offset) <= 5.1100001 and abs(b.path_angle) <= .5000001
    assert b.curvature == b.curvature_rate == 0.
    assert np.isfinite([b.path_offset, b.path_angle, new.core.offset_proportional]).all()
    if not new.diagnostics.get('feedback_enabled', False):
      assert new.core.offset_proportional == 0. and a.path_offset == b.path_offset
    if new.core.offset_proportional == 0.:
      assert a.path_offset == b.path_offset
    error = -(c['desired'][i]-c['measured'][i])*scale*cp.steerRatio*cp.wheelbase*180/np.pi
    target = vm.get_steer_from_curvature(-c['desired'][i], cs['speed'][i], pa['roll'][i])*180/np.pi+pa['angle_offset'][i]
    rows[i] = [now-meta['t0'], b.valid, a.path_offset, b.path_offset, b.path_angle, new.core.offset_proportional,
               new.diagnostics.get('feedback_enabled', False), error, target, cs['speed'][i], scale]
    if i % 10 == 0:  # Native-time integration above; CAN round trip on every tenth frame.
      wire.check(b)
  dest = output/label
  dest.mkdir(parents=True, exist_ok=True)
  np.savez_compressed(dest/'commands.npz', names=names, rows=rows)
  eligible = rows[:, 1].astype(bool) & rows[:, 6].astype(bool)
  groups = {'all': eligible, 'straight': eligible & (abs(rows[:, 8]) < 5),
            'turn': eligible & (abs(rows[:, 8]) >= 45), 'large_error': eligible & (abs(rows[:, 7]) >= 30)}
  metrics = {}
  for name, mask in groups.items():
    if mask.any():
      delta = abs(rows[mask, 3]-rows[mask, 2])
      metrics[name] = {'n': int(mask.sum()), 'delta_c0_m_quantiles': np.quantile(delta, [.5, .95, 1.]).tolist(),
                           'c0_old_capped': int((abs(rows[mask, 2]) >= 5.105).sum()),
                           'c0_new_capped': int((abs(rows[mask, 3]) >= 5.105).sum())}
  files = [source/n for n in ('route.npz', 'metadata.json', 'model_paths.npz')]
  files += [reference, Path(__file__), Path(ford_model_action.__file__)]
  report = {'route': label, 'baseline': baseline, 'baseline_sha256': old_hash, 'cycles': len(t), 'wire_round_trips': wire.count,
                'c1_identical': True, 'c0_gain': new.core.c0_proportional_gain, 'metrics': metrics,
                'sources': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
  (dest/'report.json').write_text(json.dumps(report, indent=2)+'\n')
  return report


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--output', type=Path, required=True)
  parser.add_argument('--routes', nargs='+', default=ROUTES, choices=ROUTES)
  parser.add_argument('--workers', type=int, default=4)
  parser.add_argument('--baseline', default=BASELINE, help='Controller commit to compare, including previous C0 gains')
  args = parser.parse_args()
  with ProcessPoolExecutor(max_workers=args.workers) as pool:
    jobs = {pool.submit(replay, label, args.output, args.baseline): label for label in args.routes}
    results = []
    for job in as_completed(jobs):
      result = job.result()
      results.append(result)
      print(json.dumps({k: result[k] for k in ('route', 'cycles', 'wire_round_trips', 'metrics')}), flush=True)
  (args.output/'validation.json').write_text(json.dumps({'scope': __doc__, 'routes': results}, indent=2)+'\n')
