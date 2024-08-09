# DISCLAIMER: This code is intended principally for development and debugging purposes.
# Although it provides a standalone entry point to the program, users should refer
# to the actual implementations for consumption. Usage outside of development scenarios
# is not advised and could lead to unpredictable results.

import threading
import traceback

from openpilot.common.realtime import Ratekeeper, set_core_affinity
from openpilot.selfdrive.sunnypilot.live_map_data import get_debug
from openpilot.selfdrive.sunnypilot.live_map_data.osm_map_data import OsmMapData
from openpilot.common.swaglog import cloudlog


def excepthook(args):
  get_debug(f'MapD: Threading exception:\n{args}')
  traceback.print_exception(args.exc_type, args.exc_value, args.exc_traceback)


def live_map_data_sp_thread():
  try:
    set_core_affinity([0, 1, 2, 3])
  except Exception:
    cloudlog.exception("mapd: failed to set core affinity")

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
