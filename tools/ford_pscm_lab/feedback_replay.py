"""Inspect C1 feedback commands on frozen route measurements, never vehicle motion.

Input: route.npz, model_paths.npz and metadata.json from the full-rlog extractor.
The recorded desired/actual curvature, clocks, driver input and PSCM flags stay
fixed. This verifies software behavior, not counterfactual physical tracking.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
from types import ModuleType, SimpleNamespace

import numpy as np

from openpilot.selfdrive.controls.lib import ford_model_action
from openpilot.selfdrive.controls.lib.ford_model_action import FordModelActionController, ModelActionController
from tools.ford_pscm_lab.model_action_replay import WireCheck, field_checks, sample, table, verify_dependency


BASELINE = 'a7d70e2b0890184636827351e4789d866f2a7c97'
OPENDBC = 'c21a9013700734dd20b09e05aa68329ad8cc20f9'


def original_controller():
  root = Path(__file__).resolve().parents[2]
  source = subprocess.check_output(['git', '-C', str(root), 'show',
                                   f'{BASELINE}:openpilot/selfdrive/controls/lib/ford_model_action.py'], text=True)
  module = ModuleType('ford_original_v1')
  exec(compile(source, f'{BASELINE}:ford_model_action.py', 'exec'), module.__dict__)
  return module.FordModelActionController(), hashlib.sha256(source.encode()).hexdigest()


def replay(directory, output):
  directory, output = directory.resolve(), output.resolve()
  if output == directory or directory in output.parents:
    raise ValueError('Output must be outside the source route directory')
  verify_dependency(OPENDBC)
  metadata = json.loads((directory/'metadata.json').read_text())
  with np.load(directory/'route.npz', allow_pickle=False) as z:
    r = {k: table(z, k) for k in ('controls', 'cs', 'cc', 'model', 'params', 'pscm')}
  with np.load(directory/'model_paths.npz', allow_pickle=False) as z:
    model_ns, paths = z['ns'], z['paths']
  for stream in r.values():
    if np.any(np.diff(stream['t']) < 0):
      raise ValueError('Source stream contains a backward clock')
  c = r['controls']
  t = c['t']
  cs, pa, ps = (sample(r[k], t) for k in ('cs', 'params', 'pscm'))
  cc = sample(r['cc'], t, nearest=True)
  mi = np.clip(np.searchsorted(r['model']['ns'], c['model_ns']), 0, len(r['model']['ns'])-1)
  exact = r['model']['ns'][mi] == c['model_ns']
  np.testing.assert_array_equal(model_ns, r['model']['ns'])
  models = [SimpleNamespace(position=SimpleNamespace(x=p[0], y=p[1]), orientation=SimpleNamespace(z=p[2])) for p in paths]
  old, baseline_hash = original_controller()
  controller, wire_check = FordModelActionController(), WireCheck()
  baseline = np.zeros((len(t), 4))
  commands = np.zeros_like(baseline)
  old_valid = np.zeros(len(t), bool)
  valid = np.zeros(len(t), bool)
  correction = np.zeros(len(t))
  feedback_dt = np.zeros(len(t))
  feedback_enabled = np.zeros(len(t), bool)
  pscm_limited = np.zeros(len(t), bool)
  reasons = Counter()
  for i, now in enumerate(t):
    model_time = r['model']['t'][mi[i]]
    service_valid = bool(c['valid'][i] and cc['valid'][i] and cs['valid'][i] and cs['can_valid'][i]
                         and pa['valid'][i] and r['model']['valid'][mi[i]] and exact[i]
                         and abs(cc['t'][i]-now) < .005 and 0. <= now-pa['t'][i] <= .15)
    common = {'speed': cs['speed'][i], 'yaw_rate': cs['yaw'][i], 'now': now,
              'measurement_time': cs['t'][i], 'model_time': model_time, 'reference_time': model_time,
              'active': bool(cc['active'][i]), 'valid': service_valid}
    model = models[mi[i]] if exact[i] else None
    status = SimpleNamespace(valid=bool(ps['valid'][i] and ps['status_valid'][i]), canMonoTime=round(ps['stamp'][i]*1e9),
                             limit=int(ps['limit'][i]), lateralState=int(ps['lateral_state'][i]), denied=bool(ps['denied'][i]))
    previous = old.update(model, c['desired'][i], **common)
    command = controller.update(model, c['desired'][i], current_curvature=c['measured'][i],
                                 driver_pressed=bool(cs['pressed'][i]), driver_torque=cs['torque'][i], pscm_status=status, **common)
    for destination, result in ((baseline, previous), (commands, command)):
      destination[i] = result.path_offset, result.path_angle, result.curvature, result.curvature_rate
    old_valid[i], valid[i] = previous.valid, command.valid
    d = controller.diagnostics
    reasons[d['status']] += 1
    correction[i] = controller.core.correction
    feedback_dt[i] = d.get('feedback_dt', 0.)
    feedback_enabled[i] = d.get('feedback_enabled', False)
    pscm_limited[i] = d.get('pscm_limited', False)
    wire_check.check(command)
  field_checks(commands, valid, t)
  np.testing.assert_array_equal(valid, old_valid)
  np.testing.assert_array_equal(commands[:, 0], baseline[:, 0])
  assert np.all(correction[~feedback_enabled] == 0.)
  assert np.all(abs(correction) <= 1.+1e-10)
  weight = np.minimum(np.diff(t, append=t[-1]+.01), .03)
  report = {'scope': __doc__, 'baseline_revision': BASELINE, 'baseline_source_sha256': baseline_hash,
            'calibration_approved': False, 'cycles': len(t), 'active_cycles': int(valid.sum()),
            'validity_and_c0_match_original_v1_exactly': True, 'status_counts': dict(reasons),
            'feedback_enabled_seconds': float(weight[feedback_enabled].sum()),
            'pscm_limit_2_seconds': float(weight[pscm_limited & valid].sum()),
            'c1_changed_cycles': int((abs(commands[:, 1]-baseline[:, 1]) > 1e-8).sum()),
            'max_abs_c1_change_rad': float(abs(commands[:, 1]-baseline[:, 1]).max()),
            'max_abs_correction_rad': float(abs(correction).max()), 'can_round_trips': wire_check.count,
            'source_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                              (directory/'route.npz', directory/'model_paths.npz', directory/'metadata.json',
                               Path(__file__).resolve(), Path(ford_model_action.__file__).resolve())},
            'timing_limit': 'Controls publication time proxies the computation clock; full SubMaster checks are unavailable.',
            'reference_limit': 'Uses exact consumed model publication as reference; the b8 route has no maneuver-plan messages.'}
  report['example_points'] = []
  for seconds in (130.937, 235.396, 236.250, 252.493, 674.430, 1534.519, 1562.507):
    i = int(np.argmin(abs(t-metadata['t0']-seconds)))
    report['example_points'].append({'time_s': float(t[i]-metadata['t0']), 'old_c0_c1': baseline[i, :2].tolist(),
                                     'candidate_c0_c1': commands[i, :2].tolist(), 'correction_rad': float(correction[i]),
                                     'feedback_enabled': bool(feedback_enabled[i]), 'pscm_limited': bool(pscm_limited[i])})
  output.mkdir(parents=True, exist_ok=True)
  np.savez_compressed(output/'commands.npz', t=t-metadata['t0'], baseline=baseline, candidate=commands, valid=valid,
                      correction=correction, feedback_dt=feedback_dt, feedback_enabled=feedback_enabled, pscm_limited=pscm_limited)
  (output/'report.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
  print(json.dumps({k: v for k, v in report.items() if k != 'source_sha256'}, indent=2))


def stress(cycles, output):
  verify_dependency(OPENDBC)
  rng = np.random.default_rng(20260909)
  controller, mirror, wire = ModelActionController(), ModelActionController(), WireCheck()
  for i in range(cycles):
    desired, measured = rng.uniform(-.1, .1, 2)
    speed, dt, offset = rng.uniform(.3, 55.), rng.uniform(.002, .1), rng.uniform(-8., 8.)
    active, enabled, limited = i % 211 != 0, i % 97 != 0, i % 7 == 0
    feedback_dt = 0. if i % 5 == 0 else rng.uniform(.002, .15)
    previous = controller.c0, controller.c1, controller.correction
    args = {'speed': speed, 'dt': dt, 'feedback_dt': feedback_dt, 'active': active,
            'feedback_enabled': enabled, 'pscm_limited': limited}
    def model(y):
      return SimpleNamespace(position=SimpleNamespace(x=[0., 20.], y=[y, y]), orientation=SimpleNamespace(z=[0., 0.]))
    out = controller.update(model(offset), desired, current_curvature=measured, **args)
    other = mirror.update(model(-offset), -desired, current_curvature=-measured, **args)
    state = controller.c0, controller.c1, controller.correction
    mirrored = mirror.c0, mirror.c1, mirror.correction
    np.testing.assert_allclose(state, -np.array(mirrored), rtol=0., atol=1e-10)
    assert abs(controller.c0) <= 5.11+1e-10 and abs(controller.c1) <= .5+1e-10 and abs(controller.correction) <= 1.+1e-10
    if active:
      assert abs(controller.c0-previous[0]) <= 4.*dt+1e-10
      assert abs(controller.c1-previous[1]) <= .5*dt+1e-10
      if enabled:
        delta = controller.correction-previous[2]
        request = (desired-measured)*speed*feedback_dt
        assert delta*request >= -1e-10 and abs(delta) <= abs(request)+1e-10
        if limited and request*(measured if measured else previous[1]) > 0.:
          assert abs(controller.correction) <= abs(previous[2])+1e-10
          assert controller.correction*previous[2] >= -1e-10
      else:
        assert controller.correction == 0.
    else:
      assert state == (0., 0., 0.)
    assert out.curvature == out.curvature_rate == other.curvature == other.curvature_rate == 0.
    wire.check(out)
  report = {'cycles': cycles, 'mirrored_updates': cycles, 'can_round_trips': wire.count,
            'checks': 'Mirror symmetry, reset/override, amplitude, slew, correction bounds, integration direction/size, PSCM anti-windup, CAN fields.',
            'scope': 'Numerical software invariants only; no model of vehicle motion.', 'calibration_approved': False,
            'controller_sha256': hashlib.sha256(Path(ford_model_action.__file__).read_bytes()).hexdigest()}
  output.parent.mkdir(parents=True, exist_ok=True)
  output.write_text(json.dumps(report, indent=2)+'\n')
  print(json.dumps(report, indent=2))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  sub = parser.add_subparsers(dest='mode', required=True)
  route = sub.add_parser('route')
  route.add_argument('directory', type=Path)
  route.add_argument('--output', type=Path, required=True)
  random = sub.add_parser('stress')
  random.add_argument('--cycles', type=int, default=200_000)
  random.add_argument('--output', type=Path, required=True)
  args = parser.parse_args()
  if args.mode == 'route':
    replay(args.directory, args.output)
  else:
    stress(args.cycles, args.output)
