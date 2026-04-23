"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json

from cereal import car, custom, messaging
from opendbc.car.hyundai.values import CAR as HYUNDAI_CAR, UNSUPPORTED_LONGITUDINAL_CAR
from opendbc.car.subaru.values import CAR as SUBARU_CAR, SubaruFlags
from opendbc.sunnypilot.car.tesla.values import TeslaFlagsSP
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.system.hardware import HARDWARE


# Wire-protocol version for the capabilities payload. Bump on breaking changes
# only; additive fields are backward-compatible and do not require a bump.
PROTOCOL_VERSION = 1

# All capability fields that rules may reference.
# Non-boolean fields must have defaults in CAPABILITY_DEFAULTS.
CAPABILITY_FIELDS = (
  "protocol_version",
  "has_longitudinal_control",
  "has_icbm",
  "icbm_available",
  "torque_allowed",
  "brand",
  "pcm_cruise",
  "alpha_long_available",
  "steer_control_type",
  "enable_bsm",
  "is_release",
  "is_sp_release",
  "is_development",
  "tesla_has_vehicle_bus",
  "has_stop_and_go",
  "stock_longitudinal",
  "device_type",
  "subaru_has_sng",
  "hyundai_alpha_long_available",
)

CAPABILITY_LABELS: dict[str, str] = {
  "protocol_version": "Capabilities protocol version",
  "has_longitudinal_control": "sunnypilot longitudinal control",
  "has_icbm": "ICBM enabled",
  "icbm_available": "ICBM available",
  "torque_allowed": "torque steering (not available for angle steering vehicles)",
  "brand": "Vehicle brand",
  "pcm_cruise": "PCM cruise",
  "alpha_long_available": "Alpha Longitudinal available",
  "steer_control_type": "Steer control type",
  "enable_bsm": "BSM available",
  "is_release": "Release branch",
  "is_sp_release": "SP release branch",
  "is_development": "Development branch",
  "tesla_has_vehicle_bus": "Tesla vehicle bus",
  "has_stop_and_go": "Stop and Go",
  "stock_longitudinal": "stock longitudinal",
  "device_type": "Device type",
  "subaru_has_sng": "Subaru Stop-and-Go available",
  "hyundai_alpha_long_available": "Hyundai Alpha Longitudinal available",
}

# Explicit defaults for non-boolean capability fields
CAPABILITY_DEFAULTS: dict[str, bool | str | int] = {
  "brand": "",
  "steer_control_type": "",
  "device_type": "",
  "protocol_version": PROTOCOL_VERSION,
}


def _bundle_field(bundle: dict | None, key: str) -> str:
  return bundle.get(key, "") if isinstance(bundle, dict) else ""


def generate_capabilities(params: Params | None = None) -> dict:
  """Generate a SettingsCapabilities dict from CarParams + boolean params.

  Bundle-first source of truth: when CarPlatformBundle is present, brand and
  platform derive from the bundle (mirrors Raylib settings code paths). The
  CarParams* deserialization is the fallback when the bundle has not yet been
  written (very early after first pairing).
  """
  params = params or Params()

  caps: dict = {field: CAPABILITY_DEFAULTS.get(field, False) for field in CAPABILITY_FIELDS}

  # Wire-protocol version is always set explicitly.
  caps["protocol_version"] = PROTOCOL_VERSION

  # Hardware + boolean params (no CarParams dependency)
  caps["device_type"] = HARDWARE.get_device_type()
  caps["is_release"] = params.get_bool("IsReleaseBranch")
  caps["is_sp_release"] = params.get_bool("IsReleaseSpBranch")
  caps["is_development"] = params.get_bool("IsDevelopmentBranch")
  caps["stock_longitudinal"] = params.get_bool("ToyotaEnforceStockLongitudinal")

  bundle = params.get("CarPlatformBundle")
  bundle_brand = _bundle_field(bundle, "brand")
  bundle_platform = _bundle_field(bundle, "platform")

  # Bundle-first brand resolution; CP is fallback only.
  if bundle_brand:
    caps["brand"] = bundle_brand

  # CarParams-derived capabilities
  CP_bytes = params.get("CarParamsPersistent")
  if CP_bytes is not None:
    try:
      CP = messaging.log_from_bytes(CP_bytes, car.CarParams)
      caps["alpha_long_available"] = bool(CP.alphaLongitudinalAvailable)
      if CP.alphaLongitudinalAvailable:
        caps["has_longitudinal_control"] = params.get_bool("AlphaLongitudinalEnabled")
      else:
        caps["has_longitudinal_control"] = bool(CP.openpilotLongitudinalControl)
      # CP.steerControlType is the physical control mode (angle / torque).
      # CP.lateralTuning.which() returns the tuning class (pid / torque / indi)
      # which is a separate concept and is not interchangeable.
      caps["steer_control_type"] = str(CP.steerControlType)
      caps["torque_allowed"] = CP.steerControlType != car.CarParams.SteerControlType.angle
      if not caps["brand"] and CP.brand:
        caps["brand"] = str(CP.brand)
      caps["pcm_cruise"] = bool(CP.pcmCruise)
      caps["enable_bsm"] = bool(CP.enableBsm)
      # Generic SnG fallback. Brand-specific opaque flags below override.
      caps["has_stop_and_go"] = bool(CP.openpilotLongitudinalControl)
    except Exception:
      cloudlog.exception("capabilities: failed to deserialize CarParamsPersistent")

  # CarParamsSP-derived capabilities
  CP_SP_bytes = params.get("CarParamsSPPersistent")
  if CP_SP_bytes is not None:
    try:
      CP_SP = messaging.log_from_bytes(CP_SP_bytes, custom.CarParamsSP)
      caps["icbm_available"] = bool(CP_SP.intelligentCruiseButtonManagementAvailable)
      caps["has_icbm"] = bool(CP_SP.intelligentCruiseButtonManagementAvailable) and params.get_bool("IntelligentCruiseButtonManagement")
      caps["tesla_has_vehicle_bus"] = bool(CP_SP.flags & TeslaFlagsSP.HAS_VEHICLE_BUS)
    except Exception:
      cloudlog.exception("capabilities: failed to deserialize CarParamsSPPersistent")

  # Brand-specific opaque flags. Mirror Raylib brand-settings logic so the
  # device and the dashboard agree on per-platform availability without
  # leaking the platform identifier over the wire.
  if caps["brand"] == "subaru" and bundle_platform:
    try:
      flags = SUBARU_CAR[bundle_platform].config.flags
      caps["subaru_has_sng"] = not bool(flags & (SubaruFlags.GLOBAL_GEN2 | SubaruFlags.HYBRID))
      caps["has_stop_and_go"] = caps["subaru_has_sng"]
    except KeyError:
      cloudlog.exception(f"capabilities: unknown subaru platform {bundle_platform!r}")

  if caps["brand"] == "hyundai" and bundle_platform:
    try:
      unsupported = set().union(*UNSUPPORTED_LONGITUDINAL_CAR.values())
      caps["hyundai_alpha_long_available"] = HYUNDAI_CAR[bundle_platform] not in unsupported
    except KeyError:
      cloudlog.exception(f"capabilities: unknown hyundai platform {bundle_platform!r}")

  return caps


def generate_capabilities_json(params: Params | None = None) -> str:
  """Generate SettingsCapabilities as a JSON string."""
  return json.dumps(generate_capabilities(params), separators=(",", ":"))
