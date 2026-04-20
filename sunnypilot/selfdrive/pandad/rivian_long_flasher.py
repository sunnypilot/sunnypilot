#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import os
from itertools import accumulate

from cereal import car, messaging
from panda import Panda
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog

FW_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rivian_long_fw.bin.signed")
SECTOR_SIZES = [0x4000] * 4 + [0x10000] + [0x20000] * 11


def _is_rivian() -> bool:
  params = Params()

  # check fixed fingerprint
  if bundle := params.get("CarPlatformBundle"):
    if bundle.get("brand") == "rivian":
      return True

  # check cached fingerprint
  CP_bytes = params.get("CarParamsPersistent")
  if CP_bytes is not None:
    CP = messaging.log_from_bytes(CP_bytes, car.CarParams)
    if CP.brand == "rivian":
      return True

  return False


def _flash_static(handle, code):
  assert Panda.flasher_present(handle)
  last_sector = next((i + 1 for i, v in enumerate(accumulate(SECTOR_SIZES[1:])) if v > len(code)), -1)
  assert 1 <= last_sector < 7, "Invalid firmware size"

  handle.controlWrite(Panda.REQUEST_IN, 0xb1, 0, 0, b'')
  for i in range(1, last_sector + 1):
    handle.controlWrite(Panda.REQUEST_IN, 0xb2, i, 0, b'')
  for i in range(0, len(code), 0x10):
    handle.bulkWrite(2, code[i:i + 0x10])
  try:
    handle.controlWrite(Panda.REQUEST_IN, 0xd8, 0, 0, b'', expect_disconnect=True)
  except Exception:
    pass


def _flash_panda(panda: Panda) -> None:
  expected_sig = Panda.get_signature_from_firmware(FW_PATH)
  if not panda.bootstub and panda.get_signature() == expected_sig:
    cloudlog.info(f"F4 panda {panda.get_usb_serial()} already up to date")
    return

  cloudlog.info(f"Flashing F4 panda {panda.get_usb_serial()}")
  with open(FW_PATH, "rb") as f:
    code = f.read()

  if not panda.bootstub:
    # enter bootstub directly, panda.reset() rejects deprecated hw types
    try:
      panda._handle.controlWrite(Panda.REQUEST_IN, 0xd1, 1, 0, b'', timeout=15000, expect_disconnect=True)
    except Exception:
      pass
    panda.close()
    panda.reconnect()

  _flash_static(panda._handle, code)
  panda.reconnect()
  cloudlog.info(f"Successfully flashed xnor's Rivian Longitudinal Upgrade Kit: {panda.get_usb_serial()}")


def flash_rivian_long(panda_serials: list[str]) -> None:
  if not os.path.isfile(FW_PATH):
    cloudlog.error(f"Rivian longitudinal upgrade firmware not found at {FW_PATH}")
    return

  if not _is_rivian():
    cloudlog.info("Not a Rivian, skipping longitudinal upgrade...")
    return

  # only check USB connected pandas, internal panda uses SPI and is never an external panda
  usb_serials = set(Panda.usb_list())
  for serial in panda_serials:
    if serial not in usb_serials:
      continue
    panda = Panda(serial)
    # only flash external black pandas (HW_TYPE_BLACK = 0x03)
    if panda.get_type() == b'\x03' and not panda.is_internal():
      try:
        _flash_panda(panda)
      except Exception:
        cloudlog.exception(f"Failed to flash xnor's Rivian Longitudinal Upgrade Kit: {serial}")
    panda.close()

  return


if __name__ == '__main__':
  flash_rivian_long(Panda.list())
