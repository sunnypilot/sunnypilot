"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

A ModelState that starts as the small model and upgrades to the Jetson.

modeld's large-model load is a one-shot with BIG_MODEL_TIMEOUT and a silent,
one-way fallback. That suits a chestnut, powered from the comma. A Jetson is
on the ignition rail: cranking browns it out, so its boot starts about when
the comma goes onroad and takes 45 to 100 s, long after modeld gave up.

So modeld is handed the small model it already loaded, and the Jetson is
swapped in underneath once the link, the engine and the warp are all there.
modeld re-reads `model` every frame, and `modelV2.big` keeps its meaning.

Two rules the swap keeps:

- tinygrad work happens on modeld's thread. The joining thread does link IO
  only; building the JetlinkModelState unpickles a TinyJit, and doing that
  next to the small model running frames on the same device is not safe.
- never swap while the plan is steering. The two models disagree by ~195 m of
  planned path, and the swap costs a frame or two. Require fresh, fully
  disengaged controls; standstill alone is not enough, longitudinal control
  may still hold the brake.
"""
from __future__ import annotations

import os
import threading
import time

import openpilot.cereal.messaging as messaging
from openpilot.sunnypilot import accelerators
from openpilot.common.realtime import drop_realtime, set_core_affinity
from openpilot.common.swaglog import cloudlog

# after a join fails or the large model dies mid-drive. Long enough not to
# thrash a booting Jetson, short enough to catch one that finished a moment later
REJOIN_DELAY = 5.0
# doubled per consecutive failure, reset by a join that lasted STABLE_SECONDS.
# A link that dies on its first frame every time must not cost a swap, a
# demote and an alert every few seconds
REJOIN_DELAY_MAX = 60.0
STABLE_SECONDS = 60.0
ENGAGEMENT_POLL_MS = 100
ENGAGEMENT_MAX_AGE = 0.25
# how often a link that is ready but has nowhere to land gets checked, and
# how long the check may take; both off the frame loop
KEEPALIVE_PERIOD = 10.0
PING_TIMEOUT = 2.0


def _background_priority() -> None:
  """Get this thread off modeld's realtime core before it does anything.

  A thread started after config_realtime_process(7, 54) inherits SCHED_FIFO
  and the single-core affinity, and an equal-priority thread that wakes takes
  the core until it blocks. Measured with these threads left as created: exec
  p95 90.8 ms, max 159.9, 5% frame drops, enough for modeldLagging.
  """
  drop_realtime()
  try:
    online = os.sched_getaffinity(0)
    everything = set(range(os.cpu_count() or 1))
    if everything - online:
      set_core_affinity(sorted(everything))
  except (OSError, AttributeError):
    # PC, or a kernel that will not widen the mask; SCHED_OTHER is the part
    # that matters
    pass


class JoiningModelState:
  """Duck-types selfdrive.modeld.modeld.ModelState, with a second one inside."""

  def __init__(self, cam_w: int, cam_h: int, small, connect, build, prepare=None, reset_small=None):
    self._small = small
    self._active = small
    self._cam = (cam_w, cam_h)
    self._connect = connect
    self._build = build
    self._reset_small = reset_small

    # whatever the swap would otherwise do on the frame loop, done now on
    # modeld's main thread before the frame loop exists; at the swap it cost
    # a 1.5 s frame
    if prepare is not None:
      try:
        t0 = time.monotonic()
        prepare()
        cloudlog.warning("jetlink: prepared the large model ahead of the swap in %.2f s", time.monotonic() - t0)
      except Exception:
        cloudlog.exception("jetlink: could not prepare the large model ahead of the swap")
        raise

    # handed over by the joining thread, consumed by the first frame that finds
    # it safe to swap. Only ever assigned under the lock
    self._joined: tuple[object, object] | None = None
    # kept true during a keepalive ping, which temporarily takes _joined
    self._available = False
    self._retired = None
    self._lock = threading.Lock()
    self._rejoin = threading.Event()
    self._rejoin.set()
    # earliest the join loop may try again. Without a backoff a fault that
    # recurs on the first frame after every swap is a connect, build and demote
    # every 700 ms for the drive, each costing modeld a 100 ms frame
    self._rejoin_at = 0.0
    self._failures = 0
    self._joined_at = 0.0

    # assume engaged and moving until a message says otherwise, so a swap can
    # never happen on no information
    self._engaged = True
    self._standstill = False
    self._engagement_updated = 0.0
    self._stop = threading.Event()

    # whether the large model has produced a frame; a first inference that
    # fails never announces readiness. Travels in modelV2.big and
    # modelDataV2SP, not a param: a chestnut's load is over once, this never is
    self._loading = True

    self._threads = [threading.Thread(target=self._join_loop, daemon=True),
                     threading.Thread(target=self._watch_engagement, daemon=True)]
    for t in self._threads:
      t.start()

  # -- what modeld reads ------------------------------------------------------

  @property
  def big_model_available(self) -> bool:
    """Connected and waiting to switch; published with each small-model frame."""
    return not self._stop.is_set() and self._available and self._active is self._small

  @property
  def chestnut(self) -> bool:
    # modelV2.big. False while proxying, as the small model would report
    return getattr(self._active, 'chestnut', False)

  @property
  def loading(self) -> bool:
    """Still bringing the accelerator up: the small model is driving."""
    return self._active is self._small

  @property
  def big_model_state(self) -> str:
    """modelDataV2SP.acceleratorState, one of its enum names."""
    if self._stop.is_set():
      return 'unavailable'
    if self._active is not self._small:
      return 'running'
    return 'retrying' if self._failures else 'joining'

  @property
  def vision_input_names(self):
    return self._active.vision_input_names

  @property
  def client(self):
    # read by the status publisher on every send, so the telemetry follows the link
    return getattr(self._active, 'client', None)

  @property
  def lat_delay(self):
    return self._active.lat_delay

  @lat_delay.setter
  def lat_delay(self, value):
    # modeld writes this every frame. Set on both, so a model that joins
    # mid-drive does not start on a stale delay
    self._small.lat_delay = value
    if self._active is not self._small:
      self._active.lat_delay = value

  # -- the frame path ---------------------------------------------------------

  def run(self, bufs, transforms, inputs, after_enqueue=None):
    self._maybe_swap()
    active = self._active
    try:
      result = active.run(bufs, transforms, inputs, after_enqueue)
    except Exception:
      if active is self._small:
        # nothing to do with the link; modeld's own handler owns this
        raise
      cloudlog.exception("jetlink: large model failed mid-drive, back to the small model")
      self._demote()
      if self._reset_small is not None:
        self._reset_small()
      # re-run the frame rather than propagate: modeld's fallback is permanent,
      # this one is retryable. after_enqueue is dropped, the large model may
      # already have called it
      return self._small.run(bufs, transforms, inputs, None)
    if active is not self._small and self._loading:
      # a connected engine can still fail its first inference; only announce
      # readiness after a frame the caller can publish
      self._joined_at = time.monotonic()
      self._loading = False
      accelerators.clear_progress()
      cloudlog.warning("jetlink: large model joined mid-drive, modelV2.big is now true")
    return result

  def warmup(self) -> None:
    """Nothing to do, and it still has to exist.

    The warp is warmed by `prepare` in __init__ and the first real frame
    carries the reset. modeld does not call this on the jetlink path, but a
    caller that duck-types it must not take an AttributeError, which modeld
    reads as "big model load failed".
    """

  @property
  def _window_open(self) -> bool:
    # standstill does not make an active longitudinal controller safe to swap
    fresh = 0 <= time.monotonic() - self._engagement_updated < ENGAGEMENT_MAX_AGE
    return fresh and not self._engaged

  def _maybe_swap(self) -> None:
    if self._joined is None or not self._window_open:
      return
    with self._lock:
      joined, self._joined = self._joined, None
      if joined is not None:
        self._available = False
    if joined is None:
      return
    client, spec = joined
    try:
      # everything tinygrad touches happens here, on modeld's thread. No
      # warmup: the first real frame carries the reset (~30 ms on the server),
      # where a warmup frame over the link was two more dropped frames
      t0 = time.monotonic()
      big = self._build(client, spec)
      big.lat_delay = self._small.lat_delay
      cloudlog.warning("jetlink: built the large model state in %.0f ms", (time.monotonic() - t0) * 1000)
    except Exception:
      cloudlog.exception("jetlink: could not bring up the large model, staying small")
      with self._lock:
        self._retired = client
      # backed off like a demote, or a build that fails the same way every
      # time is a connect and a build per second for the drive
      self._back_off()
      return
    self._active = big

  def _demote(self) -> None:
    big, self._active = self._active, self._small
    self._loading = True
    self._report('connect', 'lost the jetson, reconnecting')
    with self._lock:
      self._retired = big
    self._back_off()

  def _close_retired(self) -> None:
    with self._lock:
      retired, self._retired = self._retired, None
    if retired is not None:
      try:
        retired.close()
      except Exception:
        cloudlog.exception('jetlink: closing the retired link')

  def _back_off(self) -> None:
    """Push the next attempt out, further each time one fails on its heels.

    Each failed cycle is a swap frame, a demote frame, a soft disable and a
    "Big Model Ready" chime. A join that held for STABLE_SECONDS starts from
    the bottom again.
    """
    stable = self._joined_at and time.monotonic() - self._joined_at > STABLE_SECONDS
    self._failures = 1 if stable else self._failures + 1
    self._joined_at = 0.0
    delay = min(REJOIN_DELAY * 2 ** (self._failures - 1), REJOIN_DELAY_MAX)
    self._rejoin_at = time.monotonic() + delay
    self._rejoin.set()
    cloudlog.warning("jetlink: next attempt in %.0f s (failure %d)", delay, self._failures)

  # -- background -------------------------------------------------------------

  def _report(self, stage: str, msg: str) -> None:
    """Tell the UI what the join is waiting on.

    Offroad the param carries jetlinkd's provisioning; without this, a Jetson
    that is not plugged in looked like one six seconds from loading. No
    fraction to give, and the panel does not invent one.
    """
    accelerators.report_progress(stage, 0.0, msg)

  def _join_loop(self) -> None:
    """Open the link and get the engine ready. No tinygrad in here."""
    _background_priority()
    while not self._stop.is_set():
      # no timeout: once joined there is nothing to poll for, and close() sets
      # this. An idle wake per second is not free on modeld's core
      self._rejoin.wait()
      # unbind and reader joins can block; only this thread does teardown,
      # and it finishes before opening another link
      self._close_retired()
      if self._stop.is_set():
        return
      self._rejoin.clear()
      if self._stop.wait(max(0.0, self._rejoin_at - time.monotonic())):
        return
      self._report('connect', 'waiting for the jetson')
      try:
        client, spec = self._connect()
      except Exception as e:
        # expected while the Jetson boots. Not exception(): a stack trace every
        # 5 s for the first minute of every drive is noise
        cloudlog.warning("jetlink: not joined yet (%s), retrying in %.0fs", e, REJOIN_DELAY)
        if self._stop.wait(REJOIN_DELAY):
          return
        self._rejoin.set()
        continue
      with self._lock:
        if self._stop.is_set():
          client.close()
          return
        self._available = True
        self._joined = (client, spec)
      cloudlog.warning("jetlink: link ready, waiting for a window to swap")
      self._report('connect', 'ready; disengage to switch models')
      self._keep_alive()

  def _keep_alive(self) -> None:
    """Ping a link that is waiting for a swap window.

    On a drive with no stop and no disengage that is the whole drive, and a
    Jetson that reboots in there would otherwise be found at the swap: a build
    on a dead link, a demote and the backoff, all on modeld's thread.

    The client is taken out of _joined for the ping and put back after, so the
    frame loop sees a whole one or none, and never waits on the lock.
    """
    while not self._stop.is_set():
      if self._rejoin.wait(KEEPALIVE_PERIOD):
        return
      with self._lock:
        joined, self._joined = self._joined, None
      if joined is None:
        return  # swapped in on a frame, or closed under us
      try:
        joined[0].ping(timeout=PING_TIMEOUT)
      except Exception as e:
        self._available = False
        cloudlog.warning("jetlink: the link died before it could be used (%s), reopening", e)
        try:
          joined[0].close()
        except Exception:
          pass
        self._rejoin_at = time.monotonic() + REJOIN_DELAY
        self._rejoin.set()
        return
      with self._lock:
        if self._stop.is_set():
          # close() ran during the ping and found nothing to close
          joined[0].close()
          return
        self._joined = joined

  def _watch_engagement(self) -> None:
    _background_priority()
    sm = messaging.SubMaster(['selfdriveState', 'carState', 'carControl'])
    while not self._stop.is_set():
      sm.update(ENGAGEMENT_POLL_MS)
      self._update_engagement(sm)

  def _update_engagement(self, sm) -> None:
    # recheck on every poll, including ones with no new messages: that is
    # when alive turns false. The frame thread expires the snapshot too
    valid = all(sm.seen[s] and sm.alive[s] and sm.valid[s] for s in ('selfdriveState', 'carState', 'carControl'))
    # forks can keep lateral control active independently of enabled (MADS)
    self._engaged = not valid or sm['selfdriveState'].enabled or sm['carControl'].latActive or sm['carControl'].longActive
    self._standstill = valid and sm['carState'].standstill
    self._engagement_updated = time.monotonic()

  def close(self) -> None:
    self._stop.set()
    self._available = False
    self._rejoin.set()
    accelerators.clear_progress()
    with self._lock:
      joined, self._joined = self._joined, None
    if joined is not None:
      joined[0].close()
    close = getattr(self._active, 'close', None)
    if close is not None and self._active is not self._small:
      close()
