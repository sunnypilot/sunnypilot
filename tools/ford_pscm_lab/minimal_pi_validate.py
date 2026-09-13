"""Verify production commands against the archived P=.50/I=.25 offline candidate.

Fixed recorded motion verifies integration parity, not physical tracking.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from openpilot.selfdrive.controls.lib import ford_model_action
from openpilot.selfdrive.controls.lib.ford_model_action import select_model_action_controller
from opendbc.car.ford.values import FordFlags
from tools.ford_pscm_lab.feedback_replay import OPENDBC
from tools.ford_pscm_lab.model_action_replay import WireCheck, field_checks, sample, table, verify_dependency


ROUTES = ('112', '113', '114', '115', '116', '117', 'a0', 'a2', 'a5', 'a9', 'b8', 'b9', 'ca', 'raptor02')
SELECTED = 4


def replay(label, output):
  directory = Path('.cache/ford_raptor_route02' if label == 'raptor02' else f'.cache/ford_route{label}').resolve()
  previous = Path('.cache/ford_minimal_tuning/sweep')/label
  output = (output/label).resolve()
  if output == directory or directory in output.parents or output == previous.resolve():
    raise ValueError('Output must preserve previous experiments and input extracts')
  verify_dependency(OPENDBC)
  archived_report = json.loads((previous/'report.json').read_text())
  assert archived_report['settings'][SELECTED] == ['unwind_p50_i25', .5, .25, True]
  for filename in ('route.npz', 'model_paths.npz', 'metadata.json'):
    path = directory/filename
    assert hashlib.sha256(path.read_bytes()).hexdigest() == archived_report['source_sha256'][str(path)]
  archived = dict(np.load(previous/'commands.npz', allow_pickle=False))
  metadata = json.loads((directory/'metadata.json').read_text())
  with np.load(directory/'route.npz', allow_pickle=False) as raw:
    r = {key: table(raw, key) for key in ('controls', 'cs', 'cc', 'model', 'params', 'pscm')}
    if 'maneuver' in raw and len(raw['maneuver']):
      raise ValueError('Maneuver reference reconstruction is not available in this sweep')
  with np.load(directory/'model_paths.npz', allow_pickle=False) as raw:
    model_ns, paths = raw['ns'], raw['paths']
  c, t = r['controls'], r['controls']['t']
  assert all(np.all(np.diff(stream['t']) >= 0.) for stream in r.values())
  np.testing.assert_allclose(archived['t'], t-metadata['t0'], rtol=0., atol=1e-8)
  cs, pa, ps = (sample(r[key], t) for key in ('cs', 'params', 'pscm'))
  cc = sample(r['cc'], t, nearest=True)
  mi = np.clip(np.searchsorted(r['model']['ns'], c['model_ns']), 0, len(r['model']['ns'])-1)
  exact = r['model']['ns'][mi] == c['model_ns']
  np.testing.assert_array_equal(model_ns, r['model']['ns'])
  models = [SimpleNamespace(position=SimpleNamespace(x=p[0], y=p[1]), orientation=SimpleNamespace(z=p[2])) for p in paths]
  cp = SimpleNamespace(brand='ford', flags=int(FordFlags.CANFD))
  assert select_model_action_controller(cp, False) is None
  controller = select_model_action_controller(cp, True)
  assert controller is not None
  assert (controller.core.proportional_gain, controller.core.integral_gain) == (.5, .25)
  shape = (len(t),)
  commands = np.zeros((*shape, 4))
  valid = np.zeros(shape, bool)
  names = ('heading_proportional', 'heading_correction', 'heading_feedforward', 'feedback_enabled', 'offset_overflow', 'pscm_limited')
  diagnostics = {name: np.zeros(shape) for name in names}
  wire = WireCheck()
  for i, now in enumerate(t):
    model_time = r['model']['t'][mi[i]]
    services_valid = bool(c['valid'][i] and cc['valid'][i] and cs['valid'][i] and cs['can_valid'][i]
                          and pa['valid'][i] and r['model']['valid'][mi[i]] and exact[i]
                          and abs(cc['t'][i]-now) < .005 and 0. <= now-pa['t'][i] <= .15)
    model = models[mi[i]] if exact[i] else None
    status = SimpleNamespace(valid=bool(ps['valid'][i] and ps['status_valid'][i]), canMonoTime=round(ps['stamp'][i]*1e9),
                             limit=int(ps['limit'][i]), lateralState=int(ps['lateral_state'][i]), denied=bool(ps['denied'][i]))
    kwargs = {'speed': cs['speed'][i], 'yaw_rate': cs['yaw'][i], 'now': now, 'measurement_time': cs['t'][i],
              'model_time': model_time, 'reference_time': model_time, 'active': bool(cc['active'][i]), 'valid': services_valid,
              'current_curvature': c['measured'][i], 'driver_pressed': bool(cs['pressed'][i]),
              'driver_torque': cs['torque'][i], 'pscm_status': status}
    command = controller.update(model, c['desired'][i], **kwargs)
    commands[i] = command.path_offset, command.path_angle, command.curvature, command.curvature_rate
    valid[i] = command.valid
    for name in names:
      diagnostics[name][i] = controller.diagnostics.get(name, 0.)
    wire.check(command)
  field_checks(commands, valid, t)
  np.testing.assert_array_equal(commands, archived['commands'][SELECTED])
  np.testing.assert_array_equal(valid, archived['valid'][SELECTED])
  for name in names:
    np.testing.assert_array_equal(diagnostics[name], archived[name][SELECTED])
  output.mkdir(parents=True, exist_ok=True)
  sources = (directory/'route.npz', directory/'model_paths.npz', directory/'metadata.json',
             previous/'report.json', previous/'commands.npz', Path(__file__).resolve(), Path(ford_model_action.__file__).resolve())
  result = {'scope': __doc__, 'route': label, 'cycles': len(t), 'can_round_trips': wire.count,
            'production_matches_archived_trial_exactly': True, 'opendbc_revision': OPENDBC,
            'hypothesis': controller.hypothesis, 'kp': .5, 'ki': .25,
            'source_sha256': {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in sources}}
  (output/'report.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
  return result


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--routes', nargs='+', choices=ROUTES, default=ROUTES)
  parser.add_argument('--output', type=Path, required=True)
  parser.add_argument('--workers', type=int, default=4)
  args = parser.parse_args()
  with ProcessPoolExecutor(max_workers=args.workers) as pool:
    jobs = {pool.submit(replay, label, args.output): label for label in args.routes}
    for job in as_completed(jobs):
      result = job.result()
      print(json.dumps({'completed': jobs[job], 'cycles': result['cycles'], 'can_checks': result['can_round_trips']}), flush=True)
