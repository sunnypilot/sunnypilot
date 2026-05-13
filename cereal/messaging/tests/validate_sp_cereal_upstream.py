#!/usr/bin/env python3
"""Schema-level cereal compat check between sunnypilot and upstream openpilot.

Rules (per struct matched across sides by typeId):
  R1  shared ordinal must reference the same type.
  R2  sunnypilot-only ordinal in a union -> FAIL (unknown discriminant upstream).
  R3  sunnypilot-only ordinal on a regular field -> OK (additive struct evolution).
  R4  upstream-only ordinal -> OK.
  R5  sunnypilot-only struct referenced via an upstream-shared field -> FAIL.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

NO_DISCRIMINANT = 0xFFFF


def hex_id(value: int) -> str:
  return f"0x{value:016x}"


def encode_type(type_node: Any) -> dict:
  which = type_node.which()
  if which == "struct":
    return {"kind": "struct", "typeId": hex_id(type_node.struct.typeId)}
  if which == "enum":
    return {"kind": "enum", "typeId": hex_id(type_node.enum.typeId)}
  if which == "interface":
    return {"kind": "interface", "typeId": hex_id(type_node.interface.typeId)}
  if which == "list":
    return {"kind": "list", "element": encode_type(type_node.list.elementType)}
  if which == "anyPointer":
    return {"kind": "anyPointer"}
  return {"kind": which}


def encode_field(name: str, field: Any) -> dict:
  proto = field.proto
  ordinal = proto.ordinal.explicit if proto.ordinal.which() == "explicit" else None
  discriminant = proto.discriminantValue if proto.discriminantValue != NO_DISCRIMINANT else None

  if proto.which() == "group":
    type_desc = {"kind": "group", "typeId": hex_id(proto.group.typeId)}
  else:
    type_desc = encode_type(proto.slot.type)

  return {
    "name": name,
    "ordinal": ordinal,
    "discriminant": discriminant,
    "type": type_desc,
  }


def encode_struct(schema: Any) -> dict:
  node = schema.node
  return {
    "typeId": hex_id(node.id),
    "displayName": node.displayName,
    "hasUnion": node.struct.discriminantCount > 0,
    "fields": [encode_field(name, field) for name, field in schema.fields.items()],
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


def dump_schema(path: str) -> None:
  from cereal import log
  payload = {
    "root": hex_id(log.Event.schema.node.id),
    "structs": collect_schema(log.Event.schema),
  }
  with open(path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2, sort_keys=True)
  print(f"wrote schema dump with {len(payload['structs'])} structs to {path}")


def types_equal(a: dict, b: dict) -> bool:
  if a.get("kind") != b.get("kind"):
    return False
  kind = a["kind"]
  if kind in ("struct", "enum", "interface", "group"):
    return a.get("typeId") == b.get("typeId")
  if kind == "list":
    return types_equal(a["element"], b["element"])
  return True


def type_repr(t: dict) -> str:
  kind = t.get("kind", "?")
  if kind in ("struct", "enum", "interface", "group"):
    return f"{kind}({t.get('typeId')})"
  if kind == "list":
    return f"list<{type_repr(t['element'])}>"
  return kind


def field_is_union_variant(field: dict) -> bool:
  return field.get("discriminant") is not None


def index_fields_by_ordinal(struct: dict) -> dict[int, dict]:
  indexed: dict[int, dict] = {}
  for field in struct["fields"]:
    ordinal = field.get("ordinal")
    if ordinal is None:
      continue
    indexed[ordinal] = field
  return indexed


def compare(sunnypilot_dump: dict, upstream_dump: dict) -> list[str]:
  violations: list[str] = []
  sunnypilot_structs: dict[str, dict] = sunnypilot_dump["structs"]
  upstream_structs: dict[str, dict] = upstream_dump["structs"]

  sunnypilot_struct_referenced_from_shared: set[str] = set()

  for type_id, sunnypilot_struct in sunnypilot_structs.items():
    upstream_struct = upstream_structs.get(type_id)
    if upstream_struct is None:
      continue

    sunnypilot_fields = index_fields_by_ordinal(sunnypilot_struct)
    upstream_fields = index_fields_by_ordinal(upstream_struct)
    display = sunnypilot_struct["displayName"]

    for ordinal, sunnypilot_field in sunnypilot_fields.items():
      upstream_field = upstream_fields.get(ordinal)
      if upstream_field is None:
        if field_is_union_variant(sunnypilot_field):
          violations.append(
            f"[R2] {display} @{ordinal} ('{sunnypilot_field['name']}', {type_repr(sunnypilot_field['type'])}): "
            f"union variant not present upstream. upstream cannot parse this discriminant."
          )
        continue

      if not types_equal(sunnypilot_field["type"], upstream_field["type"]):
        violations.append(
          f"[R1] {display} @{ordinal}: type mismatch. "
          f"sunnypilot='{sunnypilot_field['name']}' {type_repr(sunnypilot_field['type'])} vs "
          f"upstream='{upstream_field['name']}' {type_repr(upstream_field['type'])}."
        )
        continue

      cursor = sunnypilot_field["type"]
      while cursor.get("kind") == "list":
        cursor = cursor["element"]
      if cursor.get("kind") in ("struct", "group", "interface") and cursor.get("typeId"):
        sunnypilot_struct_referenced_from_shared.add(cursor["typeId"])

  for type_id, sunnypilot_struct in sunnypilot_structs.items():
    if type_id in upstream_structs:
      continue
    if type_id in sunnypilot_struct_referenced_from_shared:
      violations.append(
        f"[R5] struct {sunnypilot_struct['displayName']} ({type_id}) exists only on sunnypilot "
        f"but is referenced from an upstream-shared field. upstream cannot resolve this type."
      )

  return violations


def load_peer(path: str) -> dict:
  with open(path, "r", encoding="utf-8") as handle:
    return json.load(handle)


def run_read(peer_path: str) -> int:
  from cereal import log
  peer_dump = load_peer(peer_path)
  local_dump = {
    "root": hex_id(log.Event.schema.node.id),
    "structs": collect_schema(log.Event.schema),
  }
  violations = compare(sunnypilot_dump=peer_dump, upstream_dump=local_dump)

  if not violations:
    print("cereal compat OK: upstream openpilot can parse sunnypilot routes "
          "(no leaked structs, no ordinal collisions).")
    return 0

  print(f"cereal compat FAIL: upstream openpilot would misparse sunnypilot routes "
        f"({len(violations)} violation(s)):")
  for v in violations:
    print(f"  {v}")
  return 1


def main() -> int:
  parser = argparse.ArgumentParser(
    description="sunnypilot <-> upstream cereal compatibility validator (schema-level)."
  )
  mode = parser.add_mutually_exclusive_group(required=True)
  mode.add_argument("-g", "--generate", action="store_true", help="dump local schema to JSON")
  mode.add_argument("-r", "--read", action="store_true", help="load peer JSON and diff against local")
  parser.add_argument("-f", "--file", default="schema.json", help="JSON file path (default: schema.json)")
  args = parser.parse_args()

  try:
    if args.generate:
      dump_schema(args.file)
      return 0
    return run_read(args.file)
  except ImportError as exc:
    print(f"error: cannot import cereal ({exc}). did scons build cereal?")
    return 2


if __name__ == "__main__":
  sys.exit(main())
