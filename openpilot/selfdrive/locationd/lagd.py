#!/usr/bin/env python3
import os
import numpy as np
import capnp
from collections import deque
from functools import partial

import openpilot.cereal.messaging as messaging
from openpilot.cereal import log
from opendbc.car.structs import car
from openpilot.cereal.services import SERVICE_LIST
from openpilot.common.constants import CV
from openpilot.common.params import Params
from openpilot.common.realtime import config_realtime_process
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.locationd.helpers import PoseCalibrator, Pose, fft_next_good_size, parabolic_peak_interp
from openpilot.sunnypilot.livedelay.lagd_toggle import LagdToggle

BLOCK_SIZE = 8
BLOCK_NUM = 30
BLOCK_NUM_NEEDED = 3
MOVING_WINDOW_SEC = 20.0
MIN_OKAY_WINDOW_SEC = 5.0
MIN_RECOVERY_BUFFER_SEC = 2.0
MIN_VEGO = 50.0 * CV.MPH_TO_MS
SPEED_BUCKET_EDGES = np.arange(0.0, 90.0, 10.0) * CV.MPH_TO_MS


def interpolate_bucket_values(speed: float, edges: np.ndarray, values: list[float]) -> float:
  if len(values) == 1:
    return values[0]
  widths = np.append(np.diff(edges), edges[-1] - edges[-2])
  return float(np.interp(speed, edges + widths / 2, values))
MIN_ABS_YAW_RATE = 0.0
MAX_YAW_RATE_SANITY_CHECK = 1.0
MIN_NCC = 0.95
MAX_LAG = 0.65
MIN_LAG = 0.15
MAX_LAG_STD = 0.1
MAX_LAT_ACCEL = 2.0
MAX_LAT_ACCEL_DIFF = 0.6
MIN_LAT_ACCEL_RANGE = 0.1
MIN_CONFIDENCE = 0.7
CORR_BORDER_OFFSET = 5
LAG_CANDIDATE_CORR_THRESHOLD = 0.9
SMOOTH_K = 5
SMOOTH_SIGMA = 1.0

VERSION = 3  # bump this to invalidate old parameter caches


def masked_symmetric_moving_average(x: np.ndarray, mask: np.ndarray, k: int, sigma: float) -> np.ndarray:
  assert k >= 1 and k % 2 == 1, "k must be positive and odd"
  pad = k // 2
  i = np.arange(k) - pad
  w = np.exp(-0.5 * (i / sigma) ** 2)
  w /= w.sum()
  xp = np.pad(x * mask, pad, mode="edge")
  mp = np.pad(mask, pad, mode="edge")
  num = np.convolve(xp, w, mode="valid")
  den = np.convolve(mp, w, mode="valid")
  return np.divide(num, den, out=np.full_like(num, np.nan, dtype=np.float64), where=den != 0)

