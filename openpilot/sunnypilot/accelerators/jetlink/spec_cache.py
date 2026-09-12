"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

The selected model's spec, cached in a param.

Reading the shapes and output slices means parsing a 766 MB ONNX. jetlinkd does
that once when it provisions; modeld reads the answer here and never touches
the file. `source` records the file the spec came from so jetlinkd can tell
nothing changed without hashing it again.
"""
from __future__ import annotations

from pathlib import Path

from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog

from openpilot.sunnypilot.accelerators.jetlink import helpers

PARAM = "JetlinkSpec"


def _raw() -> dict | None:
  # _get tolerates a params library older than these keys
  value = helpers._get(PARAM)
  return value if isinstance(value, dict) else None


def load():
  """The cached ModelSpec, or None if there is not a usable one."""
  from jetlink.spec import ModelSpec
  try:
    d = _raw()
    return ModelSpec.from_dict(d) if d else None
  except Exception:
    cloudlog.exception("jetlink: cached spec is unreadable")
    return None


def store(spec, source: Path | None = None) -> None:
  payload = spec.to_dict()
  if source is not None:
    st = source.stat()
    payload['source'] = [str(source), st.st_mtime_ns, st.st_size]
  Params().put(PARAM, payload)


def source() -> tuple[str, int, int] | None:
  """(path, mtime_ns, size) of the model the cached spec was built from."""
  try:
    d = _raw()
    src = d.get('source') if d else None
    return (str(src[0]), int(src[1]), int(src[2])) if src else None
  except Exception:
    return None
