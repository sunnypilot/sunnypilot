"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import capnp

from cereal import custom

from opendbc.car import structs
from openpilot.common.params import Params
from openpilot.common.realtime import DT_CTRL


class ParamStore:
  keys: list[str]
  values: dict[str, str]

  def __init__(self, CP: structs.CarParams):
    self.frame: int = 0
    self.update_frames: int = int(2 / DT_CTRL)
    universal_params: list[str] = []
    brand_params: list[str] = []

    if CP.brand == "hyundai":
      brand_params.extend([
        "HyundaiLongitudinalTuning",
        "LongTuningCustomToggle",
        "LongTuningAccelMin",
        "LongTuningAccelMax",
        "LongTuningVEgoStopping",
        "LongTuningStoppingDecelRate",
        "LongTuningMinUpperJerk",
        "LongTuningMinLowerJerk",
        "LongTuningJerkLimits",
      ])

    self.keys = universal_params + brand_params
    self.values = {}
    self.cached_params_list: list[capnp.lib.capnp._DynamicStructBuilder] | None = None

    self.frame = 0

  def update(self, params: Params) -> None:
    if self.frame % 300 == 0:
      old_values = dict(self.values)
      self.values = {k: params.get(k) or "0" for k in self.keys}
      if old_values != self.values:
        self.cached_params_list = None

    self.frame += 1

  def publish(self) -> list[capnp.lib.capnp._DynamicStructBuilder]:
    if self.cached_params_list is None:
      # TODO-SP: Why are we doing a list instead of a dictionary here?
      self.cached_params_list = [custom.CarControlSP.Param(key=k, value=str(self.values.get(k, "0"))) for k in self.keys]
    return self.cached_params_list
