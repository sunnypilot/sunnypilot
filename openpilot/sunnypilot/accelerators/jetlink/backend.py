"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

The accelerator backend: everything core openpilot calls, and nothing else.

A module of functions behind sunnypilot.accelerators, the only thing core
openpilot imports. Anything only jetlinkd needs lives in helpers or spec_cache.
The `jetlink` client package can be absent on a device; this module imports
without it, and the functions that need it answer their negative default when
it is not there, logging once.
"""
from __future__ import annotations

import threading
import time

from openpilot.common.swaglog import cloudlog

from openpilot.sunnypilot.accelerators.jetlink import helpers, spec_cache

# how long one attempt holds the gadget open waiting for a host. Not a deadline
# on the large model: JoiningModelState retries for the drive, since the Jetson
# boots after the comma is already onroad
CONNECT_TIMEOUT = 45.0
CONNECT_DELAY = 0.5
# ten frame periods; a dead server must not hold the frame thread for seconds
INFERENCE_TIMEOUT = 0.5
# how long the load may wait for the early gadget bind; jetlinkd may still be
# letting go of the endpoints
PRESENT_TIMEOUT = 5.0

# how long hardwared waits for jetlinkd to shut the Jetson down. Wake from
# suspend is ~8 s to a server
SHUTDOWN_TIMEOUT = 25.0

_missing_reported = False


def _package_missing(what: str) -> bool:
  """True, and logged once, if the jetlink client package cannot be imported."""
  global _missing_reported
  try:
    import jetlink.client  # noqa: F401
  except ImportError:
    if not _missing_reported:
      cloudlog.warning("jetlink: package not installed, %s unavailable", what)
      _missing_reported = True
    return True
  return False


def _wait_for_host(deadline: float) -> bool:
  reported = False
  while time.monotonic() < deadline:
    if helpers.host_attached():
      return True
    if not reported:
      cloudlog.warning("jetlink: gadget up, waiting for the jetson to enumerate")
      reported = True
    time.sleep(CONNECT_DELAY)
  return False


def _present_early(ready: dict) -> None:
  """Open and bind the gadget now, from a thread that is not modeld's.

  modeld's main thread is already SCHED_FIFO 54 on core 7, and the FunctionFS
  reader the open creates would inherit that and preempt the frame loop (see
  joining._background_priority). Bounded, so a hung open cannot hold modeld's
  load; a helper that finishes late closes what it opened.
  """
  from openpilot.sunnypilot.accelerators.jetlink.joining import _background_priority
  lock = threading.Lock()

  deadline = time.monotonic() + PRESENT_TIMEOUT

  def present():
    _background_priority()
    # retried: manager has just stopped jetlinkd, which may not have let go of
    # ep0 yet, and a single try fails in milliseconds
    client = None
    while client is None:
      try:
        client = helpers.connect()
      except Exception as e:
        if time.monotonic() >= deadline:
          cloudlog.warning("jetlink: could not present the gadget early (%s), the join will", e)
          return
        time.sleep(0.2)
    with lock:
      if ready.get('abandoned'):
        client.close()
      else:
        ready['client'] = client

  t = threading.Thread(target=present, name='jetlink-present', daemon=True)
  t.start()
  t.join(max(0.0, deadline - time.monotonic()) + 0.5)
  with lock:
    if t.is_alive():
      ready['abandoned'] = True
      cloudlog.warning("jetlink: presenting the gadget took over %.0f s, the join will", PRESENT_TIMEOUT)


def _connect_patiently(client=None):
  """Open the link, tolerating a busy gadget or a Jetson that is still booting.

  A `client` already holding the gadget (presented early) skips the open."""
  deadline = time.monotonic() + CONNECT_TIMEOUT
  last = None
  while True:
    if client is None:
      try:
        client = helpers.connect()
      except Exception as e:
        client, last = None, e
    if client is not None:
      if helpers.host_attached():
        return client
      # the gadget is held now, so the Jetson sees it the moment it is up;
      # keep it open rather than churning the endpoints
      if _wait_for_host(deadline):
        return client
      client.close()
      raise TimeoutError(f"no jetson attached within {CONNECT_TIMEOUT:.0f}s")
    if time.monotonic() > deadline:
      raise last if last is not None else TimeoutError("could not open the link")
    cloudlog.warning("jetlink: link not ready (%s), retrying", last)
    time.sleep(CONNECT_DELAY)


def enabled() -> bool:
  return helpers.enabled()


def present() -> bool:
  return helpers.gadget_present()


def ready() -> bool:
  # params only, no link IO: jetlinkd has already recorded the answer
  if not helpers.enabled() or helpers.gadget_error() is not None:
    return False
  spec = spec_cache.load()
  selected = helpers.selected_model()
  return (spec is not None and selected is not None and spec.sha256 == selected['oid']
          and helpers.engine_ready_for(spec.sha256))


def unavailable_reason() -> str | None:
  return helpers.gadget_alert()


def prepare() -> bool:
  # the link is not worth waiting for: make_model_state joins in the background.
  # The warp is: scons builds it before manager starts, so one missing now stays
  # missing for the drive, and saying no keeps modeld on the plain small model
  if _package_missing('the large model'):
    return False
  from openpilot.sunnypilot.accelerators.jetlink import warp_cache
  if not warp_cache.is_cached(*warp_cache.device_geometry()):
    cloudlog.warning("jetlink: no warp compiled yet, staying on the small model")
    return False
  # the last hook before modeld goes SCHED_FIFO on core 7, and the GPU's init
  # spawns a thread that would inherit that. See warp_cache.init_device
  warp_cache.init_device()
  return True


def make_model_state(cam_w: int, cam_h: int, small=None):
  # returns straight away with the small model driving; see joining.py
  if _package_missing('the large model'):
    return None
  from openpilot.sunnypilot.accelerators.jetlink.joining import JoiningModelState
  from openpilot.sunnypilot.accelerators.jetlink import warp_cache

  # the warp is loaded and warmed here, before the frame loop exists, rather
  # than at the swap on a driving frame. Sized from the cached spec, which is
  # what the link will hand back; another geometry is rejected
  ready: dict = {}

  def prepare():
    from openpilot.sunnypilot.accelerators.jetlink.fallback import prepare_reset
    # the gadget first, so the Jetson enumerates while the warp loads. Left to
    # the join thread the bind landed ~3 s later, behind the small model's
    # first frame, and one ignition had a 655 ms frame during the bind
    _present_early(ready)
    cached = spec_cache.load()
    if cached is not None:
      img_h, img_w = cached.input_shapes['img'][2:]
      geometry = (img_w * 2, img_h * 2)
    else:
      geometry = warp_cache.device_geometry()[2:]
    try:
      ready['reset_small'] = prepare_reset(small)
      warp = warp_cache.load_warp(cam_w, cam_h, *geometry)
      warp_cache.warm(warp, cam_w, cam_h)
    except Exception:
      client = ready.pop('client', None)
      if client is not None:
        client.close()
      raise
    ready.update(warp=warp, geometry=geometry)

  def build(client, spec):
    from openpilot.sunnypilot.accelerators.jetlink.model_state import JetlinkModelState
    img_h, img_w = spec.input_shapes['img'][2:]
    warp = ready.get('warp') if ready.get('geometry') == (img_w * 2, img_h * 2) else None
    if warp is None:
      raise RuntimeError('no prepared warp for the server model geometry')
    return JetlinkModelState(cam_w, cam_h, client, spec, small, warp=warp)

  def connect():
    # the early client is good for one attempt; after that the join thread
    # opens its own
    return _open_link(ready.pop('client', None))

  return JoiningModelState(cam_w, cam_h, small, connect, build, prepare,
                           reset_small=lambda: ready['reset_small']())


def _open_link(client=None):
  """Get a client and a spec. Link IO only, so it is safe off modeld's thread;
  everything that touches tinygrad stays in `build`."""
  from jetlink.client import EngineMissing

  cached = spec_cache.load()
  if cached is None:
    if client is not None:
      client.close()
    raise RuntimeError("no cached jetlink model spec; jetlinkd has not provisioned")

  selected = helpers.selected_model()
  if selected is None or selected['oid'] != cached.sha256:
    if client is not None:
      client.close()
    raise RuntimeError('selected jetlink model has not been provisioned')

  # the endpoints may still be held by jetlinkd, and the Jetson may still be
  # booting; both resolve on their own
  client = _connect_patiently(client)
  try:
    hello = client.hello(timeout=10.0)
    cloudlog.warning("jetlink: %s trt %s, engine %s, loaded %s",
                     hello.get('device'), hello.get('trt_version'),
                     hello.get('engine_state'), str(hello.get('loaded'))[:16])
    # normally one round trip, since jetlinkd left the engine loaded. If the
    # server restarted it is a load from the plan cache, 13 to 25 s
    try:
      spec = client.ensure_engine(cached.sha256, cached.nbytes, frame_skip=cached.frame_skip,
                                  build_timeout=120.0)
    except EngineMissing:
      # the Jetson's cache was pruned or re-flashed since jetlinkd recorded it
      # ready. Clear the record so the next parked period provisions again
      helpers.set_engine_ready(None)
      raise
    client.deadline = INFERENCE_TIMEOUT
    return client, spec
  except BaseException:
    client.close()
    raise


def make_status_publisher(pm, model):
  from openpilot.sunnypilot.accelerators.jetlink.status import JetlinkStatus
  # the model, not its client: the link arrives after this is built and may
  # come and go mid-drive. Reading model.client per send follows it
  return JetlinkStatus(pm, model)


def uses_stock_runner() -> bool:
  # the toggle alone. JetlinkModel defaults through selected_model(), so gating
  # on it left an enabled device on modeld_tinygrad where jetlink never runs.
  # Not presence or readiness: a late boot must not move manager mid-drive
  return helpers.enabled()


def model_choices() -> list[dict]:
  if not helpers.link_configured():
    return []
  selected = helpers.selected_model() or {}
  cached = helpers._get('JetlinkCachedModels') or []
  return [{'name': m['name'], 'selected': m['oid'] == selected.get('oid'),
           'cached': m['oid'] in cached} for m in helpers.model_index()]


def select_model(name: str) -> None:
  from openpilot.common.params import Params
  if name not in {m['name'] for m in helpers.model_index()}:
    raise ValueError(f'unknown jetlink model: {name}')
  Params().put(helpers.P_MODEL, name)
  Params().put_bool(helpers.P_ENABLED, True)
  Params().remove('ModelRunnerTypeCache')


def active_model_name() -> str | None:
  if not ready():
    return None
  return next((m['name'] for m in model_choices() if m['selected']), None)


def shutdown(reason: str, timeout: float = SHUTDOWN_TIMEOUT) -> None:
  """Take the Jetson down with the comma. Runs in hardwared, which cannot
  touch the link: jetlinkd owns the gadget offroad and is the only one that
  can wake a sleeping Jetson. Hand the request over and wait; the wake and one
  round trip take ~10 s, and manager will not kill jetlinkd until this returns.

  Skipped when no Jetson is known to be there (dormant counts as there). A
  jetlinkd busy in a long provision will not see the request; the timeout
  covers that.
  """
  if not helpers.enabled() or not helpers.gadget_present():
    return
  cloudlog.warning("jetlink: asking the jetson to power off: %s", reason)
  if not helpers.request_shutdown(reason):
    return
  if helpers.await_shutdown(timeout):
    cloudlog.warning("jetlink: shutdown request handed to the jetson")
  else:
    cloudlog.warning("jetlink: nobody took the shutdown request within %.0f s", timeout)
