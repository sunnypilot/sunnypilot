#!/usr/bin/env python3
#TODO: Add this to files_common to allow release to public

import time
from multiprocessing import Process

from openpilot.common.params import Params
from openpilot.selfdrive.manager.process import launcher
from openpilot.common.swaglog import cloudlog
from openpilot.system.hardware import HARDWARE
from openpilot.system.version import get_version, get_normalized_origin, get_short_branch, get_commit, is_dirty

SUNNYLINK_MGR_PID_PARAM = "SunnylinkdPid"


def main():
  params = Params()
  dongle_id = params.get("SunnylinkDongleId").decode('utf-8')
  cloudlog.bind_global(dongle_id=dongle_id,
                       version=get_version(),
                       origin=get_normalized_origin(),
                       branch=get_short_branch(),
                       commit=get_commit(),
                       dirty=is_dirty(),
                       device=HARDWARE.get_device_type())

  try:
    while 1:
      cloudlog.info("starting athena daemon")
      proc = Process(name='sunnylinkd', target=launcher, args=('selfdrive.athena.sunnylinkd', 'sunnylinkd'))
      proc.start()
      proc.join()
      cloudlog.event("sunnylinkd exited", exitcode=proc.exitcode)
      time.sleep(5)
  except Exception:
    cloudlog.exception("manage_sunnylinkd.exception")
  finally:
    params.remove(SUNNYLINK_MGR_PID_PARAM)


if __name__ == '__main__':
  main()
