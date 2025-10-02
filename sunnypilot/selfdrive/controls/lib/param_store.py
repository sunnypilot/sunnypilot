"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from cereal import custom
from opendbc.car import structs
from openpilot.common.params import Params

from sunnypilot.sunnylink.utils import get_param_as_byte


class ParamStore:
  keys: list[str]
  _params: dict[str, custom.CarControlSP.Param]

  def __init__(self, CP: structs.CarParams):
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
    self._params = {}

    self.frame = 0

  def update(self, params: Params) -> None:
    self.frame += 1
    if self.frame % 300 != 0:
      return

    for key in self.keys:
      param_type = params.get_type(key).name.lower()  # Using string instead of number because its "loose" dependency, and could change by OP at anytime.

      # Over engineering opportunity: It's possible this conversion is slow, we may check the value as params returns it for cache purposes. Not today.
      param_value = get_param_as_byte(key, params)
      if (existing_param := self._params.get(key)) is not None and existing_param.value == param_value:
        continue

      self._params[key] = custom.CarControlSP.Param(key=key, value=param_value, type=param_type)

  @property
  def param_list(self) -> list[custom.CarControlSP.Param]:
    return [v for k,v in self._params.items()]
