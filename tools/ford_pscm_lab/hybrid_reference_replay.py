"""Offline action/geometry reference comparison on frozen recorded vehicle motion.

All variants share the current gains, driver gates and PSCM status. The direct
baseline keeps its independent C0 path mapping; scalar variants use the driven
curvature-to-C0/C1 mapper. This predicts commands, never the resulting trajectory.
"""
import argparse
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


def load_route(label):
  root = Path('.cache')/f'ford_route{label}'
  recent = label in ('15a', '15b')
  source = root/('rlog_full' if recent else 'full')
  meta = json.loads((source/'metadata.json').read_text())
  with np.load(source/'route.npz') as z:
    r = {k: table(z, k) for k in ('controls', 'cs', 'cc', 'path', 'params', 'pscm', 'model')}
    if recent:
      r['geometry'] = table(z, 'geometry')
  c = r['controls']
  t = c['t']
  cs, pa, ps = [sample(r[k], t) for k in ('cs', 'params', 'pscm')]
  cc, sent = [sample(r[k], t, nearest=True) for k in ('cc', 'path')]
  sources = [source/'route.npz', source/'metadata.json']
  if recent:
    with np.load(source/'model_paths.npz') as z:
      paths, ns = z['paths'], z['ns']
    g = r['geometry']
    gi = np.clip(np.searchsorted(g['model_ns'], ns), 0, len(g['t'])-1)
    assert np.array_equal(g['model_ns'][gi], ns)
    action = g['action'][gi]
    geometry = np.where(g['valid'][gi]*g['reference_valid'][gi] > 0, g['selected'][gi], action)
    geometry_method = 'Logged original action and selected geometry; exact model timestamp joins'
    sources.append(source/'model_paths.npz')
  else:
    with np.load(root/'intake.npz') as z:
      m, paths, delay = z['model'], z['plans'], z['delay']
    intake = json.loads((root/'intake.json').read_text())
    settings = intake['settings'][0]['params']
    bundle = next(b for b in intake['bundles'].values() if b['internalName'] == settings['ModelManager_ActiveBundleChestnut'])
    tau = float(next(o['value'] for o in bundle['overrides'] if o['key'] == 'lat'))
    ns, action = m[:, 3], m[:, 7]
    ci = np.clip(np.searchsorted(c['model_ns'], ns), 0, len(t)-1)
    speed = np.maximum(cs['speed'][ci], 0.)
    learned_delay = delay[np.clip(np.searchsorted(delay[:, 0], m[:, 0], side='right')-1, 0, len(delay)-1), 3]
    preview = learned_delay+tau+.075+.4*np.clip((30-speed/.44704)/15, 0, 1)
    reference = FordGeometryReference()
    geometry = np.empty(len(m))
    for j, path in enumerate(paths):
      result = reference.update(path[2], path[3], ModelConstants.T_IDXS, speed=speed[j], preview=preview[j],
                                smooth_seconds=tau, smoothing_enabled=bundle['generation'] >= 10)
      geometry[j] = action[j] if result is None else np.float32(result[1])
    geometry_method = 'Reconstructed geometry with recorded delay/model smoothing; speed approximated by first consuming control sample'
    sources += [root/'intake.npz', root/'intake.json']
  mi = np.clip(np.searchsorted(ns, c['model_ns']), 0, len(ns)-1)
  exact = ns[mi] == c['model_ns']
  models = [SimpleNamespace(position=SimpleNamespace(x=p[0], y=p[1]), orientation=SimpleNamespace(z=p[2]),
                            action=SimpleNamespace(desiredCurvature=float(action[j])),
                            fordGeometryReference=SimpleNamespace(enabled=True, valid=True, modelMonoTime=int(ns[j]),
                                                                  selectedCurvature=float(geometry[j]))) for j, p in enumerate(paths)]
  active = cc['active'].astype(bool)
  valid = c['valid']*cs['valid']*cs['can_valid']*pa['valid'] > 0
  valid &= exact & (abs(t-cs['t']) <= .15) & (t-c['model_ns']*1e-9 >= -.005) & (t-c['model_ns']*1e-9 <= .15)
  valid &= (cs['speed'] >= .3) & (cs['speed'] <= 55.)
  car = meta['car'][0]
  cp = SimpleNamespace(**{k: car[k] for k in ('mass', 'wheelbase', 'centerToFront', 'steerRatioRear', 'tireStiffnessFront', 'tireStiffnessRear')},
                       steerRatio=car['steer_ratio'], rotationalInertia=0.)
  summary = (Path('.cache/ford_routes158_159')/f'{label}_summary.json') if recent else root/'summary.json'
  events = json.loads(summary.read_text())['events']
  return SimpleNamespace(label=label, source=source, meta=meta, c=c, t=t, cs=cs, pa=pa, ps=ps, sent=sent,
                         active=active, valid=valid, models=models, mi=mi, action=action[mi], geometry=geometry[mi], cp=cp,
                         events=events, sources=sources, geometry_method=geometry_method)


