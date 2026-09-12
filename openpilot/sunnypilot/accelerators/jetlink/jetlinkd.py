#!/usr/bin/env python3
"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Presents the USB gadget and provisions whatever large model is selected.

Something has to hold the FunctionFS endpoints or the comma never enumerates,
and the Jetson usually powers up after the comma, so this runs even with
nothing to do. Provisioning (upload plus a TensorRT build) takes minutes, far
past modeld's 60 s big-model timeout, so it happens offroad; the result is
cached on the Jetson, recorded in a param and left loaded on the server.

manager stops this with SIGINT at ignition and SIGKILLs it 5 s later, so every
long wait polls `stop`: a FunctionFS owner killed mid-transfer leaves the
gadget in a state only a reboot clears. jetlinkd owns the link offroad, modeld
onroad; on the handover the gadget briefly unbinds and the Jetson re-enumerates.

Once the engine is ready and DORMANT_HOLD has passed the gadget is released so
a Jetson on an always-on supply can sleep. It is presented again when there is
work; modeld's bind at ignition is the wake.
"""
from __future__ import annotations

import functools
import json
import os
import signal
import subprocess
import threading
import time
from pathlib import Path

from openpilot.common.realtime import Ratekeeper
from openpilot.common.swaglog import cloudlog

from openpilot.sunnypilot import accelerators
from openpilot.common.params import Params
from openpilot.sunnypilot.accelerators.jetlink import helpers, spec_cache, warp_cache

POLL_HZ = 2.0
RETRY_BACKOFF = 30.0       # after a failed provision
RETRY_BACKOFF_MAX = 900.0  # ceiling once the failures keep coming
RECONNECT_BACKOFF = 5.0    # after the link itself failed

# how long after ignition-off the gadget is released once there is nothing to
# do. The server sleeps 120 s after the gadget goes; a stop inside the hold
# rejoins at once, one outside it costs the ~8 s wake
DORMANT_HOLD = 60.0
# a sleeping Jetson wakes on the bind: ~6 s to a kernel, ~1 s to enumerate
WAKE_TIMEOUT = 20.0

# loggerd's dirty pages pile up until the kernel reclaims them synchronously,
# right while a FunctionFS transfer allocates its buffer: gadget reads stalled
# 200-350 ms, past backend.INFERENCE_TIMEOUT, and the big model fell back.
# Capping dirty memory and holding a free-memory floor took the worst frame
# from 244 to 72 ms with no lagging frames over 20 min.
#
# System-wide, since the gadget read shares the kernel with every writer.
# Applied here so a device with the link off runs stock values, which are
# recorded in SYSCTL_PREV and put back only on disable. Never restored on
# exit: manager stops this daemon at ignition, exactly when the contention
# starts, so modeld would get stock values every drive. A reboot resets them
VM_SYSCTLS = {
  'vm.dirty_bytes': '16777216',
  'vm.dirty_background_bytes': '8388608',
  'vm.min_free_kbytes': '131072',
}
# stock AGNOS runs the dirty limits in ratio mode, so both *_bytes keys read 0,
# and the kernel silently drops a 0 written back to them. Writing the ratio key
# is what zeroes the bytes key, so the ratios are recorded alongside
VM_RATIO_KEYS = {
  'vm.dirty_bytes': 'vm.dirty_ratio',
  'vm.dirty_background_bytes': 'vm.dirty_background_ratio',
}
SYSCTL_PREV = Path('/dev/shm/jetlink-sysctl-prev')
PROC_SYS = Path('/proc/sys')


def _read_sysctls(keys) -> dict[str, str]:
  values = {}
  for key in keys:
    try:
      values[key] = (PROC_SYS / key.replace('.', '/')).read_text().strip()
    except OSError:
      cloudlog.exception(f"jetlink: could not read {key}")
  return values


def _write_sysctls(values: dict[str, str]) -> None:
  # sudo -n sysctl is the same privilege setup_gadget.sh uses; root writes /proc
  for key, value in values.items():
    try:
      if os.geteuid() == 0:
        (PROC_SYS / key.replace('.', '/')).write_text(value)
      else:
        subprocess.run(['sudo', '-n', 'sysctl', '-w', f'{key}={value}'], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
    except Exception:
      cloudlog.exception(f"jetlink: could not set {key}={value}")


def apply_vm_tuning() -> None:
  """Record the stock values once, then apply ours."""
  if not SYSCTL_PREV.exists():
    prev = _read_sysctls([*VM_SYSCTLS, *VM_RATIO_KEYS.values()])
    if prev:
      try:
        SYSCTL_PREV.write_text(json.dumps(prev))
      except OSError:
        cloudlog.exception("jetlink: could not record the previous sysctls")
  _write_sysctls(VM_SYSCTLS)


def restore_vm_tuning() -> None:
  """Put the recorded values back and drop the record."""
  try:
    prev = json.loads(SYSCTL_PREV.read_text())
  except FileNotFoundError:
    return
  except (OSError, ValueError):
    cloudlog.exception("jetlink: unreadable sysctl record, leaving the values as they are")
    prev = {}
  if isinstance(prev, dict):
    values = {}
    for key in VM_SYSCTLS:
      if key not in prev:
        continue
      ratio = VM_RATIO_KEYS.get(key)
      if str(prev[key]) == '0' and ratio in prev:
        # the kernel drops a 0 written to a *_bytes key; the ratio key is the
        # way back to ratio mode
        values[ratio] = str(prev[ratio])
      else:
        values[key] = str(prev[key])
    _write_sysctls(values)
  try:
    SYSCTL_PREV.unlink()
  except OSError:
    pass


def _timed_out(e: BaseException) -> bool:
  """Did the exchange time out with the stream still usable?

  Only LinkTimeout leaves the stream in sync; every other LinkError does not.
  """
  try:
    from jetlink.transport.base import LinkTimeout
  except ImportError:
    return False  # cannot tell, so reopen
  return isinstance(e, LinkTimeout)


class Jetlinkd:
  def __init__(self):
    self.client = None
    self.stop = False
    self.ready = False
    self.next_attempt = 0.0
    self.next_provision = 0.0
    self.failures = 0
    self.was_attached = False
    self.fetch_failed = False
    self.verified = False   # the server has confirmed the ready param this attach
    self.warp_built = False  # tried the comma-side warp this run
    self.warp_thread: threading.Thread | None = None
    self.started = time.monotonic()
    self.dormant = False     # released the gadget on purpose; see go_dormant
    self.vm_tuned = False    # our sysctls are in; restored only on disable

  # -- lifecycle ------------------------------------------------------------

  def request_stop(self, *_) -> None:
    self.stop = True

  def close_link(self) -> None:
    """Always go through this: a FunctionFS owner that exits without closing
    can wedge the driver until a reboot."""
    client, self.client = self.client, None
    if client is not None:
      try:
        client.close()
      except Exception:
        cloudlog.exception("jetlink: error closing the link")

  def open_link(self) -> bool:
    """Present the gadget so a Jetson can enumerate whenever it powers on."""
    if self.client is not None:
      return True
    try:
      self.client = helpers.connect(deadline=5.0)
      cloudlog.warning("jetlink: gadget presented, waiting for a jetson")
      return True
    except Exception:
      cloudlog.exception("jetlink: could not present the gadget")
      self.next_attempt = time.monotonic() + RECONNECT_BACKOFF
      return False

  # -- provisioning ---------------------------------------------------------

  def fetch_model(self):
    """Download the pinned large model, once.

    Minutes on a slow link, so it reports progress and stops when manager
    wants the daemon gone; it is the one call in the loop that blocks for long.
    """
    if self.fetch_failed:
      return None
    try:
      path = helpers.fetch_shipped_model(
        progress=lambda frac: accelerators.report_progress('download', frac, 'downloading the large model'),
        should_stop=lambda: self.stop,
      )
    except Exception:
      cloudlog.exception("jetlink: could not fetch the large model")
      accelerators.report_progress('failed', 1.0, 'could not download the large model')
      # one attempt per run; retrying a gigabyte on a loop is worse than staying small
      self.fetch_failed = True
      return None
    return path

  def build_warp(self) -> None:
    """Build a comma-side warp only if one is missing.

    scons builds it before manager starts, so this only covers a prebuilt
    image made without the target. Independent of provision(): the warp
    depends on the camera and the small model's input size, not on the
    Jetson. On a thread because the ~9 s compile cannot poll `stop` and
    manager SIGKILLs the daemon 5 s after SIGINT, which landed mid-transfer
    twice in one evening; a killed compile writes through a temporary and
    leaves nothing behind.
    """
    if self.warp_built:
      return
    self.warp_built = True
    geometry = warp_cache.device_geometry()
    if warp_cache.is_cached(*geometry):
      return
    # only past here is there a compile to report; reporting first flashed
    # "compiling the camera warp" through the UI on every start
    accelerators.report_progress('warp', 0.0, 'compiling the camera warp')

    def build() -> None:
      if warp_cache.ensure(*geometry):
        accelerators.clear_progress()

    self.warp_thread = threading.Thread(target=build, daemon=True, name='jetlink_warp')
    self.warp_thread.start()

  @staticmethod
  def _eta(seconds: float) -> str:
    if seconds >= 90:
      return f"about {seconds / 60:.0f} min left"
    return f"about {max(seconds, 1):.0f}s left"

  def _report_with_eta(self, stage: str, frac: float, msg: str) -> None:
    """Progress, with how long the build still has to run.

    built_seconds in models.json is measured on this hardware. It belongs here
    rather than in the UI, which knows nothing about jetlink. Only the build is
    estimated: the upload reports MB of MB and a connect has nothing to predict.
    """
    if stage == 'build':
      entry = helpers.selected_model() or {}
      built = entry.get('built_seconds')
      if built:
        msg = self._eta(float(built) * max(0.0, 1.0 - frac))
    accelerators.report_progress(stage, frac, msg)

  def provision(self) -> bool:
    """Make the Jetson ready for the selected model. Host must be attached.

    The identity comes from models.json (the git-lfs oid is the sha256, size
    the byte count), so the comma can ask without holding or hashing the ONNX.
    The file is only fetched when the server asks for the bytes; the Jetson
    keeps its own copy of every ONNX and never prunes it.
    """
    # imported here: the jetlink package may be absent and this module must
    # still import. Same as backend._open_link
    from jetlink.client import EngineMissing

    entry = helpers.selected_model()
    sha256 = (entry or {}).get('oid')
    nbytes = (entry or {}).get('size')
    if not sha256 or not nbytes:
      # nothing selected, or an entry with no identity; not an error
      helpers.set_engine_ready(None)
      accelerators.clear_progress()
      return False
    nbytes = int(nbytes)

    # the param says ready, but the Jetson's cache may have been pruned or
    # re-flashed since. Ask once per attach
    if self.verified and helpers.engine_ready_for(sha256):
      return True

    # only needed if the server turns out not to have this model; None is a
    # legitimate state here, see EngineMissing below
    model_path = helpers.active_model_path()

    cloudlog.warning("jetlink: provisioning %s (%d MB, sha %s)",
                     entry.get('name', sha256[:16]), nbytes >> 20, sha256[:16])
    accelerators.report_progress('connect', 0.0, 'talking to the jetson')

    hello = self.client.hello(timeout=10.0)
    Params().put('JetlinkCachedModels', hello.get('cached_models', []))
    cloudlog.warning("jetlink: server %s trt %s", hello.get('device'), hello.get('trt_version'))
    # ask without the file first: the server answers from the sha alone when it
    # has the model, which is every poll of a parked car
    ask = functools.partial(self.client.ensure_engine, sha256, nbytes,
                            progress=self._report_with_eta,
                            build_timeout=1800.0, should_stop=lambda: self.stop)
    try:
      spec = ask(onnx_path=None)
    except EngineMissing:
      upload = self._verified_upload(model_path, sha256, nbytes)
      if upload is None:
        # nothing to give. Fetch it and let the next poll try again rather than
        # holding the link through a download that takes minutes
        if model_path is None and self.fetch_model() is not None:
          return False
        raise
      spec = ask(onnx_path=upload)

    spec_cache.store(spec, model_path)
    helpers.set_engine_ready(spec.sha256)
    cached = helpers._get('JetlinkCachedModels') or []
    Params().put('JetlinkCachedModels', sorted(set(cached) | {spec.sha256}))
    self.verified = True
    accelerators.report_progress('ready', 1.0, 'engine ready')
    helpers.cleanup_unchunked(keep=model_path)
    cloudlog.warning("jetlink: engine ready for %s", spec.sha256[:16])
    return True

  def _verified_upload(self, model_path, sha256: str, nbytes: int):
    """The file to upload, once its hash is proven to match the registry.

    Uploading under a sha the bytes do not have would leave the Jetson with a
    plan whose name lies about its contents, so the hash happens here, on the
    one path where the bytes go somewhere.
    """
    if model_path is None:
      return None
    try:
      if model_path.stat().st_size != nbytes:
        cloudlog.error("jetlink: %s is %d bytes, the registry says %d; not uploading it",
                       model_path.name, model_path.stat().st_size, nbytes)
        return None
      from jetlink.spec import sha256_file
      have, _ = sha256_file(str(model_path))
      if have != sha256:
        cloudlog.error("jetlink: %s hashes to %s, the registry says %s; not uploading it",
                       model_path.name, have[:16], sha256[:16])
        return None
    except OSError:
      return None
    return model_path

  # -- the parked car -------------------------------------------------------

  def go_dormant(self) -> None:
    """Release the gadget so the Jetson can sleep. The marker goes first so
    present() never blinks. Readiness is kept; the server is asked again on
    the next attach."""
    cloudlog.warning("jetlink: nothing left to do, releasing the gadget so the jetson can sleep")
    helpers.set_dormant(True)
    self.close_link()
    self.dormant = True
    self.was_attached = False
    self.verified = False

  def wake(self) -> None:
    """Present the gadget again. If the Jetson is asleep, the bind wakes it."""
    cloudlog.warning("jetlink: presenting the gadget again")
    helpers.set_dormant(False)
    self.dormant = False

  def has_work(self) -> bool:
    """Is there a reason to wake the Jetson? Only things the link can fix
    count; the warp is local and build_warp handles it."""
    spec = spec_cache.load()
    if spec is None or not helpers.engine_ready_for(spec.sha256):
      return True
    selected = helpers.selected_model()
    return selected is not None and selected.get('oid') != spec.sha256

  def shutdown_jetson(self, reason: str) -> None:
    """hardwared is shutting the comma down and wants the Jetson off too.
    The request file is removed whatever happens: hardwared is waiting on it."""
    cloudlog.warning("jetlink: shutting the jetson down: %s", reason)
    try:
      if self.dormant:
        self.wake()
      if not self.open_link():
        raise RuntimeError("could not present the gadget")
      deadline = time.monotonic() + WAKE_TIMEOUT
      while not helpers.host_attached():
        if self.stop or time.monotonic() > deadline:
          raise TimeoutError(f"no jetson attached within {WAKE_TIMEOUT:.0f} s")
        time.sleep(0.25)
      resp = self.client.shutdown(reason, timeout=5.0)
      cloudlog.warning("jetlink: jetson answered the shutdown request: %s", resp)
    except Exception:
      cloudlog.exception("jetlink: could not shut the jetson down")
    finally:
      helpers.finish_shutdown()

  # -- VM tuning ------------------------------------------------------------

  def tune_vm(self) -> None:
    if not self.vm_tuned:
      apply_vm_tuning()
      self.vm_tuned = True

  def untune_vm(self) -> None:
    if self.vm_tuned:
      restore_vm_tuning()
      self.vm_tuned = False

  # -- main loop ------------------------------------------------------------

  def backoff(self) -> float:
    """Wait before provisioning again, doubling per failure.

    A powered Jetson that never answers would otherwise be retried 120 times
    an hour for as long as the car is parked, each a round of USB churn.
    """
    return min(RETRY_BACKOFF * 2 ** (self.failures - 1), RETRY_BACKOFF_MAX)

  def step(self) -> None:
    if not helpers.enabled():
      if self.client is not None or self.ready:
        cloudlog.warning("jetlink: disabled, releasing the link")
        helpers.set_engine_ready(None)
        self.ready = False
        self.close_link()
      if self.dormant:
        self.wake()
      self.untune_vm()
      return

    self.tune_vm()
    reason = helpers.pending_shutdown()
    if reason is not None:
      self.shutdown_jetson(reason)
      return

    if self.dormant:
      if self.has_work():
        self.wake()
      else:
        return

    # before the link and the attach gate: the warp needs neither, and modeld
    # will not start the large model without it
    self.build_warp()

    if time.monotonic() < self.next_attempt:
      return
    if not self.open_link():
      return

    attached = helpers.host_attached()
    if attached != self.was_attached:
      cloudlog.warning("jetlink: jetson %s", "attached" if attached else "gone")
      self.was_attached = attached
      if attached:
        # a host that has just arrived gets a clean slate rather than a backoff
        # earned by whatever was on the link before it
        self.failures = 0
        self.next_provision = 0.0
        self.verified = False
      else:
        # it powered down or rebooted. Readiness is about the engine on the
        # Jetson, which survives; modeld reconnects on its own
        self.ready = False
    if not attached:
      return
    # provisioning backs off on its own timer, so a long wait for an
    # unresponsive server still watches for one that reappears
    if time.monotonic() < self.next_provision:
      return

    try:
      self.ready = self.provision()
      self.failures = 0
      self.next_provision = 0.0
      if self.ready and time.monotonic() - self.started >= DORMANT_HOLD:
        self.go_dormant()
    except Exception as e:
      cloudlog.exception("jetlink: provisioning failed")
      accelerators.report_progress('failed', 1.0, 'see the log')
      self.ready = False
      # only reopen when the link itself is suspect: unbinding makes the host
      # re-enumerate, and doing that for a server that is not up yet is hours
      # of USB churn
      if not _timed_out(e):
        self.close_link()
      self.failures += 1
      self.next_provision = time.monotonic() + self.backoff()

  def run(self) -> None:
    if helpers.enabled():
      self.tune_vm()
    rk = Ratekeeper(POLL_HZ)
    try:
      while not self.stop:
        rk.keep_time()
        try:
          self.step()
        except Exception:
          # nothing may escape: restarting in a loop is worse than sitting out a cycle
          cloudlog.exception("jetlink: unhandled error")
          self.close_link()
          self.next_attempt = time.monotonic() + RECONNECT_BACKOFF
    finally:
      # the sysctls stay: a stop here is the ignition handoff to modeld
      self.close_link()
    helpers.set_dormant(False)
    if self.warp_thread is not None and self.warp_thread.is_alive():
      cloudlog.warning("jetlink: stopped with the warp still compiling; it will rebuild next time")
    cloudlog.warning("jetlink: stopped")


def main() -> None:
  d = Jetlinkd()
  # manager stops this at the onroad transition; closing the link properly is
  # what keeps the driver healthy for modeld
  signal.signal(signal.SIGTERM, d.request_stop)
  signal.signal(signal.SIGINT, d.request_stop)
  d.run()


if __name__ == "__main__":
  main()
