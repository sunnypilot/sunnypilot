import math
import random
import numpy as np
import time
import pytest

from openpilot.cereal import messaging, log
from opendbc.car.structs import car
from openpilot.selfdrive.locationd.lagd import LateralLagEstimator, retrieve_initial_lag, masked_normalized_cross_correlation, \
                                               BLOCK_NUM, BLOCK_NUM_NEEDED, BLOCK_SIZE, MIN_OKAY_WINDOW_SEC, VERSION, MIN_LAG, MAX_LAG
from openpilot.selfdrive.locationd.lagd import SPEED_BUCKET_EDGES, interpolate_bucket_values
from openpilot.selfdrive.test.process_replay.migration import migrate, migrate_carParams
from openpilot.selfdrive.locationd.test.test_locationd_scenarios import TEST_ROUTE
from openpilot.common.params import Params
from openpilot.tools.lib.logreader import LogReader
from openpilot.tools.lagd_buckets import line_graph, ping_pong_metrics
from openpilot.common.hardware import PC

MAX_ERR_FRAMES = 1
DT = 0.05
LAGD_MIN_LAG_FRAMES, LAGD_MAX_LAG_FRAMES = int(round(MIN_LAG / DT)), int(round(MAX_LAG / DT))


def process_messages(estimator, lag_frames, n_frames, vego=25.0, rejection_threshold=0.0, start_frame=0):
  for i in range(n_frames):
    t = (start_frame + i) * estimator.dt
    desired_la = np.cos(10 * t) * 0.3
    actual_la = np.cos(10 * (t - lag_frames * estimator.dt)) * 0.3

    # if sample is masked out, set it to desired value (no lag)
    rejected = random.uniform(0, 1) < rejection_threshold
    if rejected:
      actual_la = desired_la

    desired_cuvature = float(desired_la / (vego ** 2))
    actual_yr = float(actual_la / vego)
    msgs = [
      (t, "carControl", car.CarControl(latActive=not rejected)),
      (t, "carState", car.CarState(vEgo=vego, steeringPressed=False)),
      (t, "controlsState", log.ControlsState(desiredCurvature=desired_cuvature)),
      (t, "livePose", log.LivePose(angularVelocityDevice=log.LivePose.XYZMeasurement(z=actual_yr, valid=True),
                                   posenetOK=True, inputsOK=True)),
      (t, "liveCalibration", log.LiveCalibrationData(rpyCalib=[0, 0, 0], calStatus=log.LiveCalibrationData.Status.calibrated)),
    ]
    for t, w, m in msgs:
      estimator.handle_log(t, w, m)
    estimator.update_points()
    estimator.update_estimate()


