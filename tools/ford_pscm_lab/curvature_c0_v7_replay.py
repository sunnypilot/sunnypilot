"""Circular-arc C0 experiment against the pinned continuous PI v7 controller.

Both controllers run on identical recorded motion. Replace only the encoder's
C0 target, retaining path validity, C1 overflow, continuous PI feedback and
output limits. No onroad selector or production module is modified.
"""
import argparse
from collections import Counter
import hashlib
import math
from pathlib import Path
import json
from types import SimpleNamespace

import numpy as np

from openpilot.selfdrive.controls.lib.ford_path import FordPath
from tools.ford_pscm_lab.feedback_replay import OPENDBC, original_controller
from tools.ford_pscm_lab.model_action_replay import WireCheck, field_checks, sample, table, verify_dependency


BASELINE = '08b3a14ad46260fda0f8d3a1c2cee2d272504153'
GAIN = .50
STATION = 7.


def arc_offset(curvature):
  """Circular-arc y at 7 m arc length, starting at zero position/heading.

  Equivalent to (1-cos(7*k))/k; sinc avoids cancellation near zero.
  This is reference geometry, not an inverse PSCM response model.
  """
  half_heading = .5*STATION*curvature
  sinc = math.sin(half_heading)/half_heading if half_heading else 1.
  return .5*curvature*STATION**2*sinc**2


def make_controller(curvature_c0=False):
  # original_controller creates fresh, isolated module globals each time.
  # Patching this clone cannot alter production or the other replay controller.
  original, source_hash = original_controller(BASELINE)
  controller = type(original)(proportional_gain=GAIN)
  if curvature_c0:
    namespace = controller.core.update.__globals__
    original_encoder = namespace['encode_model_action']

    def encoder(model, desired_curvature, speed):
      target = original_encoder(model, desired_curvature, speed)
      if not target.valid:
        return target
      return FordPath(True, arc_offset(desired_curvature), target.path_angle, 0., 0.)

    namespace['encode_model_action'] = encoder
    controller.hypothesis = 'curvature-c0-continuous-pi-offline-v1'
    controller.reset()
  return controller, source_hash


def replay(directory, output):
  directory, output = directory.resolve(), output.resolve()
  if output == directory or directory in output.parents:
    raise ValueError('Output must be outside the source route directory')
  verify_dependency(OPENDBC)
  metadata = json.loads((directory/'metadata.json').read_text())
  with np.load(directory/'route.npz', allow_pickle=False) as z:
    r = {k: table(z, k) for k in ('controls', 'cs', 'cc', 'model', 'params', 'pscm')}
    if 'maneuver' in z and len(z['maneuver']):
      raise ValueError('Selected maneuver publications require a separate reference reconstruction')
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
  baseline, baseline_hash = make_controller()
  candidate, candidate_hash = make_controller(True)
  assert baseline_hash == candidate_hash
  controllers = (baseline, candidate)
  shape = (2, len(t))
  commands = np.zeros((*shape, 4))
  valid = np.zeros(shape, bool)
  names = ('heading_proportional', 'heading_correction', 'heading_feedforward', 'feedback_enabled',
           'offset_overflow', 'pscm_limited', 'pscm_status_fresh')
  diagnostic = {name: np.zeros(shape) for name in names}
  status_counts = [Counter(), Counter()]
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
    for k, controller in enumerate(controllers):
      command = controller.update(model, c['desired'][i], **kwargs)
      commands[k, i] = command.path_offset, command.path_angle, command.curvature, command.curvature_rate
      valid[k, i] = command.valid
      d = controller.diagnostics
      status_counts[k][d['status']] += 1
      for name in names:
        diagnostic[name][k, i] = d.get(name, 0.)
      wire.check(command)
  np.testing.assert_array_equal(valid[0], valid[1])
  for name in ('heading_proportional', 'heading_feedforward', 'feedback_enabled', 'offset_overflow', 'pscm_limited', 'pscm_status_fresh'):
    np.testing.assert_array_equal(diagnostic[name][0], diagnostic[name][1])
  assert status_counts[0] == status_counts[1]
  np.testing.assert_array_equal(commands[0, :, 1:], commands[1, :, 1:])
  np.testing.assert_array_equal(diagnostic['heading_correction'][0], diagnostic['heading_correction'][1])
  for k in range(2):
    field_checks(commands[k], valid[k], t)
    assert np.all(abs(diagnostic['heading_correction'][k]) <= 1.+1e-10)
    assert np.all(diagnostic['heading_correction'][k, diagnostic['feedback_enabled'][k] == 0.] == 0.)
  with np.load(directory/'angles.npz') as a:
    np.testing.assert_allclose(a['t'], t-metadata['t0'], atol=1e-8, rtol=0.)
    clean = a['clean'] & valid[0] & (diagnostic['feedback_enabled'][0] != 0.)
    weight = a['weight']
  report = {'scope': __doc__, 'baseline_revision': BASELINE, 'baseline_source_sha256': baseline_hash,
            'opendbc_revision': OPENDBC, 'proportional_gain': GAIN, 'integral_gain': .25, 'station_m': STATION,
            'cycles': len(t), 'controller_updates': 2*len(t), 'active_cycles_per_controller': int(valid[0].sum()),
            'can_round_trips': wire.count, 'status_counts': dict(status_counts[0]),
            'same_activation_p_feedforward_overflow_and_feedback_gates': True,
            'changed_c1_cycles': int(np.sum(commands[0, :, 1] != commands[1, :, 1])),
            'max_abs_c1_change_rad': float(abs(commands[0, :, 1]-commands[1, :, 1]).max()),
            'changed_integral_cycles': int(np.sum(diagnostic['heading_correction'][0] != diagnostic['heading_correction'][1])),
            'pscm_status_fresh_active_seconds': float(weight[valid[0] & (diagnostic['pscm_status_fresh'][0] != 0.)].sum()),
            'clean_seconds': float(weight[clean].sum()), 'car': metadata['car'], 'identities': metadata['identities'],
            'source_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                              (directory/'route.npz', directory/'model_paths.npz', directory/'metadata.json',
                               directory/'angles.npz', Path(__file__).resolve())},
            'limitations': ['No new steering trace or physical tracking score: recorded motion stays fixed.',
                            'The baseline is v7 on every route, regardless of its recorded controller version.',
                            'C1 and integral state match exactly on fixed recorded motion; physical feedback may differ.',
                            'Publication time proxies computation time; full SubMaster state is unavailable.',
                            'The synthetic arc keeps the original model-health gates for a controlled comparison.']}
  output.mkdir(parents=True, exist_ok=True)
  np.savez_compressed(output/'commands.npz', t=t-metadata['t0'], commands=commands, valid=valid, clean=clean, weight=weight,
                      desired_curvature=c['desired'], measured_curvature=c['measured'], desired_angle=c['desired_angle'],
                      actual_angle=c['actual_angle'], speed=cs['speed'], **diagnostic)
  (output/'report.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
  print(json.dumps({k: report[k] for k in ('cycles', 'can_round_trips', 'changed_c1_cycles', 'max_abs_c1_change_rad', 'clean_seconds')}))
  return report


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('directory', type=Path)
  parser.add_argument('--output', type=Path, required=True)
  args = parser.parse_args()
  replay(args.directory, args.output)
