#!/usr/bin/env python3
"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Presents the USB gadget and provisions whatever large model is selected.

Two jobs, and the first one is the reason this runs even when there is nothing
to do: **something has to hold the gadget open**. The comma is the USB device,
and its controller only binds while a process owns the FunctionFS endpoints.
Nothing holds them, nothing enumerates, and a Jetson powered on later never
appears. The two boxes come up on different power rails - usually the comma
first - so the comma has to sit there presenting itself until the Jetson
arrives, however long that takes.

The second job is provisioning: uploading the model and building a TensorRT
engine takes minutes, far longer than modeld's 60 s big-model timeout, so it
happens offroad and the result is cached on the Jetson and recorded in a param.
The engine is also left loaded on the server, so modeld's connect at ignition
is a round trip rather than a 13 to 25 s deserialization.

manager stops this daemon with SIGINT at the onroad transition and SIGKILLs it
5 s later. Every long wait in here polls `stop`, because a FunctionFS owner
killed mid-transfer leaves the gadget in a state only a reboot reliably clears.

Ownership of the link is exclusive: jetlinkd offroad, modeld onroad. manager's
only_offroad gate enforces that. On the handover the gadget briefly unbinds and
the Jetson re-enumerates, which both ends handle.

The exception to holding the gadget is the parked car. A Jetson on an
always-on supply sleeps when it has had no gadget for a while and wakes on
the next USB edge, so once the engine is ready and DORMANT_HOLD has passed
this daemon releases the gadget on purpose and only presents it again when
there is work: a model change, a readiness the server no longer confirms, or
hardwared asking for the Jetson to be powered off with the comma. modeld's
bind at ignition is the wake.
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

# Once there is nothing left to do, how long after ignition-off (which is when
# manager starts us) the gadget is released so the Jetson can sleep. The
# server sleeps 120 s after the gadget goes, so the Jetson is down about three
# minutes after the car is parked; a quick stop inside the hold rejoins at
# once, one outside it costs the ~8 s wake. See jetlink/server/sleep.py.
DORMANT_HOLD = 60.0
# A sleeping Jetson wakes on the gadget bind: ~6 s to a kernel, ~1 s to
# enumerate on the bench.
WAKE_TIMEOUT = 20.0