def sustained(t, mask, seconds=.2):
  indices = np.flatnonzero(mask)
  if not len(indices):
    return None
  breaks = np.r_[0, np.flatnonzero((np.diff(indices) > 1) | (np.diff(t[indices]) > .03))+1, len(indices)]
  for start, end in zip(breaks[:-1], breaks[1:], strict=True):
    if t[indices[end-1]]-t[indices[start]] >= seconds:
      return float(t[indices[start]])
  return None


def summarize(d, a, names):
  t = a['t']
  live = a['valid'].astype(bool)
  dt = np.minimum(np.diff(t, append=t[-1]+.01), .03)
  consecutive = live[1:] & live[:-1] & (np.diff(t) < .03)
  low = consecutive & (a['speed'][1:] < 15*.44704)
  ordinary = live & (abs(d.action) < .01) & (abs(d.geometry) < .01)
  results = {'cycles': len(t), 'active_valid_s': float(dt[live].sum()), 'geometry_source': d.geometry_method,
             'ordinary_definition': 'Both action and geometry below 0.01 1/m; includes state carried out of earlier turns',
             'variants': {}, 'events': []}
  for name in names:
    results['variants'][name] = {
      'c0_bound_s': float(dt[live & (abs(a[name+'_c0']) >= 5.105)].sum()),
      'c1_bound_s': float(dt[live & (abs(a[name+'_c1']) >= .49975)].sum()),
      'low_speed_c0_steps_over_025m': int((abs(np.diff(a[name+'_c0'])[low]) > .250001).sum()),
      'low_speed_c1_steps_over_005rad': int((abs(np.diff(a[name+'_c1'])[low]) > .050001).sum()),
      'ordinary_difference_from_action_p50_p95_max': {
        k: np.quantile(abs(a[name+'_'+k][ordinary]-a['action_'+k][ordinary]), [.5, .95, 1]).tolist() for k in ('angle', 'c0', 'c1')},
    }
  for e in d.events:
    lo, hi = e['window']
    window = live & (t >= lo) & (t <= hi)
    if not window.any():
      continue
    sign = 1 if e['direction'] == 'left' else -1
    action_peak_i = np.flatnonzero(window)[np.argmax(sign*a['action_angle'][window])]
    action_peak_t = t[action_peak_i]
    build = window & (t <= action_peak_t)
    release = window & (t >= action_peak_t)
    item = {'id': e['id'], 'direction': e['direction'], 'window': [lo, hi], 'action_peak_t': float(action_peak_t), 'variants': {}}
    extra = sign*(a['geometry_angle']-a['action_angle'])
    assist = build & (extra > 5.) & (sign*a['action_angle'] > 0.) & (sign*a['geometry_angle'] > 50.)
    for name in names:
      angle = sign*a[name+'_angle']
      last_above = np.flatnonzero(release & (angle >= 25.))
      last_c1 = np.flatnonzero(release & (-sign*a[name+'_c1'] >= .05))
      item['variants'][name] = {
        'peak_angle_deg': float(max(angle[window])),
        'entry_50_s': sustained(t, build & (angle >= 50.)),
        'release_25_s': sustained(t, release & (angle < 25.)),
        'last_above_25_s': float(t[last_above[-1]]) if len(last_above) else None,
        'peak_abs_c0': float(max(abs(a[name+'_c0'][window]))), 'peak_abs_c1': float(max(abs(a[name+'_c1'][window]))),
        'c1_release_005_s': sustained(t, release & (-sign*a[name+'_c1'] < .05)),
        'c1_last_above_005_s': float(t[last_c1[-1]]) if len(last_c1) else None,
        'entry_geometry_extra_retained_fraction': (float(np.sum(sign*(a[name+'_angle']-a['action_angle'])[assist]*dt[assist]) /
                                                            np.sum(extra[assist]*dt[assist])) if assist.any() else None),
      }
    results['events'].append(item)
  return results


