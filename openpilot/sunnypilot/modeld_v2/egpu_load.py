"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

tinygrad guards the AMD-over-USB device with a non-blocking flock on /tmp/am_usb:<bus>-<port>.lock;
a holder that has not exited yet (e.g. a previous modeld) fails the load instantly, so retry.
"""
import time

from openpilot.common.swaglog import cloudlog

EGPU_LOAD_ATTEMPTS = 5
EGPU_LOCK_RETRY_WAIT = 3.0  # [s] between attempts
EGPU_LOAD_TIMEOUT = 60  # [s] on top of the worst-case retry wait
EGPU_LOAD_TIMEOUT_TOTAL = EGPU_LOAD_TIMEOUT + (EGPU_LOAD_ATTEMPTS - 1) * EGPU_LOCK_RETRY_WAIT


def is_lock_contention(e: BaseException) -> bool:
  # the real error is nested inside an ExceptionGroup, so match on the rendered text
  return "Failed to acquire lock file" in repr(e)


def load_with_retry(make_model, attempts: int = EGPU_LOAD_ATTEMPTS, wait: float = EGPU_LOCK_RETRY_WAIT):
  """Call make_model, retrying only on am_usb lock contention. Returns (model, error)."""
  last: Exception | None = None
  for attempt in range(1, attempts + 1):
    try:
      return make_model(), None
    except Exception as e:  # an unhandled exception in the load thread would die silently
      last = e
      if not is_lock_contention(e) or attempt == attempts:
        break
      cloudlog.warning(f"eGPU lock held (attempt {attempt}/{attempts}), retrying in {wait}s")
      time.sleep(wait)
  return None, last
