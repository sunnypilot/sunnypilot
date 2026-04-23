"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Per-bug regression tests for the Raylib-vs-schema parity audit. Each test
isolates one of the gating bugs that the design-overhaul branch fixes so a
future regression is loud and obvious. These tests are intentionally narrow
and additive — they do not replace the broader test_settings_schema.py.
"""
from __future__ import annotations

import json
import os
from typing import Any

import pytest

from openpilot.sunnypilot.sunnylink.tools.generate_settings_schema import (
  DEFINITION_PATH,
  TORQUE_VERSIONS_PATH,
  _build_torque_options,
  _load_torque_versions,
  generate_schema,
)


SCHEMA_VALIDATOR_PATH = os.path.join(os.path.dirname(DEFINITION_PATH), "settings_ui.schema.json")


def _walk_items(schema: dict[str, Any]):
  """Yield every item dict reachable from the schema (panels, sections, sub_panels, sub_items, vehicle_settings)."""
  def _yield(item: dict[str, Any]):
    yield item
    for sub in item.get("sub_items", []):
      yield from _yield(sub)

  for panel in schema.get("panels", []):
    for section in panel.get("sections", []):
      for item in section.get("items", []):
        yield from _yield(item)
      for sp in section.get("sub_panels", []):
        for item in sp.get("items", []):
          yield from _yield(item)
    for item in panel.get("items", []):
      yield from _yield(item)
    for sp in panel.get("sub_panels", []):
      for item in sp.get("items", []):
        yield from _yield(item)
  for brand in schema.get("vehicle_settings", {}).values():
    items = brand.get("items", []) if isinstance(brand, dict) else brand
    for item in items:
      yield from _yield(item)


def _find_item(schema: dict[str, Any], key: str) -> dict[str, Any] | None:
  for item in _walk_items(schema):
    if item.get("key") == key:
      return item
  return None


def _find_section(schema: dict[str, Any], panel_id: str, section_id: str) -> dict[str, Any] | None:
  for panel in schema.get("panels", []):
    if panel.get("id") != panel_id:
      continue
    for section in panel.get("sections", []):
      if section.get("id") == section_id:
        return section
  return None


def _flatten_rule_types(rules: list[dict[str, Any]] | None) -> set[str]:
  out: set[str] = set()

  def _walk(rule: dict[str, Any]) -> None:
    out.add(rule.get("type", ""))
    if rule.get("type") == "not" and "condition" in rule:
      _walk(rule["condition"])
    elif rule.get("type") in ("any", "all"):
      for c in rule.get("conditions", []):
        _walk(c)

  for rule in rules or []:
    _walk(rule)
  return out


def _references_capability_field(rules: list[dict[str, Any]] | None, field: str) -> bool:
  found = False

  def _walk(rule: dict[str, Any]) -> None:
    nonlocal found
    if rule.get("type") == "capability" and rule.get("field") == field:
      found = True
    elif rule.get("type") == "not" and "condition" in rule:
      _walk(rule["condition"])
    elif rule.get("type") in ("any", "all"):
      for c in rule.get("conditions", []):
        _walk(c)

  for rule in rules or []:
    _walk(rule)
  return found


@pytest.fixture(scope="module")
def schema():
  return generate_schema()


class TestMadsBrandGates:
  def test_mads_main_cruise_has_brand_gate(self, schema):
    """MadsMainCruiseAllowed must be disabled on rivian + tesla-no-bus to match Raylib _mads_limited_settings."""
    item = _find_item(schema, "MadsMainCruiseAllowed")
    assert item is not None
    assert _references_capability_field(item.get("enablement"), "brand")
    assert _references_capability_field(item.get("enablement"), "tesla_has_vehicle_bus")

  def test_mads_unified_engagement_has_brand_gate(self, schema):
    """MadsUnifiedEngagementMode must mirror MadsMainCruiseAllowed brand-gate."""
    item = _find_item(schema, "MadsUnifiedEngagementMode")
    assert item is not None
    assert _references_capability_field(item.get("enablement"), "brand")
    assert _references_capability_field(item.get("enablement"), "tesla_has_vehicle_bus")


class TestTestManeuversSection:
  def test_lateral_maneuver_mode_in_test_maneuvers(self, schema):
    section = _find_section(schema, "developer", "test_maneuvers")
    assert section is not None, "developer.test_maneuvers section missing"
    keys = {item["key"] for item in section.get("items", [])}
    assert "LateralManeuverMode" in keys
    assert "LongitudinalManeuverMode" in keys

  def test_test_maneuvers_section_requires_attestation(self, schema):
    section = _find_section(schema, "developer", "test_maneuvers")
    assert section is not None
    assert section.get("attestation_required") is True

  def test_test_maneuvers_section_visibility_gate(self, schema):
    section = _find_section(schema, "developer", "test_maneuvers")
    assert section is not None
    visibility = section.get("visibility")
    assert visibility, "test_maneuvers must have visibility gate"
    vis_refs = json.dumps(visibility)
    assert "is_development" in vis_refs
    assert "is_sp_release" in vis_refs
    enablement = section.get("enablement") or []
    enable_refs = json.dumps(enablement)
    assert "ShowAdvancedControls" in enable_refs, \
      "test_maneuvers must gate ShowAdvancedControls via enablement (disabled, not hidden)"


class TestValidator:
  def test_validator_accepts_real_json(self):
    """settings_ui.json must validate against settings_ui.schema.json."""
    jsonschema = pytest.importorskip("jsonschema")
    with open(DEFINITION_PATH) as f:
      data = json.load(f)
    with open(SCHEMA_VALIDATOR_PATH) as f:
      validator = json.load(f)
    jsonschema.validate(instance=data, schema=validator)


class TestTorqueOptionGeneration:
  def test_torque_versions_match_generated_options(self, schema):
    versions = _load_torque_versions()
    assert versions, "latcontrol_torque_versions.json must have at least one version"
    expected = _build_torque_options(versions)
    item = _find_item(schema, "TorqueControlTune")
    assert item is not None, "TorqueControlTune item must be present"
    assert item.get("options") == expected

  def test_torque_versions_path_resolves(self):
    assert os.path.exists(TORQUE_VERSIONS_PATH), (
      f"latcontrol_torque_versions.json not found at {TORQUE_VERSIONS_PATH}"
    )


class TestReleaseBranchGates:
  @pytest.mark.parametrize("key", [
    "JoystickDebugMode",
    "AlphaLongitudinalEnabled",
    "EnableGithubRunner",
    "QuickBootToggle",
  ])
  def test_sp_dev_items_gate_on_is_sp_release(self, schema, key):
    """SP-side dev items must hide on EITHER release branch (matches Raylib _is_release_branch = is_release OR IsReleaseSpBranch)."""
    item = _find_item(schema, key)
    assert item is not None, f"{key} not found in schema"
    rules = (item.get("visibility") or []) + (item.get("enablement") or [])
    assert _references_capability_field(rules, "is_release"), f"{key} missing is_release gate"
    assert _references_capability_field(rules, "is_sp_release"), f"{key} missing is_sp_release gate"


class TestSpuriousOffroadGatesDropped:
  def test_disengage_on_accelerator_has_no_offroad_only(self, schema):
    item = _find_item(schema, "DisengageOnAccelerator")
    assert item is not None
    assert "offroad_only" not in _flatten_rule_types(item.get("enablement"))

  def test_dynamic_experimental_has_no_offroad_only(self, schema):
    item = _find_item(schema, "DynamicExperimentalControl")
    assert item is not None
    assert "offroad_only" not in _flatten_rule_types(item.get("enablement"))


class TestNotEngagedReplacement:
  @pytest.mark.parametrize("key", [
    "AlphaLongitudinalEnabled",
    "ToyotaEnforceStockLongitudinal",
    "ToyotaStopAndGoHack",
  ])
  def test_offroad_only_replaced_with_not_engaged(self, schema, key):
    """These items can be changed safely when not engaged; must not require full offroad."""
    item = _find_item(schema, key)
    assert item is not None, f"{key} not found"
    rule_types = _flatten_rule_types(item.get("enablement"))
    assert "offroad_only" not in rule_types, f"{key} still uses offroad_only"
    assert "not_engaged" in rule_types, f"{key} missing not_engaged"
