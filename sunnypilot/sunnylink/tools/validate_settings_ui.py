#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Settings UI Validator
=====================

Validates settings_ui.json against structural, semantic, and referential
integrity constraints. Ensures the file is well-formed for consumption by
the sunnylink frontend and the device-side schema generator.

Usage:
  python validate_settings_ui.py
  python validate_settings_ui.py /path/to/settings_ui.json
"""
from __future__ import annotations

import json
import os
import sys

# Add repo root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from openpilot.sunnypilot.sunnylink.capabilities import CAPABILITY_FIELDS

VALID_WIDGETS = {"toggle", "option", "multiple_button", "button", "info"}
VALID_COMPARE_OPS = {">", "<", ">=", "<="}

DEFAULT_PATH = os.path.join(
  os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
  "settings_ui.json",
)


class ValidationResult:
  """Tracks pass/fail for each named check."""

  def __init__(self) -> None:
    self.passed: list[str] = []
    self.failed: list[tuple[str, str]] = []
    self.warnings: list[str] = []

  def ok(self, name: str) -> None:
    self.passed.append(name)
    print(f"OK: {name}")

  def error(self, name: str, details: str) -> None:
    self.failed.append((name, details))
    print(f"ERROR: {name}: {details}")

  def warn(self, msg: str) -> None:
    self.warnings.append(msg)
    print(f"WARNING: {msg}")

  @property
  def success(self) -> bool:
    return len(self.failed) == 0

  def summary(self) -> None:
    total_passed = len(self.passed)
    total_failed = len(self.failed)
    print(f"\n{'='*60}")
    print(f"Summary: {total_passed} checks passed, {total_failed} checks failed")
    if self.warnings:
      print(f"         {len(self.warnings)} warnings")
    if self.success:
      print("Result: PASS")
    else:
      print("Result: FAIL")


def validate_rule(rule: dict, path: str, result: ValidationResult,
                  capability_fields: tuple[str, ...]) -> bool:
  """Validate a single rule dict. Returns True if valid."""
  if not isinstance(rule, dict):
    result.error("rule well-formedness", f"{path}: rule is not a dict: {rule!r}")
    return False

  rule_type = rule.get("type")
  if rule_type is None:
    result.error("rule well-formedness", f"{path}: rule missing 'type' field")
    return False

  if rule_type == "offroad_only":
    # Only type required
    return True

  if rule_type == "capability":
    valid = True
    if "field" not in rule or not isinstance(rule["field"], str):
      result.error("rule well-formedness", f"{path}: capability rule missing/invalid 'field'")
      valid = False
    if "equals" not in rule:
      result.error("rule well-formedness", f"{path}: capability rule missing 'equals'")
      valid = False
    return valid

  if rule_type == "param":
    valid = True
    if "key" not in rule or not isinstance(rule["key"], str):
      result.error("rule well-formedness", f"{path}: param rule missing/invalid 'key'")
      valid = False
    if "equals" not in rule:
      result.error("rule well-formedness", f"{path}: param rule missing 'equals'")
      valid = False
    return valid

  if rule_type == "param_compare":
    valid = True
    if "key" not in rule or not isinstance(rule["key"], str):
      result.error("rule well-formedness", f"{path}: param_compare rule missing/invalid 'key'")
      valid = False
    if "op" not in rule or rule["op"] not in VALID_COMPARE_OPS:
      result.error("rule well-formedness",
                    f"{path}: param_compare rule missing/invalid 'op' (must be one of {VALID_COMPARE_OPS})")
      valid = False
    if "value" not in rule or not isinstance(rule["value"], (int, float)):
      result.error("rule well-formedness", f"{path}: param_compare rule missing/invalid 'value' (must be number)")
      valid = False
    return valid

  if rule_type == "not":
    if "condition" not in rule or not isinstance(rule["condition"], dict):
      result.error("rule well-formedness", f"{path}: 'not' rule missing/invalid 'condition'")
      return False
    return validate_rule(rule["condition"], f"{path}.not", result, capability_fields)

  if rule_type in ("any", "all"):
    if "conditions" not in rule or not isinstance(rule["conditions"], list):
      result.error("rule well-formedness", f"{path}: '{rule_type}' rule missing/invalid 'conditions' array")
      return False
    valid = True
    for i, cond in enumerate(rule["conditions"]):
      if not validate_rule(cond, f"{path}.{rule_type}[{i}]", result, capability_fields):
        valid = False
    return valid

  result.error("rule well-formedness", f"{path}: unknown rule type '{rule_type}'")
  return False


def collect_rules_from_item(item: dict) -> list[tuple[str, list[dict]]]:
  """Return list of (context, rules_list) for an item's visibility + enablement."""
  result = []
  key = item.get("key", "?")
  if "visibility" in item:
    result.append((f"item '{key}' visibility", item["visibility"]))
  if "enablement" in item:
    result.append((f"item '{key}' enablement", item["enablement"]))
  return result


