#!/usr/bin/env python3
from openpilot.common.api.sunnylink import SunnylinkApi
from openpilot.common.spinner import Spinner
from openpilot.system.version import is_prebuilt


if __name__ == "__main__":
  spinner = Spinner()
  extra_args = {}
  if not is_prebuilt():
    extra_args = {
      "verbose": True,
      "timeout": 60
    }

  SunnylinkApi(None).register_device(spinner, **extra_args)
  spinner.close()
