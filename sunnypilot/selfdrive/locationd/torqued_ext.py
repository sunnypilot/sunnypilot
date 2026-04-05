"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np

from cereal import car, log

from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.common.swaglog import cloudlog
from openpilot.sunnypilot import PARAMS_UPDATE_PERIOD

RELAXED_MIN_BUCKET_POINTS = np.array([1, 200, 300, 500, 500, 300, 200, 1])

ALLOWED_CARS = ['toyota', 'hyundai', 'rivian', 'honda']

# Default speed bins — used when car has no speed_dependent.toml entry.
DEFAULT_SPEED_BIN_BOUNDS = [(5, 8), (8, 12), (12, 18), (18, 24), (24, 29), (29, 35), (35, 40)]
DEFAULT_SPEED_BIN_CENTERS = [6.5, 10.0, 15.0, 21.0, 26.5, 32.0, 37.5]


class TorqueEstimatorExt:
  """SP extension mixed into TorqueEstimator via multiple inheritance.

  Adds per-speed-bin learning on top of upstream's single-value torqued.
  Gated by SpeedDependentTorqueToggle (offroad-only).

  Data flow:
    1. torqued calls _on_torque_point() for each quality-filtered sample → routed to speed bin
    2. _estimate_params_speed_binned() runs independent SVD fit per bin (same algo as upstream)
    3. Per-bin validity uses upstream's is_valid() — requires sufficient steer-range coverage
    4. _extend_msg() writes per-bin values to cereal; invalid bins fall back to seed/global values
    5. The lateral controller interpolates latAccelFactor and friction by speed each frame

  Bin configuration:
    - Cars with a speed_dependent.toml entry use per-car bin centers (and derived bounds)
    - Cars without an entry use DEFAULT_SPEED_BIN_BOUNDS and seed all bins with global offline values
  """

  def __init__(self, CP: car.CarParams):
    self.CP = CP
    self._params = Params()
    self.frame = -1

    self.enforce_torque_control_toggle = self._params.get_bool("EnforceTorqueControl")  # only during init
    self.use_params = self.CP.brand in ALLOWED_CARS and self.CP.lateralTuning.which() == 'torque'
    self.use_live_torque_params = self._params.get_bool("LiveTorqueParamsToggle")
    self.torque_override_enabled = self._params.get_bool("TorqueParamsOverrideEnabled")
    # Independently gated — not restricted by ALLOWED_CARS brand list
    self.speed_binned = (self.CP.lateralTuning.which() == 'torque'
                         and self._params.get_bool("SpeedDependentTorqueToggle"))
    # Defaults — overwritten by TorqueEstimator.__init__ before initialize_custom_params runs
    self.min_bucket_points = RELAXED_MIN_BUCKET_POINTS
    self.factor_sanity = 0.0
    self.friction_sanity = 0.0
    self.offline_latAccelFactor = 0.0
    self.offline_friction = 0.0

  def initialize_custom_params(self, decimated=False):
    self.update_use_params()

    if self.enforce_torque_control_toggle:
      if self._params.get_bool("LiveTorqueParamsRelaxedToggle"):
        self.min_bucket_points = RELAXED_MIN_BUCKET_POINTS / (10 if decimated else 1)
        self.factor_sanity = 0.5 if decimated else 1.0
        self.friction_sanity = 0.8 if decimated else 1.0

      if self._params.get_bool("CustomTorqueParams"):
        self.offline_latAccelFactor = float(self._params.get("TorqueParamsOverrideLatAccelFactor", return_default=True))
        self.offline_friction = float(self._params.get("TorqueParamsOverrideFriction", return_default=True))

    # Init speed bins and restore cached values before first get_msg
    if self.speed_binned:
      self._post_reset()
      self._restore_ext_cache()

  def _update_params(self):
    if self.frame % int(PARAMS_UPDATE_PERIOD / DT_MDL) == 0:
      self.use_live_torque_params = self._params.get_bool("LiveTorqueParamsToggle")
      self.torque_override_enabled = self._params.get_bool("TorqueParamsOverrideEnabled")

  def update_use_params(self):
    self._update_params()

    if self.enforce_torque_control_toggle:
      if self.torque_override_enabled:
        self.use_params = False
      else:
        self.use_params = self.use_live_torque_params

    self.frame += 1

  # --- Speed-binned learning hooks (called from TorqueEstimator) ---

  @staticmethod
  def _centers_to_bounds(centers):
    """Derive bin bounds from centers using midpoints between consecutive centers.
    First bin starts at default lower edge (5 m/s), last bin ends at default upper edge (40 m/s)."""
    bounds = []
    for i, c in enumerate(centers):
      lo = DEFAULT_SPEED_BIN_BOUNDS[0][0] if i == 0 else (centers[i - 1] + c) / 2
      hi = DEFAULT_SPEED_BIN_BOUNDS[-1][1] if i == len(centers) - 1 else (c + centers[i + 1]) / 2
      bounds.append((lo, hi))
    return bounds

  def _post_reset(self):
    """Initializes per-speed-bin buckets and filters. Must run after factor_sanity/offline values are set."""
    if not self.speed_binned:
      return

    from openpilot.selfdrive.locationd.torqued import TorqueBuckets, STEER_BUCKET_BOUNDS, \
      POINTS_PER_BUCKET, MIN_FILTER_DECAY
    from opendbc.sunnypilot.car.interfaces import get_speed_dep_config

    cfg = get_speed_dep_config().get(self.CP.carFingerprint, {})

    if 'speed_bp' in cfg:
      self.speed_bin_centers = list(cfg['speed_bp'])
      self.speed_bin_bounds = self._centers_to_bounds(self.speed_bin_centers)
    else:
      self.speed_bin_bounds = list(DEFAULT_SPEED_BIN_BOUNDS)
      self.speed_bin_centers = list(DEFAULT_SPEED_BIN_CENTERS)

    n_bins = len(self.speed_bin_bounds)

    self.speed_bin_points = [self._make_speed_bin_bucket(TorqueBuckets, STEER_BUCKET_BOUNDS, POINTS_PER_BUCKET) for _ in range(n_bins)]
    self._speed_bin_last_len = [0] * n_bins
    self._speed_bin_last_valid = [False] * n_bins

    # Seed values: from TOML if configured, otherwise global offline values for all bins
    ref_lafs = cfg.get('laf_bp', [self.offline_latAccelFactor] * n_bins)
    ref_frictions = cfg.get('friction_bp', [self.offline_friction] * n_bins)
    self.speed_bin_decays = [MIN_FILTER_DECAY] * n_bins
    self.speed_bin_filtered = [
      {'latAccelFactor': FirstOrderFilter(ref_lafs[i], self.speed_bin_decays[i], DT_MDL),
       'frictionCoefficient': FirstOrderFilter(ref_frictions[i], self.speed_bin_decays[i], DT_MDL)}
      for i in range(n_bins)
    ]
    # SVD results get clipped to ±sanity% of seeds to prevent runaway learning
    self.speed_bin_lat_accel_factor_bounds = [
      ((1.0 - self.factor_sanity) * factor, (1.0 + self.factor_sanity) * factor)
      for factor in ref_lafs
    ]
    self.speed_bin_friction_bounds = [
      ((1.0 - self.friction_sanity) * f, (1.0 + self.friction_sanity) * f)
      for f in ref_frictions
    ]

  def _make_speed_bin_bucket(self, TorqueBuckets, STEER_BUCKET_BOUNDS, POINTS_PER_BUCKET):
    """Create a single speed-bin TorqueBuckets instance.
    Per-bucket minimums are scaled down from the global learner since each
    speed bin sees a fraction of the total data."""
    scaled_min = np.maximum(self.min_bucket_points // len(self.speed_bin_bounds), 1)
    return TorqueBuckets(x_bounds=STEER_BUCKET_BOUNDS,
                         min_points=scaled_min,
                         min_points_total=int(scaled_min.sum()),
                         points_per_bucket=POINTS_PER_BUCKET,
                         rowsize=3)

  def _on_torque_point(self, steer, lateral_acc, vego):
    """Called from handle_log. Routes quality-filtered points to speed bins."""
    if not self.speed_binned:
      return
    for i, (lo, hi) in enumerate(self.speed_bin_bounds):
      if lo <= vego < hi:
        self.speed_bin_points[i].add_point(steer, lateral_acc)
        break

  def _restore_ext_cache(self, cache_ltp=None):
    """Restores per-bin filter values and points from cache.
    Reads from Params when cache_ltp is not provided."""
    if not self.speed_binned:
      return
    try:
      if cache_ltp is None:
        cache = self._params.get("LiveTorqueParameters")
        if not cache:
          return
        with log.Event.from_bytes(cache) as evt:
          cache_ltp = evt.liveTorqueParameters
      from openpilot.selfdrive.locationd.torqued import MIN_FILTER_DECAY
      n_bins = len(self.speed_bin_bounds)
      # Reject cache from a different config (e.g. TOML update changed bin centers)
      if not np.allclose(list(cache_ltp.speedBinCenters), self.speed_bin_centers, atol=0.01):
        cloudlog.info("speed-dep: config changed, restarting learning")
        return
      if (len(cache_ltp.speedBinLatAccelFactors) == n_bins and
          len(cache_ltp.speedBinFrictions) == n_bins):
        for i in range(n_bins):
          self.speed_bin_filtered[i]['latAccelFactor'].x = cache_ltp.speedBinLatAccelFactors[i]
          self.speed_bin_filtered[i]['frictionCoefficient'].x = cache_ltp.speedBinFrictions[i]
        if len(cache_ltp.speedBinPoints) == n_bins:
          for i in range(n_bins):
            self.speed_bin_points[i].load_points(cache_ltp.speedBinPoints[i])
        # self.decay doesn't exist yet at init time (set by upstream reset()), fallback is intentional
        self.speed_bin_decays = [getattr(self, 'decay', MIN_FILTER_DECAY)] * n_bins
        cloudlog.info("restored speed-bin torque params from cache")
    except Exception:
      cloudlog.exception("speed-dep: failed to restore cache")

  def _estimate_params_speed_binned(self):
    """Run independent SVD fit per speed bin. Resets bin on NaN with valid data."""
    from openpilot.selfdrive.locationd.torqued import TorqueBuckets, STEER_BUCKET_BOUNDS, \
      POINTS_PER_BUCKET, FRICTION_FACTOR, FIT_POINTS_TOTAL, slope2rot, MIN_FILTER_DECAY, MAX_FILTER_DECAY

    results = []
    for i, bucket in enumerate(self.speed_bin_points):
      if not bucket.is_calculable():
        results.append((i, False))
        continue

      # Skip bins with no new data since last fit
      cur_len = len(bucket)
      if cur_len == self._speed_bin_last_len[i]:
        results.append((i, self._speed_bin_last_valid[i]))
        continue

      # Same total least squares SVD as upstream's estimate_params()
      points = bucket.get_points(FIT_POINTS_TOTAL)
      try:
        _, _, v = np.linalg.svd(points, full_matrices=False)
        slope, offset = -v.T[0:2, 2] / v.T[2, 2]  # slope = latAccelFactor
        _, spread = np.matmul(points[:, [0, 2]], slope2rot(slope)).T
        friction_coeff = np.std(spread) * FRICTION_FACTOR
        if not any(np.isnan(val) for val in [slope, friction_coeff]):
          factor_lo, factor_hi = self.speed_bin_lat_accel_factor_bounds[i]
          fric_lo, fric_hi = self.speed_bin_friction_bounds[i]
          self.speed_bin_decays[i] = min(self.speed_bin_decays[i] + DT_MDL, MAX_FILTER_DECAY)  # slow down filter over time
          self.speed_bin_filtered[i]['latAccelFactor'].update(np.clip(slope, factor_lo, factor_hi))
          self.speed_bin_filtered[i]['latAccelFactor'].update_alpha(self.speed_bin_decays[i])
          self.speed_bin_filtered[i]['frictionCoefficient'].update(np.clip(friction_coeff, fric_lo, fric_hi))
          self.speed_bin_filtered[i]['frictionCoefficient'].update_alpha(self.speed_bin_decays[i])
          self._speed_bin_last_len[i] = cur_len
          self._speed_bin_last_valid[i] = bucket.is_valid()
          results.append((i, self._speed_bin_last_valid[i]))
          continue
      except np.linalg.LinAlgError:
        pass

      # NaN with valid data = poisoned bucket, reset to recover
      if bucket.is_valid():
        cloudlog.warning(f"speed-dep: bin {i} produced NaN with valid data, resetting bin")
        self.speed_bin_points[i] = self._make_speed_bin_bucket(TorqueBuckets, STEER_BUCKET_BOUNDS, POINTS_PER_BUCKET)
        self.speed_bin_decays[i] = MIN_FILTER_DECAY
        self._speed_bin_last_len[i] = 0
      self._speed_bin_last_valid[i] = False
      results.append((i, False))
    return results

  def _extend_msg(self, ltp, with_points):
    """Appends per-bin values to the cereal msg. with_points=True on cache writes (every 60s)."""
    if not self.speed_binned:
      return
    bin_results = self._estimate_params_speed_binned()
    n_bins = len(self.speed_bin_bounds)

    lat_factors, frictions, valid_flags = [], [], []
    bin_points = [] if with_points else None
    for i in range(n_bins):
      lat_factors.append(float(self.speed_bin_filtered[i]['latAccelFactor'].x))
      frictions.append(float(self.speed_bin_filtered[i]['frictionCoefficient'].x))
      _, valid = bin_results[i]
      valid_flags.append(valid)
      if with_points:
        bin_points.append(self.speed_bin_points[i].get_points()[:, [0, 2]].tolist())

    ltp.speedBinCenters = self.speed_bin_centers
    ltp.speedBinLatAccelFactors = lat_factors
    ltp.speedBinFrictions = frictions
    ltp.speedBinValid = valid_flags
    if with_points:
      ltp.speedBinPoints = bin_points