def masked_normalized_cross_correlation(expected_sig: np.ndarray, actual_sig: np.ndarray, mask: np.ndarray, n: int):
  """
  References:
    D. Padfield. "Masked FFT registration". In Proc. Computer Vision and
    Pattern Recognition, pp. 2918-2925 (2010).
    :DOI:`10.1109/CVPR.2010.5540032`
  """

  eps = np.finfo(np.float64).eps
  expected_sig = np.asarray(expected_sig, dtype=np.float64)
  actual_sig = np.asarray(actual_sig, dtype=np.float64)

  expected_sig[~mask] = 0.0
  actual_sig[~mask] = 0.0

  rotated_expected_sig = expected_sig[::-1]
  rotated_mask = mask[::-1]

  fft = partial(np.fft.fft, n=n)

  actual_sig_fft = fft(actual_sig)
  rotated_expected_sig_fft = fft(rotated_expected_sig)
  actual_mask_fft = fft(mask.astype(np.float64))
  rotated_mask_fft = fft(rotated_mask.astype(np.float64))

  number_overlap_masked_samples = np.fft.ifft(rotated_mask_fft * actual_mask_fft).real
  number_overlap_masked_samples[:] = np.round(number_overlap_masked_samples)
  number_overlap_masked_samples[:] = np.fmax(number_overlap_masked_samples, eps)
  masked_correlated_actual_fft = np.fft.ifft(rotated_mask_fft * actual_sig_fft).real
  masked_correlated_expected_fft = np.fft.ifft(actual_mask_fft * rotated_expected_sig_fft).real

  numerator = np.fft.ifft(rotated_expected_sig_fft * actual_sig_fft).real
  numerator -= masked_correlated_actual_fft * masked_correlated_expected_fft / number_overlap_masked_samples

  actual_squared_fft = fft(actual_sig ** 2)
  actual_sig_denom = np.fft.ifft(rotated_mask_fft * actual_squared_fft).real
  actual_sig_denom -= masked_correlated_actual_fft ** 2 / number_overlap_masked_samples
  actual_sig_denom[:] = np.fmax(actual_sig_denom, 0.0)

  rotated_expected_squared_fft = fft(rotated_expected_sig ** 2)
  expected_sig_denom = np.fft.ifft(actual_mask_fft * rotated_expected_squared_fft).real
  expected_sig_denom -= masked_correlated_expected_fft ** 2 / number_overlap_masked_samples
  expected_sig_denom[:] = np.fmax(expected_sig_denom, 0.0)

  denom = np.sqrt(actual_sig_denom * expected_sig_denom)

  # zero-out samples with very small denominators
  tol = 1e3 * eps * np.max(np.abs(denom), keepdims=True)
  nonzero_indices = denom > tol

  ncc = np.zeros_like(denom, dtype=np.float64)
  ncc[nonzero_indices] = numerator[nonzero_indices] / denom[nonzero_indices]
  np.clip(ncc, -1, 1, out=ncc)

  return ncc