def run(label, output, baseline=None):
  d = load_route(label)
  names = ['action', 'geometry', 'direct', 'stronger', 'half', 'hybrid']
  evaluated = ['hybrid'] if baseline else names
  cores = [FordModelActionController(direct_path=name == 'direct', geometry_assist=name == 'hybrid') for name in evaluated]
  wires = [WireCheck() for _ in evaluated]
  hybrid_controller = cores[evaluated.index('hybrid')]
  hybrid = hybrid_controller.geometry_assist
  selected = np.zeros(len(evaluated))
  vm = VehicleModel(d.cp)
  columns = ['t', 'valid', 'active', 'speed', 'driver', 'wheel', 'weight', 'action_peak', 'action_raw', 'geometry_raw']
  for name in names:
    columns.extend(name+'_'+k for k in ('reference', 'angle', 'c0', 'c1', 'i'))
  rows = np.empty((len(d.t), len(columns)))
  saved_columns = list(range(10))+[columns.index(name+'_'+k) for name in evaluated for k in ('reference', 'angle', 'c0', 'c1', 'i')]
  if baseline:
    with np.load(baseline/label/'commands.npz') as z:
      assert z['names'].tolist() == columns
      rows[:] = z['rows']
    np.testing.assert_allclose(rows[:, 0], d.t-d.meta['t0'], atol=1e-9)
  for i, now in enumerate(d.t):
    cs, pa, ps, c = d.cs, d.pa, d.ps, d.c
    vm.update_params(max(pa['stiffness'][i], .1), max(pa['steer_ratio'][i], .1))
    scale = vm.get_steer_from_curvature(1., cs['speed'][i], 0.)/(d.cp.steerRatio*d.cp.wheelbase)
    error = c['desired'][i]-c['measured'][i]
    angle_scale = -vm.sR/vm.curvature_factor(cs['speed'][i])*180./np.pi
    if abs(error) > 1e-5:
      angle_scale = (c['desired_angle'][i]-c['actual_angle'][i])/error
      scale = -np.radians(angle_scale)/(d.cp.steerRatio*d.cp.wheelbase)
    status = SimpleNamespace(valid=bool(ps['valid'][i] and ps['status_valid'][i]), canMonoTime=round(ps['stamp'][i]*1e9),
                             limit=int(ps['limit'][i]), lateralState=int(ps['lateral_state'][i]), denied=bool(ps['denied'][i]))
    action, geometry = float(d.action[i]), float(d.geometry[i])
    maximum = geometry if action*geometry > 0 and abs(geometry) > abs(action) else action
    combined = hybrid_controller.select_reference(d.models[d.mi[i]], model_mono_time=int(c['model_ns'][i]),
                                                  active=bool(d.active[i]), valid=bool(d.valid[i]))
    targets = {'action': action, 'geometry': geometry, 'stronger': maximum, 'half': .5*(action+geometry), 'hybrid': combined}
    if 'direct' in evaluated:
      targets['direct'] = cores[evaluated.index('direct')].path_curvature(d.models[d.mi[i]], cs['speed'][i])
    row = [now-d.meta['t0'], False, d.active[i], cs['speed'][i],
           cs['pressed'][i] or abs(cs['torque'][i]) > 1. or status.limit == 3, c['actual_angle'][i],
           hybrid.weight, hybrid.action_peak, action, geometry]
    validity = []
    for j, (core, name) in enumerate(zip(cores, evaluated, strict=True)):
      target = targets[name]
      selected[j], _ = clip_curvature(cs['speed'][i], selected[j], target if d.active[i] else c['measured'][i], pa['roll'][i])
      command = core.update(d.models[d.mi[i]], selected[j], current_curvature=c['measured'][i],
                            speed=cs['speed'][i], yaw_rate=cs['yaw'][i], now=now, measurement_time=cs['t'][i],
                            model_time=c['model_ns'][i]*1e-9, reference_time=c['model_ns'][i]*1e-9,
                            active=bool(d.active[i]), valid=bool(d.valid[i]),
                            driver_pressed=bool(cs['pressed'][i]), driver_torque=cs['torque'][i],
                            pscm_status=status, curvature_scale=scale, roll=pa['roll'][i])
      assert np.isfinite([command.path_offset, command.path_angle]).all()
      assert abs(command.path_offset) <= 5.1100001 and abs(command.path_angle) <= .5000001
      assert command.curvature == command.curvature_rate == 0.
      if command.valid and row[4] and (status.limit != 3 or (status.valid and -.005 <= now-ps['stamp'][i] <= .15)):
        assert not core.diagnostics['feedback_enabled']
        assert core.core.correction == core.core.proportional == core.core.offset_proportional == 0.
      if i % 10 == 0:
        wires[j].check(command)
      angle = c['desired_angle'][i]+angle_scale*(selected[j]-c['desired'][i])
      row.extend([selected[j], angle, command.path_offset, command.path_angle, core.core.correction])
      validity.append(command.valid)
    assert all(v == validity[0] for v in validity)
    row[1] = validity[0]
    if baseline:
      assert rows[i, 1] == row[1]
    rows[i, saved_columns] = row
  a = dict(zip(columns, rows.T, strict=True))
  results = summarize(d, a, names)
  results['wire_checks'] = sum(w.count for w in wires)
  results['variants_evaluated_this_run'] = evaluated
  results['cached_baseline'] = str(baseline/label) if baseline else None
  results['reference_design'] = {'start_curvature': hybrid.start, 'full_curvature': hybrid.full, 'release_power': hybrid.release_power}
  files = d.sources+[Path(__file__), Path('openpilot/selfdrive/controls/lib/ford_geometry_action.py'),
                     Path('openpilot/selfdrive/controls/lib/ford_model_action.py')]
  if baseline:
    files += [baseline/label/'commands.npz', baseline/label/'report.json']
  results['sources_sha256'] = {str(f): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
  dest = output/label
  dest.mkdir(parents=True, exist_ok=True)
  np.savez_compressed(dest/'commands.npz', names=columns, rows=rows)
  (dest/'report.json').write_text(json.dumps(results, indent=2, allow_nan=False)+'\n')
  print(json.dumps({'route': label, 'cycles': results['cycles'], 'wire_checks': results['wire_checks'], 'events': len(results['events'])}), flush=True)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--route', required=True)
  parser.add_argument('--output', type=Path, required=True)
  parser.add_argument('--baseline', type=Path, help='Reuse unchanged baseline columns and replay the hybrid only')
  args = parser.parse_args()
  run(args.route, args.output, args.baseline)
