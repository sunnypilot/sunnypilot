"""Replay the geometry reference and current C0/C1 controller on frozen route measurements.

Requires cached full/route.npz, full/metadata.json, intake.npz and intake.json.
This is command validation, not a simulation of the truck following new requests.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from opendbc.car.vehicle_model import VehicleModel
from openpilot.selfdrive.controls.lib.drive_helpers import clip_curvature
from openpilot.selfdrive.controls.lib.ford_model_action import FordModelActionController
from openpilot.sunnypilot.modeld_v2.constants import ModelConstants
from openpilot.sunnypilot.modeld_v2.ford_geometry import FordGeometryReference
from tools.ford_pscm_lab.model_action_replay import WireCheck, sample, table


def replay(label, output):
  source = Path('.cache')/f'ford_route{label}'
  meta = json.loads((source/'full/metadata.json').read_text())
  intake = json.loads((source/'intake.json').read_text())
  with np.load(source/'full/route.npz') as z:
    r = {k: table(z, k) for k in ('controls', 'cs', 'cc', 'params', 'pscm')}
  with np.load(source/'intake.npz') as z:
    m, paths, delays = z['model'], z['plans'], z['delay']
  c, t = r['controls'], r['controls']['t']
  cs, pa, ps = [sample(r[k], t) for k in ('cs', 'params', 'pscm')]
  cc = sample(r['cc'], t, nearest=True)
  mi = np.clip(np.searchsorted(m[:, 3], c['model_ns']), 0, len(m)-1)
  exact = m[mi, 3] == c['model_ns']
  # Approximation: first control sample consuming each model, not the unavailable
  # exact carState latched at inference start. No future model points are used.
  ci = np.clip(np.searchsorted(c['model_ns'], m[:, 3]), 0, len(t)-1)
  speed = np.maximum(cs['speed'][ci], 0.)  # modeld clamps the filtered speed at standstill.
  delay = delays[np.clip(np.searchsorted(delays[:, 0], m[:, 0], side='right')-1, 0, len(delays)-1), 3]
  settings = intake['settings'][0]['params']
  assert settings['FordC0TimeBased'] == '0' and settings['LagdToggle'] == '1'
  assert np.all(m[:, 6] == 1), 'This replay expects one big model throughout the route'
  bundle = next(b for b in intake['bundles'].values() if b['internalName'] == settings['ModelManager_ActiveBundleChestnut'])
  tau = float(next(o['value'] for o in bundle['overrides'] if o['key'] == 'lat'))
  preview = delay+tau+.075+.4*np.clip((30-speed/.44704)/15, 0, 1)
  reference = FordGeometryReference()
  geometry = np.empty(len(m))
  fallback = 0
  for j, p in enumerate(paths):
    result = reference.update(p[2], p[3], ModelConstants.T_IDXS, speed=speed[j], preview=preview[j],
                              smooth_seconds=tau, smoothing_enabled=bundle['generation'] >= 10)
    geometry[j] = np.float32(m[j, 7] if result is None else result[1])
    fallback += result is None
  car = {**json.loads(Path('.cache/ford_route112/metadata.json').read_text())['car'][0], **meta['car'][0]}
  cp = SimpleNamespace(**{k: car[k] for k in ('mass', 'wheelbase', 'centerToFront', 'steerRatioRear',
                                             'tireStiffnessFront', 'tireStiffnessRear')},
                       steerRatio=car['steer_ratio'], rotationalInertia=0.)
  vm = VehicleModel(cp)
  cores = [FordModelActionController(), FordModelActionController()]
  models = [SimpleNamespace(position=SimpleNamespace(x=p[0], y=p[1]), orientation=SimpleNamespace(z=p[2])) for p in paths]
  selected = [0., 0.]
  wires = [WireCheck(), WireCheck()]
  names = ['t', 'valid', 'feedback', 'speed', 'driver', 'actual_angle', 'action_angle', 'geometry_angle',
           'action_c0', 'geometry_c0', 'action_c1', 'geometry_c1']
  rows = np.empty((len(t), len(names)))
  for i, now in enumerate(t):
    good_params = np.isfinite([pa['stiffness'][i], pa['steer_ratio'][i]]).all() and min(pa['stiffness'][i], pa['steer_ratio'][i]) > 0
    if good_params:
      vm.update_params(max(pa['stiffness'][i], .1), max(pa['steer_ratio'][i], .1))
    scale = vm.get_steer_from_curvature(1., cs['speed'][i], 0.)/(cp.steerRatio*cp.wheelbase)
    valid = bool(c['valid'][i] and cc['valid'][i] and cs['valid'][i] and cs['can_valid'][i] and good_params
                 and pa['valid'][i] and m[mi[i], 2] and exact[i] and abs(cc['t'][i]-now) < .005
                 and 0 <= now-pa['t'][i] <= .15)
    status = SimpleNamespace(valid=bool(ps['valid'][i] and ps['status_valid'][i]), canMonoTime=round(ps['stamp'][i]*1e9),
                             limit=int(ps['limit'][i]), lateralState=int(ps['lateral_state'][i]), denied=bool(ps['denied'][i]))
    active = bool(cc['active'][i])
    targets = [m[mi[i], 7], geometry[mi[i]]]
    angles, commands = [], []
    for j, core in enumerate(cores):
      selected[j], _ = clip_curvature(cs['speed'][i], selected[j], targets[j] if active else c['measured'][i], pa['roll'][i])
      command = core.update(models[mi[i]], selected[j], current_curvature=c['measured'][i], yaw_rate=cs['yaw'][i],
                            speed=cs['speed'][i], now=now, measurement_time=cs['t'][i], model_time=m[mi[i], 0],
                            reference_time=m[mi[i], 0], active=active, valid=valid, curvature_scale=scale,
                            driver_pressed=bool(cs['pressed'][i]), driver_torque=cs['torque'][i], pscm_status=status)
      assert abs(command.path_offset) <= 5.1100001 and abs(command.path_angle) <= .5000001
      assert command.curvature == command.curvature_rate == 0.
      assert np.isfinite([command.path_offset, command.path_angle]).all()
      if not core.diagnostics.get('feedback_enabled', False):
        assert core.core.offset_proportional == core.core.correction == 0.
      if i % 10 == 0:
        wires[j].check(command)
      commands.append(command)
      angles.append(vm.get_steer_from_curvature(-selected[j], cs['speed'][i], pa['roll'][i])*180/np.pi+pa['angle_offset'][i])
    assert commands[0].valid == commands[1].valid
    a, b = commands
    rows[i] = [now-meta['t0'], b.valid, cores[1].diagnostics.get('feedback_enabled', False), cs['speed'][i],
               bool(cs['pressed'][i] or abs(cs['torque'][i]) > 1. or status.limit == 3), cs['angle'][i], *angles,
               a.path_offset, b.path_offset, a.path_angle, b.path_angle]
  eligible = rows[:, 1].astype(bool) & rows[:, 2].astype(bool)
  metrics = {}
  for name, mask in {'all': eligible, 'straight': eligible & (abs(rows[:, 6]) < 10),
                     'turn': eligible & (abs(rows[:, 6]) >= 45)}.items():
    if not mask.any():
      continue
    metrics[name] = {'samples': int(mask.sum()),
                     'angle_reference_difference_deg_p50_p95_max': np.quantile(abs(rows[mask, 7]-rows[mask, 6]), [.5, .95, 1.]).tolist(),
                     'action_c0_bound_samples': int((abs(rows[mask, 8]) >= 5.105).sum()),
                     'geometry_c0_bound_samples': int((abs(rows[mask, 9]) >= 5.105).sum()),
                     'action_c1_bound_samples': int((abs(rows[mask, 10]) >= .49975).sum()),
                     'geometry_c1_bound_samples': int((abs(rows[mask, 11]) >= .49975).sum())}
  sources = [source/'full/route.npz', source/'full/metadata.json', source/'intake.npz', source/'intake.json', Path(__file__),
             Path('openpilot/sunnypilot/modeld_v2/ford_geometry.py'), Path('openpilot/selfdrive/controls/lib/ford_model_action.py')]
  report = {'route': label, 'model': bundle['internalName'], 'cycles': len(t), 'model_frames': len(m), 'fallback_frames': fallback,
            'wire_round_trips': sum(w.count for w in wires), 'metrics': metrics,
            'sources_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
  dest = output/label
  dest.mkdir(parents=True, exist_ok=True)
  np.savez_compressed(dest/'commands.npz', names=names, rows=rows)
  (dest/'report.json').write_text(json.dumps(report, indent=2)+'\n')
  return report


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--output', type=Path, required=True)
  parser.add_argument('--routes', nargs='+', default=['149', '151', '157'])
  args = parser.parse_args()
  results = []
  with ProcessPoolExecutor(max_workers=3) as pool:
    for job in as_completed([pool.submit(replay, route, args.output) for route in args.routes]):
      result = job.result()
      results.append(result)
      print(json.dumps({k: v for k, v in result.items() if k != 'sources_sha256'}), flush=True)
  (args.output/'validation.json').write_text(json.dumps({'scope': __doc__, 'routes': results}, indent=2)+'\n')
