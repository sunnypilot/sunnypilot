#!/usr/bin/env python3
# simple pandad wrapper that updates the panda first
import os
import signal
import subprocess
import time
from pathlib import Path

import usb1

from panda import Panda, PandaDFU, PandaProtocolMismatch, McuType, FW_PATH
from openpilot.common.basedir import BASEDIR
from openpilot.common.params import Params
from openpilot.common.hardware import HARDWARE
from openpilot.common.swaglog import cloudlog

from openpilot.sunnypilot.selfdrive.pandad.rivian_long_flasher import flash_rivian_long


def get_expected_signature() -> bytes:
  fn = os.path.join(FW_PATH, McuType.H7.config.app_fn)
  return Panda.get_signature_from_firmware(fn)

def flash_panda(panda_serial: str):
  panda = Panda(panda_serial)

  # skip flashing if the detected panda is not supported
  if panda.get_type() not in Panda.SUPPORTED_DEVICES:
    cloudlog.warning(f"Panda {panda_serial} is not supported (hw_type: {panda.get_type()}), skipping flash...")
    panda.close()
    return

  fw_signature = get_expected_signature()
  internal_panda = panda.is_internal()

  panda_version = "bootstub" if panda.bootstub else panda.get_version()
  panda_signature = b"" if panda.bootstub else panda.get_signature()
  cloudlog.warning(f"Panda {panda_serial} connected, version: {panda_version}, signature {panda_signature.hex()[:16]}, expected {fw_signature.hex()[:16]}")

  if panda.bootstub or panda_signature != fw_signature:
    cloudlog.info("Panda firmware out of date, update required")
    panda.flash()
    cloudlog.info("Done flashing")

  if panda.bootstub:
    bootstub_version = panda.get_version()
    cloudlog.info(f"Flashed firmware not booting, flashing development bootloader. {bootstub_version=}, {internal_panda=}")
    if internal_panda:
      HARDWARE.recover_internal_panda()
    panda.recover(reset=(not internal_panda))
    cloudlog.info("Done flashing bootstub")

  if panda.bootstub:
    cloudlog.info("Panda still not booting, exiting")
    raise AssertionError

  panda_signature = panda.get_signature()
  if panda_signature != fw_signature:
    cloudlog.info("Version mismatch after flashing, exiting")
    raise AssertionError

  panda.close()


# Cooperative handoff for short-lived direct-Panda tools. SIGWINCH is ignored
# by an unmodified wrapper, so an older running pandad fails closed instead of
# being killed by a lease request meant for this version.
DIRECT_PANDA_LEASE_SIGNAL = signal.SIGWINCH
DIRECT_PANDA_LEASE_PATH = Path("/tmp/openpilot-pandad-direct-lease")
DIRECT_PANDA_LEASE_READY_PATH = Path("/tmp/openpilot-pandad-direct-ready")
TSS3_ORACLE_HANDOFF_EXIT_CODE = 42
TSS3_ORACLE_LEASE_WAIT_SECONDS = 1.0


def _active_direct_panda_lease() -> str | None:
  try:
    lease = DIRECT_PANDA_LEASE_PATH.read_text(encoding="utf-8").strip()
    pid_text, token = lease.split(" ", 1)
    if not token:
      raise ValueError("empty direct-Panda lease token")
    os.kill(int(pid_text), 0)
    return lease
  except (FileNotFoundError, ProcessLookupError, PermissionError, ValueError):
    DIRECT_PANDA_LEASE_PATH.unlink(missing_ok=True)
    DIRECT_PANDA_LEASE_READY_PATH.unlink(missing_ok=True)
    return None


def _publish_direct_panda_lease_ready(lease: str) -> None:
  tmp = DIRECT_PANDA_LEASE_READY_PATH.with_name(f".{DIRECT_PANDA_LEASE_READY_PATH.name}.{os.getpid()}")
  tmp.write_text(lease + "\n", encoding="utf-8")
  os.replace(tmp, DIRECT_PANDA_LEASE_READY_PATH)


def _wait_for_direct_panda_lease(timeout: float) -> str | None:
  deadline = time.monotonic() + timeout
  while time.monotonic() < deadline:
    lease = _active_direct_panda_lease()
    if lease is not None:
      return lease
    time.sleep(0.005)
  return _active_direct_panda_lease()


def check_panda_support(panda_serials: list[str]) -> list[str]:
  spi_serials = set(Panda.spi_list())
  for serial in panda_serials:
    if serial in spi_serials:
      return [serial]

  for serial in panda_serials:
    panda = Panda(serial)
    is_internal = panda.is_internal()
    panda.close()
    if is_internal:
      return [serial]

  return []


