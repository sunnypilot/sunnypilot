#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Scans all per-page YAML files in settings_ui_src/pages/ and replaces inlined
rule blocks that exactly match a macro definition in _macros.yaml with $ref
references.

Match policy:
  - Whole-list match (exact): replace the entire list with [{$ref}].
  - Single-rule match: any individual rule whose canonical form equals macro[0]
    (when macro is exactly one rule) is replaced with {$ref}.

Re-run is idempotent (already-substituted $refs are skipped).

Usage:
  python apply_macros.py [--src DIR] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import yaml

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SRC = os.path.join(DIR, "settings_ui_src")


class _BlockDumper(yaml.SafeDumper):
  pass


def _represent_dict(dumper, data):
  return dumper.represent_mapping("tag:yaml.org,2002:map", data.items(), flow_style=False)


def _represent_list(dumper, data):
  flow = all(not isinstance(x, (dict, list)) for x in data) and len(data) <= 8
  return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=flow)


_BlockDumper.add_representer(dict, _represent_dict)
_BlockDumper.add_representer(list, _represent_list)


def _dump_yaml(data) -> str:
  return yaml.dump(data, Dumper=_BlockDumper, sort_keys=False, allow_unicode=True, width=120)


def _canon(node) -> str:
  return json.dumps(node, sort_keys=True, separators=(",", ":"))


def _is_ref(node) -> bool:
  return isinstance(node, dict) and len(node) == 1 and "$ref" in node


def _make_ref(name: str) -> dict:
  return {"$ref": f"#/macros/{name}"}


def _substitute_rules(rules: list, whole_list: dict, single_rule: dict) -> list:
  if not isinstance(rules, list) or not rules:
    return rules
  full_canon = _canon(rules)
  if full_canon in whole_list:
    return [_make_ref(whole_list[full_canon])]
  out = []
  for r in rules:
    if _is_ref(r):
      out.append(r)
      continue
    rc = _canon(r)
    if rc in single_rule:
      out.append(_make_ref(single_rule[rc]))
    else:
      out.append(r)
  return out


def _walk_item(item: dict, whole_list: dict, single_rule: dict) -> bool:
  changed = False
  for ctx in ("visibility", "enablement"):
    if ctx in item:
      new = _substitute_rules(item[ctx], whole_list, single_rule)
      if new != item[ctx]:
        item[ctx] = new
        changed = True
  if "options" in item:
    for opt in item["options"]:
      if not isinstance(opt, dict):
        continue
      for ctx in ("visibility", "enablement"):
        if ctx in opt:
          new = _substitute_rules(opt[ctx], whole_list, single_rule)
          if new != opt[ctx]:
            opt[ctx] = new
            changed = True
  if "sub_items" in item:
    for sub in item["sub_items"]:
      if _walk_item(sub, whole_list, single_rule):
        changed = True
  return changed


def _walk_page(page: dict, whole_list: dict, single_rule: dict) -> bool:
  changed = False
  for sec in page.get("sections", []) or []:
    for ctx in ("visibility", "enablement"):
      if ctx in sec:
        new = _substitute_rules(sec[ctx], whole_list, single_rule)
        if new != sec[ctx]:
          sec[ctx] = new
          changed = True
    for it in sec.get("items", []) or []:
      if _walk_item(it, whole_list, single_rule):
        changed = True
    for sp in sec.get("sub_panels", []) or []:
      for it in sp.get("items", []) or []:
        if _walk_item(it, whole_list, single_rule):
          changed = True
  for it in page.get("items", []) or []:
    if _walk_item(it, whole_list, single_rule):
      changed = True
  for sp in page.get("sub_panels", []) or []:
    for it in sp.get("items", []) or []:
      if _walk_item(it, whole_list, single_rule):
        changed = True
  return changed


def _build_macro_indices(macros: dict) -> tuple[dict, dict]:
  whole_list = {}
  single_rule = {}
  for name, body in macros.items():
    if isinstance(body, list):
      whole_list[_canon(body)] = name
      if len(body) == 1 and isinstance(body[0], dict):
        single_rule[_canon(body[0])] = name
    elif isinstance(body, dict):
      single_rule[_canon(body)] = name
  return whole_list, single_rule


def _read_yaml_with_header(path: str) -> tuple[list[str], dict]:
  with open(path) as f:
    text = f.read()
  header_lines = []
  for line in text.splitlines(keepends=True):
    if line.startswith("#"):
      header_lines.append(line)
    elif line.strip() == "":
      header_lines.append(line)
    else:
      break
  doc = yaml.safe_load(text) or {}
  return header_lines, doc


def _write_yaml_with_header(path: str, header: list[str], doc: dict) -> None:
  with open(path, "w") as f:
    if header:
      # Keep at most one trailing blank line in header
      while len(header) > 1 and header[-1].strip() == "" and header[-2].strip() == "":
        header.pop()
      for line in header:
        f.write(line)
    f.write(_dump_yaml(doc))


def apply(src_dir: str, dry_run: bool) -> int:
  with open(os.path.join(src_dir, "_macros.yaml")) as f:
    macros_doc = yaml.safe_load(f) or {}
  macros = (macros_doc.get("macros") or {}) if isinstance(macros_doc, dict) else {}
  whole_list, single_rule = _build_macro_indices(macros)

  changed_files = 0
  pages_dir = os.path.join(src_dir, "pages")
  if os.path.isdir(pages_dir):
    for fn in sorted(os.listdir(pages_dir)):
      if not fn.endswith((".yaml", ".yml")) or fn.startswith("_"):
        continue
      path = os.path.join(pages_dir, fn)
      header, doc = _read_yaml_with_header(path)
      if _walk_page(doc, whole_list, single_rule):
        changed_files += 1
        if not dry_run:
          _write_yaml_with_header(path, header, doc)
        else:
          print(f"would-rewrite: {path}")

  print(f"{'Would rewrite' if dry_run else 'Rewrote'} {changed_files} files")
  return 0


def _main() -> int:
  parser = argparse.ArgumentParser(description="Substitute inlined rule blocks with $ref macros across pages/.")
  parser.add_argument("--src", default=DEFAULT_SRC)
  parser.add_argument("--dry-run", action="store_true")
  args = parser.parse_args()
  return apply(args.src, args.dry_run)


if __name__ == "__main__":
  sys.exit(_main())
