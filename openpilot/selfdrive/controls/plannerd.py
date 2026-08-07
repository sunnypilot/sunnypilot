#!/usr/bin/env python3
from openpilot.cereal import custom
from opendbc.car.structs import car
from openpilot.common.gps import get_gps_location_service
from openpilot.common.params import Params
from openpilot.common.realtime import Priority, config_realtime_process
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.controls.lib.ldw import LaneDepartureWarning
from openpilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlanner
import openpilot.cereal.messaging as messaging


def main():
  config_realtime_process(5, Priority.CTRL_LOW)

  cloudlog.info("plannerd is waiting for CarParams")
  params = Params()
  CP = messaging.log_from_bytes(params.get("CarParams", block=True), car.CarParams)
  cloudlog.info("plannerd got CarParams: %s", CP.brand)

  cloudlog.info("plannerd is waiting for CarParamsSP")
  CP_SP = messaging.log_from_bytes(params.get("CarParamsSP", block=True), custom.CarParamsSP)
  cloudlog.info("plannerd got CarParamsSP")

  gps_location_service = get_gps_location_service(params)
  ignore_services = ["liveMapDataSP", gps_location_service]

  ldw = LaneDepartureWarning()
  longitudinal_planner = LongitudinalPlanner(CP, CP_SP)
  pm = messaging.PubMaster(['longitudinalPlan', 'driverAssistance', 'longitudinalPlanSP'])
  sm = messaging.SubMaster(
    [
      'carControl',
      'carState',
      'controlsState',
      'liveParameters',
      'radarState',
      'modelV2',
      'selfdriveState',
      'liveMapDataSP',
      'carStateSP',
      gps_location_service,
    ],
    poll='carState',
    ignore_alive=ignore_services,
    ignore_avg_freq=ignore_services,
    ignore_valid=ignore_services,
  )

  output_dependencies = {
    'longitudinalPlan': ('carState', 'controlsState', 'selfdriveState', 'radarState'),
    'driverAssistance': ('carState', 'carControl', 'modelV2', 'liveParameters'),
    'longitudinalPlanSP': ('carState', 'controlsState'),
  }
  last_comm_diagnostics = None

  while True:
    sm.update()
    longitudinal_planner.sla.update_car_state(sm['carState'])
    if sm.updated['modelV2']:
      failed_outputs = {
        output: {
          service: {
            'valid': sm.valid[service],
            'alive': sm.alive[service],
            'freqOk': sm.freq_ok[service],
            'frameAge': sm.frame - sm.recv_frame[service],
          }
          for service in dependencies
          if not (sm.valid[service] and sm.alive[service] and sm.freq_ok[service])
        }
        for output, dependencies in output_dependencies.items()
        if not sm.all_checks(list(dependencies))
      }
      comm_diagnostics = tuple(
        (output, tuple((service, values['valid'], values['alive'], values['freqOk'], values['frameAge']) for service, values in services.items()))
        for output, services in failed_outputs.items()
      )

      if comm_diagnostics != last_comm_diagnostics:
        if failed_outputs:
          published_valid = {
            output: sm.all_valid(list(output_dependencies[output]))
            for output in failed_outputs
          }
          cloudlog.event('plannerdCommDiagnostics', error=True, failedOutputs=failed_outputs,
                         publishedValid=published_valid, frame=sm.frame)
        elif last_comm_diagnostics:
          cloudlog.event('plannerdCommDiagnosticsRecovered', frame=sm.frame)
        last_comm_diagnostics = comm_diagnostics

      longitudinal_planner.update(sm)
      longitudinal_planner.publish(sm, pm)

      ldw.update(sm.frame, sm['modelV2'], sm['carState'], sm['carControl'])
      msg = messaging.new_message('driverAssistance')
      # Only propagate payload validity here. Transport health remains available through
      # plannerdCommDiagnostics, without cascading a transient local frequency check into
      # a commIssue on all plannerd outputs.
      msg.valid = sm.all_valid(['carState', 'carControl', 'modelV2', 'liveParameters'])
      msg.driverAssistance.leftLaneDeparture = ldw.left
      msg.driverAssistance.rightLaneDeparture = ldw.right
      pm.send('driverAssistance', msg)


if __name__ == "__main__":
  main()