class TestLagd:
  def test_interpolate_bucket_values(self):
    edges = np.array([0.0, 10.0, 20.0])
    values = [.2, .4, .3]
    assert interpolate_bucket_values(0, edges, values) == .2
    assert interpolate_bucket_values(10, edges, values) == pytest.approx(.3)
    assert interpolate_bucket_values(20, edges, values) == pytest.approx(.35)
    assert interpolate_bucket_values(30, edges, values) == .3

  def test_ping_pong_metrics(self):
    samples = [(i / 20, 2.5 * math.sin(2 * math.pi * 1.2 * i / 20)) for i in range(101)]
    severity, amplitude, frequency, duration = ping_pong_metrics(samples)
    assert severity == "MODERATE"
    assert 2.4 < amplitude < 2.6
    assert 1.0 < frequency < 1.3
    assert duration == 5

  def test_line_graph(self):
    graph = line_graph([0.15, 0.4, 0.65], ["estimated", "unestimated", "invalid"], 1)
    assert all(marker in graph for marker in ["●", "◆", "×"])
    assert "0.65s" in graph and "0.15s" in graph
    assert "centers" in graph and "5" in graph
    assert any("⠀" < char <= "⣿" for char in graph)
    assert "⠒" in line_graph([0.3, 0.3], ["estimated", "estimated"], -1)

  def test_read_saved_params(self):
    params = Params()

    lr = migrate(LogReader(TEST_ROUTE), [migrate_carParams])
    CP = next(m for m in lr if m.which() == "carParams").carParams

    msg = messaging.new_message('liveDelay')
    msg.liveDelay.lateralDelayBuckets = [random.random() for _ in SPEED_BUCKET_EDGES]
    msg.liveDelay.validBlocksBuckets = [random.randint(1, 10) for _ in SPEED_BUCKET_EDGES]
    msg.liveDelay.blockValuesBuckets = [[random.random() for _ in range(BLOCK_NUM)] for _ in SPEED_BUCKET_EDGES]
    msg.liveDelay.blockIdxBuckets = [random.randrange(BLOCK_NUM) for _ in SPEED_BUCKET_EDGES]
    msg.liveDelay.sampleIdxBuckets = [random.randrange(BLOCK_SIZE) for _ in SPEED_BUCKET_EDGES]
    msg.liveDelay.version = VERSION
    params.put("LiveDelay", msg.to_bytes(), block=True)
    params.put("CarParamsPrevRoute", CP.as_builder().to_bytes(), block=True)

    saved_lag_params = retrieve_initial_lag(params, CP)
    assert saved_lag_params is not None

    for state, values, block_idx, sample_idx, valid_blocks in zip(saved_lag_params, msg.liveDelay.blockValuesBuckets,
                                                                  msg.liveDelay.blockIdxBuckets, msg.liveDelay.sampleIdxBuckets,
                                                                  msg.liveDelay.validBlocksBuckets, strict=True):
      assert np.allclose(state[0], values)
      assert state[1:] == (block_idx, sample_idx, valid_blocks)

    old_msg = messaging.new_message('liveDelay')
    old_msg.liveDelay.version = VERSION
    old_msg.liveDelay.speedBucket = 4
    old_msg.liveDelay.calPerc = 12
    old_msg.liveDelay.lateralDelayBuckets = [0.3] * len(SPEED_BUCKET_EDGES)
    old_msg.liveDelay.validBlocksBuckets = [0] * len(SPEED_BUCKET_EDGES)
    params.put("LiveDelay", old_msg.to_bytes(), block=True)
    assert retrieve_initial_lag(params, CP)[4][2] == 3

  def test_read_invalid_saved_params(self, subtests):
    params = Params()

    lr = migrate(LogReader(TEST_ROUTE), [migrate_carParams])
    CP = next(m for m in lr if m.which() == "carParams").carParams

    valid = {'version': VERSION, 'lateralDelayBuckets': [0.3] * len(SPEED_BUCKET_EDGES),
             'validBlocksBuckets': [1] * len(SPEED_BUCKET_EDGES)}
    for msg_dict in [valid | {'version': 0}, valid | {'status': 'invalid'}, valid | {'validBlocksBuckets': [100] * 4}]:
      with subtests.test(msg=f"liveDelay={msg_dict}"):
        msg = messaging.new_message('liveDelay')
        msg.liveDelay = msg_dict
        params.put("LiveDelay", msg.to_bytes(), block=True)
        params.put("CarParamsPrevRoute", CP.as_builder().to_bytes(), block=True)
        assert retrieve_initial_lag(params, CP) is None

  def test_ncc(self):
    rng = np.random.default_rng()
    lag_frames = random.randint(1, 19)

    desired_sig = np.sin(np.arange(0.0, 10.0, 0.1))
    actual_sig = np.sin(np.arange(0.0, 10.0, 0.1) - lag_frames * 0.1)
    mask = np.ones(len(desired_sig), dtype=bool)

    corr = masked_normalized_cross_correlation(desired_sig, actual_sig, mask, 200)[len(desired_sig) - 1:len(desired_sig) + 20]
    assert np.argmax(corr) == lag_frames

    # add some noise
    desired_sig += rng.normal(0, 0.05, len(desired_sig))
    actual_sig += rng.normal(0, 0.05, len(actual_sig))
    corr = masked_normalized_cross_correlation(desired_sig, actual_sig, mask, 200)[len(desired_sig) - 1:len(desired_sig) + 20]
    assert np.argmax(corr)  in range(lag_frames - MAX_ERR_FRAMES, lag_frames + MAX_ERR_FRAMES + 1)

    # mask out 40% of the values, and make them noise
    mask = rng.choice([True, False], size=len(desired_sig), p=[0.6, 0.4])
    desired_sig[~mask] = rng.normal(0, 1, size=np.sum(~mask))
    actual_sig[~mask] = rng.normal(0, 1, size=np.sum(~mask))
    corr = masked_normalized_cross_correlation(desired_sig, actual_sig, mask, 200)[len(desired_sig) - 1:len(desired_sig) + 20]
    assert np.argmax(corr) in range(lag_frames - MAX_ERR_FRAMES, lag_frames + MAX_ERR_FRAMES + 1)

  def test_empty_estimator(self):
    mocked_CP = car.CarParams(steerActuatorDelay=0.5)
    estimator = LateralLagEstimator(mocked_CP, DT)
    msg = estimator.get_msg(True)
    assert msg.liveDelay.status == 'unestimated'
    assert np.allclose(msg.liveDelay.lateralDelay, estimator.initial_lag)
    assert np.allclose(msg.liveDelay.lateralDelayEstimate, estimator.initial_lag)
    assert msg.liveDelay.validBlocks == 0
    assert msg.liveDelay.calPerc == 0

  def test_estimator_basics(self, subtests):
    for lag_frames in range(LAGD_MIN_LAG_FRAMES, LAGD_MAX_LAG_FRAMES - 1):
      with subtests.test(msg=f"lag_frames={lag_frames}"):
        mocked_CP = car.CarParams(steerActuatorDelay=0.5)
        estimator = LateralLagEstimator(mocked_CP, DT, min_recovery_buffer_sec=0.0, min_yr=0.0)
        process_messages(estimator, lag_frames, int(MIN_OKAY_WINDOW_SEC / DT) + BLOCK_NUM_NEEDED * BLOCK_SIZE)
        msg = estimator.get_msg(True)
        assert msg.liveDelay.status == 'estimated'
        assert np.allclose(msg.liveDelay.lateralDelay, lag_frames * DT, atol=0.01)
        assert np.allclose(msg.liveDelay.lateralDelayEstimate, lag_frames * DT, atol=0.01)
        assert np.allclose(msg.liveDelay.lateralDelayEstimateStd, 0.0, atol=0.01)
        assert msg.liveDelay.validBlocks == BLOCK_NUM_NEEDED
        assert msg.liveDelay.calPerc == 100

  def test_estimator_masking(self):
    mocked_CP, lag_frames = car.CarParams(steerActuatorDelay=0.5), random.randint(LAGD_MIN_LAG_FRAMES, LAGD_MAX_LAG_FRAMES - 1)
    estimator = LateralLagEstimator(mocked_CP, DT, min_recovery_buffer_sec=0.0, min_yr=0.0, min_valid_block_count=1)
    masked_frames = int(MIN_OKAY_WINDOW_SEC / DT)
    process_messages(estimator, lag_frames, masked_frames, rejection_threshold=0.4)
    process_messages(estimator, lag_frames, masked_frames + BLOCK_SIZE * 2, start_frame=masked_frames)
    msg = estimator.get_msg(True)
    assert np.allclose(msg.liveDelay.lateralDelayEstimate, lag_frames * DT, atol=0.01)
    assert np.allclose(msg.liveDelay.lateralDelayEstimateStd, 0.0, atol=0.01)
    assert msg.liveDelay.calPerc == 100

  def test_learning_countdown_resets(self):
    mocked_CP = car.CarParams(steerActuatorDelay=0.3)
    estimator = LateralLagEstimator(mocked_CP, DT, window_sec=10.0, okay_window_sec=5.0,
                                    min_recovery_buffer_sec=0.0, min_vego=0.0, min_yr=0.0)
    process_messages(estimator, 5, 80)
    assert np.allclose(estimator.get_msg(True).liveDelay.learningCountdownBuckets, [1.0])

    process_messages(estimator, 5, 1, rejection_threshold=1.0, start_frame=80)
    msg = estimator.get_msg(True).liveDelay
    assert np.allclose(msg.learningCountdownBuckets, [5.0])
    assert list(msg.learningResetReasonBuckets) == ["lateral inactive"]

  def test_speed_buckets(self):
    mocked_CP = car.CarParams(steerActuatorDelay=0.3)
    estimator = LateralLagEstimator(mocked_CP, DT, block_size=10, min_valid_block_count=1, window_sec=5.0,
                                    okay_window_sec=2.0, min_recovery_buffer_sec=0.0, min_vego=0.0, min_yr=0.0,
                                    speed_bucket_edges=np.array([0.0, 20.0]))
    frame_count = int(5.0 / DT) + 10
    process_messages(estimator, 5, frame_count, vego=15.0)
    process_messages(estimator, 9, frame_count, vego=25.0, start_frame=frame_count)

    msg = estimator.get_msg(True).liveDelay
    assert msg.speedBucket == 1
    assert np.allclose(msg.lateralDelayBuckets, [5 * DT, 9 * DT], atol=0.01)
    assert all(blocks > 0 for blocks in msg.validBlocksBuckets)

  @pytest.mark.skipif(PC, reason="only on device")
  def test_estimator_performance(self):
    mocked_CP = car.CarParams(steerActuatorDelay=0.5)
    estimator = LateralLagEstimator(mocked_CP, DT)

    ds = []
    for _ in range(1000):
      st = time.perf_counter()
      estimator.update_points()
      estimator.update_estimate()
      d = time.perf_counter() - st
      ds.append(d)

    assert np.mean(ds) < DT
