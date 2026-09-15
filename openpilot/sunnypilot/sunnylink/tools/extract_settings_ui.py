#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

One-shot extractor: settings_ui.json -> settings_ui_src/pages/*.yaml.

Reads the existing monolithic settings_ui.json and produces one YAML file per
page (panel) plus pages/vehicle.yaml for the per-brand settings. Macros remain
unwritten by extract; populate _macros.yaml separately.

Usage:
  python extract_settings_ui.py [--src DIR] [--definition PATH]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys

import yaml

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DEFINITION = os.path.join(DIR, "settings_ui.json")
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


# Item field order in per-page YAML (mirrors settings_ui.json conventions).
_ITEM_ORDER = [
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


def _ordered_item(item: dict) -> dict:
  out: dict = {}
  for k in _ITEM_ORDER:
    if k in item:
      v = item[k]
      if k == "sub_items":
        v = [_ordered_item(s) for s in v]
      out[k] = v
  for k, v in item.items():
    if k not in out:
      out[k] = v
  return out


def _ordered_section(section: dict) -> dict:
  out: dict = {"id": section["id"], "title": section["title"]}
  for f in ("description", "order", "visibility", "enablement", "attestation_required"):
    if f in section:
      out[f] = section[f]
  if "items" in section:
    out["items"] = [_ordered_item(i) for i in section["items"]]
  if "sub_panels" in section and section["sub_panels"]:
    out["sub_panels"] = [_ordered_sub_panel(sp) for sp in section["sub_panels"]]
  for k, v in section.items():
    if k not in out:
      out[k] = v
  return out


def _ordered_sub_panel(sp: dict) -> dict:
  out: dict = {"id": sp["id"], "label": sp["label"], "trigger_key": sp["trigger_key"]}
  if "trigger_condition" in sp:
    out["trigger_condition"] = sp["trigger_condition"]
  if "items" in sp:
    out["items"] = [_ordered_item(i) for i in sp["items"]]
  for k, v in sp.items():
    if k not in out:
      out[k] = v
  return out


def _ordered_page(panel: dict) -> dict:
  out: dict = {
    "id": panel["id"],
    "label": panel["label"],
    "icon": panel["icon"],
    "order": panel["order"],
  }
  for f in ("remote_configurable", "description"):
    if f in panel:
      out[f] = panel[f]
  if "sections" in panel and panel["sections"]:
    out["sections"] = [_ordered_section(s) for s in panel["sections"]]
  if "items" in panel and panel["items"]:
    out["items"] = [_ordered_item(i) for i in panel["items"]]
  if "sub_panels" in panel and panel["sub_panels"]:
    out["sub_panels"] = [_ordered_sub_panel(sp) for sp in panel["sub_panels"]]
  for k, v in panel.items():
    if k not in out:
      out[k] = v
  return out


def _ordered_vehicle_page(vehicle_settings: dict) -> dict:
  """Convert wire-format vehicle_settings dict into a page-shape YAML.

  Brand becomes a section id. Each brand's items become section items.
  """
  sections = []
  for brand in sorted(vehicle_settings.keys()):
    bd = vehicle_settings[brand]
    items = bd.get("items", []) if isinstance(bd, dict) else bd
    sec: dict = {
      "id": brand,
      "title": bd.get("title", "") if isinstance(bd, dict) else "",
    }
    if isinstance(bd, dict) and "description" in bd:
      sec["description"] = bd["description"]
    sec["items"] = [_ordered_item(i) for i in items]
    sections.append(sec)
  return {
    "id": "vehicle",
    "label": "Vehicle",
    "icon": "vehicle",
    "order": 99,
    "kind": "vehicle",  # signals to compiler: emit as vehicle_settings, not panels
    "sections": sections,
  }


def extract(definition_path: str, src_dir: str) -> None:
  with open(definition_path) as f:
    data = json.load(f)

  pages_dir = os.path.join(src_dir, "pages")
  if os.path.isdir(pages_dir):
    shutil.rmtree(pages_dir)
  os.makedirs(pages_dir)

  count = 0
  for panel in data.get("panels", []):
    page = _ordered_page(panel)
    path = os.path.join(pages_dir, f"{panel['id']}.yaml")
    with open(path, "w") as f:
      f.write(f"# Page: {panel['id']}\n")
      f.write("# Edit this file. Run compile_settings_ui.py to emit settings_ui.json.\n")
      f.write(_dump_yaml(page))
    count += 1

  vehicle_settings = data.get("vehicle_settings", {})
  if vehicle_settings:
    vehicle_page = _ordered_vehicle_page(vehicle_settings)
    path = os.path.join(pages_dir, "vehicle.yaml")
    with open(path, "w") as f:
      f.write("# Page: vehicle (per-brand settings)\n")
      f.write("# Compiles to settings_ui.json#vehicle_settings (brand = section id).\n")
      f.write(_dump_yaml(vehicle_page))
    count += 1

  # Ensure _macros.yaml exists
  macros_path = os.path.join(src_dir, "_macros.yaml")
  if not os.path.exists(macros_path):
    with open(macros_path, "w") as f:
      f.write("# Named rule fragments. Reference from pages via {$ref: \"#/macros/<name>\"}.\n")
      f.write(_dump_yaml({"macros": {}}))

  print(f"Extracted: {count} pages -> {pages_dir}")


def _main() -> int:
  parser = argparse.ArgumentParser(description="Extract settings_ui.json into per-page YAML files.")
  parser.add_argument("--definition", default=DEFAULT_DEFINITION, help="path to settings_ui.json")
  parser.add_argument("--src", default=DEFAULT_SRC, help="path to settings_ui_src/ output dir")
  args = parser.parse_args()
  extract(args.definition, args.src)
  return 0


if __name__ == "__main__":
  sys.exit(_main())
