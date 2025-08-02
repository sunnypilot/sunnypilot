"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from openpilot.common.params import Params
from opendbc.car import structs
from opendbc.safety import ALTERNATIVE_EXPERIENCE
from opendbc.sunnypilot.car.hyundai.values import HyundaiFlagsSP, HyundaiSafetyFlagsSP


class MadsSteeringModeOnBrake:
  REMAIN_ACTIVE = 0
  PAUSE = 1
  DISENGAGE = 2


def get_mads_limited_brands(CP: structs.CarParams) -> bool:
  return CP.brand in ("rivian", "tesla")


def read_steering_mode_param(CP: structs.CarParams, params: Params):
  if get_mads_limited_brands(CP):
    return MadsSteeringModeOnBrake.DISENGAGE

  try:
    return int(params.get("MadsSteeringMode"))
  except (ValueError, TypeError):
    return MadsSteeringModeOnBrake.REMAIN_ACTIVE


def set_alternative_experience(CP: structs.CarParams, params: Params):
  enabled = params.get_bool("Mads")
  steering_mode = read_steering_mode_param(CP, params)

  if enabled:
    CP.alternativeExperience |= ALTERNATIVE_EXPERIENCE.ENABLE_MADS

    if steering_mode == MadsSteeringModeOnBrake.DISENGAGE:
      CP.alternativeExperience |= ALTERNATIVE_EXPERIENCE.MADS_DISENGAGE_LATERAL_ON_BRAKE
    elif steering_mode == MadsSteeringModeOnBrake.PAUSE:
      CP.alternativeExperience |= ALTERNATIVE_EXPERIENCE.MADS_PAUSE_LATERAL_ON_BRAKE


def set_car_specific_params(CP: structs.CarParams, CP_SP: structs.CarParamsSP, params: Params):
  if CP.brand == "hyundai":
    # TODO-SP: This should be separated from MADS module for future implementations
    #          Use "HyundaiLongitudinalMainCruiseToggleable" param
    hyundai_cruise_main_toggleable = True
    if hyundai_cruise_main_toggleable:
      CP_SP.flags |= HyundaiFlagsSP.LONGITUDINAL_MAIN_CRUISE_TOGGLEABLE.value
      CP_SP.safetyParam |= HyundaiSafetyFlagsSP.LONG_MAIN_CRUISE_TOGGLEABLE

  # MADS Partial Support
  # MADS is currently partially supported for these platforms due to lack of consistent states to engage controls
  # Only MadsSteeringModeOnBrake.DISENGAGE is supported for these platforms
  # TODO-SP: To enable MADS full support for Rivian/Tesla, identify consistent signals for MADS toggling
  mads_partial_support = get_mads_limited_brands(CP)
  if mads_partial_support:
    params.put("MadsSteeringMode", "2")
    params.put_bool("MadsUnifiedEngagementMode", True)
    params.remove("MadsMainCruiseAllowed")