def main() -> None:
  process = None
  do_exit = False
  direct_lease_requested = False

  # Normal manager shutdown still terminates the native child and exits this
  # wrapper. A direct-Panda lease is different: keep this managed wrapper alive,
  # intentionally release only the native child, then restart it without the
  # reset/recovery/flash path when the lease ends.
  def signal_handler(signum, frame):
    cloudlog.info(f"Caught signal {signum}, exiting")
    nonlocal do_exit
    do_exit = True
    if process is not None and process.poll() is None:
      process.send_signal(signal.SIGINT)

  def direct_lease_signal_handler(signum, frame):
    nonlocal direct_lease_requested
    lease = _active_direct_panda_lease()
    if lease is None:
      cloudlog.warning("Ignoring direct-Panda lease signal without a live lease")
      return
    direct_lease_requested = True
    cloudlog.info(f"Direct-Panda lease requested: {lease}")
    if process is not None and process.poll() is None:
      process.send_signal(signal.SIGINT)

  def hold_direct_panda_lease(lease: str) -> None:
    cloudlog.info(f"Direct-Panda lease ready: {lease}")
    _publish_direct_panda_lease_ready(lease)
    try:
      while not do_exit and _active_direct_panda_lease() == lease:
        time.sleep(0.05)
    finally:
      try:
        if DIRECT_PANDA_LEASE_READY_PATH.read_text(encoding="utf-8").strip() == lease:
          DIRECT_PANDA_LEASE_READY_PATH.unlink(missing_ok=True)
      except FileNotFoundError:
        pass
    cloudlog.info(f"Direct-Panda lease released: {lease}")

  signal.signal(signal.SIGINT, signal_handler)
  signal.signal(signal.SIGTERM, signal_handler)
  signal.signal(DIRECT_PANDA_LEASE_SIGNAL, direct_lease_signal_handler)

  # check health for lost heartbeat
  try:
    for s in Panda.list():
      with Panda(s) as p:
        health = p.health()
        if p.is_internal() and health["heartbeat_lost"]:
          Params().put_bool("PandaHeartbeatLost", True, block=True)
          cloudlog.event("heartbeat lost", deviceState=health)
  except Exception:
    cloudlog.exception("pandad.uncaught_exception")

  count = 0
  restart_without_recovery = False
  while not do_exit:
    try:
      if not restart_without_recovery:
        cloudlog.event("pandad.flash_and_connect", count=count)
        if (count % 2) == 0:
          HARDWARE.reset_internal_panda()
        else:
          HARDWARE.recover_internal_panda()
        count += 1

        # Flash all Pandas in DFU mode.
        for serial in PandaDFU.list():
          cloudlog.info(f"Panda in DFU mode found, flashing recovery {serial}")
          PandaDFU(serial).recover()
          time.sleep(1)

        panda_serials = Panda.list()
        if not panda_serials:
          continue

        # Preserve Sunnypilot's custom Rivian flasher and supported-device
        # selection before yielding the Panda to the native daemon.
        flash_rivian_long(panda_serials)
        panda_serials = check_panda_support(panda_serials)
        assert len(panda_serials) == 1
        cloudlog.info(f"{len(panda_serials)} panda found, connecting - {panda_serials}")
        flash_panda(panda_serials[0])
      restart_without_recovery = False

      lease = _active_direct_panda_lease()
      if direct_lease_requested or lease is not None:
        direct_lease_requested = False
        if lease is not None:
          hold_direct_panda_lease(lease)
        if do_exit:
          break
        restart_without_recovery = True
        continue

      # run real pandad
      os.environ['MANAGER_DAEMON'] = 'pandad'
      process = subprocess.Popen(["./pandad"], cwd=os.path.join(BASEDIR, "openpilot/selfdrive/pandad"))
      returncode = process.wait()
      process = None
      if do_exit:
        break

      lease = _active_direct_panda_lease()
      if returncode == TSS3_ORACLE_HANDOFF_EXIT_CODE and lease is None:
        # Native pandad has already sent 10 02, published the exact catch
        # marker, and closed its SPI handle. The daemon notification precedes
        # creation of the cooperative lease by a few milliseconds, so bridge
        # that bounded race without entering Panda reset/recovery.
        lease = _wait_for_direct_panda_lease(TSS3_ORACLE_LEASE_WAIT_SECONDS)
      if direct_lease_requested or lease is not None:
        direct_lease_requested = False
        if lease is not None:
          hold_direct_panda_lease(lease)
        if do_exit:
          break
        restart_without_recovery = True
        continue

      if returncode == TSS3_ORACLE_HANDOFF_EXIT_CODE:
        cloudlog.error("TSS3 oracle catcher exited for handoff, but no cooperative Panda lease arrived")
        restart_without_recovery = True
        continue

      # An unrequested native-child exit remains a real Panda failure and goes
      # through the reset/re-flash path on the next loop.
    # TODO: wrap all panda exceptions in a base panda exception
    except (usb1.USBErrorNoDevice, usb1.USBErrorPipe):
      process = None
      cloudlog.exception("Panda USB exception while setting up")
    except PandaProtocolMismatch:
      process = None
      cloudlog.exception("pandad.protocol_mismatch")
    except Exception:
      process = None
      cloudlog.exception("pandad.uncaught_exception")


if __name__ == "__main__":
  main()
