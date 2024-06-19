#!/usr/bin/env python3

from openpilot.common.api.sunnylink import SunnylinkApi
from openpilot.common.params import Params
from openpilot.system.version import is_prebuilt
import time


def main():
  extra_args = {}

  if not Params().get_bool("SunnylinkEnabled"):
    print("Sunnylink is not enabled. Exiting.")
    # spinner.close()
    exit(0)

  if not is_prebuilt():
    extra_args = {
      "verbose": True,
      "timeout": 60
    }

  sunnylink_id = SunnylinkApi(None).register_device(None, **extra_args)
  print(f"SunnyLinkId: {sunnylink_id}")

  # Set the last ping time to the current time since we just registered
  last_ping = int(time.monotonic() * 1e9)
  Params().put("LastSunnylinkPingTime", str(last_ping))


if __name__ == "__main__":
  main()
