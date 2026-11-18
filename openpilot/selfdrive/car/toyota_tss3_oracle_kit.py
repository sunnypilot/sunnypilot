from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_ORACLE_TOOL = Path(__file__).resolve().with_name("toyota_tss3_oracle") / "tss3-request-signer"


def oracle_kit_compatibility(tool_path: Path) -> tuple[bool, str]:
  """The kit is a per-vehicle signed bundle, so accept any structurally valid
  kit; the vehicle it targets is the operator's choice, not a fixed platform."""
  if not tool_path.is_file() or not os.access(tool_path, os.X_OK):
    return False, f"oracle tool unavailable: {tool_path}"

  meta_path = tool_path.parent / "bundle" / "request_signer.json"
  try:
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    target = meta["target"]["name"]
  except (OSError, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError):
    return False, f"oracle kit metadata invalid: {meta_path}"

  if not isinstance(target, str) or not target:
    return False, f"oracle kit metadata invalid: {meta_path}"
  return True, ""
