# DISCLAIMER: This code is intended principally for development and debugging purposes.
# Although it provides a standalone entry point to the program, users should refer
# to the actual implementations for consumption. Usage outside of development scenarios
# is not advised and could lead to unpredictable results.

import threading
import traceback

from cereal import messaging
from openpilot.common.realtime import set_core_affinity
from openpilot.selfdrive.controls.lib.sunnypilot.common import Policy
from openpilot.selfdrive.controls.lib.sunnypilot.speed_limit_resolver import SpeedLimitResolver
from openpilot.selfdrive.sunnypilot.live_map_data import get_debug
from openpilot.common.swaglog import cloudlog


def excepthook(args):
  get_debug(f'MapD: Threading exception:\n{args}')
  traceback.print_exception(args.exc_type, args.exc_value, args.exc_traceback)


def live_map_data_sp_thread():
  try:
    set_core_affinity([0, 1, 2, 3])
  except Exception:
    cloudlog.exception("mapd: failed to set core affinity")

  while True:
    live_map_data_sp_thread_debug()


def live_map_data_sp_thread_debug():
  _sub_master = messaging.SubMaster(['carState', 'navInstruction', 'liveLocationKalman', 'liveMapDataSP', 'longitudinalPlanSP'])
  _sub_master.update()

  v_ego = _sub_master['carState'].vEgo
  long_spl = _sub_master['longitudinalPlanSP'].speedLimit
  _policy = Policy.car_state_priority
  _resolver = SpeedLimitResolver(_policy)
  _speed_limit, _distance, _source = _resolver.resolve(v_ego, long_spl, _sub_master)
  print(_speed_limit, _distance, _source, " <-> ", long_spl)


def main():
  threading.excepthook = excepthook
  live_map_data_sp_thread()


if __name__ == "__main__":
  main()
