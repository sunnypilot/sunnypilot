"""Integration tests for speed-dependent torque — controller pipeline.

Tests the full data flow from torqued output through controlsd to the
torque_params used in the steering controller: per-frame latAccelFactor and friction
interpolation, sanity bounds, toggle-off behavior, and manual override.

Tests LatControlTorqueExtOverride directly (the class that owns the
per-frame interpolation logic) rather than LatControlTorqueExt, which
inherits from NNLC and requires model files to init.
"""
import numpy as np
import pytest

from unittest.mock import MagicMock, patch  # noqa: TID251
from opendbc.sunnypilot.car.interfaces import get_speed_dep_config
from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_torque_ext import LatControlTorqueExt
from openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_torque_ext_override import LatControlTorqueExtOverride

SPEED_DEP_CARS = get_speed_dep_config()

PATCH_PARAMS_OVERRIDE = 'openpilot.sunnypilot.selfdrive.controls.lib.latcontrol_torque_ext_override.Params'
PATCH_PARAMS_TORQUED_EXT = 'openpilot.sunnypilot.selfdrive.locationd.torqued_ext.Params'
PATCH_PARAMS_TORQUED = 'openpilot.selfdrive.locationd.torqued.Params'
PATCH_GET_SPEED_DEP_CONFIG = 'opendbc.sunnypilot.car.interfaces.get_speed_dep_config'

# Sample tables
SAMPLE_SPEED_BP = [6.5, 10.0, 15.0, 21.0, 26.5, 32.0, 37.5]
SAMPLE_LAT_ACCEL_FACTOR_BP = [2.39, 2.52, 2.71, 2.39, 2.28, 2.22, 2.21]
SAMPLE_FRICTION_BP = [0.177, 0.158, 0.131, 0.118, 0.113, 0.109, 0.108]


class TorqueParams:
  """Mutable stand-in for CarParams.LateralTorqueTuning builder."""
  def __init__(self, latAccelFactor=2.0, latAccelOffset=0.0, friction=0.15):
    self.latAccelFactor = latAccelFactor
    self.latAccelOffset = latAccelOffset
    self.friction = friction


@patch(PATCH_PARAMS_OVERRIDE)
def make_override(mock_params_cls, enforce=False, manual_override=False,
                  manual_lat_accel_factor='200', manual_friction='15'):
  """Create a LatControlTorqueExtOverride with mocked Params."""
  mock_inst = mock_params_cls.return_value
  mock_inst.get_bool.side_effect = lambda k: {
    'EnforceTorqueControl': enforce,
    'TorqueParamsOverrideEnabled': manual_override,
  }.get(k, False)
  mock_inst.get.side_effect = lambda k, **kw: {
    'TorqueParamsOverrideLatAccelFactor': manual_lat_accel_factor,
    'TorqueParamsOverrideFriction': manual_friction,
  }.get(k)

  CP = MagicMock()
  ovr = LatControlTorqueExtOverride(CP)
  return ovr


def activate_speed_dep(ovr, speed_bp=None, lat_accel_factor_bp=None, friction_bp=None):
  """Simulate update_speed_dep_torque setting tables on the override."""
  ovr._speed_dep_active = True
  ovr._speed_dep_speed_bp = speed_bp or list(SAMPLE_SPEED_BP)
  ovr._speed_dep_lat_accel_factor_bp = lat_accel_factor_bp or list(SAMPLE_LAT_ACCEL_FACTOR_BP)
  ovr._speed_dep_friction_bp = friction_bp or list(SAMPLE_FRICTION_BP)


class TestLafInterpolatedBySpeed:
  """torque_params.latAccelFactor must be speed-interpolated
  before torque_from_lateral_accel reads it."""

  def test_lat_accel_factor_set_to_interpolated_value(self):
    ovr = make_override()
    activate_speed_dep(ovr)
    tp = TorqueParams(latAccelFactor=999.0)  # sentinel

    ovr._last_vego = 10.0
    ovr.update_override_torque_params(tp)

    expected = float(np.interp(10.0, SAMPLE_SPEED_BP, SAMPLE_LAT_ACCEL_FACTOR_BP))
    assert tp.latAccelFactor == pytest.approx(expected, abs=1e-4), \
      f"latAccelFactor should be {expected}, got {tp.latAccelFactor}"

  def test_lat_accel_factor_differs_at_different_speeds(self):
    ovr = make_override()
    activate_speed_dep(ovr)

    tp = TorqueParams()
    ovr._last_vego = 6.5
    ovr.update_override_torque_params(tp)
    factor_low = tp.latAccelFactor

    tp = TorqueParams()
    ovr._last_vego = 37.5
    ovr.update_override_torque_params(tp)
    factor_high = tp.latAccelFactor

    assert factor_low != pytest.approx(factor_high, abs=0.01), \
      "latAccelFactor must differ between 6.5 m/s and 37.5 m/s"

  def test_lat_accel_factor_not_global_value(self):
    """latAccelFactor should NOT be the global scalar."""
    ovr = make_override()
    activate_speed_dep(ovr)
    global_factor = 2.0
    tp = TorqueParams(latAccelFactor=global_factor)

    ovr._last_vego = 6.5  # seed latAccelFactor at 6.5 is 2.39, not 2.0
    ovr.update_override_torque_params(tp)

    assert tp.latAccelFactor != pytest.approx(global_factor, abs=0.01), \
      "latAccelFactor should be speed-interpolated, not the global value"


