"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from typing import Any

from opendbc.car import structs
from opendbc.car.interfaces import CarInterfaceBase
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.sunnypilot.selfdrive.controls.lib.nnlc.helpers import get_nn_model_path
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.helpers import set_speed_limit_assist_availability

import openpilot.system.sentry as sentry

from sunnypilot.sunnylink.statsd import STATSLOGSP


def log_fingerprint(CP: structs.CarParams) -> None:
  if CP.carFingerprint == "MOCK":
    sentry.capture_fingerprint_mock()
  else:
    sentry.capture_fingerprint(CP.carFingerprint, CP.brand)


def _enforce_torque_lateral_control(CP: structs.CarParams, params: Params = None, enabled: bool = False) -> bool:
  if params is None:
    params = Params()

  if CP.steerControlType != structs.CarParams.SteerControlType.angle:
    enabled = params.get_bool("EnforceTorqueControl")

  return enabled


def _initialize_neural_network_lateral_control(CP: structs.CarParams, CP_SP: structs.CarParamsSP,
                                               params: Params = None, enabled: bool = False) -> bool:
  if params is None:
    params = Params()

  nnlc_model_path, nnlc_model_name, exact_match = get_nn_model_path(CP)

  if nnlc_model_name == "MOCK":
    cloudlog.error({"nnlc event": "car doesn't match any Neural Network model"})

  if nnlc_model_name != "MOCK" and CP.steerControlType != structs.CarParams.SteerControlType.angle:
    enabled = params.get_bool("NeuralNetworkLateralControl")

  CP_SP.neuralNetworkLateralControl.model.path = nnlc_model_path
  CP_SP.neuralNetworkLateralControl.model.name = nnlc_model_name
  CP_SP.neuralNetworkLateralControl.fuzzyFingerprint = not exact_match

  return enabled


def _initialize_intelligent_cruise_button_management(CP: structs.CarParams, CP_SP: structs.CarParamsSP, params: Params = None) -> None:
  if params is None:
    params = Params()

  icbm_enabled = params.get_bool("IntelligentCruiseButtonManagement")
  if icbm_enabled and CP_SP.intelligentCruiseButtonManagementAvailable and not CP.openpilotLongitudinalControl:
    CP_SP.pcmCruiseSpeed = False


def _initialize_torque_lateral_control(CI: CarInterfaceBase, CP: structs.CarParams, enforce_torque: bool, nnlc_enabled: bool) -> None:
  if nnlc_enabled or enforce_torque:
    CI.configure_torque_tune(CP.carFingerprint, CP.lateralTuning)


def _cleanup_unsupported_params(CP: structs.CarParams, CP_SP: structs.CarParamsSP, params: Params = None) -> None:
  if params is None:
    params = Params()

  if CP.steerControlType == structs.CarParams.SteerControlType.angle:
    cloudlog.warning("SteerControlType is angle, cleaning up params")
    params.remove("NeuralNetworkLateralControl")
    params.remove("EnforceTorqueControl")

  if not CP_SP.intelligentCruiseButtonManagementAvailable or CP.openpilotLongitudinalControl:
    cloudlog.warning("ICBM not available or openpilot Longitudinal Control enabled, cleaning up params")
    params.remove("IntelligentCruiseButtonManagement")

  if not CP.openpilotLongitudinalControl and CP_SP.pcmCruiseSpeed:
    cloudlog.warning("openpilot Longitudinal Control and ICBM not available, cleaning up params")
    params.remove("DynamicExperimentalControl")
    params.remove("CustomAccIncrementsEnabled")
    params.remove("SmartCruiseControlVision")
    params.remove("SmartCruiseControlMap")

  set_speed_limit_assist_availability(CP, CP_SP, params)


def setup_interfaces(CI: CarInterfaceBase, params: Params = None) -> None:
  CP = CI.CP
  CP_SP = CI.CP_SP

  enforce_torque = _enforce_torque_lateral_control(CP, params)
  nnlc_enabled = _initialize_neural_network_lateral_control(CP, CP_SP, params)
  _initialize_intelligent_cruise_button_management(CP, CP_SP, params)
  _initialize_torque_lateral_control(CI, CP, enforce_torque, nnlc_enabled)
  _cleanup_unsupported_params(CP, CP_SP)

  STATSLOGSP.raw('sunnypilot.car_params', CP.to_dict())
  # STATSLOGSP.raw('sunnypilot_params.car_params_sp', CP_SP.to_dict()) # https://github.com/sunnypilot/opendbc/pull/361


def initialize_params(params) -> list[dict[str, Any]]:
  keys: list = []

  # hyundai
  keys.extend([
    "HyundaiLongitudinalTuning"
  ])

  # subaru
  keys.extend([
    "SubaruStopAndGo",
    "SubaruStopAndGoManualParkingBrake",
  ])

  # tesla
  keys.extend([
    "TeslaCoopSteering",
  ])

  return [{k: params.get(k, return_default=True)} for k in keys]
