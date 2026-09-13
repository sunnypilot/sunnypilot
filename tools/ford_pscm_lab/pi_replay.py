"""Compare explicit C1 P gains and feedback delays on fixed route measurements.

No PSCM plant is fitted. A change in command is not a predicted change in wheel
angle. Feedforward uses the current selected request. Only P and elapsed-distance
integration use the delayed request; v5's conditional I retirement is preserved.
"""
import argparse
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from openpilot.selfdrive.controls.lib import ford_model_action
from openpilot.selfdrive.controls.lib.ford_model_action import FordModelActionController
from tools.ford_pscm_lab.feedback_replay import OPENDBC, original_controller
from tools.ford_pscm_lab.model_action_replay import WireCheck, field_checks, sample, table, verify_dependency


BASELINE = '22d188776cb557acea459a1fca70812bdb2df46c'
GAINS = (0., .1, .25, .5)
DELAYS = (0., .2, .4)


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
  c, t = r['controls'], r['controls']['t']
  assert all(np.all(np.diff(stream['t']) >= 0.) for stream in r.values())
  cs, pa, ps = (sample(r[k], t) for k in ('cs', 'params', 'pscm'))
  cc = sample(r['cc'], t, nearest=True)
  mi = np.clip(np.searchsorted(r['model']['ns'], c['model_ns']), 0, len(r['model']['ns'])-1)
  exact = r['model']['ns'][mi] == c['model_ns']
  np.testing.assert_array_equal(model_ns, r['model']['ns'])
  models = [SimpleNamespace(position=SimpleNamespace(x=p[0], y=p[1]), orientation=SimpleNamespace(z=p[2])) for p in paths]
  settings = [(gain, delay) for delay in DELAYS for gain in GAINS]
  controllers = [FordModelActionController(proportional_gain=gain) for gain, _ in settings]
  reference, reference_hash = original_controller(BASELINE)
  delayed = {}
  for delay in DELAYS:
    # Causal history lookup at the steering measurement's time. Zero delay is
    # the original v5 same-cycle request, kept exact for baseline comparison.
    ix = np.searchsorted(t, cs['t']-delay, side='right')-1
    delayed[delay] = np.where(ix >= 0, c['desired'][np.maximum(ix, 0)], c['measured']) if delay else c['desired']
  shape = (len(settings), len(t))
  commands = np.zeros((*shape, 4))
  proportional, integral, feedforward, feedback_error = (np.zeros(shape) for _ in range(4))
  enabled = np.zeros(shape, bool)
  valid = np.zeros(shape, bool)
  wire = WireCheck()
  for i, now in enumerate(t):
    model_time = r['model']['t'][mi[i]]
    service_valid = bool(c['valid'][i] and cc['valid'][i] and cs['valid'][i] and cs['can_valid'][i]
                         and pa['valid'][i] and r['model']['valid'][mi[i]] and exact[i]
                         and abs(cc['t'][i]-now) < .005 and 0. <= now-pa['t'][i] <= .15)
    model = models[mi[i]] if exact[i] else None
    status = SimpleNamespace(valid=bool(ps['valid'][i] and ps['status_valid'][i]), canMonoTime=round(ps['stamp'][i]*1e9),
                             limit=int(ps['limit'][i]), lateralState=int(ps['lateral_state'][i]), denied=bool(ps['denied'][i]))
    kwargs = {'speed': cs['speed'][i], 'yaw_rate': cs['yaw'][i], 'now': now, 'measurement_time': cs['t'][i],
              'model_time': model_time, 'reference_time': model_time, 'active': bool(cc['active'][i]), 'valid': service_valid,
              'current_curvature': c['measured'][i], 'driver_pressed': bool(cs['pressed'][i]),
              'driver_torque': cs['torque'][i], 'pscm_status': status}
    old = reference.update(model, c['desired'][i], **kwargs)
    for k, (controller, (_, delay)) in enumerate(zip(controllers, settings, strict=True)):
      command = controller.update(model, c['desired'][i], feedback_curvature=delayed[delay][i], **kwargs)
      if k == 0:
        assert command == old
        assert controller.core.correction == reference.core.correction
      commands[k, i] = command.path_offset, command.path_angle, command.curvature, command.curvature_rate
      valid[k, i] = command.valid
      d = controller.diagnostics
      proportional[k, i] = d.get('heading_proportional', 0.)
      integral[k, i] = d.get('heading_correction', 0.)
      feedforward[k, i] = d.get('heading_feedforward', 0.)
      feedback_error[k, i] = delayed[delay][i]-c['measured'][i]
      enabled[k, i] = d.get('feedback_enabled', False)
      wire.check(command)
  for k in range(len(settings)):
    field_checks(commands[k], valid[k], t)
    np.testing.assert_array_equal(valid[k], valid[0])
    np.testing.assert_array_equal(commands[k, :, 0], commands[0, :, 0])
    assert np.all(proportional[k, ~enabled[k]] == 0.)
    assert np.all(integral[k, ~enabled[k]] == 0.)
    assert np.all(abs(integral[k]) <= 1.+1e-10)
  report = {'scope': __doc__, 'baseline_revision': BASELINE, 'baseline_source_sha256': reference_hash,
            'cycles': len(t), 'candidate_updates': len(settings)*len(t), 'can_round_trips': wire.count,
            'zero_gain_zero_delay_matches_v5_exactly': True, 'all_c0_and_activation_match_exactly': True,
            'calibration_approved': False, 'settings': [],
            'source_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                              (directory/'route.npz', directory/'model_paths.npz', directory/'metadata.json',
                               Path(__file__).resolve(), Path(ford_model_action.__file__).resolve())},
            'limitations': ['Recorded model, steering, driver and PSCM inputs stay fixed; no tracking improvement score.',
                            '0.2/0.4 s are diagnostic timing alternatives, not fitted or validated PSCM delays.',
                            'Gain sweep does not identify a physically optimal or stable gain.',
                            'Publication clock proxies computation time; maneuver references are not reconstructed.']}
  for k, (gain, delay) in enumerate(settings):
    report['settings'].append({'index': k, 'kp': gain, 'delay_s': delay,
                               'max_abs_c1_change_rad': float(abs(commands[k, :, 1]-commands[0, :, 1]).max()),
                               'max_abs_p_rad': float(abs(proportional[k]).max()),
                               'max_abs_i_rad': float(abs(integral[k]).max())})
  output.mkdir(parents=True, exist_ok=True)
  np.savez_compressed(output/'commands.npz', t=t-metadata['t0'], settings=np.array(settings), commands=commands,
                      valid=valid, proportional=proportional, integral=integral, feedforward=feedforward,
                      feedback_error=feedback_error, feedback_enabled=enabled,
                      desired_curvature=c['desired'], measured_curvature=c['measured'],
                      desired_angle=c['desired_angle'], actual_angle=c['actual_angle'], speed=cs['speed'])
  (output/'report.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
  print(json.dumps({k: v for k, v in report.items() if k != 'source_sha256'}, indent=2))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('directory', type=Path)
  parser.add_argument('--output', type=Path, required=True)
  args = parser.parse_args()
  replay(args.directory, args.output)
