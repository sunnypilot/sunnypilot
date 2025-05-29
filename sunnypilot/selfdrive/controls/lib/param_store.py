"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import capnp

from cereal import custom

from opendbc.car import structs
from openpilot.common.params import Params


class ParamStore:
  keys: list[str]
  values: dict[str, str]

  def __init__(self, CP: structs.CarParams):
    universal_params: list[str] = []
    brand_params: list[str] = []

    self.keys = universal_params + brand_params
    self.values = {}

  def update(self, params: Params) -> None:
    self.values = {k: params.get(k, encoding='utf8') or "0" for k in self.keys}

  def publish(self) -> list[capnp.lib.capnp._DynamicStructBuilder]:
    params_list: list[capnp.lib.capnp._DynamicStructBuilder] = []

    for k in self.keys:
      params_list.append(custom.CarControlSP.Param(key=k, value=self.values[k]))

    return params_list
