"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math

from opendbc.car import structs
from opendbc.car.ford.values import FordFlags
from opendbc.car.common.conversions import Conversions as CV
from openpilot.common.params import Params


def get_lat_delay(params: Params, stock_lat_delay: float) -> float:
# live learning on: use what lagd publishes.
# off: use the fixed steerActuatorDelay + software delay sum that LagdToggle caches.

  if params.get_bool("LagdToggle"):
    return stock_lat_delay

  return float(params.get("LagdValueCache", return_default=True))


def get_ford_delay_offset(CP: structs.CarParams, enabled: bool, v_ego: float) -> float:
  """Extra model preview for the opt-in C0/C1 controller; never alters learned delay."""
  if not enabled or CP.brand != 'ford' or not CP.flags & FordFlags.CANFD or not math.isfinite(v_ego):
    return 0.
  # Route 146 trial: full preview through 15 mph, fading to zero at 30 mph.
  return .4 * max(0., min(1., (30. - v_ego / CV.MPH_TO_MS) / 15.))
