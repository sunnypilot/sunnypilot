import hashlib

import numpy as np
import pytest

from openpilot.selfdrive.controls.lib.ford_path import FordPath
from tools.ford_pscm_lab import model_action_replay as replay
from tools.ford_pscm_lab import damping_replay


def test_service_sampling_keeps_original_gaps_and_never_pulls_future_inputs():
  stream = {'t': np.array([1., 1.01, 2.]), 'value': np.array([3., 4., 5.])}
  sampled = replay.sample(stream, np.array([1.005, 1.5, 2.]))
  np.testing.assert_array_equal(sampled['t'], [1., 1.01, 2.])
  np.testing.assert_array_equal(sampled['value'], [3., 4., 5.])
  assert 1.5-sampled['t'][1] > .15  # The adapter sees the gap, not a resampled fresh input.


@pytest.mark.parametrize('times', [[], [1., .9]])
def test_replay_does_not_sort_away_backward_time_or_invent_missing_streams(times):
  with pytest.raises(ValueError):
    replay.sample({'t': np.array(times)}, np.array([1.]))


def test_dependency_mismatch_fails_before_replaying(monkeypatch):
  monkeypatch.setattr(replay, 'revision', lambda _: 'wrong_revision')
  with pytest.raises(ValueError, match='Expected opendbc'):
    replay.verify_dependency()


@pytest.mark.parametrize('revision', ['HEAD', '744a97d9b', '--help', 'z'*40])
def test_archived_controller_requires_an_immutable_commit(revision):
  with pytest.raises(ValueError, match='immutable'):
    replay.load_controller(revision)


def test_archived_loader_uses_exact_source_and_records_its_hash(monkeypatch):
  # Unit tests must also work in shallow checkouts. Full replays verify real archived code.
  calls = []
  source = b'archived_value = 42\n'

  def read_source(command):
    calls.append(command)
    return source

  monkeypatch.setattr(replay.subprocess, 'check_output', read_source)
  replay.load_controller.cache_clear()
  try:
    for commit in (replay.V1_REVISION, replay.V2_REVISION, replay.V3_REVISION, replay.V4_REVISION):
      module = replay.load_controller(commit)
      assert module.archived_value == 42
      assert module.source_sha256 == hashlib.sha256(source).hexdigest()
      assert calls[-1][-2:] == ['show', f'{commit}:openpilot/selfdrive/controls/lib/ford_model_action.py']
      assert replay.load_controller(commit) is module
    assert len(calls) == 4
  finally:
    replay.load_controller.cache_clear()


def test_explicit_stress_dependency_still_requires_an_exact_match(monkeypatch):
  monkeypatch.setattr(replay, 'revision', lambda _: 'deployment_commit')
  replay.verify_dependency('deployment_commit')
  with pytest.raises(ValueError, match='Expected opendbc'):
    replay.verify_dependency('different_commit')
  with pytest.raises(ValueError, match='Expected opendbc'):
    replay.verify_dependency()  # Historical replay never silently follows the local checkout.


def test_source_route_directory_cannot_be_overwritten(tmp_path):
  with pytest.raises(ValueError, match='outside the source'):
    replay.run(tmp_path, tmp_path/'selected_controller')


def test_current_replay_rejects_missing_model_clocks_before_comparing_outputs(tmp_path, monkeypatch):
  source = tmp_path/'source'
  source.mkdir()
  np.savez(source/'route.npz', model_paths=np.zeros((1, 4, 33)))
  monkeypatch.setattr(replay, 'verify_dependency', lambda: tmp_path)
  with pytest.raises(ValueError, match='requires original model_position_t and model_orientation_t'):
    replay.run(source, tmp_path/'output')
  assert not (tmp_path/'output').exists()


def test_extract_models_preserves_both_actual_clocks_and_rejects_count_mismatch():
  clocks = np.array([[0., .3, 1.7]])
  raw = {'model_paths': np.zeros((1, 4, 3)), 'model_position_t': clocks, 'model_orientation_t': clocks+.01}
  model, = replay.extract_models(raw)
  np.testing.assert_array_equal(model.position.t, clocks[0])
  np.testing.assert_array_equal(model.orientation.t, clocks[0]+.01)
  raw['model_orientation_t'] = clocks[:, :2]
  with pytest.raises(ValueError, match='must match'):
    replay.extract_models(raw)


def test_historical_damping_replay_rejects_current_controller(tmp_path):
  with pytest.raises(ValueError, match='historical damping replay requires unchanged C1'):
    damping_replay.run(tmp_path/'source', tmp_path/'output', candidate_version='current')


@pytest.mark.parametrize('field,value', [(0, 5.12), (1, .501), (2, .00002), (3, .000001), (0, np.nan)])
def test_field_validation_catches_range_and_zero_c2_c3_violations(field, value):
  command = np.zeros((2, 4))
  command[0, field] = value
  with pytest.raises(AssertionError):
    replay.field_checks(command, np.array([True, True]), np.array([1., 1.01]))


def test_invalid_cycles_cannot_publish_a_retained_command():
  with pytest.raises(AssertionError):
    replay.field_checks(np.array([[.01, 0., 0., 0.]]), np.array([False]), np.array([1.]))


def test_field_validation_catches_excessive_slew_with_original_dt():
  with pytest.raises(AssertionError):
    replay.field_checks(np.array([[0., 0., 0., 0.], [.08, 0., 0., 0.]]), np.array([True, True]), np.array([1., 1.01]))


def test_wire_validator_checks_real_curvature_fields_instead_of_filling_them_with_zero():
  with pytest.raises(AssertionError):
    replay.WireCheck().check(FordPath(True, 0., 0., .001, 0.))
