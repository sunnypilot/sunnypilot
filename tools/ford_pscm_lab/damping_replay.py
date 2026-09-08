"""Compare pinned historical selected-action controllers on complete rlogs.

Original controls publication times proxy computation time. Consumed model
timestamps are exact; carState is causal and carControl is matched within 5 ms.
This compares commands on a fixed recording, never counterfactual vehicle motion.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import zstandard

from openpilot.cereal import log
from openpilot.selfdrive.controls.lib import ford_model_action
from tools.ford_pscm_lab.model_action_replay import (
  V1_REVISION, V2_REVISION, V3_REVISION, V4_REVISION, WireCheck, field_checks, load_controller, sample, verify_dependency,
)


DEPLOYMENT_OPENDBC = 'c21a9013700734dd20b09e05aa68329ad8cc20f9'


def extract(directory):
  columns = {'cs': 't valid can_valid speed yaw torque pressed', 'controls': 't valid desired model_ns',
             'cc': 't valid active', 'params': 't valid', 'path': 't valid active c0 c1', 'model': 't valid ns'}
  rows = {name: [] for name in columns}
  models, sources = [], {}
  t0 = None
  files = sorted(directory.glob('*--rlog.zst'), key=lambda p: int(p.name.split('--')[-2]))
  if not files:
    raise ValueError('No complete rlogs found')
  for file in files:
    compressed = file.read_bytes()
    sources[file.name] = hashlib.sha256(compressed).hexdigest()
    data = zstandard.ZstdDecompressor().stream_reader(compressed).read()
    for event in log.Event.read_multiple_bytes(data):
      kind, t, valid = event.which(), event.logMonoTime*1e-9, event.valid
      if t0 is None:
        t0 = t
      if kind == 'carState':
        cs = event.carState
        rows['cs'].append((t, valid, cs.canValid, cs.vEgo, -cs.yawRate, cs.steeringTorque, cs.steeringPressed))
      elif kind == 'controlsState':
        cs = event.controlsState
        rows['controls'].append((t, valid, cs.desiredCurvature, cs.lateralPlanMonoTime))
      elif kind == 'carControl':
        rows['cc'].append((t, valid, event.carControl.latActive))
      elif kind == 'vehicleParameters':
        rows['params'].append((t, valid))
      elif kind == 'carControlSP':
        path = event.carControlSP.fordLateralPath
        rows['path'].append((t, valid, path.valid, path.pathOffset, path.pathAngle))
      elif kind == 'modelV2':
        model = event.modelV2
        models.append(SimpleNamespace(position=SimpleNamespace(x=list(model.position.x), y=list(model.position.y)),
                                      orientation=SimpleNamespace(z=list(model.orientation.z))))
        rows['model'].append((t, valid, event.logMonoTime))
      elif kind == 'lateralManeuverPlan':
        raise ValueError('This replay requires routes without a separate maneuver reference')
  streams = {}
  for name, fields in columns.items():
    values = np.array(rows[name])
    if not len(values) or np.any(np.diff(values[:, 0]) < 0.):
      raise ValueError(f'Missing or backward {name} stream')
    streams[name] = dict(zip(fields.split(), values.T, strict=True))
  return streams, models, sources, t0


def run(directory, output, baseline_version='v1', candidate_version='v2', windows=()):
  directory, output = directory.resolve(), output.resolve()
  if output == directory or directory in output.parents:
    raise ValueError('Output must be outside the source route directory')
  if candidate_version == 'current':
    raise ValueError('This historical damping replay requires unchanged C1 and does not preserve model clocks; ' +
                     'select a pinned v2/v3/v4 candidate, or use a model-point replay for current code')
  verify_dependency(DEPLOYMENT_OPENDBC)
  revisions = {'v1': V1_REVISION, 'v2': V2_REVISION, 'v3': V3_REVISION, 'v4': V4_REVISION}
  baseline_source = load_controller(revisions[baseline_version])
  candidate_source = load_controller(revisions[candidate_version])
  streams, models, sources, t0 = extract(directory)
  controls, model = streams['controls'], streams['model']
  t = controls['t']
  cs, params = (sample(streams[name], t) for name in ('cs', 'params'))
  cc, recorded = (sample(streams[name], t, nearest=True) for name in ('cc', 'path'))
  mi = np.clip(np.searchsorted(model['ns'], controls['model_ns']), 0, len(models)-1)
  exact = model['ns'][mi] == controls['model_ns']
  services = ((controls['valid'] == 1) & (cc['valid'] == 1) & (abs(cc['t']-t) < .005) &
              (cs['valid'] == 1) & (cs['can_valid'] == 1) & (params['valid'] == 1) &
              (t-params['t'] >= 0.) & (t-params['t'] <= .15) & exact & (model['valid'][mi] == 1))
  baseline, candidate, wire = baseline_source.FordModelActionController(), candidate_source.FordModelActionController(), WireCheck()
  before, after = np.zeros((len(t), 4)), np.zeros((len(t), 4))
  eligible = np.zeros(len(t), bool)
  reasons = Counter()
  for i, now in enumerate(t):
    kwargs = {'speed': cs['speed'][i], 'now': now, 'measurement_time': cs['t'][i], 'model_time': model['t'][mi[i]],
              'reference_time': model['t'][mi[i]], 'active': bool(cc['active'][i]), 'valid': bool(services[i])}
    geometry = models[mi[i]] if exact[i] else None
    a = baseline.update(geometry, controls['desired'][i], yaw_rate=cs['yaw'][i], **kwargs)
    b = candidate.update(geometry, controls['desired'][i], yaw_rate=cs['yaw'][i], **kwargs)
    assert a.valid == b.valid and a.path_angle == b.path_angle
    before[i] = a.path_offset, a.path_angle, a.curvature, a.curvature_rate
    after[i] = b.path_offset, b.path_angle, b.curvature, b.curvature_rate
    eligible[i] = b.valid
    reasons[candidate.diagnostics['status']] += 1
    wire.check(a)
    wire.check(b)
  field_checks(before, eligible, t)
  field_checks(after, eligible, t)
  clean = eligible & (cs['pressed'] == 0) & (abs(cs['torque']) <= 1.)
  # Erode driver eligibility by one second in each direction on original time.
  bad = np.r_[0, np.cumsum(~clean)]
  left, right = np.searchsorted(t, t-1.), np.searchsorted(t, t+1., side='right')
  clean &= (bad[right] == bad[left]) & (t >= t[0]+1.) & (t <= t[-1]-1.)
  relative = t-t0
  masks = {'eligible': eligible, 'driver_clean': clean,
           'driver_clean_low_request_above_8mps': clean & (cs['speed'] >= 8.) & (abs(controls['desired'])*cs['speed']**2 < .15),
           'turn': clean & (abs(controls['desired'])*cs['speed']**2 >= .5)}
  for label, start, end in windows:
    start, end = float(start), float(end)
    if not np.isfinite([start, end]).all() or start >= end or label in masks:
      raise ValueError('Focus windows need unique labels and finite increasing bounds')
    masks[label] = eligible & (relative >= start) & (relative < end)
  weight = np.minimum(np.diff(t, append=t[-1]+.01), .03)
  difference = abs(before[:, 0]-after[:, 0])
  cohorts = {}
  for name, mask in masks.items():
    if mask.any():
      cohorts[name] = {'cycles': int(mask.sum()), 'seconds': float(weight[mask].sum()),
                       'changed_c0_cycles': int((difference[mask] > 1e-9).sum()),
                       'mean_absolute_c0_change_m': float(np.average(difference[mask], weights=weight[mask])),
                       'max_absolute_c0_change_m': float(difference[mask].max()),
                       'increased_absolute_c0_cycles': int((abs(after[mask, 0])-abs(before[mask, 0]) > 1e-9).sum()),
                       'decreased_absolute_c0_cycles': int((abs(before[mask, 0])-abs(after[mask, 0]) > 1e-9).sum()),
                       'driver_input_percent': float(100*np.average((cs['pressed'][mask] == 1) | (abs(cs['torque'][mask]) > 1.), weights=weight[mask])),
                       'baseline_peak_absolute_c0_m': float(abs(before[mask, 0]).max()),
                       'candidate_peak_absolute_c0_m': float(abs(after[mask, 0]).max())}
  paired = eligible & (recorded['valid'] == 1) & (recorded['active'] == 1) & (abs(recorded['t']-t) < .005)
  actual = np.column_stack((recorded['c0'], recorded['c1']))
  error = abs(before[:, :2]-actual)
  report = {'scope': 'Fixed-input command replay only; no physical improvement or stability claim.', 'calibration_approved': False,
            'cycles': len(t), 'eligible_cycles': int(eligible.sum()), 'status_counts': dict(reasons),
            'c1_exactly_unchanged': True, 'same_validity': True, 'field_slew_zero_c2_c3_pass': True,
            'float32_can_round_trips': wire.count, 'cohorts': cohorts,
            'baseline_commands_vs_recorded_publications': {'paired_cycles': int(paired.sum()),
              'within_one_quantum_cycles': int(np.all(error[paired] <= [.010001, .0005001], axis=1).sum()),
              'maximum_absolute_error_c0_c1': np.max(error[paired], axis=0).tolist()},
            'timing': 'Publication-time proxy, causal carState, exact consumed model; full SubMaster health unavailable.',
            'baseline_version': baseline_version, 'baseline_revision': revisions[baseline_version],
            'candidate_version': candidate_version, 'candidate_revision': revisions.get(candidate_version, 'working_tree'),
            'focus_windows': windows, 'baseline_source_sha256': baseline_source.source_sha256,
            'candidate_source_sha256': candidate_source.source_sha256,
            'source_rlog_sha256': sources, 'opendbc_head': DEPLOYMENT_OPENDBC,
            'source_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (Path(__file__), Path(ford_model_action.__file__))}}
  output.mkdir(parents=True, exist_ok=True)
  np.savez_compressed(output/'commands.npz', t=relative, before=before, after=after, eligible=eligible,
                      speed=cs['speed'], yaw=cs['yaw'], desired=controls['desired'], torque=cs['torque'])
  (output/'report.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
  print(json.dumps({k: v for k, v in report.items() if k not in ('source_rlog_sha256', 'source_sha256')}, indent=2))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('rlog_directory', type=Path)
  parser.add_argument('--output', type=Path, required=True)
  parser.add_argument('--baseline', choices=['v1', 'v2', 'v3', 'v4'], default='v1')
  parser.add_argument('--candidate', choices=['v2', 'v3', 'v4', 'current'], default='v2')
  parser.add_argument('--window', action='append', nargs=3, metavar=('LABEL', 'START_SECONDS', 'END_SECONDS'), default=[])
  args = parser.parse_args()
  run(args.rlog_directory, args.output, args.baseline, args.candidate, args.window)
