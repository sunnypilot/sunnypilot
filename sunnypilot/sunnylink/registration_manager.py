#!/usr/bin/env python3
import time

from openpilot.common.params import Params
from openpilot.common.realtime import Ratekeeper
from openpilot.common.swaglog import cloudlog

from cereal import log, messaging
from sunnypilot.sunnylink.utils import register_sunnylink

NetworkType = log.DeviceState.NetworkType


def main():
  """The main method is expected to be called by the manager when the device boots up."""
  try:
    rk = Ratekeeper(.5)
    sm = messaging.SubMaster(['deviceState'], poll='deviceState')
    while True:
      sm.update(1000)
      if sm['deviceState'].networkType != NetworkType.none:
        break

      cloudlog.info(f"Waiting to become online... {time.monotonic()}")
      rk.keep_time()

    register_sunnylink()
  except Exception:
    cloudlog.exception("Sunnylink registration failed")
    Params().put_bool("SunnylinkTempFault", True)
    raise


if __name__ == "__main__":
  main()