# Keep a recording-writeback storm from stalling the gadget read path.
# loggerd/encoderd write video continuously; on a memory-tight comma (stock
# min_free_kbytes ~7 MB, ~40 MB free) a segment's dirty pages pile up until the
# kernel has to reclaim them synchronously - write them back before it can
# evict them - exactly while a FunctionFS transfer is allocating its buffer.
# Measured on the 2026-09-06 bench: nr_dirty to 108 MB, direct reclaim, and the
# gadget read stalled 200-350 ms, past backend.INFERENCE_TIMEOUT, so the big
# model fell back and rejoined (91 lagging frames, three losses in 15 min).
# Capping dirty memory (so reclaim finds clean, evictable pages) and holding a
# real free-memory floor (so allocations do not reclaim at all) removed it:
# dirty peak 7 MB, worst frame 244 -> 72 ms, zero lagging frames over 20 min;
# under a 500 MB memory hog plus CPU contention, 128 MB/16 MB held it too.
#
# System-wide on purpose - the gadget read shares the kernel with every writer.
# Applied here rather than at boot so a device with the link switched off runs
# stock values: the previous ones are recorded in SYSCTL_PREV before the first
# change and put back on the way out. A SIGKILL skips the restore and leaves
# them in place until reboot; that record survives us in /dev/shm so the next
# run still knows the stock values and never records our own as them.
VM_SYSCTLS = {
  'vm.dirty_bytes': '16777216',
  'vm.dirty_background_bytes': '8388608',
  'vm.min_free_kbytes': '131072',
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
  # The launcher runs us as comma; sysctl -w through sudo -n is the same
  # privilege setup_gadget.sh uses. Root (a bench run) writes /proc directly.
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
    prev = _read_sysctls(VM_SYSCTLS)
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
    _write_sysctls({k: str(v) for k, v in prev.items() if k in VM_SYSCTLS})
  try:
    SYSCTL_PREV.unlink()
  except OSError:
    pass


def _timed_out(e: BaseException) -> bool:
  """Did the exchange time out with the stream still usable?

  jetlink draws that line itself: LinkTimeout is documented as leaving the
  stream in sync, every other LinkError as not.
  """
  try:
    from jetlink.transport.base import LinkTimeout
  except ImportError:
    return False  # no way to tell, so assume the worst and reopen
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
    self.vm_tuned = False    # our sysctls are in; restore on the way out

  # -- lifecycle ------------------------------------------------------------

  def request_stop(self, *_) -> None:
    self.stop = True

  def close_link(self) -> None:
    """Always go through this. A FunctionFS owner that exits without closing
    leaves the gadget bound with nothing servicing it, and the next teardown
    can wedge the driver hard enough that only a reboot clears it."""
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
    """Download the pinned large model, once, on a device that has a Jetson.

    The install carries a pointer rather than the object, so the first time a
    Jetson is attached we have to go and get it. Minutes on a slow link, so it
    reports progress and gives up the moment manager wants us gone - the loop
    is single threaded and this is the one call in it that blocks for long.
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
      # One attempt per run. Retrying a gigabyte on a loop would be worse than
      # staying on the small model until the next boot.
      self.fetch_failed = True
      return None
    return path

  def build_warp(self) -> None:
    """Make sure a comma-side warp exists. Normally there is nothing to do.

    scons builds it (accelerators/SConscript), which runs from the launcher
    before manager starts, so on any device that ran a build this returns at
    the is_cached check. What is left for this to cover is a prebuilt install
    whose image was made without the target - there is no other way to get a
    warp there, and without one modeld will not start the large model at all.

    Not part of provision(): the warp depends only on this device's camera and
    the small model's input size, not on which large model is selected or on
    the Jetson answering. A warp that cannot be built costs the large model,
    not the drive - modeld falls back exactly as it does for any other
    big-model load failure.

    On a thread, because the compile is ~9 s of GPU work with nothing in it
    that can poll `stop`, and manager SIGKILLs this daemon 5 s after the SIGINT
    it sends at the onroad transition. Blocking the loop here meant the link
    was still open when the kill landed - observed twice in one evening, 7.5 s
    and 5 s - which is exactly the mid-transfer kill the module docstring says
    to avoid. Abandoning the compile is safe: it touches no link, and it writes
    the pickle through a temporary, so a killed build leaves nothing
    half-written for the next run to find.
    """
    if self.warp_built:
      return
    self.warp_built = True
    geometry = warp_cache.device_geometry()
    if warp_cache.is_cached(*geometry):
      return
    # Only past here is there a real compile to report. Reporting first meant a
    # "compiling the camera warp" that flashed through the UI on every start
    # for a warp the build had already made.
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

    models.json carries `built_seconds` per model and has since it was written,
    measured on this hardware, so that the UI could say how long a first
    provision takes. Nothing ever read it, and the panel showed "build 12%"
    while a driver waited out five minutes with no idea it was five and not
    thirty. The number belongs here rather than in the UI: it comes from the
    backend's own registry, and openpilot/selfdrive/ui stays free of any
    knowledge that jetlink exists.

    Only the build is estimated. The upload already reports MB of MB, and a
    connect has nothing to predict.
    """
    if stage == 'build':
      entry = helpers.selected_model() or {}
      built = entry.get('built_seconds')
      if built:
        msg = self._eta(float(built) * max(0.0, 1.0 - frac))
    accelerators.report_progress(stage, frac, msg)

  def provision(self) -> bool:
    """Make the Jetson ready for the selected model. Host must be attached.

    The identity comes from the registry, not from the file. models.json
    carries the git-lfs `oid`, which is the sha256, and `size`, which is the
    byte count - exactly the pair ENGINE_REQ wants. This used to hash the local
    ONNX to derive them, which meant the comma could not so much as ask the
    Jetson what it already had without holding 766 MB itself, and re-derived a
    number that was sitting in the registry the whole time.

    The Jetson keeps its own copy of every ONNX and never prunes them, so once
    a model has been provisioned the comma's copy is dead weight. Now it is
    only fetched when the server actually asks for the bytes, which means a
    model change with no network works as long as the Jetson has the engine.
    """
    # Imported here rather than at module scope: jetlinkd is constructed on
    # devices whose jetlink package may be absent, and the module must import
    # without it. Same reason backend._open_link does it.
    from jetlink.client import EngineMissing

    entry = helpers.selected_model()
    sha256 = (entry or {}).get('oid')
    nbytes = (entry or {}).get('size')
    if not sha256 or not nbytes:
      # Nothing selected, or a registry entry with no identity. Not an error.
      helpers.set_engine_ready(None)
      accelerators.clear_progress()
      return False
    nbytes = int(nbytes)

    # The param says ready, but the Jetson's cache may have been pruned,
    # re-flashed or swapped since. Ask once per attach; after that the answer
    # cannot change under us.
    if self.verified and helpers.engine_ready_for(sha256):
      return True

    # Only needed if the server turns out not to have this model. None is a
    # legitimate state here, not a failure: see EngineMissing below.
    model_path = helpers.active_model_path()

    cloudlog.warning("jetlink: provisioning %s (%d MB, sha %s)",
                     entry.get('name', sha256[:16]), nbytes >> 20, sha256[:16])
    accelerators.report_progress('connect', 0.0, 'talking to the jetson')

    hello = self.client.hello(timeout=10.0)
    Params().put('JetlinkCachedModels', hello.get('cached_models', []))
    cloudlog.warning("jetlink: server %s trt %s", hello.get('device'), hello.get('trt_version'))
    # Asked without the file first, always. The server answers from the sha
    # alone when it already has the model, which is every poll of a parked car,
    # and only the answer "I need the bytes" is worth reading 766 MB for.
    ask = functools.partial(self.client.ensure_engine, sha256, nbytes,
                            progress=self._report_with_eta,
                            build_timeout=1800.0, should_stop=lambda: self.stop)
    try:
      spec = ask(onnx_path=None)
    except EngineMissing:
      upload = self._verified_upload(model_path, sha256, nbytes)
      if upload is None:
        # Nothing to give. Fetch it and let the next poll try again rather than
        # holding the link through a download that takes minutes.
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
    """The file to upload if the server asks for it, once it is proven to be it.

    Taking the identity from the registry moves the trust from the file to
    models.json, which is right for asking a question and wrong for answering
    one: uploading under a sha the bytes do not have would leave the Jetson
    with a plan whose name lies about its contents, and nothing downstream
    would ever notice. So the hash happens here, on the one path where the
    bytes actually go somewhere, rather than on every poll of a parked car.
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
    present() never blinks: presence follows it, not the UDC, while we are
    dormant. Readiness is kept; the server is asked again on the next
    attach as it is after any other detach."""
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
    count: the warp is local and build_warp handles it regardless."""
    spec = spec_cache.load()
    if spec is None or not helpers.engine_ready_for(spec.sha256):
      return True
    selected = helpers.selected_model()
    return selected is not None and selected.get('oid') != spec.sha256

  def shutdown_jetson(self, reason: str) -> None:
    """hardwared is shutting the comma down and wants the Jetson off too.
    The request file is ours to remove, whatever happens: hardwared is
    waiting on it and the comma goes down either way."""
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
    """How long to wait before provisioning again, doubling per failure.

    A Jetson that is powered but never answers is the case this exists for:
    at a flat 30 s it would be retried 120 times an hour for as long as the
    car is parked, and every one of those costs a round of USB churn.
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

    # Before the link and before the attach gate: the warp needs neither, and
    # it is the one thing modeld refuses to start the large model without. It
    # used to sit below `if not attached: return`, so a Jetson that was slow to
    # enumerate delayed the compile as well. Cheap now that the build normally
    # got there first, but the ordering still matters on the install that has
    # to fall back.
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
        # A host that has just arrived gets a clean slate rather than sitting
        # out a backoff earned by whatever was on the link before it, and its
        # engine cache is checked before the ready param is trusted again.
        self.failures = 0
        self.next_provision = 0.0
        self.verified = False
      else:
        # It powered down or rebooted. Readiness is about the engine on the
        # Jetson, which survives, so keep it; modeld reconnects on its own.
        self.ready = False
    if not attached:
      return
    # Provisioning backs off on its own timer, so that a long wait for an
    # unresponsive server still leaves us watching for one that reappears.
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
      # Only reopen when the link itself is suspect. Unbinding the gadget
      # makes the host re-enumerate, and doing that every time a server that
      # is simply not up yet fails to answer is hours of USB churn.
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
          # Nothing may escape: this daemon restarting in a loop would be worse
          # than it sitting out a cycle.
          cloudlog.exception("jetlink: unhandled error")
          self.close_link()
          self.next_attempt = time.monotonic() + RECONNECT_BACKOFF
    finally:
      self.close_link()
      self.untune_vm()
    helpers.set_dormant(False)
    if self.warp_thread is not None and self.warp_thread.is_alive():
      cloudlog.warning("jetlink: stopped with the warp still compiling; it will rebuild next time")
    cloudlog.warning("jetlink: stopped")


def main() -> None:
  d = Jetlinkd()
  # manager stops us with SIGTERM at the onroad transition. Closing the link
  # properly on the way out is what keeps the driver healthy for modeld.
  signal.signal(signal.SIGTERM, d.request_stop)
  signal.signal(signal.SIGINT, d.request_stop)
  d.run()


if __name__ == "__main__":
  main()
