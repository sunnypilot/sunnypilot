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

_config_cache: dict | None = None


def _read_config() -> dict:
  global _config_cache

  if _config_cache is not None:
    return _config_cache

  try:
    with SLC_CONFIG_PATH.open() as f:
      config = json.load(f)
  except (FileNotFoundError, json.JSONDecodeError, OSError):
    _config_cache = {}
    return {}

  _config_cache = config if isinstance(config, dict) else {}
  return _config_cache


def _clip_float(value, minimum: float, maximum: float, default: float) -> float:
  try:
    return max(minimum, min(maximum, float(value)))
  except (TypeError, ValueError):
    return default


def _get_slc_lookahead_speed_factor(key: str, fallback_key: str = "lookaheadSpeedFactor") -> float:
  config = _read_config()
  value = config.get(key, config.get(fallback_key))
  return _clip_float(value, LOOKAHEAD_SPEED_FACTOR_MIN, LOOKAHEAD_SPEED_FACTOR_MAX, LOOKAHEAD_SPEED_FACTOR_MIN)


def get_slc_lookahead_speed_factor_up() -> float:
  return _get_slc_lookahead_speed_factor("lookaheadSpeedFactorUp")


def get_slc_lookahead_speed_factor_down() -> float:
  return _get_slc_lookahead_speed_factor("lookaheadSpeedFactorDown")


def get_slc_lookahead_lower_limits() -> bool:
  return bool(_read_config().get("lookaheadLowerLimits", False))
