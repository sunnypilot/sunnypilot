"""Compare v8 and direct C0/C1 on fixed logged inputs, without predicting motion."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from openpilot.selfdrive.controls.lib import ford_model_action
from tools.ford_pscm_lab.feedback_replay import OPENDBC, original_controller
from tools.ford_pscm_lab.model_action_replay import WireCheck, sample, table, verify_dependency

BASELINE = '57ae29f257498f58170e2beec140c0f8103c1b43'


def replay(directory, output, maneuver=None):
  verify_dependency(OPENDBC)
  with np.load(directory/'route.npz', allow_pickle=False) as z:
    r = {k: table(z, k) for k in ('controls', 'cs', 'cc', 'model', 'params', 'pscm')}
  c = r['controls']
  t = c['t']
  md = r['model']
  cs, pa, ps = (sample(r[k], t) for k in ('cs', 'params', 'pscm'))
  cc = sample(r['cc'], t, nearest=True)
  mi = np.clip(np.searchsorted(md['ns'], c['model_ns']), 0, len(md['ns'])-1)
  exact = md['ns'][mi] == c['model_ns']
  with np.load(directory/'model_paths.npz', allow_pickle=False) as z:
    np.testing.assert_array_equal(z['ns'], md['ns'])
    models = [SimpleNamespace(position=SimpleNamespace(x=p[0], y=p[1]), orientation=SimpleNamespace(z=p[2])) for p in z['paths']]
  reference_time = md['t'][mi].copy()
  if maneuver is not None:
    # Valid synthetic publications supersede model references only while fresh.
    with np.load(maneuver, allow_pickle=False) as z:
      mt = z['plans'][:, 0]
    idx = np.clip(np.searchsorted(mt, t, side='right')-1, 0, len(mt)-1)
    fresh = (t >= mt[idx]) & (t-mt[idx] <= .06)
    reference_time[fresh] = mt[idx[fresh]]
  old, source_hash = original_controller(BASELINE)
  controllers = [old, ford_model_action.FordModelActionController()]
  commands = np.zeros((2, len(t), 4))
  valid = np.zeros((2, len(t)), bool)
  names = ('heading_feedforward', 'heading_proportional', 'heading_correction', 'feedback_enabled', 'pscm_limited')
  diagnostics = {name: np.zeros((2, len(t))) for name in names}
  statuses = [Counter(), Counter()]
  wire = WireCheck()
  for i, now in enumerate(t):
    healthy = bool(c['valid'][i] and cc['valid'][i] and cs['valid'][i] and cs['can_valid'][i] and pa['valid'][i]
                   and md['valid'][mi[i]] and exact[i] and abs(cc['t'][i]-now) < .005 and 0. <= now-pa['t'][i] <= .15)
    status = SimpleNamespace(valid=bool(ps['valid'][i] and ps['status_valid'][i]), canMonoTime=round(ps['stamp'][i]*1e9),
                             limit=int(ps['limit'][i]), lateralState=int(ps['lateral_state'][i]), denied=bool(ps['denied'][i]))
    kwargs = {'current_curvature': c['measured'][i], 'yaw_rate': cs['yaw'][i], 'speed': cs['speed'][i], 'now': now,
              'measurement_time': cs['t'][i], 'model_time': md['t'][mi[i]], 'reference_time': reference_time[i],
              'active': bool(cc['active'][i]), 'valid': healthy, 'driver_pressed': bool(cs['pressed'][i]),
              'driver_torque': cs['torque'][i], 'pscm_status': status}
    for k, controller in enumerate(controllers):
      command = controller.update(models[mi[i]] if exact[i] else None, c['desired'][i], **kwargs)
      commands[k, i] = command.path_offset, command.path_angle, command.curvature, command.curvature_rate
      valid[k, i] = command.valid
      d = controller.diagnostics
      statuses[k][d['status']] += 1
      for name in names:
        diagnostics[name][k, i] = d.get(name, 0.)
      if k == 1 and command.valid:
        raw = max(7., cs['speed'][i])*c['desired'][i]
        base = min(.5, max(-.5, raw))
        curvature = c['desired'][i]
        half = 3.5*curvature
        sinc = np.sinc(half/np.pi)
        expected_c0 = min(5.11, max(-5.11, 24.5*curvature*sinc*sinc+7.*(raw-base)))
        expected_c1 = min(.5, max(-.5, base+d['heading_proportional']+d['heading_correction']))
        assert abs(command.path_offset-expected_c0) <= .0050001
        assert abs(command.path_angle-expected_c1) <= .0002501
      wire.check(command)
  np.testing.assert_array_equal(valid[0], valid[1])
  assert statuses[0] == statuses[1]
  for name in ('heading_feedforward', 'heading_proportional', 'feedback_enabled', 'pscm_limited'):
    np.testing.assert_array_equal(diagnostics[name][0], diagnostics[name][1])
  assert np.isfinite(commands).all()
  assert np.all(abs(commands[:, :, :2]) <= [5.1100001, .5000001])
  assert np.all(commands[:, :, 2:] == 0.)
  assert np.all(commands[~valid] == 0.)
  assert np.all(diagnostics['heading_correction'][diagnostics['feedback_enabled'] == 0.] == 0.)
  delta = abs(commands[1]-commands[0])
  result = {'scope': __doc__, 'baseline': BASELINE, 'baseline_source_sha256': source_hash,
            'cycles': len(t), 'controller_updates': 2*len(t), 'can_round_trips': wire.count,
            'status_counts': dict(statuses[1]), 'identical_validity_feedforward_p_and_feedback_gates': True,
            'all_candidate_outputs_match_current_bounded_request': True,
            'changed_c0_cycles': int((delta[:, 0] > 1e-8).sum()), 'changed_c1_cycles': int((delta[:, 1] > 1e-8).sum()),
            'max_abs_c0_change_m': float(delta[:, 0].max()), 'max_abs_c1_change_rad': float(delta[:, 1].max()),
            'max_abs_integral_rad': float(abs(diagnostics['heading_correction'][1]).max()),
            'limitations': ['Recorded motion remains fixed; this cannot establish improved tracking or stability.',
                            'Publication time proxies computation time; reconstructed baseline is not exact onroad parity.',
                            'Synthetic reference freshness is approximated from valid publications; upstream selection itself is unchanged.'],
            'source_sha256': {str(p.resolve()): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                              (directory/'route.npz', directory/'model_paths.npz', Path(__file__), Path(ford_model_action.__file__))}}
  output.mkdir(exist_ok=True, parents=True)
  (output/'report.json').write_text(json.dumps(result, indent=2)+'\n')
  np.savez_compressed(output/'commands.npz', t=t, commands=commands, valid=valid, **diagnostics)
  print(json.dumps(result), flush=True)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('directory', type=Path)
  parser.add_argument('--output', type=Path, required=True)
  parser.add_argument('--maneuver', type=Path)
  args = parser.parse_args()
  replay(args.directory, args.output, args.maneuver)