def walk_rules_flat(rules: list[dict]) -> list[dict]:
  """Flatten all rules recursively into a single list."""
  flat: list[dict] = []
  for rule in rules:
    flat.append(rule)
    if rule.get("type") == "not" and "condition" in rule:
      flat.extend(walk_rules_flat([rule["condition"]]))
    elif rule.get("type") in ("any", "all") and "conditions" in rule:
      flat.extend(walk_rules_flat(rule["conditions"]))
  return flat


def collect_all_items(data: dict) -> list[tuple[str, dict]]:
  """Collect all items with their location path from the schema.

  Returns (path, item_dict) tuples. Traverses sections, sub_panels, sub_items,
  and vehicle_settings.
  """
  items: list[tuple[str, dict]] = []

  for panel in data.get("panels", []):
    pid = panel.get("id", "?")

    # Flat items on panel
    for item in panel.get("items", []):
      _collect_item(f"panel '{pid}'", item, items)

    # Sections
    for section in panel.get("sections", []):
      sid = section.get("id", "?")
      for item in section.get("items", []):
        _collect_item(f"panel '{pid}' > section '{sid}'", item, items)
      for sp in section.get("sub_panels", []):
        spid = sp.get("id", "?")
        for item in sp.get("items", []):
          _collect_item(f"panel '{pid}' > section '{sid}' > sub_panel '{spid}'", item, items)

    # Top-level sub_panels on panel (no section)
    for sp in panel.get("sub_panels", []):
      spid = sp.get("id", "?")
      for item in sp.get("items", []):
        _collect_item(f"panel '{pid}' > sub_panel '{spid}'", item, items)

  # Vehicle settings (supports both flat list and { title, items } structure)
  for brand, brand_data in data.get("vehicle_settings", {}).items():
    brand_items = brand_data.get("items", []) if isinstance(brand_data, dict) else brand_data
    for item in brand_items:
      _collect_item(f"vehicle_settings '{brand}'", item, items)

  return items


def _collect_item(path: str, item: dict, items: list[tuple[str, dict]]) -> None:
  """Recursively collect an item and its sub_items."""
  items.append((path, item))
  for sub in item.get("sub_items", []):
    _collect_item(f"{path} > sub_item", sub, items)


def collect_panel_keys(panel: dict) -> set[str]:
  """Collect all item keys within a single panel (sections, sub_panels, sub_items)."""
  keys: set[str] = set()

  def _add(item: dict) -> None:
    if "key" in item:
      keys.add(item["key"])
    for sub in item.get("sub_items", []):
      _add(sub)

  for item in panel.get("items", []):
    _add(item)
  for section in panel.get("sections", []):
    for item in section.get("items", []):
      _add(item)
    for sp in section.get("sub_panels", []):
      for item in sp.get("items", []):
        _add(item)
  for sp in panel.get("sub_panels", []):
    for item in sp.get("items", []):
      _add(item)

  return keys


def check_json_parseable(path: str, result: ValidationResult) -> dict | None:
  """Check 1: JSON parseable."""
  try:
    with open(path) as f:
      data = json.load(f)
    result.ok("JSON parseable")
    return data
  except json.JSONDecodeError as e:
    result.error("JSON parseable", str(e))
    return None
  except FileNotFoundError:
    result.error("JSON parseable", f"file not found: {path}")
    return None