class TestFrictionInterpolatedBySpeed:
  """torque_params.friction must be speed-interpolated
  before get_friction reads it."""

  def test_friction_set_to_interpolated_value(self):
    ovr = make_override()
    activate_speed_dep(ovr)
    tp = TorqueParams(friction=999.0)

    ovr._last_vego = 35.0
    ovr.update_override_torque_params(tp)

    expected = float(np.interp(35.0, SAMPLE_SPEED_BP, SAMPLE_FRICTION_BP))
    assert tp.friction == pytest.approx(expected, abs=1e-4)

  def test_friction_differs_at_different_speeds(self):
    ovr = make_override()
    activate_speed_dep(ovr)

    tp = TorqueParams()
    ovr._last_vego = 6.5
    ovr.update_override_torque_params(tp)
    fric_low = tp.friction

    tp = TorqueParams()
    ovr._last_vego = 37.5
    ovr.update_override_torque_params(tp)
    fric_high = tp.friction

    assert fric_low != pytest.approx(fric_high, abs=0.01)


class TestToggleOffClearsState:
  """_speed_dep_active must be cleared when bins disappear."""

  def test_inactive_by_default(self):
    ovr = make_override()
    assert not ovr._speed_dep_active

  def test_deactivated_does_not_modify_params(self):
    ovr = make_override()
    activate_speed_dep(ovr)
    # Deactivate
    ovr._speed_dep_active = False

    tp = TorqueParams(latAccelFactor=99.0, friction=99.0)
    ovr._last_vego = 15.0
    ovr.update_override_torque_params(tp)

    assert tp.latAccelFactor == 99.0, "Should not modify params when inactive"
    assert tp.friction == 99.0

  def test_empty_speed_bp_does_not_modify_params(self):
    ovr = make_override()
    activate_speed_dep(ovr)
    ovr._speed_dep_speed_bp = []  # empty

    tp = TorqueParams(latAccelFactor=99.0, friction=99.0)
    ovr._last_vego = 15.0
    ovr.update_override_torque_params(tp)

    assert tp.latAccelFactor == 99.0
    assert tp.friction == 99.0


class TestManualOverridePriority:
  """Manual override must take priority over speed-dep."""

  def test_manual_overwrites_speed_dep(self):
    ovr = make_override(enforce=True, manual_override=True,
                        manual_lat_accel_factor='350', manual_friction='25')
    activate_speed_dep(ovr)
    ovr._last_vego = 15.0

    tp = TorqueParams()
    # frame = -1, after +1 -> frame=0, 0 % 300 == 0 -> manual fires
    ovr.update_override_torque_params(tp)

    assert tp.latAccelFactor == pytest.approx(350.0, abs=0.1), \
      "Manual latAccelFactor should overwrite speed-dep"
    assert tp.friction == pytest.approx(25.0, abs=0.1), \
      "Manual friction should overwrite speed-dep"

  def test_speed_dep_used_when_manual_off(self):
    ovr = make_override(enforce=True, manual_override=False)
    activate_speed_dep(ovr)
    ovr._last_vego = 15.0

    tp = TorqueParams()
    ovr.update_override_torque_params(tp)

    expected_factor = float(np.interp(15.0, SAMPLE_SPEED_BP, SAMPLE_LAT_ACCEL_FACTOR_BP))
    assert tp.latAccelFactor == pytest.approx(expected_factor, abs=1e-4), \
      "Without manual override, speed-dep should be used"