class Points:
  def __init__(self, num_points: int):
    self.times = deque[float]([0.0] * num_points, maxlen=num_points)
    self.okay = deque[bool]([False] * num_points, maxlen=num_points)
    self.desired = deque[float]([0.0] * num_points, maxlen=num_points)
    self.actual = deque[float]([0.0] * num_points, maxlen=num_points)

  @property
  def num_points(self):
    return len(self.desired)

  @property
  def num_okay(self):
    return np.count_nonzero(self.okay)

  def update(self, t: float, desired: float, actual: float, okay: bool):
    self.times.append(t)
    self.okay.append(okay)
    self.desired.append(desired)
    self.actual.append(actual)

  def get(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    return np.array(self.times), np.array(self.desired), np.array(self.actual), np.array(self.okay)


class BlockAverage:
  def __init__(self, num_blocks: int, block_size: int, valid_blocks: int, initial_value: float):
    self.num_blocks = num_blocks
    self.block_size = block_size
    self.block_idx = valid_blocks % num_blocks
    self.idx = 0

    self.values = np.tile(initial_value, (num_blocks, 1))
    self.valid_blocks = valid_blocks

  def update(self, value: float):
    self.values[self.block_idx] = (self.idx * self.values[self.block_idx] + value) / (self.idx + 1)
    self.idx = (self.idx + 1) % self.block_size
    if self.idx == 0:
      self.block_idx = (self.block_idx + 1) % self.num_blocks
      self.valid_blocks = min(self.valid_blocks + 1, self.num_blocks)

  def restore(self, values: list[float], block_idx: int, idx: int):
    assert len(values) == self.num_blocks and 0 <= block_idx < self.num_blocks and 0 <= idx < self.block_size
    self.values = np.asarray(values, dtype=float).reshape(self.num_blocks, 1)
    self.block_idx = block_idx
    self.idx = idx

  def get(self) -> tuple[float, float, float, float]:
    valid_block_idx = [i for i in range(self.valid_blocks) if i != self.block_idx]
    valid_and_current_idx = valid_block_idx + ([self.block_idx] if self.idx > 0 else [])

    if len(valid_block_idx) > 0:
      valid_mean = float(np.mean(self.values[valid_block_idx], axis=0).item())
      valid_std = float(np.std(self.values[valid_block_idx], axis=0).item())
    else:
      valid_mean, valid_std = float('nan'), float('nan')

    if len(valid_and_current_idx) > 0:
      current_mean = float(np.mean(self.values[valid_and_current_idx], axis=0).item())
      current_std = float(np.std(self.values[valid_and_current_idx], axis=0).item())
    else:
      current_mean, current_std = float('nan'), float('nan')

    return valid_mean, valid_std, current_mean, current_std


class LateralLagEstimator:
  inputs = {"carControl", "carState", "controlsState", "liveCalibration", "livePose"}

  def __init__(self, CP: car.CarParams, dt: float,
               block_count: int = BLOCK_NUM, min_valid_block_count: int = BLOCK_NUM_NEEDED, block_size: int = BLOCK_SIZE,
               window_sec: float = MOVING_WINDOW_SEC, okay_window_sec: float = MIN_OKAY_WINDOW_SEC, min_recovery_buffer_sec: float = MIN_RECOVERY_BUFFER_SEC,
               min_vego: float = MIN_VEGO, min_yr: float = MIN_ABS_YAW_RATE, min_ncc: float = MIN_NCC,
               max_lat_accel: float = MAX_LAT_ACCEL, max_lat_accel_diff: float = MAX_LAT_ACCEL_DIFF, min_confidence: float = MIN_CONFIDENCE,
               speed_bucket_edges: np.ndarray | None = None):
    self.dt = dt
    self.window_sec = window_sec
    self.okay_window_sec = okay_window_sec
    self.min_recovery_buffer_sec = min_recovery_buffer_sec
    self.initial_lag = CP.steerActuatorDelay + 0.2
    self.block_size = block_size
    self.block_count = block_count
    self.min_valid_block_count = min_valid_block_count
    self.min_vego = min_vego
    self.min_yr = min_yr
    self.min_ncc = min_ncc
    self.min_confidence = min_confidence
    self.max_lat_accel = max_lat_accel
    self.max_lat_accel_diff = max_lat_accel_diff
    self.speed_bucket_edges = np.asarray(speed_bucket_edges if speed_bucket_edges is not None else [0.0], dtype=float)
    assert len(self.speed_bucket_edges) > 0 and self.speed_bucket_edges[0] == 0.0 and np.all(np.diff(self.speed_bucket_edges) > 0)

    self.t = 0.0
    self.lat_active = False
    self.steering_pressed = False
    self.steering_saturated = False
    self.desired_curvature = 0.0
    self.v_ego = 0.0
    self.yaw_rate = 0.0
    self.yaw_rate_std = 0.0
    self.pose_valid = False

    self.last_lat_inactive_t = 0.0
    self.last_steering_pressed_t = 0.0
    self.last_steering_saturated_t = 0.0
    self.last_pose_invalid_t = 0.0
    self.last_estimate_ts = [0.0] * len(self.speed_bucket_edges)
    self.consecutive_okay = [0] * len(self.speed_bucket_edges)
    self.learning_reset_reasons = ["not started"] * len(self.speed_bucket_edges)

    self.calibrator = PoseCalibrator()

    self.reset(self.initial_lag, 0)

  def reset(self, initial_lag: float, valid_blocks: int):
    window_len = int(self.window_sec / self.dt)
    self.points = [Points(window_len) for _ in self.speed_bucket_edges]
    self.block_avgs = [BlockAverage(self.block_count, self.block_size, valid_blocks, initial_lag) for _ in self.speed_bucket_edges]

  @property
  def speed_bucket(self) -> int:
    return max(0, int(np.searchsorted(self.speed_bucket_edges, self.v_ego, side="right") - 1))

  def get_msg(self, valid: bool, debug: bool = False) -> capnp._DynamicStructBuilder:
    msg = messaging.new_message('liveDelay')

    msg.valid = valid

    liveDelay = msg.liveDelay

    bucket_values = [avg.get() for avg in self.block_avgs]
    bucket_statuses = []
    bucket_applied = []
    for avg, (valid_mean, valid_std, _, _) in zip(self.block_avgs, bucket_values, strict=True):
      if avg.valid_blocks < self.min_valid_block_count or np.isnan(valid_mean) or np.isnan(valid_std):
        status = "unestimated"
      elif valid_std > MAX_LAG_STD:
        status = "invalid"
      else:
        status = "estimated"
      bucket_statuses.append(status)
      bucket_applied.append(min(MAX_LAG, max(MIN_LAG, valid_mean)) if status == "estimated" else self.initial_lag)

    block_avg = self.block_avgs[self.speed_bucket]
    _, _, current_mean_lag, current_std = bucket_values[self.speed_bucket]
    liveDelay.status = bucket_statuses[self.speed_bucket]
    liveDelay.lateralDelay = interpolate_bucket_values(self.v_ego, self.speed_bucket_edges, bucket_applied)

    if not np.isnan(current_mean_lag) and not np.isnan(current_std):
      liveDelay.lateralDelayEstimate = current_mean_lag
      liveDelay.lateralDelayEstimateStd = current_std
    else:
      liveDelay.lateralDelayEstimate = self.initial_lag
      liveDelay.lateralDelayEstimateStd = 0.0

    liveDelay.validBlocks = block_avg.valid_blocks
    liveDelay.calPerc = min(100 * (block_avg.valid_blocks * self.block_size + block_avg.idx) //
                            (self.min_valid_block_count * self.block_size), 100)
    liveDelay.speedBucket = self.speed_bucket
    liveDelay.speedBucketEdges = self.speed_bucket_edges.tolist()
    liveDelay.lateralDelayBuckets = [min(MAX_LAG, max(MIN_LAG, value[2])) if not np.isnan(value[2]) else self.initial_lag for value in bucket_values]
    liveDelay.lateralDelayEstimateStdBuckets = [value[3] if not np.isnan(value[3]) else 0.0 for value in bucket_values]
    liveDelay.validBlocksBuckets = [avg.valid_blocks for avg in self.block_avgs]
    liveDelay.calPercBuckets = [min(100 * (avg.valid_blocks * self.block_size + avg.idx) //
                                        (self.min_valid_block_count * self.block_size), 100) for avg in self.block_avgs]
    liveDelay.statusBuckets = bucket_statuses
    liveDelay.lateralDelayAppliedBuckets = bucket_applied
    liveDelay.blockIdxBuckets = [avg.block_idx for avg in self.block_avgs]
    liveDelay.sampleIdxBuckets = [avg.idx for avg in self.block_avgs]
    liveDelay.blockValuesBuckets = [avg.values.flatten().tolist() for avg in self.block_avgs]
    liveDelay.learningCountdownBuckets = [max(0.0, self.okay_window_sec - count * self.dt) for count in self.consecutive_okay]
    liveDelay.learningResetReasonBuckets = self.learning_reset_reasons
    if debug:
      liveDelay.points = np.concatenate([avg.values.flatten() for avg in self.block_avgs]).tolist()
    liveDelay.version = VERSION

    return msg

  def handle_log(self, t: float, which: str, msg: capnp._DynamicStructReader):
    if which == "carControl":
      self.lat_active = msg.latActive
    elif which == "carState":
      self.steering_pressed = msg.steeringPressed
      self.v_ego = msg.vEgo
    elif which == "controlsState":
      self.steering_saturated = getattr(msg.lateralControlState, msg.lateralControlState.which()).saturated
      self.desired_curvature = msg.desiredCurvature
    elif which == "liveCalibration":
      self.calibrator.feed_live_calib(msg)
    elif which == "livePose":
      device_pose = Pose.from_live_pose(msg)
      calibrated_pose = self.calibrator.build_calibrated_pose(device_pose)
      self.yaw_rate = calibrated_pose.angular_velocity.yaw
      self.yaw_rate_std = calibrated_pose.angular_velocity.yaw_std
      self.pose_valid = msg.angularVelocityDevice.valid and msg.posenetOK and msg.inputsOK
    self.t = t

  def points_enough(self, points: Points):
    return points.num_points >= int(self.okay_window_sec / self.dt)

  def points_valid(self, points: Points, speed_bucket: int):
    required_points = int(self.okay_window_sec / self.dt)
    return points.num_okay >= required_points and self.consecutive_okay[speed_bucket] >= required_points

  def update_points(self):
    la_desired = self.desired_curvature * self.v_ego * self.v_ego
    la_actual_pose = self.yaw_rate * self.v_ego

    fast = self.v_ego > self.min_vego
    turning = np.abs(self.yaw_rate) >= self.min_yr
    sensors_valid = self.pose_valid and np.abs(self.yaw_rate) < MAX_YAW_RATE_SANITY_CHECK and self.yaw_rate_std < MAX_YAW_RATE_SANITY_CHECK
    la_valid = np.abs(la_actual_pose) <= self.max_lat_accel and np.abs(la_desired - la_actual_pose) <= self.max_lat_accel_diff
    calib_valid = self.calibrator.calib_valid

    if not self.lat_active:
      self.last_lat_inactive_t = self.t
    if self.steering_pressed:
      self.last_steering_pressed_t = self.t
    if self.steering_saturated:
      self.last_steering_saturated_t = self.t
    if not sensors_valid or not la_valid:
      self.last_pose_invalid_t = self.t

    has_recovered = all( # wait for recovery after !lat_active, steering_pressed, steering_saturated, !sensors/la_valid
      self.t - last_t >= self.min_recovery_buffer_sec
      for last_t in [self.last_lat_inactive_t, self.last_steering_pressed_t, self.last_steering_saturated_t, self.last_pose_invalid_t]
    )
    okay = self.lat_active and not self.steering_pressed and not self.steering_saturated and \
           fast and turning and has_recovered and calib_valid and sensors_valid and la_valid

    speed_bucket = self.speed_bucket
    for i, points in enumerate(self.points):
      in_bucket_okay = okay and i == speed_bucket
      points.update(self.t, la_desired, la_actual_pose, in_bucket_okay)
      if in_bucket_okay:
        self.consecutive_okay[i] += 1
        if self.consecutive_okay[i] >= int(self.okay_window_sec / self.dt):
          self.learning_reset_reasons[i] = ""
      else:
        self.consecutive_okay[i] = 0
        if i != speed_bucket:
          self.learning_reset_reasons[i] = "outside speed band"
        elif self.steering_pressed:
          self.learning_reset_reasons[i] = "driver steering"
        elif not self.lat_active:
          self.learning_reset_reasons[i] = "lateral inactive"
        elif self.steering_saturated:
          self.learning_reset_reasons[i] = "steering saturated"
        elif not calib_valid:
          self.learning_reset_reasons[i] = "calibration invalid"
        elif not sensors_valid:
          self.learning_reset_reasons[i] = "pose invalid"
        elif not la_valid:
          self.learning_reset_reasons[i] = "lateral error"
        elif not fast:
          self.learning_reset_reasons[i] = "speed too low"
        elif not turning:
          self.learning_reset_reasons[i] = "insufficient yaw"

  def update_estimate(self):
    speed_bucket = self.speed_bucket
    points = self.points[speed_bucket]
    if not self.points_enough(points):
      return

    times, desired, actual, okay = points.get()
    # check if there are any new valid data points since the last update
    is_valid = self.points_valid(points, speed_bucket) and (actual.max() - actual.min() >= MIN_LAT_ACCEL_RANGE)
    last_estimate_t = self.last_estimate_ts[speed_bucket]
    if last_estimate_t != 0 and times[0] <= last_estimate_t:
      new_values_start_idx = next(-i for i, t in enumerate(reversed(times)) if t <= last_estimate_t)
      is_valid = is_valid and not (new_values_start_idx == 0 or not np.any(okay[new_values_start_idx:]))

    desired = masked_symmetric_moving_average(desired, okay, SMOOTH_K, SMOOTH_SIGMA)
    actual = masked_symmetric_moving_average(actual, okay, SMOOTH_K, SMOOTH_SIGMA)

    delay, corr, confidence = self.actuator_delay(desired, actual, okay, self.dt, MIN_LAG, MAX_LAG)
    if corr < self.min_ncc or confidence < self.min_confidence or not is_valid:
      return

    self.block_avgs[speed_bucket].update(delay)
    self.last_estimate_ts[speed_bucket] = self.t

  @staticmethod
  def actuator_delay(expected_sig: np.ndarray, actual_sig: np.ndarray, mask: np.ndarray,
                     dt: float, min_lag: float, max_lag: float) -> tuple[float, float, float]:
    assert len(expected_sig) == len(actual_sig)
    min_lag_samples, max_lag_samples, one_sec_samples = int(round(min_lag / dt)), int(round(max_lag / dt)), int(round(1.0 / dt))
    padded_size = fft_next_good_size(len(expected_sig) + max(max_lag_samples, one_sec_samples))

    ncc = masked_normalized_cross_correlation(expected_sig, actual_sig, mask, padded_size)

    # only consider lags from ranges:
    roi = np.s_[len(expected_sig) - 1 + min_lag_samples: len(expected_sig) - 1 + max_lag_samples] # min_lag - max_lag range
    threshold_roi = np.s_[len(expected_sig) - 1: len(expected_sig) - 1 + one_sec_samples] # 0 - 1 second range
    confidence_roi = np.s_[threshold_roi.start - CORR_BORDER_OFFSET: threshold_roi.stop + CORR_BORDER_OFFSET] # threshold range +/- border
    roi_ncc, confidence_roi_ncc, threshold_roi_ncc = ncc[roi], ncc[confidence_roi], ncc[threshold_roi]

    max_corr_index = np.argmax(roi_ncc)
    corr = roi_ncc[max_corr_index]
    lag = parabolic_peak_interp(roi_ncc, max_corr_index) * dt + min_lag

    # to estimate lag confidence, gather all high-correlation candidates and see how spread they are
    # if e.g. 0.8 and 0.4 are both viable, this is an ambiguous case
    ncc_thresh = (threshold_roi_ncc.max() - threshold_roi_ncc.min()) * LAG_CANDIDATE_CORR_THRESHOLD + threshold_roi_ncc.min()
    good_lag_candidate_mask = confidence_roi_ncc >= ncc_thresh
    good_lag_candidate_edges = np.diff(good_lag_candidate_mask.astype(int), prepend=0, append=0)
    starts, ends = np.where(good_lag_candidate_edges == 1)[0], np.where(good_lag_candidate_edges == -1)[0] - 1
    run_idx = np.searchsorted(starts, max_corr_index + CORR_BORDER_OFFSET, side='right') - 1
    width = ends[run_idx] - starts[run_idx] + 1
    confidence = np.clip(1 - width * dt, 0, 1)

    return lag, corr, confidence


def retrieve_initial_lag(params: Params, CP: car.CarParams):
  last_lag_data = params.get("LiveDelay")
  last_carparams_data = params.get("CarParamsPrevRoute")

  if last_lag_data is not None:
    try:
      with log.Event.from_bytes(last_lag_data) as last_lag_msg, car.CarParams.from_bytes(last_carparams_data) as last_CP:
        ld = last_lag_msg.liveDelay
        if last_CP.carFingerprint != CP.carFingerprint:
          raise Exception("Car model mismatch")

        lags, valid_blocks, status, version = list(ld.lateralDelayBuckets), list(ld.validBlocksBuckets), ld.status, ld.version
        assert len(lags) == len(SPEED_BUCKET_EDGES) and len(valid_blocks) == len(SPEED_BUCKET_EDGES), "Invalid number of speed buckets"
        assert all(blocks <= BLOCK_NUM for blocks in valid_blocks), "Invalid number of valid blocks"
        assert status != log.LiveDelayData.Status.invalid, "Lag estimate is invalid"
        assert version == VERSION, f"Lag estimate is from a different version (got {version}, expected {VERSION})"
        values = [list(v) for v in ld.blockValuesBuckets]
        if len(values) == len(SPEED_BUCKET_EDGES):
          block_indices, sample_indices = list(ld.blockIdxBuckets), list(ld.sampleIdxBuckets)
          assert len(block_indices) == len(values) and len(sample_indices) == len(values), "Invalid saved bucket state"
          assert all(len(v) == BLOCK_NUM for v in values), "Invalid saved block values"
        else:  # migrate version 3 state saved before per-bucket progress persistence
          values = [[lag] * BLOCK_NUM for lag in lags]
          block_indices = [blocks % BLOCK_NUM for blocks in valid_blocks]
          sample_indices = [0] * len(valid_blocks)
          active_bucket = ld.speedBucket
          accepted = round(ld.calPerc * (BLOCK_NUM_NEEDED * BLOCK_SIZE) / 100) - valid_blocks[active_bucket] * BLOCK_SIZE
          sample_indices[active_bucket] = min(max(accepted, 0), BLOCK_SIZE - 1)
        return list(zip(values, block_indices, sample_indices, valid_blocks, strict=True))
    except Exception as e:
      cloudlog.error(f"Failed to retrieve initial lag: {e}")
      params.remove("LiveDelay")

  return None


def main():
  config_realtime_process([0, 1, 2, 3], 5)

  DEBUG = bool(int(os.getenv("DEBUG", "0")))

  pm = messaging.PubMaster(['liveDelay'])
  sm = messaging.SubMaster(['livePose', 'liveCalibration', 'carState', 'controlsState', 'carControl'], poll='livePose')

  params = Params()
  CP = messaging.log_from_bytes(params.get("CarParams", block=True), car.CarParams)

  lag_learner = LateralLagEstimator(CP, 1. / SERVICE_LIST['livePose'].frequency, min_vego=0.0, speed_bucket_edges=SPEED_BUCKET_EDGES)
  if (initial_lag_params := retrieve_initial_lag(params, CP)) is not None:
    for avg, (values, block_idx, idx, valid_blocks) in zip(lag_learner.block_avgs, initial_lag_params, strict=True):
      avg.valid_blocks = valid_blocks
      avg.restore(values, block_idx, idx)

  lagd_toggle = LagdToggle(CP)
  last_cache_t = 0.0
  last_cached_progress = None

  while True:
    sm.update()
    if sm.all_checks():
      for which in sorted(sm.updated.keys(), key=lambda x: sm.logMonoTime[x]):
        if sm.updated[which]:
          t = sm.logMonoTime[which] * 1e-9
          lag_learner.handle_log(t, which, sm[which])
      lag_learner.update_points()

    # 4Hz driven by livePose
    if sm.frame % 5 == 0:
      lag_learner.update_estimate()
      lag_msg = lag_learner.get_msg(sm.all_checks(), DEBUG)
      lag_msg_dat = lag_msg.to_bytes()
      pm.send('liveDelay', lag_msg_dat)

      progress = tuple((avg.valid_blocks, avg.idx) for avg in lag_learner.block_avgs)
      if progress != last_cached_progress and lag_learner.t - last_cache_t >= 5.0:
        params.put("LiveDelay", lag_msg_dat)
        last_cache_t = lag_learner.t
        last_cached_progress = progress

      if sm.frame % 60 == 0:  # read from and write to params every 3 seconds
        lagd_toggle.update(lag_msg)