def check_structural(data: dict, result: ValidationResult) -> None:
  """Check 2: Required fields on panels, sections, items, sub_panels."""
  errors: list[str] = []

  for i, panel in enumerate(data.get("panels", [])):
    for field in ("id", "label", "icon", "order"):
      if field not in panel:
        errors.append(f"panels[{i}]: missing required field '{field}'")

    for j, section in enumerate(panel.get("sections", [])):
      for field in ("id", "title"):
        if field not in section:
          errors.append(f"panels[{i}].sections[{j}]: missing required field '{field}'")

      for k, sp in enumerate(section.get("sub_panels", [])):
        for field in ("id", "label", "trigger_key"):
          if field not in sp:
            errors.append(f"panels[{i}].sections[{j}].sub_panels[{k}]: missing required field '{field}'")

    for k, sp in enumerate(panel.get("sub_panels", [])):
      for field in ("id", "label", "trigger_key"):
        if field not in sp:
          errors.append(f"panels[{i}].sub_panels[{k}]: missing required field '{field}'")

  # Validate items
  all_items = collect_all_items(data)
  for path, item in all_items:
    if "key" not in item:
      errors.append(f"{path}: item missing required field 'key'")
    if "widget" not in item:
      errors.append(f"{path}: item missing required field 'widget'")
    elif item["widget"] not in VALID_WIDGETS:
      errors.append(
        f"{path}: item '{item.get('key', '?')}' has invalid widget '{item['widget']}'"
        + f" (must be one of {VALID_WIDGETS})"
      )

  if errors:
    result.error("structural", "; ".join(errors))
  else:
    result.ok("structural")


def check_item_completeness(data: dict, result: ValidationResult) -> None:
  """Check 3: All items have required metadata (title, options for dropdowns)."""
  all_items = collect_all_items(data)
  issues: list[str] = []

  for _path, item in all_items:
    key = item.get("key", "unknown")
    if "title" not in item:
      issues.append(f"{key}: missing 'title'")
    elif item["title"] == key:
      issues.append(f"{key}: title must not equal key (use a human-readable title)")
    widget = item.get("widget")
    if widget in ("multiple_button", "option") and "options" in item:
      opts = item["options"]
      if not isinstance(opts, list):
        issues.append(f"{key}: options must be a list")
      else:
        for opt in opts:
          if not isinstance(opt, dict) or "value" not in opt or "label" not in opt:
            issues.append(f"{key}: each option must have 'value' and 'label'")
            break

  if issues:
    for issue in issues:
      result.error("item completeness", issue)
  else:
    result.ok("item completeness")


def check_no_duplicate_keys(data: dict, result: ValidationResult) -> None:
  """Check 4: No param key appears in more than one panel."""
  panel_keys: dict[str, list[str]] = {}  # key -> list of panel ids

  for panel in data.get("panels", []):
    pid = panel.get("id", "?")
    keys = collect_panel_keys(panel)
    for key in keys:
      panel_keys.setdefault(key, []).append(pid)

  # Also check vehicle_settings keys don't collide with panel keys
  for brand, brand_data in data.get("vehicle_settings", {}).items():
    brand_items = brand_data.get("items", []) if isinstance(brand_data, dict) else brand_data
    for item in brand_items:
      key = item.get("key")
      if key:
        panel_keys.setdefault(key, []).append(f"vehicle_settings.{brand}")

  duplicates = {k: v for k, v in panel_keys.items() if len(v) > 1}
  if duplicates:
    details = "; ".join(f"'{k}' in [{', '.join(v)}]" for k, v in duplicates.items())
    result.error("no duplicate keys", details)
  else:
    result.ok("no duplicate keys")


def check_rule_wellformedness(data: dict, result: ValidationResult) -> None:
  """Check 5: All rules have valid structure."""
  all_items = collect_all_items(data)

  # Save current error count to detect new errors
  error_count_before = len(result.failed)

  for path, item in all_items:
    for ctx, rules in collect_rules_from_item(item):
      for i, rule in enumerate(rules):
        validate_rule(rule, f"{path} > {ctx}[{i}]", result, CAPABILITY_FIELDS)

  # Also validate trigger_condition rules on sub_panels
  for panel in data.get("panels", []):
    pid = panel.get("id", "?")
    for section in panel.get("sections", []):
      for sp in section.get("sub_panels", []):
        if "trigger_condition" in sp:
          validate_rule(sp["trigger_condition"], f"panel '{pid}' > sub_panel '{sp.get('id', '?')}' trigger_condition",
                        result, CAPABILITY_FIELDS)

  if len(result.failed) == error_count_before:
    result.ok("rule well-formedness")


