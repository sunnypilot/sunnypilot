#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Reads settings_ui_src/ (the dev-friendly authoring tree) and emits the
canonical settings_ui.json that the device generator + frontend consume.

Source layout:
  _macros.yaml                                # named rule fragments
  pages/<page_id>.yaml                        # one file per panel/page
  pages/vehicle.yaml                          # special: emits vehicle_settings

Each page.yaml contains the full panel: metadata + sections + items + sub_panels
inline. Sub-panels are nested inside the section they belong to. Items appear
in the order written in the file.

Macro references use JSON-Schema-style $ref pointers:
  enablement:
    - {$ref: "#/macros/offroad"}
    - {$ref: "#/macros/mads_full_platforms"}

Macros may reference other macros (max depth 3). Cycles raise an error.

Usage:
  python compile_settings_ui.py [--src DIR] [--out PATH] [--check]
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys

import yaml

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SRC = os.path.join(DIR, "settings_ui_src")
DEFAULT_OUT = os.path.join(DIR, "settings_ui.json")

SCHEMA_VERSION = "1.0"
MAX_MACRO_DEPTH = 3


class CompileError(Exception):
  pass


def _load_yaml(path: str):
  with open(path) as f:
    return yaml.safe_load(f) or {}


def _is_ref(node) -> bool:
  return isinstance(node, dict) and len(node) == 1 and "$ref" in node


def _ref_name(node: dict) -> str:
  ref = node["$ref"]
  if not isinstance(ref, str) or not ref.startswith("#/macros/"):
    raise CompileError(f"unsupported $ref: {ref!r} (must start with '#/macros/')")
  return ref[len("#/macros/"):]


def _resolve_refs(node, macros: dict, visiting: tuple[str, ...] = ()):
  """Resolve $ref nodes against macros. Recursive; depth-limited; cycle-safe.

  - $ref in list-context: macro's list spliced into parent list.
  - $ref in scalar-context (object value): macro's value substitutes.
  - Non-list macro values may not be referenced from list contexts.
  """
  if _is_ref(node):
    name = _ref_name(node)
    if name in visiting:
      raise CompileError(f"$ref cycle: {' -> '.join(visiting + (name,))}")
    if len(visiting) >= MAX_MACRO_DEPTH:
      raise CompileError(f"$ref nesting exceeds depth {MAX_MACRO_DEPTH}: {' -> '.join(visiting + (name,))}")
    if name not in macros:
      raise CompileError(f"unknown macro: {name}")
    return _resolve_refs(copy.deepcopy(macros[name]), macros, visiting + (name,))

  if isinstance(node, dict):
    return {k: _resolve_refs(v, macros, visiting) for k, v in node.items()}

  if isinstance(node, list):
    out = []
    for item in node:
      if _is_ref(item):
        resolved = _resolve_refs(item, macros, visiting)
        if not isinstance(resolved, list):
          raise CompileError(
            f"macro '{_ref_name(item)}' must resolve to a list when used in a list context"
          )
        out.extend(resolved)
      else:
        out.append(_resolve_refs(item, macros, visiting))
    return out

  return node


# Output JSON key order. Mirrors the conventions in the original hand-written
# settings_ui.json so structural diffs after extraction are minimal.
_ITEM_KEY_ORDER = [
  "key",
  "widget",
  "needs_onroad_cycle",
  "requires_attestation",
  "blocked",
  "title",
  "description",
  "details",
  "title_param_suffix",
  "min",
  "max",
  "step",
  "unit",
  "options",
  "visibility",
  "enablement",
  "sub_items",
]


def _canon_item(item: dict, macros: dict) -> dict:
  resolved = dict(item)
  for ctx in ("visibility", "enablement"):
    if ctx in resolved:
      resolved[ctx] = _resolve_refs(resolved[ctx], macros)
  if "options" in resolved:
    new_opts = []
    for opt in resolved["options"]:
      if isinstance(opt, dict):
        opt = dict(opt)
        for ctx in ("visibility", "enablement"):
          if ctx in opt:
            opt[ctx] = _resolve_refs(opt[ctx], macros)
      new_opts.append(opt)
    resolved["options"] = new_opts
  if "sub_items" in resolved:
    resolved["sub_items"] = [_canon_item(s, macros) for s in resolved["sub_items"]]

  out: dict = {}
  for k in _ITEM_KEY_ORDER:
    if k in resolved:
      out[k] = resolved[k]
  for k, v in resolved.items():
    if k not in out:
      out[k] = v
  return out


def _canon_section(section: dict, macros: dict) -> dict:
  out: dict = {"id": section["id"], "title": section["title"]}
  if "description" in section:
    out["description"] = section["description"]
  for k in ("visibility", "enablement"):
    if k in section:
      out[k] = _resolve_refs(section[k], macros)
  if "attestation_required" in section:
    out["attestation_required"] = section["attestation_required"]
  out["items"] = [_canon_item(i, macros) for i in section.get("items", [])]
  if "sub_panels" in section and section["sub_panels"]:
    out["sub_panels"] = [_canon_sub_panel(sp, macros) for sp in section["sub_panels"]]
  for k, v in section.items():
    if k not in out and k != "order":
      out[k] = v
  return out


