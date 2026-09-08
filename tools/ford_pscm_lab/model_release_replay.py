"""Compare C1 release commands on timestamp-preserving recorded model extracts.

The model cache contains ns and points shaped (models,4,points): x,y,heading,t.
Its shared t must be copied from original model position/orientation clocks after
verifying that those clocks agree; this tool never synthesizes missing clocks.
Recorded motion and eligibility are frozen. Output compares commands, never
predicts steering or establishes whether physical unwind would improve.
"""
import argparse
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from openpilot.selfdrive.controls.lib import ford_model_action
from tools.ford_pscm_lab.model_action_replay import WireCheck, field_checks, load_controller, sample, table

BASELINE_REVISION = '4bd841eccd116f535a2ee99b920a631d1718f0cc'
WARMUP_S = 3.


def read_models(filename):
  with np.load(filename, allow_pickle=False) as raw:
    if 'points' not in raw or 'ns' not in raw:
      raise ValueError('Model cache requires ns and original x,y,heading,t arrays')
    points, ns = raw['points'], raw['ns']
  if points.ndim != 3 or points.shape[1] != 4 or points.shape[2] < 2 or not len(points):
    raise ValueError('Model cache requires four arrays per model, including original timestamps')
  if ns.shape != (len(points),) or not np.issubdtype(ns.dtype, np.integer) or np.any(np.diff(ns) <= 0):
    raise ValueError('Model ns must be strictly increasing integer timestamps')
  if not np.isfinite(points).all() or np.any(points[:, 3, 0] != 0.) or np.any(np.diff(points[:, 3], axis=1) <= 0.):
    raise ValueError('Model points and original timestamps must be finite, with times starting at zero and increasing')
  models = [SimpleNamespace(position=SimpleNamespace(x=p[0], y=p[1], t=p[3]),
                            orientation=SimpleNamespace(z=p[2], t=p[3])) for p in points]
  return ns, models


def crossings(t, values, valid, threshold, quantum, *, direction):
  below = direction * values <= threshold + quantum + 1e-9
  selected = below & valid
  first = np.flatnonzero(selected)
  crossed = np.flatnonzero(selected[1:] & valid[:-1] & ~below[:-1]) + 1
  return {'threshold': threshold, 'quantum_tolerance': quantum, 'original_turn_direction': direction,
          'starts_at_or_below': bool(selected[0]),
          'first_at_or_below_s': float(t[first[0]]) if len(first) else None,
          'first_downcross_s': float(t[crossed[0]]) if len(crossed) else None}


def compare_window(t, old, new, valid, label, lo, hi):
  keep = (t >= lo) & (t <= hi)
  if not keep.any():
    raise ValueError(f'No exact consumed models for window {label}')
  t, old, new, valid = t[keep], old[keep], new[keep], valid[keep]
  if not valid.any():
    raise ValueError(f'No eligible commands in window {label}')
  delta = abs(old[:, 1]) - abs(new[:, 1])
  fields = {}
  for column, name, thresholds, quantum in [(0, 'c0', [.5, .05, 0.], .01), (1, 'c1', [.1, .035, 0.], .0005)]:
    peak = old[valid, column][np.argmax(abs(old[valid, column]))]
    direction = -1. if peak < 0. else 1.
    fields[name] = [{'baseline': crossings(t, old[:, column], valid, threshold, quantum, direction=direction),
                     'candidate': crossings(t, new[:, column], valid, threshold, quantum, direction=direction)} for threshold in thresholds]
  return {'window_s': [lo, hi], 'cycles': len(t), 'eligible_cycles': int(valid.sum()),
          'baseline_mean_abs_c1': float(np.mean(abs(old[valid, 1]))),
          'candidate_mean_abs_c1': float(np.mean(abs(new[valid, 1]))),
          'c1_reduced_more_than_one_quantum_percent': float(100*np.mean(delta[valid] > .0005001)),
          'c1_increased_more_than_one_quantum_percent': float(100*np.mean(delta[valid] < -.0005001)),
          'largest_c1_magnitude_reduction_rad': float(np.max(delta[valid])),
          'exact_c0_equality': bool(np.array_equal(old[:, 0], new[:, 0])), 'published_crossings': fields}


