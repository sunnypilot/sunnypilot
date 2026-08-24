"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json
import os
from pathlib import Path

SLC_CONFIG_PATH = Path(os.getenv("SUNNYPILOT_SLC_CONFIG", "/data/sunnypilot/slc.json"))

LOOKAHEAD_SPEED_FACTOR_MIN = 0.0
LOOKAHEAD_SPEED_FACTOR_MAX = 10.0
NO_BRAKE_ACCEL_MIN = -1.2
NO_BRAKE_ACCEL_MAX = 0.0
NO_BRAKE_ACCEL_DEFAULT = -0.05
NO_BRAKE_RELEASE_GAP_KPH_MIN = 0.0
NO_BRAKE_RELEASE_GAP_KPH_MAX = 30.0
NO_BRAKE_RELEASE_GAP_KPH_DEFAULT = 5.0
NO_BRAKE_MODE_DEFAULT = "fixed"
# "idle" is currently implemented as a Hyundai CAN-FD SCC output mode.
NO_BRAKE_MODES = ("fixed", "dynamic", "idle")
LONGITUDINAL_NO_LEAD_DECEL_MODE_DEFAULT = "normal"
# longitudinalNoLeadDecelMode values:
# - "normal": keep normal planner/controller accel requests, including negative decel.
# - "idle": for ordinary no-lead cruise decel, send the Hyundai CAN-FD SCC idle output instead.
LONGITUDINAL_NO_LEAD_DECEL_MODES = ("normal", "idle")
LONGITUDINAL_NO_LEAD_DECEL_MODE_ALIASES = {"accel": "normal"}
LONGITUDINAL_NO_LEAD_IDLE_MIN_DECEL_MIN = -1.2
LONGITUDINAL_NO_LEAD_IDLE_MIN_DECEL_MAX = 0.0
LONGITUDINAL_NO_LEAD_IDLE_MIN_DECEL_DEFAULT = -0.15
LONGITUDINAL_NO_LEAD_IDLE_OVERSPEED_MARGIN_KPH_MIN = 0.0
LONGITUDINAL_NO_LEAD_IDLE_OVERSPEED_MARGIN_KPH_MAX = 10.0
LONGITUDINAL_NO_LEAD_IDLE_OVERSPEED_MARGIN_KPH_DEFAULT = 1.0
LONGITUDINAL_NO_LEAD_IDLE_DECEL_COOLDOWN_S_MIN = 0.0
LONGITUDINAL_NO_LEAD_IDLE_DECEL_COOLDOWN_S_MAX = 10.0
LONGITUDINAL_NO_LEAD_IDLE_DECEL_COOLDOWN_S_DEFAULT = 2.0
SPEED_LIMIT_MAX_DECEL_MIN = -2.0
SPEED_LIMIT_MAX_DECEL_MAX = 0.0
SPEED_LIMIT_MAX_DECEL_DEFAULT = -0.5

_config_cache: dict | None = None
_config_cache_mtime_ns: int | None = None


def _config_value(config: dict, key: str, *fallback_keys: str):
  for candidate in (key, *fallback_keys):
    if candidate in config:
      return config[candidate]
  return None


def _read_config() -> dict:
  global _config_cache, _config_cache_mtime_ns

  try:
    config_mtime_ns = SLC_CONFIG_PATH.stat().st_mtime_ns
  except OSError:
    config_mtime_ns = None

  if _config_cache is not None and _config_cache_mtime_ns == config_mtime_ns:
    return _config_cache

  try:
    with SLC_CONFIG_PATH.open() as f:
      config = json.load(f)
  except (FileNotFoundError, json.JSONDecodeError, OSError):
    _config_cache = {}
    _config_cache_mtime_ns = config_mtime_ns
    return {}

  _config_cache = config if isinstance(config, dict) else {}
  _config_cache_mtime_ns = config_mtime_ns
  return _config_cache


def _clip_float(value, minimum: float, maximum: float, default: float) -> float:
  try:
    return max(minimum, min(maximum, float(value)))
  except (TypeError, ValueError):
    return default


def _get_slc_lookahead_speed_factor(key: str, *fallback_keys: str) -> float:
  config = _read_config()
  value = _config_value(config, key, *fallback_keys, "lookaheadSpeedFactor")
  return _clip_float(value, LOOKAHEAD_SPEED_FACTOR_MIN, LOOKAHEAD_SPEED_FACTOR_MAX, LOOKAHEAD_SPEED_FACTOR_MIN)


