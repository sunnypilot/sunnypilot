"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
# DISCLAIMER: This code is intended principally for development and debugging purposes.
# Although it provides a standalone entry point to the program, users should refer
# to the actual implementations for consumption. Usage outside of development scenarios
# is not advised and could lead to unpredictable results.

import threading
import traceback

from cereal import messaging
from openpilot.common.gps import get_gps_location_service
from openpilot.common.params import Params
from openpilot.common.realtime import config_realtime_process
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller.common import Policy
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit_controller.speed_limit_resolver import SpeedLimitResolver
from openpilot.sunnypilot.mapd.live_map_data import get_debug


def excepthook(args):
  get_debug(f'MapD: Threading exception:\n{args}')
  traceback.print_exception(args.exc_type, args.exc_value, args.exc_traceback)


def live_map_data_sp_thread():
  config_realtime_process([0, 1, 2, 3], 5)

  params = Params()
  gps_location_service = get_gps_location_service(params)

  while True:
    live_map_data_sp_thread_debug(gps_location_service)


def live_map_data_sp_thread_debug(gps_location_service):
  _sub_master = messaging.SubMaster(['carState', 'livePose', 'liveMapDataSP', 'longitudinalPlanSP', 'carStateSP', gps_location_service])
  _sub_master.update()

  v_ego = _sub_master['carState'].vEgo
  _resolver = SpeedLimitResolver()
  _resolver.policy = Policy.car_state_priority
  _resolver.update(v_ego, _sub_master)
  print(_resolver.speed_limit, _resolver.distance, _resolver.source)


def main():
  threading.excepthook = excepthook
  live_map_data_sp_thread()


if __name__ == "__main__":
  main()