def check_capability_refs(data: dict, result: ValidationResult) -> None:
  """Check 6: All capability rule field values are in CAPABILITY_FIELDS."""
  all_items = collect_all_items(data)
  invalid_refs: list[str] = []
  cap_set = set(CAPABILITY_FIELDS)

  for _path, item in all_items:
    for _ctx, rules in collect_rules_from_item(item):
      for rule in walk_rules_flat(rules):
        if rule.get("type") == "capability":
          field = rule.get("field")
          if field and field not in cap_set:
            invalid_refs.append(f"'{field}' in item '{item.get('key', '?')}'")

  # Also check trigger_conditions
  for panel in data.get("panels", []):
    for section in panel.get("sections", []):
      for sp in section.get("sub_panels", []):
        if "trigger_condition" in sp:
          for rule in walk_rules_flat([sp["trigger_condition"]]):
            if rule.get("type") == "capability":
              field = rule.get("field")
              if field and field not in cap_set:
                invalid_refs.append(f"'{field}' in sub_panel '{sp.get('id', '?')}' trigger_condition")

  if invalid_refs:
    result.error("capability refs", f"unknown capability fields: {', '.join(invalid_refs)}")
  else:
    result.ok("capability refs")


def check_no_self_reference(data: dict, result: ValidationResult) -> None:
  """Check 7: Item's rules must not reference the item's own key."""
  all_items = collect_all_items(data)
  self_refs: list[str] = []

  for path, item in all_items:
    key = item.get("key")
    if not key:
      continue
    for _ctx, rules in collect_rules_from_item(item):
      for rule in walk_rules_flat(rules):
        if rule.get("type") in ("param", "param_compare") and rule.get("key") == key:
          self_refs.append(f"'{key}' at {path}")

  if self_refs:
    result.error("no self-reference", f"items reference their own key: {', '.join(self_refs)}")
  else:
    result.ok("no self-reference")


def check_sub_panel_triggers(data: dict, result: ValidationResult) -> None:
  """Check 8: Sub-panel trigger_key must reference a key in the same panel."""
  errors: list[str] = []

  for panel in data.get("panels", []):
    pid = panel.get("id", "?")
    panel_keys = collect_panel_keys(panel)

    # Check sub_panels at section level
    for section in panel.get("sections", []):
      for sp in section.get("sub_panels", []):
        trigger = sp.get("trigger_key")
        if trigger and trigger not in panel_keys:
          errors.append(
            f"sub_panel '{sp.get('id', '?')}' trigger_key '{trigger}'"
            + f" not found in panel '{pid}'"
          )

    # Check top-level sub_panels
    for sp in panel.get("sub_panels", []):
      trigger = sp.get("trigger_key")
      if trigger and trigger not in panel_keys:
        errors.append(
          f"sub_panel '{sp.get('id', '?')}' trigger_key '{trigger}'"
          + f" not found in panel '{pid}'"
        )

  if errors:
    result.error("sub-panel triggers", "; ".join(errors))
  else:
    result.ok("sub-panel triggers")


def check_ordering(data: dict, result: ValidationResult) -> None:
  """Check 9: Panel order values must be unique."""
  orders: dict[int, list[str]] = {}
  for panel in data.get("panels", []):
    order = panel.get("order")
    if order is not None:
      orders.setdefault(order, []).append(panel.get("id", "?"))

  duplicates = {o: ids for o, ids in orders.items() if len(ids) > 1}
  if duplicates:
    details = "; ".join(f"order {o}: [{', '.join(ids)}]" for o, ids in duplicates.items())
    result.error("ordering", f"duplicate order values: {details}")
  else:
    result.ok("ordering")


def check_vehicle_brands(data: dict, result: ValidationResult) -> None:
  """Check 10: Vehicle settings keys should be lowercase strings."""
  vehicle = data.get("vehicle_settings", {})
  bad_brands: list[str] = []

  for brand in vehicle:
    if not isinstance(brand, str) or brand != brand.lower():
      bad_brands.append(brand)

  if bad_brands:
    result.error("vehicle brands", f"non-lowercase brand keys: {', '.join(bad_brands)}")
  else:
    result.ok("vehicle brands")


def validate(path: str) -> bool:
  """Run all validation checks on the given settings_ui.json file.

  Returns True if all checks pass.
  """
  result = ValidationResult()

  # Check 1: JSON parseable
  data = check_json_parseable(path, result)
  if data is None:
    result.summary()
    return False

  # Checks 2-10
  check_structural(data, result)
  check_item_completeness(data, result)
  check_no_duplicate_keys(data, result)
  check_rule_wellformedness(data, result)
  check_capability_refs(data, result)
  check_no_self_reference(data, result)
  check_sub_panel_triggers(data, result)
  check_ordering(data, result)
  check_vehicle_brands(data, result)

  result.summary()
  return result.success


if __name__ == "__main__":
  target = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH
  success = validate(target)
  sys.exit(0 if success else 1)
