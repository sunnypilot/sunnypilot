import json
import os

from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit import slc_config


def reset_slc_config_cache():
  slc_config._config_cache = None
  slc_config._config_cache_mtime_ns = None


def write_slc_config(path, config, mtime_ns):
  path.write_text(json.dumps(config))
  os.utime(path, ns=(mtime_ns, mtime_ns))


def test_slc_config_cache_reloads_when_file_changes(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {"speedLimitLowerDecelControlEnabled": False}, 1_000_000_000)
  assert not slc_config.get_slc_no_brake()

  write_slc_config(config_path, {"speedLimitLowerDecelControlEnabled": True}, 2_000_000_000)
  assert slc_config.get_slc_no_brake()


def test_slc_no_brake_accel_defaults_to_gentle_decel(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {}, 1_000_000_000)

  assert slc_config.get_slc_no_brake_accel() == -0.05


def test_slc_lookahead_reads_explicit_keys(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {
    "speedLimitLowerLookaheadEnabled": True,
    "speedLimitLookaheadFactorDown": 4.0,
    "speedLimitLookaheadFactorUp": 1.0,
  }, 1_000_000_000)

  assert slc_config.get_slc_lookahead_lower_limits()
  assert slc_config.get_slc_lookahead_speed_factor_down() == 4.0
  assert slc_config.get_slc_lookahead_speed_factor_up() == 1.0


def test_slc_no_brake_mode_defaults_to_fixed(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {}, 1_000_000_000)

  assert slc_config.get_slc_no_brake_mode() == "fixed"


def test_slc_no_brake_mode_reads_dynamic(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {"speedLimitLowerDecelMode": "dynamic"}, 1_000_000_000)

  assert slc_config.get_slc_no_brake_mode() == "dynamic"


def test_slc_no_brake_mode_reads_idle(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {"speedLimitLowerDecelMode": "idle"}, 1_000_000_000)

  assert slc_config.get_slc_no_brake_mode() == "idle"


def test_slc_no_brake_mode_rejects_unknown_values(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {"speedLimitLowerDecelMode": "other"}, 1_000_000_000)

  assert slc_config.get_slc_no_brake_mode() == "fixed"


def test_slc_no_brake_accel_reads_configured_value(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {"speedLimitLowerDecelFixedAccel": -0.05}, 1_000_000_000)

  assert slc_config.get_slc_no_brake_accel() == -0.05


def test_slc_no_brake_accel_clips_to_negative_range(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {"speedLimitLowerDecelFixedAccel": 0.2}, 1_000_000_000)
  assert slc_config.get_slc_no_brake_accel() == 0.0

  write_slc_config(config_path, {"speedLimitLowerDecelFixedAccel": -2.0}, 2_000_000_000)
  assert slc_config.get_slc_no_brake_accel() == -1.2


def test_slc_no_brake_release_gap_defaults_to_5_kph(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {}, 1_000_000_000)

  assert slc_config.get_slc_no_brake_release_gap_kph() == 5.0


def test_slc_no_brake_release_gap_reads_configured_value(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {"speedLimitLowerDecelReleaseGapKph": 8.0}, 1_000_000_000)

  assert slc_config.get_slc_no_brake_release_gap_kph() == 8.0


def test_slc_speed_limit_max_decel_defaults_to_moderate_decel(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {}, 1_000_000_000)

  assert slc_config.get_slc_speed_limit_max_decel() == -0.5


def test_slc_speed_limit_max_decel_reads_configured_value(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {"speedLimitMaxDecelMps2": -0.7}, 1_000_000_000)

  assert slc_config.get_slc_speed_limit_max_decel() == -0.7


def test_slc_speed_limit_max_decel_clips_to_negative_range(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {"speedLimitMaxDecelMps2": 0.2}, 1_000_000_000)
  assert slc_config.get_slc_speed_limit_max_decel() == 0.0

  write_slc_config(config_path, {"speedLimitMaxDecelMps2": -3.0}, 2_000_000_000)
  assert slc_config.get_slc_speed_limit_max_decel() == -2.0


def test_longitudinal_no_lead_decel_mode_defaults_to_normal(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {}, 1_000_000_000)

  assert slc_config.get_longitudinal_no_lead_decel_mode() == "normal"


def test_longitudinal_no_lead_decel_mode_reads_idle(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {"longitudinalNoLeadDecelMode": "idle"}, 1_000_000_000)

  assert slc_config.get_longitudinal_no_lead_decel_mode() == "idle"


def test_longitudinal_no_lead_decel_mode_rejects_unknown_values(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {"longitudinalNoLeadDecelMode": "other"}, 1_000_000_000)

  assert slc_config.get_longitudinal_no_lead_decel_mode() == "normal"


def test_longitudinal_no_lead_decel_mode_accepts_legacy_accel_alias(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {"longitudinalNoLeadDecelMode": "accel"}, 1_000_000_000)

  assert slc_config.get_longitudinal_no_lead_decel_mode() == "normal"


def test_longitudinal_no_lead_idle_min_decel_defaults_to_moderate_request(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {}, 1_000_000_000)

  assert slc_config.get_longitudinal_no_lead_idle_min_decel() == -0.15


def test_longitudinal_no_lead_idle_min_decel_reads_configured_value(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {"longitudinalNoLeadIdleMinDecelMps2": -0.25}, 1_000_000_000)

  assert slc_config.get_longitudinal_no_lead_idle_min_decel() == -0.25


