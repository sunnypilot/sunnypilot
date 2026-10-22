"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.cereal import log
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.controls.lib.accel_boost import AccelBoost, ACCEL_BOOST_MAX
from openpilot.sunnypilot import PARAMS_UPDATE_PERIOD

SCALE_RELAXED = 0.3
SCALE_STANDARD = 0.5
SCALE_AGGRESSIVE = 0.7


def get_accel_boost_scale(personality) -> float:
  if personality == log.LongitudinalPersonality.aggressive:
    return SCALE_AGGRESSIVE
  if personality == log.LongitudinalPersonality.relaxed:
    return SCALE_RELAXED
  return SCALE_STANDARD


def get_accel_boost_max(personality, extra_enabled: bool = True) -> float:
  if not extra_enabled:
    return ACCEL_BOOST_MAX
  return ACCEL_BOOST_MAX * (1.0 + get_accel_boost_scale(personality))


class AccelBoostExt:
  def __init__(self, stock: AccelBoost | None = None):
    self._stock = stock if stock is not None else AccelBoost()
    self._extra = AccelBoost()
    self.params = Params()
    self.frame = -1
    self.enabled = self.params.get_bool("FollowDistanceAccelBoost")

    self.stock_boost = 0.0
    self.extra_boost = 0.0

  @property
  def total_boost(self) -> float:
    return self._stock.total_boost + self.extra_boost

  def _update_params(self) -> None:
    if self.frame % int(PARAMS_UPDATE_PERIOD / DT_MDL) == 0:
      self.enabled = self.params.get_bool("FollowDistanceAccelBoost")

  def update(self, sm, output_a_target_e2e, output_a_target_mpc, a_cruise):
    self.frame += 1
    self._update_params()

    if self.enabled and sm['selfdriveState'].enabled:
      scale = get_accel_boost_scale(sm['selfdriveState'].personality)
      extra_output = self._extra.update(sm, output_a_target_e2e, output_a_target_mpc, a_cruise)
      self.extra_boost = (extra_output - output_a_target_e2e) * scale
    else:
      self.extra_boost = 0.0
      self._extra.total_boost = 0.0
      self._extra.boost_this_override = 0.0
      self._extra.boost_eligible = False

      output = self._stock.update(sm, output_a_target_e2e, output_a_target_mpc, a_cruise)
      self.stock_boost = output - output_a_target_e2e
      return output

    target = output_a_target_e2e + self.extra_boost
    output = self._stock.update(sm, target, output_a_target_mpc, a_cruise)
    self.stock_boost = output - target
    return output
