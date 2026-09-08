import numpy as np
import pytest

from tools.ford_pscm_lab.model_release_replay import compare_window, crossings, read_models, run


def original_models():
  return np.array([[[0., 7., 14.], [0., .1, .2], [0., .02, .04], [0., 1., 2.]]])


def test_model_clock_roundtrip(tmp_path):
  filename = tmp_path/'models.npz'
  points = original_models()
  np.savez(filename, ns=np.array([123], dtype=np.int64), points=points)
  ns, models = read_models(filename)
  np.testing.assert_array_equal(ns, [123])
  np.testing.assert_array_equal(models[0].position.t, points[0, 3])
  np.testing.assert_array_equal(models[0].orientation.t, points[0, 3])
  np.testing.assert_array_equal(models[0].orientation.z, points[0, 2])


@pytest.mark.parametrize('times', [[1., 2., 3.], [0., 1., 1.], [0., 2., 1.], [0., np.nan, 2.]])
def test_reject_bad_original_model_clocks(tmp_path, times):
  points = original_models()
  points[0, 3] = times
  filename = tmp_path/'models.npz'
  np.savez(filename, ns=np.array([123]), points=points)
  with pytest.raises(ValueError, match='timestamps'):
    read_models(filename)


def test_run_rejects_missing_clocks_before_comparison(tmp_path):
  filename = tmp_path/'models.npz'
  np.savez(filename, ns=np.array([123]), points=original_models()[:, :3])
  with pytest.raises(ValueError, match='original timestamps'):
    run(tmp_path/'route.npz', filename, tmp_path/'metadata.json', tmp_path/'report.json', [])
  assert not (tmp_path/'report.json').exists()


def test_reject_noninteger_model_stamp(tmp_path):
  filename = tmp_path/'models.npz'
  np.savez(filename, ns=np.array([123.5]), points=original_models())
  with pytest.raises(ValueError, match='integer timestamps'):
    read_models(filename)


def test_downcross_respects_quantum_and_invalid_cycles():
  stamps = np.arange(6.)
  # Invalid zero cannot count as release; threshold plus one quantum can.
  values = np.array([.2, 0., .2, .1005, .1, 0.])
  actual = crossings(stamps, values, np.array([True, False, True, True, True, True]), .1, .0005, direction=1.)
  assert not actual['starts_at_or_below']
  assert actual['first_at_or_below_s'] == actual['first_downcross_s'] == 3.
  no_cross = crossings(stamps, np.full(6, .1006), np.ones(6, dtype=bool), .1, .0005, direction=1.)
  assert no_cross['first_at_or_below_s'] is no_cross['first_downcross_s'] is None


@pytest.mark.parametrize('direction', [-1., 1.])
def test_sign_jump_counts_as_release(direction):
  values = direction * np.array([.002, -.003, -.01])
  actual = crossings(np.arange(3.), values, np.ones(3, dtype=bool), 0., .0005, direction=direction)
  assert actual['first_at_or_below_s'] == actual['first_downcross_s'] == 1.


def test_comparison_uses_baseline_direction_for_both_versions():
  old, new = np.zeros((3, 4)), np.zeros((3, 4))
  old[:, 1] = [.1, .05, -.01]
  new[:, 1] = [.02, -.04, -.04]
  result = compare_window(np.arange(3.), old, new, np.ones(3, dtype=bool), 'turn', 0., 2.)
  zero = result['published_crossings']['c1'][-1]
  assert zero['baseline']['original_turn_direction'] == zero['candidate']['original_turn_direction'] == 1.
  assert zero['baseline']['first_downcross_s'] == 2.
  assert zero['candidate']['first_downcross_s'] == 1.
