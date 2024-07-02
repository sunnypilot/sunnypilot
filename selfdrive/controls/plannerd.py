#!/usr/bin/env python3
import os
import numpy as np
from cereal import car
from openpilot.common.params import Params
from openpilot.common.realtime import Priority, config_realtime_process
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlanner
from openpilot.selfdrive.controls.lib.lateral_planner import LateralPlanner
from openpilot.selfdrive.modeld.model_capabilities import ModelCapabilities
from openpilot.selfdrive.sunnypilot import get_model_generation
import cereal.messaging as messaging


def plannerd_thread():
  config_realtime_process(5, Priority.CTRL_LOW)

  cloudlog.info("plannerd is waiting for CarParams")
  params = Params()
  with car.CarParams.from_bytes(params.get("CarParams", block=True)) as msg:
    CP = msg
  cloudlog.info("plannerd got CarParams: %s", CP.carName)

  debug_mode = bool(int(os.getenv("DEBUG", "0")))

  longitudinal_planner = LongitudinalPlanner(CP)

  custom_model, model_gen = get_model_generation(params)
  model_capabilities = ModelCapabilities.get_by_gen(model_gen)
  model_use_lateral_planner = custom_model and model_capabilities & ModelCapabilities.LateralPlannerSolution
  lateral_planner = LateralPlanner(CP, debug=debug_mode, model_use_lateral_planner=model_use_lateral_planner)
  lateral_planner_svs = ['lateralPlanDEPRECATED', 'lateralPlanSPDEPRECATED']

  pm = messaging.PubMaster(['longitudinalPlan', 'longitudinalPlanSP'] + lateral_planner_svs)
  sm = messaging.SubMaster(['carControl', 'carState', 'controlsState', 'radarState', 'modelV2',
                            'longitudinalPlan', 'navInstruction', 'longitudinalPlanSP',
                            'liveMapDataSP', 'e2eLongStateSP', 'controlsStateSP'] + lateral_planner_svs,
                           poll='modelV2', ignore_avg_freq=['radarState'])

  while True:
    sm.update()
    if sm.updated['modelV2']:
      lateral_planner.update(sm)
      lateral_planner.publish(sm, pm)
      longitudinal_planner.update(sm)
      longitudinal_planner.publish(sm, pm)


def main():
  plannerd_thread()


if __name__ == "__main__":
  main()
