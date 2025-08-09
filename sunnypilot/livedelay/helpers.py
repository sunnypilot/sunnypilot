"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.common.params import Params


def get_lat_delay(params: Params, cur_val: float, updated: bool) -> float:
  if updated and params.get_bool("LagdToggle"):
    return params.get("LagdValueCache")

  return cur_val
