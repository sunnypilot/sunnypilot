import numpy as np
import pytest

from openpilot.selfdrive.controls.lib.ford_path import FordPath
from tools.ford_pscm_lab import model_action_replay as replay


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
