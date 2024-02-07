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
import cereal.messaging as messaging

USE_LATERAL_PLANNER = True
MODEL_USE_LATERAL_PLANNER = False


def cumtrapz(x, t):
  return np.concatenate([[0], np.cumsum(((x[0:-1] + x[1:])/2) * np.diff(t))])

def publish_ui_plan(sm, pm, lateral_planner=None, longitudinal_planner=None):
  # TODO: SP - Reimplement lateral planner with legacy models
  if MODEL_USE_LATERAL_PLANNER:
    plan_odo = cumtrapz(longitudinal_planner.v_desired_trajectory_full, ModelConstants.T_IDXS)
    model_odo = cumtrapz(lateral_planner.v_plan, ModelConstants.T_IDXS)

  ui_send = messaging.new_message('uiPlan')
  ui_send.valid = sm.all_checks(service_list=['carState', 'controlsState', 'modelV2'])
  uiPlan = ui_send.uiPlan
  uiPlan.frameId = sm['modelV2'].frameId
  # TODO: SP - Reimplement lateral planner with legacy models
  if MODEL_USE_LATERAL_PLANNER:
    x_fp = (lateral_planner.x_sol if lateral_planner.dynamic_lane_profile_status else lateral_planner.lat_mpc.x_sol)[:,0]
    y_fp = (lateral_planner.x_sol if lateral_planner.dynamic_lane_profile_status else lateral_planner.lat_mpc.x_sol)[:,1]
  uiPlan.position.x = np.interp(plan_odo, model_odo, x_fp).tolist() if MODEL_USE_LATERAL_PLANNER else list(sm['modelV2'].position.x)
  uiPlan.position.y = np.interp(plan_odo, model_odo, y_fp).tolist() if MODEL_USE_LATERAL_PLANNER else list(sm['modelV2'].position.y)
  uiPlan.position.z = np.interp(plan_odo, model_odo, lateral_planner.path_xyz[:,2]).tolist() if MODEL_USE_LATERAL_PLANNER else list(sm['modelV2'].position.z)
  uiPlan.accel = longitudinal_planner.a_desired_trajectory_full.tolist()
  pm.send('uiPlan', ui_send)

def plannerd_thread():
  config_realtime_process(5, Priority.CTRL_LOW)

  cloudlog.info("plannerd is waiting for CarParams")
  params = Params()
  with car.CarParams.from_bytes(params.get("CarParams", block=True)) as msg:
    CP = msg
  cloudlog.info("plannerd got CarParams: %s", CP.carName)

  debug_mode = bool(int(os.getenv("DEBUG", "0")))

  use_lanelines = False

  cloudlog.event("e2e mode", on=use_lanelines)

  longitudinal_planner = LongitudinalPlanner(CP)
  # TODO: SP - Reimplement lateral planner with legacy models
  lateral_planner = LateralPlanner(CP, debug=debug_mode, use_lanelines=use_lanelines) if USE_LATERAL_PLANNER else None
  lateral_planner_svs = ['lateralPlanDEPRECATED', 'lateralPlanSPDEPRECATED'] if USE_LATERAL_PLANNER else []

  pm = messaging.PubMaster(['longitudinalPlan', 'uiPlan', 'longitudinalPlanSP'] + lateral_planner_svs)
  sm = messaging.SubMaster(['carControl', 'carState', 'controlsState', 'radarState', 'modelV2',
                            'longitudinalPlan', 'navInstruction', 'longitudinalPlanSP',
                            'liveMapDataSP', 'e2eLongStateSP'] + lateral_planner_svs,
                           poll=['radarState', 'modelV2'], ignore_avg_freq=['radarState'])

  while True:
    sm.update()

    if sm.updated['modelV2']:
      # TODO: SP - Reimplement lateral planner with legacy models
      if USE_LATERAL_PLANNER:
        lateral_planner.update(sm)
        lateral_planner.publish(sm, pm)
      longitudinal_planner.update(sm)
      longitudinal_planner.publish(sm, pm)
      publish_ui_plan(sm, pm, lateral_planner=lateral_planner, longitudinal_planner=longitudinal_planner)

def main():
  plannerd_thread()


if __name__ == "__main__":
  main()