class TestChangeDetection:
  """update_override_torque_params should only return changed=True when values differ."""

  def test_no_change_returns_false(self):
    ovr = make_override()
    activate_speed_dep(ovr)
    ovr._last_vego = 15.0

    tp = TorqueParams()
    # First call sets values
    ovr.update_override_torque_params(tp)
    # Second call at same speed — no change
    changed = ovr.update_override_torque_params(tp)
    assert not changed, "Should return False when values haven't changed"

  def test_speed_change_returns_true(self):
    ovr = make_override()
    activate_speed_dep(ovr)

    tp = TorqueParams()
    ovr._last_vego = 6.5
    ovr.update_override_torque_params(tp)

    ovr._last_vego = 37.5  # big speed change -> values change
    changed = ovr.update_override_torque_params(tp)
    assert changed, "Should return True when values changed"


class TestLearnerSanityBounds:
  """Speed-bin sanity bounds must allow learning regardless of
  the 'Less Restrict' toggle."""

  @patch(PATCH_PARAMS_TORQUED_EXT)
  @patch(PATCH_PARAMS_TORQUED)
  def test_sanity_bounds_allow_learning_without_relaxed(self, mock_params_cls, mock_ext_cls):
    """With LiveTorqueParamsRelaxedToggle OFF (factor_sanity=0.0),
    speed bins must still have +/-30% bounds, not (seed, seed)."""
    mock_params_cls.return_value.get.return_value = None
    mock_ext_cls.return_value.get_bool.side_effect = lambda k: {
      'SpeedDependentTorqueToggle': True,
      'EnforceTorqueControl': False,
      'LiveTorqueParamsRelaxedToggle': False,
    }.get(k, False)
    mock_ext_cls.return_value.get.return_value = None

    from openpilot.selfdrive.locationd.torqued import TorqueEstimator
    CP = MagicMock()
    CP.brand = 'test'
    CP.carFingerprint = next(iter(SPEED_DEP_CARS)) if SPEED_DEP_CARS else 'FAKE'
    CP.lateralTuning.which.return_value = 'torque'
    CP.lateralTuning.torque.latAccelFactor = 2.0
    CP.lateralTuning.torque.friction = 0.15

    est = TorqueEstimator(CP)
    est._on_torque_point(0.1, 0.3, 10.0)  # trigger lazy init

    for i, (lo, hi) in enumerate(est.speed_bin_lat_accel_factor_bounds):
      assert hi > lo, f"Bin {i} latAccelFactor bounds ({lo:.3f}, {hi:.3f}) must allow a range"

    for i, (lo, hi) in enumerate(est.speed_bin_friction_bounds):
      assert hi > lo, f"Bin {i} friction bounds ({lo:.3f}, {hi:.3f}) must allow a range"

  @patch(PATCH_PARAMS_TORQUED_EXT)
  @patch(PATCH_PARAMS_TORQUED)
  def test_clip_allows_10pct_movement(self, mock_params_cls, mock_ext_cls):
    """A learned value 10% above seed should pass through np.clip with +/-30% bounds."""
    mock_params_cls.return_value.get.return_value = None
    mock_ext_cls.return_value.get_bool.side_effect = lambda k: {
      'SpeedDependentTorqueToggle': True,
    }.get(k, False)
    mock_ext_cls.return_value.get.return_value = None

    from openpilot.selfdrive.locationd.torqued import TorqueEstimator
    CP = MagicMock()
    CP.brand = 'test'
    CP.carFingerprint = next(iter(SPEED_DEP_CARS)) if SPEED_DEP_CARS else 'FAKE'
    CP.lateralTuning.which.return_value = 'torque'
    CP.lateralTuning.torque.latAccelFactor = 2.0
    CP.lateralTuning.torque.friction = 0.15

    est = TorqueEstimator(CP)
    est._on_torque_point(0.1, 0.3, 10.0)

    seed_factor = est.speed_bin_filtered[0]['latAccelFactor'].x
    nudged = seed_factor * 1.10
    lo, hi = est.speed_bin_lat_accel_factor_bounds[0]
    clipped = np.clip(nudged, lo, hi)
    assert clipped == pytest.approx(nudged, abs=1e-6), \
      f"+10% nudge ({nudged:.3f}) should not be clipped by +/-30% bounds ({lo:.3f}, {hi:.3f})"


