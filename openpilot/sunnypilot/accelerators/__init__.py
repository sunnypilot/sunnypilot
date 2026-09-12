"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

An accelerator that runs the large driving model off the comma: jetlink.

comma's chestnut board is not one of these: modeld, hardwared and the UI handle
it natively and only ask here when no board is fitted. Selection is
`if chestnut_present(): native elif accelerators.ready(): jetlink`.

Every function is a thin call into jetlink.backend and is safe on any device:
feature off costs a param read, package absent answers the negative default.
present(), ready(), progress() and uses_stock_runner() are polled by the UI at
5 Hz and must stay cheap.
"""
from __future__ import annotations

import threading
from collections.abc import Callable
from typing import NamedTuple

from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog

from openpilot.sunnypilot.accelerators.jetlink import backend

# written by jetlinkd and the joining state, read by the UI; a param because
# the writer is another process
P_PROGRESS = "AcceleratorProgress"


class Daemon(NamedTuple):
  """An offroad process the accelerator needs.

  A description, not a PythonProcess: manager imports this package, so this
  package cannot import manager. process_config owns the onroad gating.
  """
  name: str
  module: str
  should_run: Callable[..., bool]


def present() -> bool:
  """Is a Jetson attached, or asleep and known to be there? USB-independent."""
  return backend.present()


def ready() -> bool:
  """Can the large model run right now? Params only, what the UI calls 'compiled'."""
  return backend.ready()


def unavailable_reason() -> str | None:
  """Why the link the user asked for cannot run, for the offroad alert. None unless enabled."""
  return backend.unavailable_reason()


def prepare() -> bool:
  """Process-wide setup modeld must do before going realtime, and a last veto. modeld only."""
  return backend.prepare()


def make_model_state(cam_w: int, cam_h: int, small=None):
  """The joining ModelState: the small model driving now, the Jetson swapped in later."""
  return backend.make_model_state(cam_w, cam_h, small)


def make_status_publisher(pm, model):
  """modeld's after_enqueue callback. Publishes nothing; logs telemetry at 1 Hz."""
  return backend.make_status_publisher(pm, model)


def uses_stock_runner() -> bool:
  """Should manager run stock modeld regardless of the stored bundle?

  Configuration only, never link state or ready(): a Jetson that boots late
  must not move manager between modelds mid-drive.
  """
  return backend.uses_stock_runner()


def model_choices() -> list[dict]:
  return backend.model_choices()


def select_model(name: str) -> None:
  backend.select_model(name)


def active_model_name() -> str | None:
  return backend.active_model_name()


def daemons() -> list[Daemon]:
  """Offroad processes for process_config to build."""
  return [Daemon("jetlinkd", "openpilot.sunnypilot.accelerators.jetlink.jetlinkd",
                 lambda started, params, CP: backend.enabled())]


def progress() -> dict | None:
  """{stage, frac, msg} while something provisions, else None.

  Read from the UI's param thread, so nothing may escape, UnknownKeyName included.
  """
  try:
    value = Params().get(P_PROGRESS)
  except Exception:
    return None
  return value if isinstance(value, dict) else None


def report_progress(stage: str, frac: float, msg: str = '') -> None:
  """Never raises: called from except handlers."""
  try:
    Params().put(P_PROGRESS, {'stage': stage, 'frac': round(frac, 4), 'msg': msg})
  except Exception:
    cloudlog.exception("accelerators: could not report progress")


def clear_progress() -> None:
  try:
    Params().remove(P_PROGRESS)
  except Exception:
    cloudlog.exception("accelerators: could not clear progress")


def shutdown(reason: str = '', timeout: float = 25.0) -> None:
  """The device is powering off for good. Tell the Jetson, within `timeout`.

  hardwared calls this before DoShutdown and publishes no deviceState until it
  returns, so the request runs on a thread and is abandoned at the deadline.
  """
  if not backend.enabled():
    return

  def request():
    try:
      backend.shutdown(reason, timeout)
    except Exception:
      cloudlog.exception("accelerators: shutdown request failed")

  t = threading.Thread(target=request, name='accelerator-shutdown', daemon=True)
  t.start()
  t.join(timeout)
  if t.is_alive():
    cloudlog.warning("accelerators: shutdown request still pending after %.0f s, going on without it", timeout)