def run(route_extract, models_file, metadata_file, output, windows):
  inputs = [route_extract.resolve(), models_file.resolve(), metadata_file.resolve()]
  output = output.resolve()
  commands_output = output.with_suffix('.npz')
  if output in inputs or commands_output in inputs:
    raise ValueError('Output must not overwrite an input extract')
  ns, models = read_models(models_file)
  metadata = json.loads(metadata_file.read_text())
  if not metadata['identities'] or any(identity['commit'] != BASELINE_REVISION or identity['dirty'] for identity in metadata['identities']):
    raise ValueError('Recorded route must use the pinned baseline revision')
  with np.load(route_extract, allow_pickle=False) as raw:
    streams = {name: table(raw, name) for name in ('controls', 'cs', 'path', 'wire')}
  controls = streams['controls']
  mi = np.searchsorted(ns, controls['model_ns'])
  exact = (mi < len(ns)) & (ns[np.minimum(mi, len(ns)-1)] == controls['model_ns'])
  indices = np.flatnonzero(exact)
  if not len(indices):
    raise ValueError('No extracted model matches a consumed model timestamp')
  mi = mi[indices]
  controls = {key: values[indices] for key, values in controls.items()}
  now = controls['t']
  if np.any(np.diff(now) <= 0):
    raise ValueError('Control timestamps must increase strictly')
  cs = sample(streams['cs'], now)
  recorded = sample(streams['path'], now, nearest=True)
  if np.any(abs(recorded['t'] - now) >= .005):
    raise ValueError('Recorded command publication is not from the same control cycle')
  active = recorded['active'].astype(bool)
  archived = load_controller(BASELINE_REVISION)
  old_core, new_core = archived.ModelActionController(), ford_model_action.ModelActionController()
  old = np.zeros((len(now), 4))
  new = np.zeros_like(old)
  valid = np.zeros(len(now), dtype=bool)
  settled = np.zeros(len(now), dtype=bool)
  old_targets, new_targets = [], []
  for model in models:
    a = archived.encode_model_action(model, 0., 10.)
    b = ford_model_action.encode_model_action(model, 0., 10.)
    if not a.valid or not b.valid:
      raise ValueError('Model cache contains a path rejected by one of the encoders')
    old_targets.append([a.path_offset, a.path_angle])
    new_targets.append([b.path_offset, b.path_angle])
  old_targets, new_targets = np.array(old_targets), np.array(new_targets)
  np.testing.assert_array_equal(old_targets[:, 0], new_targets[:, 0])
  assert (abs(new_targets[:, 1]) <= abs(old_targets[:, 1]) + 1e-12).all()
  assert (old_targets[:, 1] * new_targets[:, 1] >= 0.).all()
  wire = WireCheck()
  span_start = now[0]
  previous_valid = False
  for i, timestamp in enumerate(now):
    if i == 0 or indices[i] != indices[i-1]+1 or timestamp-now[i-1] > .1:
      old_core.reset()
      new_core.reset()
      previous_valid = False
      span_start = timestamp
    dt = timestamp-now[i-1] if previous_valid else .01
    kwargs = {'speed': cs['speed'][i], 'yaw_rate': cs['yaw'][i], 'dt': dt, 'active': bool(active[i])}
    a = old_core.update(models[mi[i]], controls['desired'][i], **kwargs)
    b = new_core.update(models[mi[i]], controls['desired'][i], **kwargs)
    assert a.valid == b.valid
    old[i] = a.path_offset, a.path_angle, a.curvature, a.curvature_rate
    new[i] = b.path_offset, b.path_angle, b.curvature, b.curvature_rate
    valid[i] = a.valid
    settled[i] = timestamp - span_start >= WARMUP_S
    wire.check(a)
    wire.check(b)
    previous_valid = a.valid
  np.testing.assert_array_equal(valid, active)
  np.testing.assert_array_equal(old[:, 0], new[:, 0])
  for command in (old, new):
    field_checks(command, valid, now)
  baseline_recorded = np.column_stack([recorded['c0'], recorded['c1']])
  baseline_delta = abs(old[:, :2].astype(np.float32).astype(float) - baseline_recorded)
  if not settled.any() or not valid[settled].any():
    raise ValueError('No eligible commands remain after the three-second cache-boundary warmup')
  assert (baseline_delta[settled] <= [.010001, .0005001]).all(), 'Baseline differs from recorded output by more than one DBC quantum'
  elapsed = now - metadata['t0']
  window_reports = {}
  for label, lo, hi in windows:
    keep = (elapsed >= lo) & (elapsed <= hi)
    if not keep.any() or not settled[keep].all():
      raise ValueError(f'Window {label} lacks complete cache-boundary warmup')
    window_reports[label] = compare_window(elapsed, old, new, valid, label, lo, hi)
  # Keep the recorded 20 Hz transmission schedule. This samples the proposed
  # publication; it does not simulate a different sender or vehicle response.
  wire_t = streams['wire']['t']
  wi = np.searchsorted(now, wire_t, side='right')-1
  in_scope = (wi >= 0) & (wire_t-now[np.maximum(wi, 0)] <= .02)
  wi = wi[in_scope]
  scheduled_t = wire_t[in_scope]
  scheduled_old, scheduled_new = old[wi], new[wi]
  np.testing.assert_array_equal(scheduled_old[:, 0], scheduled_new[:, 0])
  output.parent.mkdir(parents=True, exist_ok=True)
  np.savez_compressed(commands_output, t=elapsed, baseline=old, candidate=new, valid=valid, settled=settled,
                      recorded=baseline_recorded, model_ns=controls['model_ns'], model_cache_index=mi,
                      raw_baseline=old_targets[mi], raw_candidate=new_targets[mi],
                      scheduled_t=scheduled_t-metadata['t0'], scheduled_baseline=scheduled_old, scheduled_candidate=scheduled_new)
  sources = [Path(__file__), *inputs, Path(ford_model_action.__file__),
             Path(__file__).with_name('model_action_replay.py')]
  report = {'scope': 'Command-only comparison on exact consumed recorded models with frozen recorded eligibility and motion; no physical steering prediction.',
            'baseline_revision': BASELINE_REVISION, 'baseline_source_sha256': archived.source_sha256,
            'clock_source': 'Cache row3 contains original shared model position/orientation times; omitted clocks are rejected.',
            'models': len(models), 'control_cycles': len(now), 'eligible_cycles': int(valid.sum()),
            'three_second_cache_boundary_warmup_cycles': int((~settled).sum()),
            'baseline_matches_recorded_within_one_quantum_after_warmup': True,
            'baseline_timing_limit': ('Replay uses logged control-message times; internal core-entry times are not logged on every cycle. ' +
                                      'Baseline agreement is therefore checked within one DBC quantum, not asserted bit-for-bit.'),
            'baseline_nonidentical_published_values_after_warmup': int(np.count_nonzero(baseline_delta[settled])),
            'baseline_max_recorded_error_after_warmup': np.max(baseline_delta[settled], axis=0).tolist(),
            'exact_c0_equality_raw_published_and_scheduled': True,
            'raw_c1_never_amplifies_or_reverses': True,
            'float32_CAN_roundtrips': wire.count,
            'finite_caps_slew_zero_c2_c3_checks': True,
            'recorded_schedule_samples': len(scheduled_t),
            'recorded_median_CAN_period_s': float(np.median(np.diff(streams['wire']['t']))),
            'scheduled_command_scope': ('Latest proposed publication at each original send timestamp, restricted to <=20ms old; ' +
                                        'existing sender behavior is unchanged.'),
            'crossing_method': ('First command into the original turn at/below a diagnostic threshold plus one DBC quantum. ' +
                                'Direction is the sign of the largest absolute valid baseline value per field/window and is shared by both versions; ' +
                                'opposite-sign commands count as release. Downcross requires an immediately preceding above-threshold valid command. ' +
                                'The 0.035 rad level is a comparison marker, not an established hardware limit. No physical-response score.'),
            'windows': window_reports,
            'source_sha256': {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in sources},
            'command_artifact': str(commands_output)}
  output.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
  return report


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--route-extract', type=Path, required=True)
  parser.add_argument('--models', type=Path, required=True)
  parser.add_argument('--metadata', type=Path, required=True)
  parser.add_argument('--output', type=Path, required=True)
  parser.add_argument('--window', action='append', default=[], metavar='LABEL:START:END')
  args = parser.parse_args()
  windows = []
  for value in args.window:
    label, lo, hi = value.split(':')
    lo, hi = float(lo), float(hi)
    if not np.isfinite([lo, hi]).all() or hi <= lo:
      parser.error('Window end must be finite and later than its start')
    windows.append((label, lo, hi))
  report = run(args.route_extract, args.models, args.metadata, args.output, windows)
  print(json.dumps({key: value for key, value in report.items() if key not in ('windows', 'source_sha256')}, indent=2))


if __name__ == '__main__':
  main()