class TestToggleOffFallback:
  """When speed-dep is deactivated, controller must not use stale tables."""

  def test_deactivation_via_empty_bins(self):
    """Simulates toggle-off: update_speed_dep_torque receives empty bins."""
    ovr = make_override()
    activate_speed_dep(ovr)
    assert ovr._speed_dep_active

    # Simulate toggle-off (torqued sends empty speedBinCenters)
    ovr._speed_dep_active = False

    tp = TorqueParams(latAccelFactor=2.35, friction=0.12)
    ovr._last_vego = 15.0
    ovr.update_override_torque_params(tp)

    # Global values should pass through unmodified
    assert tp.latAccelFactor == 2.35
    assert tp.friction == 0.12

  def test_reactivation_after_deactivation(self):
    """Speed-dep can be re-enabled after being disabled."""
    ovr = make_override()
    ovr._speed_dep_active = False

    # Re-enable
    activate_speed_dep(ovr)
    assert ovr._speed_dep_active

    tp = TorqueParams()
    ovr._last_vego = 15.0
    ovr.update_override_torque_params(tp)

    expected_factor = float(np.interp(15.0, SAMPLE_SPEED_BP, SAMPLE_LAT_ACCEL_FACTOR_BP))
    assert tp.latAccelFactor == pytest.approx(expected_factor, abs=1e-4)


class TestUpdateSpeedDepTorqueFallback:
  """Tests for update_speed_dep_torque fallback logic (TOML seeds vs global filtered)."""

  @staticmethod
  def _make_mock_tp(speed_bp, lafs, frictions, valid, global_laf=2.0, global_fric=0.15):
    tp = MagicMock()
    tp.speedBinCenters = speed_bp
    tp.speedBinLatAccelFactors = lafs
    tp.speedBinFrictions = frictions
    tp.speedBinValid = valid
    tp.latAccelFactorFiltered = global_laf
    tp.frictionCoefficientFiltered = global_fric
    tp.latAccelOffsetFiltered = 0.0
    return tp

  @staticmethod
  def _make_mock_self(fingerprint='TEST_CAR'):
    mock_self = MagicMock()
    mock_self.CP.carFingerprint = fingerprint
    mock_self._speed_dep_active = False
    mock_self._speed_dep_speed_bp = []
    mock_self._speed_dep_lat_accel_factor_bp = []
    mock_self._speed_dep_friction_bp = []
    mock_self._speed_dep_car_cfg = None
    return mock_self

  @patch(PATCH_GET_SPEED_DEP_CONFIG)
  def test_toml_seeds_used_for_invalid_bins(self, mock_get_config):
    """Invalid bins should fall back to TOML seed values, not global filtered."""
    seed_lafs = [2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7]
    seed_frictions = [0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17]
    mock_get_config.return_value = {
      'TEST_CAR': {'speed_bp': SAMPLE_SPEED_BP, 'laf_bp': seed_lafs, 'friction_bp': seed_frictions}
    }

    mock_self = self._make_mock_self()
    mock_tp = self._make_mock_tp(SAMPLE_SPEED_BP, [999.0] * 7, [999.0] * 7,
                                 [False] * 7, global_laf=1.0, global_fric=0.05)

    LatControlTorqueExt.update_speed_dep_torque(mock_self, mock_tp)

    assert mock_self._speed_dep_lat_accel_factor_bp == seed_lafs
    assert mock_self._speed_dep_friction_bp == seed_frictions

  @patch(PATCH_GET_SPEED_DEP_CONFIG)
  def test_global_filtered_fallback_when_no_config(self, mock_get_config):
    """Unconfigured car: invalid bins should use global filtered values."""
    mock_get_config.return_value = {}

    mock_self = self._make_mock_self(fingerprint='UNKNOWN_CAR')
    mock_tp = self._make_mock_tp(SAMPLE_SPEED_BP, [999.0] * 7, [999.0] * 7,
                                 [False] * 7, global_laf=2.0, global_fric=0.15)

    LatControlTorqueExt.update_speed_dep_torque(mock_self, mock_tp)

    assert mock_self._speed_dep_lat_accel_factor_bp == [2.0] * 7
    assert mock_self._speed_dep_friction_bp == [0.15] * 7

  @patch(PATCH_GET_SPEED_DEP_CONFIG)
  def test_friction_bp_missing_uses_global_fallback(self, mock_get_config):
    """Config with laf_bp but no friction_bp should use global fallback (not crash)."""
    mock_get_config.return_value = {
      'TEST_CAR': {'speed_bp': SAMPLE_SPEED_BP, 'laf_bp': [2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7]}
      # 'friction_bp' intentionally missing
    }

    mock_self = self._make_mock_self()
    mock_tp = self._make_mock_tp(SAMPLE_SPEED_BP, [999.0] * 7, [999.0] * 7,
                                 [False] * 7, global_laf=2.0, global_fric=0.15)

    LatControlTorqueExt.update_speed_dep_torque(mock_self, mock_tp)

    assert mock_self._speed_dep_lat_accel_factor_bp == [2.0] * 7
    assert mock_self._speed_dep_friction_bp == [0.15] * 7

  @patch(PATCH_GET_SPEED_DEP_CONFIG)
  def test_laf_bp_length_mismatch_uses_global_fallback(self, mock_get_config):
    """Config with wrong-length laf_bp should use global fallback."""
    mock_get_config.return_value = {
      'TEST_CAR': {'speed_bp': SAMPLE_SPEED_BP, 'laf_bp': [2.1, 2.2], 'friction_bp': [0.1, 0.2]}
    }

    mock_self = self._make_mock_self()
    mock_tp = self._make_mock_tp(SAMPLE_SPEED_BP, [999.0] * 7, [999.0] * 7,
                                 [False] * 7, global_laf=2.0, global_fric=0.15)

    LatControlTorqueExt.update_speed_dep_torque(mock_self, mock_tp)

    assert mock_self._speed_dep_lat_accel_factor_bp == [2.0] * 7
    assert mock_self._speed_dep_friction_bp == [0.15] * 7

  @patch(PATCH_GET_SPEED_DEP_CONFIG)
  def test_mixed_valid_invalid_bins(self, mock_get_config):
    """Valid bins use learned values, invalid bins use TOML seeds."""
    seed_lafs = [2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7]
    seed_frictions = [0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17]
    mock_get_config.return_value = {
      'TEST_CAR': {'speed_bp': SAMPLE_SPEED_BP, 'laf_bp': seed_lafs, 'friction_bp': seed_frictions}
    }

    learned_lafs = [3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6]
    learned_frictions = [0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27]
    valid = [True, False, True, False, True, False, False]

    mock_self = self._make_mock_self()
    mock_tp = self._make_mock_tp(SAMPLE_SPEED_BP, learned_lafs, learned_frictions, valid)

    LatControlTorqueExt.update_speed_dep_torque(mock_self, mock_tp)

    for i in range(7):
      if valid[i]:
        assert mock_self._speed_dep_lat_accel_factor_bp[i] == learned_lafs[i]
        assert mock_self._speed_dep_friction_bp[i] == learned_frictions[i]
      else:
        assert mock_self._speed_dep_lat_accel_factor_bp[i] == seed_lafs[i]
        assert mock_self._speed_dep_friction_bp[i] == seed_frictions[i]

  @patch(PATCH_GET_SPEED_DEP_CONFIG)
  def test_empty_bins_deactivate(self, mock_get_config):
    mock_get_config.return_value = {}
    mock_self = self._make_mock_self()
    mock_self._speed_dep_active = True

    mock_tp = MagicMock()
    mock_tp.speedBinCenters = []

    LatControlTorqueExt.update_speed_dep_torque(mock_self, mock_tp)

    assert mock_self._speed_dep_active is False


