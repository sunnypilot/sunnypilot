"""
Copyright (c) 2021-, rav4kumar, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from dataclasses import dataclass
from typing import Literal

import numpy as np

from openpilot.cereal import messaging
from opendbc.car import structs
from openpilot.common.params import Params
from openpilot.selfdrive.modeld.constants import ModelConstants

ModeType = Literal['acc', 'blended']

_DECEL_LOOKAHEAD_MIN_T = 1.0
_DECEL_LOOKAHEAD_MAX_T = 6.0
_T_IDXS = np.array(ModelConstants.T_IDXS)
_DECEL_IDX = np.where((_T_IDXS >= _DECEL_LOOKAHEAD_MIN_T) & (_T_IDXS <= _DECEL_LOOKAHEAD_MAX_T))[0]
_DECEL_INV_T = 1.0 / _T_IDXS[_DECEL_IDX]

DECEL_INTENT_A_HINT = 0.35
DECEL_INTENT_A_FULL = 1.30
DECEL_INTENT_TRIGGER = 0.5
DECEL_INTENT_CURVE_OVERRIDE = 0.9

CURVE_Y_MAX = 5.0

LEAD_FUTURE_PROB_VANISH = 0.35

MODEL_DROP_TRUST_FULL = 5.0
MODEL_DROP_TRUST_NONE = 30.0
MODEL_TRUST_MIN = 0.5

CREEP_SPEED_ENTER = 2.0
CREEP_SPEED_EXIT = 3.0

ENTER_FRAMES = 3
EXIT_FRAMES = 16
MIN_BLENDED_FRAMES = 20

PARAM_READ_FRAMES = 5


@dataclass
class DecSignals:
  decel_intent: float = 0.0
  curve_detected: bool = False
  model_trust: float = 1.0
  creeping: bool = False


def should_blend(s: DecSignals) -> bool:
  degraded = s.model_trust < MODEL_TRUST_MIN
  curve_gate = s.decel_intent >= DECEL_INTENT_CURVE_OVERRIDE or not s.curve_detected
  slowdown_detected = not degraded and s.decel_intent >= DECEL_INTENT_TRIGGER and curve_gate
  return slowdown_detected or s.creeping


class ModeHysteresis:
  def __init__(self):
    self.mode: ModeType = 'acc'
    self.above = 0
    self.below = 0
    self.blended_frames = 0

  def update(self, want_blended: bool, override: bool, veto: bool) -> ModeType:
    self.above = self.above + 1 if want_blended else 0
    self.below = 0 if want_blended else self.below + 1

    if override:
      self.mode, self.blended_frames = 'blended', 0
    elif veto:
      self.mode = 'acc'
    elif self.mode == 'acc':
      if self.above >= ENTER_FRAMES:
        self.mode, self.blended_frames = 'blended', 0
    else:
      self.blended_frames += 1
      if self.blended_frames >= MIN_BLENDED_FRAMES and self.below >= EXIT_FRAMES:
        self.mode = 'acc'
    return self.mode

  def reset(self) -> None:
    self.mode = 'acc'
    self.above = 0
    self.below = 0
    self.blended_frames = 0


class DynamicExperimentalController:
  def __init__(self, CP: structs.CarParams, mpc, params=None):
    self._mpc = mpc
    self._params = params or Params()
    self._enabled: bool = self._params.get_bool("DynamicExperimentalControl")
    self._active: bool = False
    self._frame: int = 0

    self._hysteresis = ModeHysteresis()
    self._creeping = False

    self.signals = DecSignals()
    self.want_blended = False
    self.lead_veto = False

  def _update_creeping(self, v_ego: float) -> bool:
    self._creeping = v_ego < CREEP_SPEED_EXIT if self._creeping else v_ego <= CREEP_SPEED_ENTER
    return self._creeping

  def _read_params(self) -> None:
    if self._frame % PARAM_READ_FRAMES == 0:
      self._enabled = self._params.get_bool("DynamicExperimentalControl")

  def mode(self) -> str:
    return self._hysteresis.mode

  def enabled(self) -> bool:
    return self._enabled

  def active(self) -> bool:
    return self._active

  @staticmethod
  def _decel_intent(md) -> float:
    v = np.asarray(md.velocity.x)
    if len(v) != len(_T_IDXS):
      return 0.0
    a_req = float(np.min((v[_DECEL_IDX] - v[0]) * _DECEL_INV_T))
    return float(np.interp(-a_req, [DECEL_INTENT_A_HINT, DECEL_INTENT_A_FULL], [0.0, 1.0]))

  @staticmethod
  def _curve_detected(md) -> bool:
    y = md.position.y
    if len(y) < 1:
      return False
    return abs(y[-1]) >= CURVE_Y_MAX

  @staticmethod
  def _model_trust(md) -> float:
    if len(md.velocity.x) != len(_T_IDXS):
      return 0.0
    return float(np.interp(md.frameDropPerc, [MODEL_DROP_TRUST_FULL, MODEL_DROP_TRUST_NONE], [1.0, 0.0]))

  @staticmethod
  def _lead_veto(radar_state, md) -> bool:
    lead_one, lead_two = radar_state.leadOne, radar_state.leadTwo
    lead_now = lead_one.present or lead_two.present
    probs = md.leadsV3
    future = min(probs[1].prob, probs[2].prob) if len(probs) >= 3 else 1.0
    return bool(lead_now and future > LEAD_FUTURE_PROB_VANISH)

  def update(self, sm: messaging.SubMaster) -> None:
    self._read_params()

    car_state = sm['carState']
    md = sm['modelV2']
    radar_state = sm['radarState']

    is_creeping = self._update_creeping(car_state.vEgo)
    self.lead_veto = self._lead_veto(radar_state, md)

    self.signals = DecSignals(
      decel_intent=self._decel_intent(md),
      curve_detected=self._curve_detected(md),
      model_trust=self._model_trust(md),
      creeping=is_creeping,
    )
    self.want_blended = should_blend(self.signals)

    crash_override = self._mpc.crash_cnt >= 1
    hard_brake_override = bool(md.meta.hardBrakePredicted)
    override = (crash_override or hard_brake_override) and not self.lead_veto

    if self._enabled:
      self._hysteresis.update(self.want_blended, override, self.lead_veto)
    else:
      self._hysteresis.reset()

    self._active = sm['selfdriveState'].experimentalMode and self._enabled
    self._frame += 1