def get_slc_lookahead_speed_factor_up() -> float:
  return _get_slc_lookahead_speed_factor("speedLimitLookaheadFactorUp", "lookaheadSpeedFactorUp")


def get_slc_lookahead_speed_factor_down() -> float:
  return _get_slc_lookahead_speed_factor("speedLimitLookaheadFactorDown", "lookaheadSpeedFactorDown")


def get_slc_lookahead_lower_limits() -> bool:
  config = _read_config()
  return bool(_config_value(config, "speedLimitLowerLookaheadEnabled", "lookaheadLowerLimits"))


def get_slc_no_brake() -> bool:
  config = _read_config()
  return bool(_config_value(config, "speedLimitLowerDecelControlEnabled", "noBrakeForSpeedLimit"))


def get_slc_no_brake_mode() -> str:
  config = _read_config()
  mode = _config_value(config, "speedLimitLowerDecelMode", "noBrakeMode")
  return mode if mode in NO_BRAKE_MODES else NO_BRAKE_MODE_DEFAULT


def get_slc_no_brake_accel() -> float:
  config = _read_config()
  value = _config_value(config, "speedLimitLowerDecelFixedAccel", "noBrakeAccel")
  return _clip_float(value, NO_BRAKE_ACCEL_MIN, NO_BRAKE_ACCEL_MAX, NO_BRAKE_ACCEL_DEFAULT)


def get_slc_no_brake_release_gap_kph() -> float:
  config = _read_config()
  value = _config_value(config, "speedLimitLowerDecelReleaseGapKph", "noBrakeReleaseGapKph")
  return _clip_float(value, NO_BRAKE_RELEASE_GAP_KPH_MIN,
                     NO_BRAKE_RELEASE_GAP_KPH_MAX, NO_BRAKE_RELEASE_GAP_KPH_DEFAULT)


def get_longitudinal_no_lead_decel_mode() -> str:
  mode = _read_config().get("longitudinalNoLeadDecelMode", LONGITUDINAL_NO_LEAD_DECEL_MODE_DEFAULT)
  mode = LONGITUDINAL_NO_LEAD_DECEL_MODE_ALIASES.get(mode, mode)
  return mode if mode in LONGITUDINAL_NO_LEAD_DECEL_MODES else LONGITUDINAL_NO_LEAD_DECEL_MODE_DEFAULT


def get_longitudinal_no_lead_idle_min_decel() -> float:
  value = _read_config().get("longitudinalNoLeadIdleMinDecelMps2")
  return _clip_float(value, LONGITUDINAL_NO_LEAD_IDLE_MIN_DECEL_MIN,
                     LONGITUDINAL_NO_LEAD_IDLE_MIN_DECEL_MAX, LONGITUDINAL_NO_LEAD_IDLE_MIN_DECEL_DEFAULT)


def get_longitudinal_no_lead_idle_overspeed_margin_kph() -> float:
  value = _read_config().get("longitudinalNoLeadIdleOverspeedMarginKph")
  return _clip_float(value, LONGITUDINAL_NO_LEAD_IDLE_OVERSPEED_MARGIN_KPH_MIN,
                     LONGITUDINAL_NO_LEAD_IDLE_OVERSPEED_MARGIN_KPH_MAX,
                     LONGITUDINAL_NO_LEAD_IDLE_OVERSPEED_MARGIN_KPH_DEFAULT)


def get_longitudinal_no_lead_idle_decel_cooldown_s() -> float:
  value = _read_config().get("longitudinalNoLeadIdleDecelCooldownS")
  return _clip_float(value, LONGITUDINAL_NO_LEAD_IDLE_DECEL_COOLDOWN_S_MIN,
                     LONGITUDINAL_NO_LEAD_IDLE_DECEL_COOLDOWN_S_MAX,
                     LONGITUDINAL_NO_LEAD_IDLE_DECEL_COOLDOWN_S_DEFAULT)


def get_slc_speed_limit_max_decel() -> float:
  config = _read_config()
  value = _config_value(config, "speedLimitMaxDecelMps2", "speedLimitMaxDecel")
  return _clip_float(value, SPEED_LIMIT_MAX_DECEL_MIN,
                     SPEED_LIMIT_MAX_DECEL_MAX, SPEED_LIMIT_MAX_DECEL_DEFAULT)