class TestExtrapolationAtBoundaries:
  """np.interp clamps to edge values for speeds outside the bin range."""

  def test_speed_below_first_bin_clamps(self):
    ovr = make_override()
    activate_speed_dep(ovr)
    tp = TorqueParams()
    ovr._last_vego = 0.0
    ovr.update_override_torque_params(tp)
    assert tp.latAccelFactor == pytest.approx(SAMPLE_LAT_ACCEL_FACTOR_BP[0], abs=1e-4)
    assert tp.friction == pytest.approx(SAMPLE_FRICTION_BP[0], abs=1e-4)

  def test_speed_above_last_bin_clamps(self):
    ovr = make_override()
    activate_speed_dep(ovr)
    tp = TorqueParams()
    ovr._last_vego = 100.0
    ovr.update_override_torque_params(tp)
    assert tp.latAccelFactor == pytest.approx(SAMPLE_LAT_ACCEL_FACTOR_BP[-1], abs=1e-4)
    assert tp.friction == pytest.approx(SAMPLE_FRICTION_BP[-1], abs=1e-4)

  def test_speed_at_exact_bin_center(self):
    ovr = make_override()
    activate_speed_dep(ovr)
    for i, speed in enumerate(SAMPLE_SPEED_BP):
      tp = TorqueParams()
      ovr._last_vego = speed
      ovr.update_override_torque_params(tp)
      assert tp.latAccelFactor == pytest.approx(SAMPLE_LAT_ACCEL_FACTOR_BP[i], abs=1e-4)
      assert tp.friction == pytest.approx(SAMPLE_FRICTION_BP[i], abs=1e-4)
