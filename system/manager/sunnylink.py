#!/usr/bin/env python3

from openpilot.common.api.sunnylink import SunnylinkApi
from openpilot.common.params import Params
from openpilot.common.spinner import Spinner
from openpilot.system.version import is_prebuilt


if __name__ == "__main__":
  spinner = Spinner()
  extra_args = {}

  if not Params().get_bool("SunnylinkEnabled"):
    print("Sunnylink is not enabled. Exiting.")
    spinner.close()
    exit(0)

  if not is_prebuilt():
    extra_args = {
      "verbose": True,
      "timeout": 60
    }

  sunnylink_id = SunnylinkApi(None).register_device(spinner, **extra_args)
  print(f"SunnyLinkId: {sunnylink_id}")
  spinner.close()