def _canon_sub_panel(sp: dict, macros: dict) -> dict:
  out: dict = {"id": sp["id"], "label": sp["label"], "trigger_key": sp["trigger_key"]}
  if "trigger_condition" in sp:
    out["trigger_condition"] = _resolve_refs(sp["trigger_condition"], macros)
  out["items"] = [_canon_item(i, macros) for i in sp.get("items", [])]
  for k, v in sp.items():
    if k not in out:
      out[k] = v
  return out


def _canon_panel(page: dict, macros: dict) -> dict:
  out: dict = {
    "id": page["id"],
    "label": page["label"],
    "icon": page["icon"],
    "order": page["order"],
  }
  if "remote_configurable" in page:
    out["remote_configurable"] = page["remote_configurable"]
  if "description" in page:
    out["description"] = page["description"]
  if "sections" in page and page["sections"]:
    out["sections"] = [_canon_section(s, macros) for s in page["sections"]]
  if "items" in page and page["items"]:
    out["items"] = [_canon_item(i, macros) for i in page["items"]]
  if "sub_panels" in page and page["sub_panels"]:
    out["sub_panels"] = [_canon_sub_panel(sp, macros) for sp in page["sub_panels"]]
  return out


def _canon_vehicle(page: dict, macros: dict) -> dict:
  """Convert page-shape vehicle.yaml to wire-format vehicle_settings dict."""
  out: dict = {}
  for sec in page.get("sections", []):
    brand = sec["id"]
    brand_out: dict = {"title": sec.get("title", "")}
    if "description" in sec:
      brand_out["description"] = sec["description"]
    brand_out["items"] = [_canon_item(i, macros) for i in sec.get("items", [])]
    out[brand] = brand_out
  return out


def _load_pages(src: str) -> list[dict]:
  pages_dir = os.path.join(src, "pages")
  if not os.path.isdir(pages_dir):
    return []
  pages = []
  for fn in sorted(os.listdir(pages_dir)):
    if not fn.endswith((".yaml", ".yml")):
      continue
    if fn.startswith("_"):
      continue
    path = os.path.join(pages_dir, fn)
    page = _load_yaml(path)
    if not isinstance(page, dict):
      raise CompileError(f"{path}: page YAML must be an object")
    if "id" not in page:
      raise CompileError(f"{path}: page missing 'id'")
    page["__source"] = path
    pages.append(page)
  return pages


def compile_schema(src: str) -> dict:
  macros_doc = _load_yaml(os.path.join(src, "_macros.yaml"))
  macros = (macros_doc.get("macros") or {}) if isinstance(macros_doc, dict) else {}

  pages = _load_pages(src)

  panels_out = []
  vehicle_out: dict = {}

  # Order panels by `order` field (falling back to file position).
  panel_pages = [p for p in pages if p.get("kind") != "vehicle"]
  panel_pages.sort(key=lambda p: (p.get("order", 999), p["id"]))

  for page in panel_pages:
    panels_out.append(_canon_panel(page, macros))

  for page in pages:
    if page.get("kind") == "vehicle":
      vehicle_out = _canon_vehicle(page, macros)

  return {
    "$schema": "./settings_ui.schema.json",
    "schema_version": SCHEMA_VERSION,
    "panels": panels_out,
    "vehicle_settings": vehicle_out,
  }


def _main() -> int:
  parser = argparse.ArgumentParser(description="Compile settings_ui_src/ -> settings_ui.json")
  parser.add_argument("--src", default=DEFAULT_SRC)
  parser.add_argument("--out", default=DEFAULT_OUT)
  parser.add_argument("--check", action="store_true",
                      help="Compile and diff against existing settings_ui.json; exit non-zero on diff.")
  args = parser.parse_args()

  schema = compile_schema(args.src)
  rendered = json.dumps(schema, indent=2) + "\n"

  if args.check:
    if not os.path.exists(args.out):
      print(f"--check: {args.out} does not exist", file=sys.stderr)
      return 1
    with open(args.out) as f:
      current = f.read()
    if current.strip() == rendered.strip():
      print(f"--check: {args.out} matches compiled output")
      return 0
    print(f"--check: {args.out} differs from compiled output", file=sys.stderr)
    cur_obj = json.loads(current)
    if cur_obj == schema:
      print("(structurally equal; only formatting differs)", file=sys.stderr)
    return 1

  with open(args.out, "w") as f:
    f.write(rendered)
  print(f"Wrote {args.out}")
  return 0


if __name__ == "__main__":
  sys.exit(_main())
