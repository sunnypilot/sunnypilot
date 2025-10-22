"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import custom, car
from openpilot.common.constants import CV
from openpilot.common.params import Params
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.common import Mode as SpeedLimitMode


def compare_cluster_target(v_cruise_cluster: float, target_set_speed: float, is_metric: bool) -> tuple[bool, bool]:
  speed_conv = CV.MS_TO_KPH if is_metric else CV.MS_TO_MPH
  v_cruise_cluster_conv = round(v_cruise_cluster * speed_conv)
  target_set_speed_conv = round(target_set_speed * speed_conv)

  req_plus = v_cruise_cluster_conv < target_set_speed_conv
  req_minus = v_cruise_cluster_conv > target_set_speed_conv

  return req_plus, req_minus


def set_speed_limit_assist_availability(CP: car.CarParams, CP_SP: custom.CarParamsSP, params: Params = None) -> None:
  if params is None:
    params = Params()

  allowed = True

  if not CP.openpilotLongitudinalControl and CP_SP.pcmCruiseSpeed:
    allowed = False

  if not allowed:
    if params.get("SpeedLimitMode", return_default=True) == SpeedLimitMode.assist:
      params.put("SpeedLimitMode", int(SpeedLimitMode.warning))
