#!/usr/bin/env python3
import time

from cereal import car, log, messaging
from common.params import Params
from selfdrive.manager.process_config import managed_processes

if __name__ == "__main__":
  CP = car.CarParams(notCar=True)
  Params().put("CarParams", CP.to_bytes())

  procs = ['camerad', 'ui', 'modeld', 'calibrationd']
  for p in procs:
    managed_processes[p].start()

  pm = messaging.PubMaster(['controlsState', 'deviceState', 'pandaStates', 'carParams', 'lateralPlan', 'carState'])

  msgs = {s: messaging.new_message(s) for s in ['controlsState', 'deviceState', 'carParams', 'carState']}
  msgs['deviceState'].deviceState.started = True
  msgs['carParams'].carParams.openpilotLongitudinalControl = True

  msgs['pandaStates'] = messaging.new_message('pandaStates', 1)
  msgs['pandaStates'].pandaStates[0].ignitionLine = True
  msgs['pandaStates'].pandaStates[0].pandaType = log.PandaState.PandaType.uno

  v_ego = 0
  try:
    while True:
      time.sleep(1 / 100)  # continually send, rate doesn't matter

      msgs['carState'].carState.vEgoCluster = v_ego
      v_ego += 0.02
      if v_ego > 40:
        v_ego = 0

      for s in msgs:
        pm.send(s, msgs[s])
  except KeyboardInterrupt:
    for p in procs:
      managed_processes[p].stop()