def test_longitudinal_no_lead_idle_min_decel_clips_to_negative_range(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {"longitudinalNoLeadIdleMinDecelMps2": 0.2}, 1_000_000_000)
  assert slc_config.get_longitudinal_no_lead_idle_min_decel() == 0.0

  write_slc_config(config_path, {"longitudinalNoLeadIdleMinDecelMps2": -2.0}, 2_000_000_000)
  assert slc_config.get_longitudinal_no_lead_idle_min_decel() == -1.2


def test_longitudinal_no_lead_idle_overspeed_margin_defaults_to_1_kph(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {}, 1_000_000_000)

  assert slc_config.get_longitudinal_no_lead_idle_overspeed_margin_kph() == 1.0


def test_longitudinal_no_lead_idle_overspeed_margin_reads_configured_value(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {"longitudinalNoLeadIdleOverspeedMarginKph": 1.5}, 1_000_000_000)

  assert slc_config.get_longitudinal_no_lead_idle_overspeed_margin_kph() == 1.5


def test_longitudinal_no_lead_idle_overspeed_margin_clips_to_range(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {"longitudinalNoLeadIdleOverspeedMarginKph": -1.0}, 1_000_000_000)
  assert slc_config.get_longitudinal_no_lead_idle_overspeed_margin_kph() == 0.0

  write_slc_config(config_path, {"longitudinalNoLeadIdleOverspeedMarginKph": 20.0}, 2_000_000_000)
  assert slc_config.get_longitudinal_no_lead_idle_overspeed_margin_kph() == 10.0


def test_longitudinal_no_lead_idle_decel_cooldown_defaults_to_2_seconds(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {}, 1_000_000_000)

  assert slc_config.get_longitudinal_no_lead_idle_decel_cooldown_s() == 2.0


def test_longitudinal_no_lead_idle_decel_cooldown_reads_configured_value(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {"longitudinalNoLeadIdleDecelCooldownS": 3.0}, 1_000_000_000)

  assert slc_config.get_longitudinal_no_lead_idle_decel_cooldown_s() == 3.0


def test_longitudinal_no_lead_idle_decel_cooldown_clips_to_range(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {"longitudinalNoLeadIdleDecelCooldownS": -1.0}, 1_000_000_000)
  assert slc_config.get_longitudinal_no_lead_idle_decel_cooldown_s() == 0.0

  write_slc_config(config_path, {"longitudinalNoLeadIdleDecelCooldownS": 20.0}, 2_000_000_000)
  assert slc_config.get_longitudinal_no_lead_idle_decel_cooldown_s() == 10.0


def test_explicit_slc_keys_take_precedence_over_legacy_keys(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {
    "speedLimitLowerLookaheadEnabled": True,
    "lookaheadLowerLimits": False,
    "speedLimitLookaheadFactorDown": 4.0,
    "lookaheadSpeedFactorDown": 2.0,
    "speedLimitLookaheadFactorUp": 1.0,
    "lookaheadSpeedFactorUp": 3.0,
    "speedLimitLowerDecelControlEnabled": True,
    "noBrakeForSpeedLimit": False,
    "speedLimitLowerDecelMode": "dynamic",
    "noBrakeMode": "fixed",
    "speedLimitLowerDecelFixedAccel": -0.08,
    "noBrakeAccel": -0.2,
    "speedLimitLowerDecelReleaseGapKph": 6.0,
    "noBrakeReleaseGapKph": 10.0,
    "speedLimitMaxDecelMps2": -0.6,
    "speedLimitMaxDecel": -1.0,
    "longitudinalNoLeadIdleOverspeedMarginKph": 1.5,
    "longitudinalNoLeadIdleDecelCooldownS": 3.0,
  }, 1_000_000_000)

  assert slc_config.get_slc_lookahead_lower_limits()
  assert slc_config.get_slc_lookahead_speed_factor_down() == 4.0
  assert slc_config.get_slc_lookahead_speed_factor_up() == 1.0
  assert slc_config.get_slc_no_brake()
  assert slc_config.get_slc_no_brake_mode() == "dynamic"
  assert slc_config.get_slc_no_brake_accel() == -0.08
  assert slc_config.get_slc_no_brake_release_gap_kph() == 6.0
  assert slc_config.get_slc_speed_limit_max_decel() == -0.6
  assert slc_config.get_longitudinal_no_lead_idle_overspeed_margin_kph() == 1.5
  assert slc_config.get_longitudinal_no_lead_idle_decel_cooldown_s() == 3.0


def test_legacy_no_brake_keys_remain_supported(tmp_path, monkeypatch):
  config_path = tmp_path / "slc.json"
  monkeypatch.setattr(slc_config, "SLC_CONFIG_PATH", config_path)
  reset_slc_config_cache()

  write_slc_config(config_path, {
    "lookaheadLowerLimits": True,
    "lookaheadSpeedFactorDown": 4.0,
    "lookaheadSpeedFactorUp": 1.0,
    "noBrakeForSpeedLimit": True,
    "noBrakeMode": "dynamic",
    "noBrakeAccel": -0.08,
    "noBrakeReleaseGapKph": 6.0,
    "speedLimitMaxDecel": -0.6,
  }, 1_000_000_000)

  assert slc_config.get_slc_lookahead_lower_limits()
  assert slc_config.get_slc_lookahead_speed_factor_down() == 4.0
  assert slc_config.get_slc_lookahead_speed_factor_up() == 1.0
  assert slc_config.get_slc_no_brake()
  assert slc_config.get_slc_no_brake_mode() == "dynamic"
  assert slc_config.get_slc_no_brake_accel() == -0.08
  assert slc_config.get_slc_no_brake_release_gap_kph() == 6.0
  assert slc_config.get_slc_speed_limit_max_decel() == -0.6
