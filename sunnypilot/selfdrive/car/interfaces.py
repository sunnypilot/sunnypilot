"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from opendbc.car import structs
from opendbc.car.interfaces import CarInterfaceBase
from opendbc.sunnypilot.car.hyundai.longitudinal.helpers import LongitudinalTuningType
from opendbc.sunnypilot.car.hyundai.values import HyundaiFlagsSP
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.sunnypilot.selfdrive.controls.lib.nnlc.helpers import get_nn_model_path

import openpilot.system.sentry as sentry


def log_fingerprint(CP: structs.CarParams) -> None:
  if CP.carFingerprint == "MOCK":
    sentry.capture_fingerprint_mock()
  else:
    sentry.capture_fingerprint(CP.carFingerprint, CP.brand)


def _initialize_custom_longitudinal_tuning(CI: CarInterfaceBase, CP: structs.CarParams, CP_SP: structs.CarParamsSP,
                                           params: Params = None) -> None:
  if params is None:
    params = Params()

  # Hyundai Custom Longitudinal Tuning
  if CP.brand == 'hyundai':
    hyundai_longitudinal_tuning = int(params.get("HyundaiLongitudinalTuning", encoding="utf8") or 0)
    if hyundai_longitudinal_tuning == LongitudinalTuningType.DYNAMIC:
      CP_SP.flags |= HyundaiFlagsSP.LONG_TUNING_DYNAMIC.value
    if hyundai_longitudinal_tuning == LongitudinalTuningType.PREDICTIVE:
      CP_SP.flags |= HyundaiFlagsSP.LONG_TUNING_PREDICTIVE.value

  CP_SP = CI.get_longitudinal_tuning_sp(CP, CP_SP)


def _initialize_neural_network_lateral_control(CI: CarInterfaceBase, CP: structs.CarParams, CP_SP: structs.CarParamsSP,
                                               params: Params = None, enabled: bool = False) -> None:
  if params is None:
    params = Params()

  nnlc_model_path, nnlc_model_name, exact_match = get_nn_model_path(CP)

  if nnlc_model_name == "MOCK":
    cloudlog.error({"nnlc event": "car doesn't match any Neural Network model"})

  if nnlc_model_name != "MOCK" and CP.steerControlType != structs.CarParams.SteerControlType.angle:
    enabled = params.get_bool("NeuralNetworkLateralControl")

  if enabled:
    CI.configure_torque_tune(CP.carFingerprint, CP.lateralTuning)

  CP_SP.neuralNetworkLateralControl.model.path = nnlc_model_path
  CP_SP.neuralNetworkLateralControl.model.name = nnlc_model_name
  CP_SP.neuralNetworkLateralControl.fuzzyFingerprint = not exact_match


def setup_interfaces(CI: CarInterfaceBase, params: Params = None) -> None:
  CP = CI.CP
  CP_SP = CI.CP_SP

  _initialize_custom_longitudinal_tuning(CI, CP, CP_SP, params)
  _initialize_neural_network_lateral_control(CI, CP, CP_SP, params)
