"""Replay the selected core and its adapter on route90/95 original-time extracts.

The historical pass deliberately uses the archived eligibility mask to check
command compatibility. The separate adapter pass reconstructs input eligibility
from service records, never from candidate/baseline output validity. Neither
pass scores counterfactual motion. Source extracts and archived reports are
read-only; --output selects a separate destination.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import numpy as np
import opendbc
from opendbc.can import CANPacker, CANParser
from opendbc.car.ford.fordcan import CanBus, create_lat_ctl2_msg
from openpilot.cereal import custom
from openpilot.selfdrive.controls.lib import ford_model_action
from openpilot.selfdrive.controls.lib.ford_model_action import FordModelActionController, ModelActionController
from openpilot.selfdrive.controls.lib.ford_path import _model_path


PINNED_OPENDBC = '72a775d35e54c21ff5c5798acef22016eedcc0a7'


def revision(directory):
  return subprocess.check_output(['git', '-C', str(directory), 'rev-parse', 'HEAD'], text=True).strip()


def verify_dependency(expected=PINNED_OPENDBC):
  directory = Path(opendbc.__file__).resolve().parent.parent
  actual = revision(directory)
  if actual != expected:
    raise ValueError(f'Expected opendbc {expected}; imported {directory} at {actual}')
  return directory


def table(raw, name):
  return dict(zip(raw[name+'_names'], raw[name].T, strict=True))


def sample(stream, query, *, nearest=False):
  if len(stream['t']) == 0 or np.any(np.diff(stream['t']) < 0):
    raise ValueError('Replay requires nonempty streams in original timestamp order')
  if nearest:
    right = np.clip(np.searchsorted(stream['t'], query), 0, len(stream['t'])-1)
    left = np.maximum(right-1, 0)
    index = np.where(abs(stream['t'][right]-query) < abs(stream['t'][left]-query), right, left)
  else:
    index = np.clip(np.searchsorted(stream['t'], query, side='right')-1, 0, len(stream['t'])-1)
  return {key: values[index] for key, values in stream.items()}


def field_checks(command, valid, t):
  assert np.isfinite(command).all()
  assert (abs(command[:, :2]) <= [5.1100001, .5000001]).all()
  assert (command[:, 2:] == 0.).all()
  assert (command[~valid] == 0.).all()
  dt = np.r_[.01, np.diff(t)]
  consecutive = valid[1:] & valid[:-1]
  assert (abs(np.diff(command[:, :2], axis=0))[consecutive] <=
          (dt[1:, None]*[4., .5]+[.0100001, .0005001])[consecutive]).all()
  return True


class WireCheck:
  """Real Float32 publication and in-memory CAN round trips on every cycle."""
  def __init__(self):
    self.packer = CANPacker('ford_lincoln_base_pt')
    self.parser = CANParser('ford_lincoln_base_pt', [('LateralMotionControl2', 100)], 0)
    self.bus = CanBus(fingerprint={0: {}})
    self.count = 0

  def check(self, path):
    msg = custom.CarControlSP.new_message()
    msg.fordLateralPath.valid = path.valid
    msg.fordLateralPath.pathOffset = path.path_offset
    msg.fordLateralPath.pathAngle = path.path_angle
    msg.fordLateralPath.curvature = path.curvature
    msg.fordLateralPath.curvatureRate = path.curvature_rate
    p = msg.fordLateralPath
    counter = self.count % 16
    packet = create_lat_ctl2_msg(self.packer, self.bus, 2 if path.valid else 0,
                                -p.pathOffset, -p.pathAngle, -p.curvature, -p.curvatureRate, counter)
    self.count += 1
    # Synthetic parser clock only; input times and gaps are never resampled.
    self.parser.update([self.count*10_000_000, [packet]])
    decoded = self.parser.vl['LateralMotionControl2']
    assert abs(decoded['LatCtlPathOffst_L_Actl']+path.path_offset) < 1e-9
    assert abs(decoded['LatCtlPath_An_Actl']+path.path_angle) < 1e-9
    assert decoded['LatCtlCurv_No_Actl'] == decoded['LatCtlCrv_NoRate2_Actl'] == 0.
    assert decoded['LatCtl_D2_Rq'] == (2 if path.valid else 0)
    assert decoded['LatCtlPath_No_Cnt'] == counter


def run(directory, output):
  directory, output = directory.resolve(), output.resolve()
  if output == directory or directory in output.parents:
    raise ValueError('Output must be outside the source route directory')
  dependency = verify_dependency()
  with np.load(directory/'route.npz', allow_pickle=False) as raw:
    streams = {name: table(raw, name) for name in ('controls', 'cs', 'cc', 'model', 'params', 'path')}
    if len(raw['maneuver']):
      raise ValueError('This extract cannot identify the selected maneuver service per cycle; use the integration tests for that source')
    models = [SimpleNamespace(position=SimpleNamespace(x=p[1], y=p[2]), orientation=SimpleNamespace(z=p[3])) for p in raw['model_paths']]
  with np.load(directory/'encoder_comparison.npz', allow_pickle=False) as archive:
    baseline = {key: archive[key] for key in ('t', 'valid', 'action_heading')}
  with np.load(directory/'pose_candidate/pose_replay.npz', allow_pickle=False) as pose:
    np.testing.assert_array_equal(pose['t'], baseline['t'])
    clean = pose['clean']
  controls = streams['controls']
  t = controls['t']
  np.testing.assert_array_equal(t, baseline['t'])
  cs, params = (sample(streams[name], t) for name in ('cs', 'params'))
  cc = sample(streams['cc'], t, nearest=True)  # same-cycle publication match, never a motion sample
  mi = np.clip(np.searchsorted(streams['model']['ns'], controls['model_ns']), 0, len(models)-1)
  model = {key: values[mi] for key, values in streams['model'].items()}
  exact = model['ns'] == controls['model_ns']
  services_valid = ((controls['valid'] == 1) & (cc['valid'] == 1) & (abs(cc['t']-t) < .005) &
                    (cs['valid'] == 1) & (cs['can_valid'] == 1) & (params['valid'] == 1) &
                    (t-params['t'] >= 0.) & (t-params['t'] <= .15) & exact & (model['valid'] == 1))
  dt = np.r_[.01, np.diff(t)]
  core, entry_clock_core, adapter, wire = ModelActionController(), ModelActionController(), FordModelActionController(), WireCheck()
  commands = np.zeros((len(t), 4))
  adapted = np.zeros_like(commands)
  valid = np.zeros(len(t), bool)
  adapter_valid = np.zeros_like(valid)
  reasons = Counter()
  for i, now in enumerate(t):
    selected_model = models[mi[i]] if exact[i] else None
    old_gate = core.update(selected_model, controls['desired'][i], speed=cs['speed'][i], dt=dt[i], active=bool(baseline['valid'][i]))
    commands[i] = old_gate.path_offset, old_gate.path_angle, old_gate.curvature, old_gate.curvature_rate
    valid[i] = old_gate.valid
    wire.check(old_gate)
    new_gate = adapter.update(selected_model, controls['desired'][i], speed=cs['speed'][i], yaw_rate=cs['yaw'][i], now=now,
                              measurement_time=cs['t'][i], model_time=model['t'][i], reference_time=model['t'][i],
                              active=bool(cc['active'][i]), valid=bool(services_valid[i]))
    adapted[i] = new_gate.path_offset, new_gate.path_angle, new_gate.curvature, new_gate.curvature_rate
    adapter_valid[i] = new_gate.valid
    reasons[adapter.diagnostics['status']] += 1
    wire.check(new_gate)
    # Isolate the adapter's fresh 10 ms engagement tick from the archived
    # harness, which used the preceding publication interval even on engage.
    entry_dt = dt[i] if i > 0 and baseline['valid'][i-1] else .01
    expected_adapter = entry_clock_core.update(selected_model, controls['desired'][i], speed=cs['speed'][i], dt=entry_dt,
                                               active=bool(baseline['valid'][i]))
    assert new_gate == expected_adapter, f'Unexplained adapter difference at cycle {i}'
  np.testing.assert_array_equal(valid, baseline['valid'])
  np.testing.assert_array_equal(commands[:, :2], baseline['action_heading'])
  field_checks(commands, valid, t)
  field_checks(adapted, adapter_valid, t)

  # Recompute the archived cohorts from actual commands, retaining the original
  # interval-clean driver mask and time weights. No recorded yaw performance score.
  v = cs['speed']
  demand = abs(controls['desired'])*v**2
  masks = {'small_request': clean & (demand < .15), 'turn': clean & (demand >= .5)}
  for low, high in ((2, 8), (8, 15), (15, 55)):
    for name in ('small', 'turn'):
      masks[f'{name}_speed_{low}_{high}'] = masks['small_request' if name == 'small' else name] & (v >= low) & (v < high)
  paths = [_model_path(m) for m in models]
  y10 = np.array([np.interp(10., p[0], p[2]) if p is not None else np.nan for p in paths])
  h10 = np.array([np.interp(10., p[0], p[3]) if p is not None else np.nan for p in paths])
  coverage = np.array([p[0][-1] if p is not None else 0. for p in paths])[mi]
  masks['pose_quiet'] = masks['small_request'] & (v >= 8) & (abs(y10[mi]) <= .1) & (abs(h10[mi]) <= np.radians(.5))
  recorded = sample(streams['path'], t, nearest=True)
  recorded = np.column_stack((recorded['c0'], recorded['c1']))
  weight = np.minimum(np.diff(t, append=t[-1]+.01), .03)
  cohorts = {}
  previous_report = json.loads((directory/'encoder_comparison.json').read_text())
  for name, mask in masks.items():
    def rms(values, selected=mask):
      return np.sqrt(np.average(values[selected, :2]**2, weights=weight[selected], axis=0)).tolist() if selected.any() else None
    cohorts[name] = {'seconds': float(weight[mask].sum()), 'core_c0_c1_rms': rms(commands), 'recorded_v8_c0_c1_rms': rms(recorded),
                     'adapter_eligible_seconds': float(weight[mask & adapter_valid].sum()),
                     'adapter_c0_c1_rms': rms(adapted, mask & adapter_valid)}
    expected = previous_report['cohorts'][name]
    np.testing.assert_allclose(cohorts[name]['seconds'], expected['seconds'], rtol=0., atol=1e-8)
    np.testing.assert_allclose(cohorts[name]['core_c0_c1_rms'], expected['candidates']['action_heading']['c0_c1_rms'], rtol=0., atol=1e-12)
    np.testing.assert_allclose(cohorts[name]['recorded_v8_c0_c1_rms'], expected['v8_c0_c1_rms'], rtol=0., atol=1e-12)
  root = Path(__file__).resolve().parents[2]
  sources = [Path(__file__), Path(ford_model_action.__file__),
             root/'openpilot/selfdrive/controls/lib/ford_path.py', directory/'route.npz', directory/'metadata.json',
             directory/'encoder_comparison.npz', directory/'encoder_comparison.json', directory/'pose_candidate/pose_replay.npz']
  report = {'scope': 'Command construction and adapter reconstruction only; no counterfactual closed-loop score.',
            'calibration_approved': False, 'executes_live_selector': False, 'cycles': len(t),
            'core_active_cycles': int(valid.sum()), 'core_exact_archived_match': True, 'cohorts_reproduced': True,
            'adapter_active_cycles': int(adapter_valid.sum()), 'adapter_status_counts': dict(reasons),
            'adapter_exact_match_with_fresh_engagement_dt': True,
            'core_active_path_shorter_than_7m_cycles': int(np.sum(valid & (coverage < 7.))),
            'adapter_validity_differs_from_archive_cycles': int(np.sum(adapter_valid != valid)),
            'adapter_command_differs_from_archive_cycles': int(np.any(abs(adapted-commands) > 1e-9, axis=1).sum()),
            'adapter_max_absolute_command_difference_c0_c1': np.max(abs(adapted[:, :2]-commands[:, :2]), axis=0).tolist(),
            'field_slew_zero_c2_c3_pass': True, 'float32_can_round_trips': wire.count,
            'timing': 'Original controls publication timestamps proxy computation time; repeated frames and gaps retained. No identified delay.',
            'eligibility': 'Adapter checks recorded services independently; full SubMaster health is unavailable. Core uses archived validity.',
            'reference': 'Recorded controlsState.desiredCurvature, already selected/limited. These two routes have no maneuver publications.',
            'host_yaw': 'Extract cs.yaw already equals -carState.yawRate. Used only for inherited finite/range gate, never feedback.',
            'cohorts': cohorts, 'workspace_head': revision(root), 'opendbc_import_head': revision(dependency),
            'opendbc_import_path': str(dependency),
            'source_sha256': {str(p.resolve()): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
  output.mkdir(parents=True, exist_ok=True)
  np.savez_compressed(output/'commands.npz', t=t, core=commands, core_valid=valid, adapter=adapted, adapter_valid=adapter_valid)
  (output/'report.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
  print(json.dumps({k: v for k, v in report.items() if k not in ('cohorts', 'source_sha256')}, indent=2))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('route_directory', type=Path)
  parser.add_argument('--output', type=Path, required=True)
  args = parser.parse_args()
  run(args.route_directory, args.output)
