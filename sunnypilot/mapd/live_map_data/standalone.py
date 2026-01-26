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

from openpilot.common.realtime import Ratekeeper, config_realtime_process
from openpilot.sunnypilot.mapd.live_map_data import get_debug
from openpilot.sunnypilot.mapd.live_map_data.osm_map_data import OsmMapData


def excepthook(args):
  get_debug(f'MapD: Threading exception:\n{args}')
  traceback.print_exception(args.exc_type, args.exc_value, args.exc_traceback)


def live_map_data_sp_thread():
  config_realtime_process([0, 1, 2, 3], 5)

  live_map_sp = OsmMapData()
  rk = Ratekeeper(1, print_delay_threshold=None)

  while True:
    live_map_sp.tick()
    rk.keep_time()


def main():
  threading.excepthook = excepthook
  live_map_data_sp_thread()


if __name__ == "__main__":
  main()
