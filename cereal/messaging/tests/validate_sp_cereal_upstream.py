#!/usr/bin/env python3
"""Validate sunnypilot routes are parseable by stock commaai/openpilot.

Cap'n Proto is wire-compatible across renames, type relocations, and
additive fields. The only breaking change is a union variant that
upstream doesn't recognize — an unknown discriminant makes the entire
union unreadable.

This script checks: for every struct with a union that exists in both
schemas, does sunnypilot introduce union variants upstream doesn't have?
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

NO_DISCRIMINANT = 0xFFFF


def hex_id(value: int) -> str:
  return f"0x{value:016x}"


def encode_struct(schema: Any) -> dict:
  node = schema.node
  fields = []
  for name, field in schema.fields.items():
    proto = field.proto
    ordinal = proto.ordinal.explicit if proto.ordinal.which() == "explicit" else None
    discriminant = proto.discriminantValue if proto.discriminantValue != NO_DISCRIMINANT else None
    fields.append({"name": name, "ordinal": ordinal, "discriminant": discriminant})
  return {
    "typeId": hex_id(node.id),
    "displayName": node.displayName,
    "hasUnion": node.struct.discriminantCount > 0,
    "fields": fields,
  }


def _child_struct_schema(field: Any) -> Any:
  proto = field.proto
  if proto.which() == "group":
    return field.schema
  type_node = proto.slot.type
  which = type_node.which()
  if which == "struct":
    return field.schema
  if which == "list":
    container = field.schema
    element_type = type_node.list.elementType
    while element_type.which() == "list":
      container = container.elementType
      element_type = element_type.list.elementType
    if element_type.which() == "struct":
      return container.elementType
  return None


def collect_schema(root: Any) -> dict[str, dict]:
  structs: dict[str, dict] = {}
  stack = [root]
  while stack:
    schema = stack.pop()
    type_id = hex_id(schema.node.id)
    if type_id in structs:
      continue
    structs[type_id] = encode_struct(schema)
    for _name, field in schema.fields.items():
      try:
        child = _child_struct_schema(field)
      except Exception:
        child = None
      if child is not None:
        stack.append(child)
  return structs


def load_log(cereal_dir: str, extra_imports: list[str] | None = None) -> Any:
  import capnp
  cereal_dir = os.path.abspath(cereal_dir)
  capnp.remove_import_hook()
  imports = [cereal_dir] + [os.path.abspath(p) for p in (extra_imports or [])]
  return capnp.load(os.path.join(cereal_dir, "log.capnp"), imports=imports)


def dump_schema(cereal_dir: str, path: str, extra_imports: list[str] | None = None) -> None:
  log = load_log(cereal_dir, extra_imports)
  payload = {
    "root": hex_id(log.Event.schema.node.id),
    "structs": collect_schema(log.Event.schema),
  }
  with open(path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2, sort_keys=True)
  print(f"wrote schema dump with {len(payload['structs'])} structs to {path}")


def compare(sunnypilot_dump: dict, upstream_dump: dict) -> list[str]:
  violations: list[str] = []
  sunnypilot_structs = sunnypilot_dump["structs"]
  upstream_structs = upstream_dump["structs"]

  for type_id, sp_struct in sunnypilot_structs.items():
    if not sp_struct["hasUnion"]:
      continue
    up_struct = upstream_structs.get(type_id)
    if up_struct is None:
      continue

    up_ordinals = {f["ordinal"] for f in up_struct["fields"] if f.get("discriminant") is not None}
    display = sp_struct["displayName"]

    for field in sp_struct["fields"]:
      if field.get("discriminant") is None:
        continue
      if field["ordinal"] not in up_ordinals:
        violations.append(
          f"{display} @{field['ordinal']} '{field['name']}': "
          f"union variant not present upstream (discriminant={field['discriminant']})"
        )

  return violations


def run_read(cereal_dir: str, peer_path: str, extra_imports: list[str] | None = None) -> int:
  log = load_log(cereal_dir, extra_imports)
  with open(peer_path, "r", encoding="utf-8") as f:
    peer_dump = json.load(f)
  local_dump = {
    "root": hex_id(log.Event.schema.node.id),
    "structs": collect_schema(log.Event.schema),
  }
  violations = compare(sunnypilot_dump=peer_dump, upstream_dump=local_dump)

  if not violations:
    print("cereal compat OK: upstream can parse sunnypilot routes.")
    return 0

  print(f"cereal compat FAIL ({len(violations)} leaked union variant(s)):")
  for v in violations:
    print(f"  {v}")
  return 1


def main() -> int:
  parser = argparse.ArgumentParser(description="sunnypilot cereal upstream compat check")
  mode = parser.add_mutually_exclusive_group(required=True)
  mode.add_argument("-g", "--generate", action="store_true", help="dump local schema to JSON")
  mode.add_argument("-r", "--read", action="store_true", help="validate against peer schema")
  parser.add_argument("-f", "--file", default="schema.json", help="JSON file path")
  parser.add_argument("--cereal-dir", required=True, help="path to cereal directory")
  parser.add_argument("-I", "--import-path", action="append", default=[], help="extra capnp import paths")
  args = parser.parse_args()

  if args.generate:
    dump_schema(args.cereal_dir, args.file, args.import_path)
    return 0
  return run_read(args.cereal_dir, args.file, args.import_path)


if __name__ == "__main__":
  sys.exit(main())
