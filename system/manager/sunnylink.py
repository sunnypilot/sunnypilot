#!/usr/bin/env python3
from cereal import log
from openpilot.common.api.sunnylink import SunnylinkApi, UNREGISTERED_SUNNYLINK_DONGLE_ID
from openpilot.common.params import Params
from openpilot.system.hardware import HARDWARE
from openpilot.system.version import is_prebuilt
import time

NetworkType = log.DeviceState.NetworkType


def is_network_connected() -> bool:
  """Check if the device is connected to a network."""
  return HARDWARE.get_network_type() != NetworkType.none


def get_sunnylink_status(params=Params()) -> tuple[bool, bool]:
  """Get the status of Sunnylink on the device. Returns a tuple of (is_sunnylink_enabled, is_registered)."""
  is_sunnylink_enabled = params.get_bool("SunnylinkEnabled")
  is_registered = params.get("SunnylinkDongleId", encoding='utf-8') not in (None, UNREGISTERED_SUNNYLINK_DONGLE_ID)
  return is_sunnylink_enabled, is_registered


def sunnylink_ready(params=Params()) -> bool:
  """Check if the device is ready to communicate with Sunnylink. That means it is enabled and registered."""
  is_sunnylink_enabled, is_registered = get_sunnylink_status(params)
  return is_sunnylink_enabled and is_registered


def sunnylink_need_register(params=Params()) -> bool:
  """Check if the device needs to be registered with Sunnylink."""
  is_sunnylink_enabled, is_registered = get_sunnylink_status(params)
  return is_sunnylink_enabled and not is_registered and is_network_connected()


def register_sunnylink():
  """Register the device with Sunnylink if it is enabled."""
  extra_args = {}

  if not Params().get_bool("SunnylinkEnabled"):
    print("Sunnylink is not enabled. Exiting.")
    exit(0)

  if not is_prebuilt():
    extra_args = {
      "verbose": True,
      "timeout": 60
    }

  sunnylink_id = SunnylinkApi(None).register_device(None, **extra_args)
  print(f"SunnyLinkId: {sunnylink_id}")


def main():
  """The main method is expected to be called by the manager when the device boots up."""
  register_sunnylink()


if __name__ == "__main__":
  main()
