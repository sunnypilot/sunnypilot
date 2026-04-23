"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json
import pytest

from openpilot.common.params import Params
from openpilot.sunnypilot.sunnylink.tools.generate_settings_schema import (
  SCHEMA_VERSION,
  generate_schema,
  generate_schema_json,
  collect_all_keys,
  collect_capability_refs,
)
from openpilot.sunnypilot.sunnylink.capabilities import CAPABILITY_FIELDS


VALID_WIDGET_TYPES = {"toggle", "option", "multiple_button", "button", "info"}
VALID_RULE_TYPES = {"offroad_only", "not_engaged", "capability", "param", "param_compare", "not", "any", "all"}
VALID_COMPARE_OPS = {">", "<", ">=", "<="}
MAX_ALLOWED_MISSING_TITLES = 0  # All items must have titles (metadata is inline in settings_ui.json)


def _iter_panel_items(panel: dict):
  """Yield top-level items reachable from a panel: panel.items, panel.sub_panels.items,
  panel.sections.items, panel.sections.sub_panels.items. Does not recurse sub_items."""
  for item in panel.get("items", []):
    yield item
  for sp in panel.get("sub_panels", []):
    for item in sp.get("items", []):
      yield item
  for section in panel.get("sections", []):
    for item in section.get("items", []):
      yield item
    for sp in section.get("sub_panels", []):
      for item in sp.get("items", []):
        yield item


def _iter_all_sub_panels(panel: dict):
  """Yield every sub_panel (panel-level + section-nested)."""
  yield from panel.get("sub_panels", [])
  for section in panel.get("sections", []):
    yield from section.get("sub_panels", [])


def _brand_items(brand_data) -> list[dict]:
  """vehicle_settings[brand] is dict {title, description?, items}; tolerate raw list."""
  if isinstance(brand_data, dict):
    return brand_data.get("items", [])
  if isinstance(brand_data, list):
    return brand_data
  return []


@pytest.fixture(scope="module")
def schema():
  return generate_schema()


@pytest.fixture(scope="module")
def all_param_keys():
  """All keys registered in the device param store."""
  return {k.decode("utf-8") for k in Params().all_keys()}


class TestSchemaStructure:
  def test_schema_is_valid_json(self):
    """Schema can be serialized to valid JSON."""
    raw = generate_schema_json()
    parsed = json.loads(raw)
    assert isinstance(parsed, dict)

  def test_has_required_top_level_fields(self, schema):
    assert "schema_version" in schema
    assert schema["schema_version"] == SCHEMA_VERSION
    assert "generated_at" in schema
    assert "panels" in schema
    assert "vehicle_settings" in schema
    assert "capability_fields" in schema

  def test_panels_are_list(self, schema):
    assert isinstance(schema["panels"], list)
    assert len(schema["panels"]) > 0

  def test_all_panels_have_required_fields(self, schema):
    for panel in schema["panels"]:
      assert "id" in panel, f"Panel missing 'id': {panel}"
      assert "label" in panel, f"Panel {panel.get('id')} missing 'label'"
      assert "order" in panel, f"Panel {panel.get('id')} missing 'order'"
      has_sections = "sections" in panel
      has_items = "items" in panel
      assert has_sections or has_items, \
        f"Panel {panel['id']} must have 'sections' or 'items'"
      if has_sections:
        assert isinstance(panel["sections"], list)
        for sec in panel["sections"]:
          assert "id" in sec, f"Section in panel {panel['id']} missing 'id'"
          assert "items" in sec, f"Section {panel['id']}.{sec.get('id')} missing 'items'"
          assert isinstance(sec["items"], list)
      if has_items:
        assert isinstance(panel["items"], list)

  def test_all_items_have_key_and_widget(self, schema):
    for panel in schema["panels"]:
      for item in _iter_panel_items(panel):
        assert "key" in item, f"Item in panel {panel['id']} missing 'key'"
        assert "widget" in item, f"Item {item.get('key')} missing 'widget'"
        assert item["widget"] in VALID_WIDGET_TYPES, \
          f"Item {item['key']} has invalid widget type: {item['widget']}"

  def test_sub_panel_items_have_key_and_widget(self, schema):
    for panel in schema["panels"]:
      for sp in _iter_all_sub_panels(panel):
        assert "id" in sp
        assert "items" in sp
        for item in sp["items"]:
          assert "key" in item
          assert "widget" in item
          assert item["widget"] in VALID_WIDGET_TYPES

  def test_vehicle_settings_structure(self, schema):
    vs = schema["vehicle_settings"]
    assert isinstance(vs, dict)
    for brand, data in vs.items():
      assert isinstance(brand, str)
      assert isinstance(data, dict), \
        f"vehicle_settings[{brand}] must be a dict {{title, items, ...}}"
      assert "items" in data, f"vehicle_settings[{brand}] missing 'items'"
      assert isinstance(data["items"], list)
      for item in data["items"]:
        assert "key" in item, f"Vehicle item for {brand} missing 'key'"
        assert "widget" in item, f"Vehicle item {item.get('key')} missing 'widget'"

  def test_no_duplicate_keys_across_panels(self, schema):
    """Each param key should appear in at most one panel to avoid double-rendering."""
    seen: dict[str, str] = {}  # key -> panel_id
    for panel in schema["panels"]:
      for item in _iter_panel_items(panel):
        key = item["key"]
        if key in seen:
          pytest.fail(f"Key '{key}' appears in both panel '{seen[key]}' and '{panel['id']}'")
        seen[key] = panel["id"]
        for sub in item.get("sub_items", []):
          sub_key = sub["key"]
          if sub_key in seen:
            pytest.fail(f"Sub-item key '{sub_key}' appears in both '{seen[sub_key]}' and '{panel['id']}'")
          seen[sub_key] = panel["id"]


class TestSchemaCoverage:
  def test_all_schema_keys_exist_in_params(self, schema, all_param_keys):
    """Every key referenced in the schema must exist in Params().all_keys()."""
    schema_keys = collect_all_keys(schema)
    missing = schema_keys - all_param_keys
    assert not missing, f"Schema references keys not in Params: {missing}"

  def test_all_capability_fields_are_declared(self, schema):
    """Every capability field used in rules must be in capability_fields."""
    declared = set(schema["capability_fields"])
    referenced = collect_capability_refs(schema)
    undeclared = referenced - declared
    assert not undeclared, f"Rules reference undeclared capability fields: {undeclared}"

  def test_capability_fields_match_constant(self, schema):
    """Schema capability_fields must match the CAPABILITY_FIELDS constant."""
    assert set(schema["capability_fields"]) == set(CAPABILITY_FIELDS)


class TestRuleWellFormedness:
  def _validate_rule(self, rule: dict, context: str = ""):
    """Recursively validate a single rule dict."""
    assert "type" in rule, f"Rule missing 'type' in {context}"
    rtype = rule["type"]
    assert rtype in VALID_RULE_TYPES, f"Invalid rule type '{rtype}' in {context}"

    if rtype == "capability":
      assert "field" in rule, f"Capability rule missing 'field' in {context}"
      assert "equals" in rule, f"Capability rule missing 'equals' in {context}"
    elif rtype == "param":
      assert "key" in rule, f"Param rule missing 'key' in {context}"
      assert "equals" in rule, f"Param rule missing 'equals' in {context}"
    elif rtype == "param_compare":
      assert "key" in rule, f"Param compare rule missing 'key' in {context}"
      assert "op" in rule, f"Param compare rule missing 'op' in {context}"
      assert rule["op"] in VALID_COMPARE_OPS, f"Invalid op '{rule['op']}' in {context}"
      assert "value" in rule, f"Param compare rule missing 'value' in {context}"
    elif rtype == "not":
      assert "condition" in rule, f"Not rule missing 'condition' in {context}"
      self._validate_rule(rule["condition"], context=f"{context} > not")
    elif rtype in ("any", "all"):
      assert "conditions" in rule, f"{rtype} rule missing 'conditions' in {context}"
      assert isinstance(rule["conditions"], list)
      for c in rule["conditions"]:
        self._validate_rule(c, context=f"{context} > {rtype}")

  def _validate_items(self, items: list[dict], context: str):
    for item in items:
      key = item.get("key", "unknown")
      for rules_field in ("visibility", "enablement"):
        rules = item.get(rules_field)
        if rules:
          assert isinstance(rules, list), f"{key}.{rules_field} must be a list"
          for rule in rules:
            self._validate_rule(rule, context=f"{context}.{key}.{rules_field}")
      for sub in item.get("sub_items", []):
        self._validate_items([sub], context=f"{context}.{key}")

  def _validate_section_rules(self, section: dict, context: str):
    for rules_field in ("visibility", "enablement"):
      rules = section.get(rules_field) or []
      for rule in rules:
        self._validate_rule(rule, context=f"{context}.{rules_field}")

  def test_all_panel_rules_well_formed(self, schema):
    for panel in schema["panels"]:
      self._validate_items(list(_iter_panel_items(panel)), context=f"panel:{panel['id']}")
      for sp in _iter_all_sub_panels(panel):
        self._validate_items(sp["items"], context=f"subpanel:{sp['id']}")
      for section in panel.get("sections", []):
        self._validate_section_rules(section, context=f"section:{panel['id']}.{section['id']}")

  def test_all_vehicle_rules_well_formed(self, schema):
    for brand, data in schema["vehicle_settings"].items():
      self._validate_items(_brand_items(data), context=f"vehicle:{brand}")

  def test_no_self_referencing_visibility(self, schema):
    """An item's visibility/enablement rules should not depend on its own key."""
    def _check_self_ref(item: dict, rules_field: str):
      key = item.get("key")
      for rule in item.get(rules_field, []):
        if rule.get("type") == "param" and rule.get("key") == key:
          pytest.fail(f"Item {key} has self-referencing {rules_field} rule")

    for panel in schema["panels"]:
      for item in _iter_panel_items(panel):
        _check_self_ref(item, "visibility")
        _check_self_ref(item, "enablement")

    for brand_data in schema.get("vehicle_settings", {}).values():
      for item in _brand_items(brand_data):
        _check_self_ref(item, "visibility")
        _check_self_ref(item, "enablement")


class TestKnownPanels:
  def test_expected_panels_exist(self, schema):
    panel_ids = {p["id"] for p in schema["panels"]}
    expected = {"steering", "cruise", "display", "visuals", "device", "software", "developer"}
    assert expected.issubset(panel_ids), f"Missing panels: {expected - panel_ids}"

  def test_mads_sub_panel_exists(self, schema):
    steering = next(p for p in schema["panels"] if p["id"] == "steering")
    sub_ids = {sp["id"] for sp in _iter_all_sub_panels(steering)}
    assert "mads_settings" in sub_ids

  def test_mutual_exclusion_torque_nnlc(self, schema):
    """EnforceTorqueControl and NNLC should have cross-param rules."""
    torque = nnlc = None
    for panel in schema["panels"]:
      for item in _iter_panel_items(panel):
        if item["key"] == "EnforceTorqueControl":
          torque = item
        elif item["key"] == "NeuralNetworkLateralControl":
          nnlc = item
    assert torque is not None, "EnforceTorqueControl item missing"
    assert nnlc is not None, "NeuralNetworkLateralControl item missing"
    torque_enable_keys = {r.get("key") for r in torque.get("enablement", []) if r.get("type") == "param"}
    assert "NeuralNetworkLateralControl" in torque_enable_keys
    nnlc_enable_keys = {r.get("key") for r in nnlc.get("enablement", []) if r.get("type") == "param"}
    assert "EnforceTorqueControl" in nnlc_enable_keys


class TestKnownVehicleSettings:
  def test_hyundai_has_longitudinal_tuning(self, schema):
    keys = {i["key"] for i in _brand_items(schema["vehicle_settings"].get("hyundai"))}
    assert "HyundaiLongitudinalTuning" in keys

  def test_toyota_has_enforce_stock_and_stop_go(self, schema):
    keys = {i["key"] for i in _brand_items(schema["vehicle_settings"].get("toyota"))}
    assert "ToyotaEnforceStockLongitudinal" in keys
    assert "ToyotaStopAndGoHack" in keys

  def test_tesla_has_coop_steering(self, schema):
    keys = {i["key"] for i in _brand_items(schema["vehicle_settings"].get("tesla"))}
    assert "TeslaCoopSteering" in keys

  def test_subaru_has_stop_and_go(self, schema):
    keys = {i["key"] for i in _brand_items(schema["vehicle_settings"].get("subaru"))}
    assert "SubaruStopAndGo" in keys
    assert "SubaruStopAndGoManualParkingBrake" in keys


class TestItemCompleteness:
  def _collect_all_items(self, schema):
    """Collect every item, including sub_items, across panels (sections + flat) + vehicle_settings."""
    items = []
    for panel in schema["panels"]:
      for item in _iter_panel_items(panel):
        items.append(item)
        for sub in item.get("sub_items", []):
          items.append(sub)
    for brand_data in schema.get("vehicle_settings", {}).values():
      for item in _brand_items(brand_data):
        items.append(item)
        for sub in item.get("sub_items", []):
          items.append(sub)
    return items

  def test_all_items_have_titles(self, schema):
    """Every item must have a title (metadata is inline, no enrichment fallback)."""
    missing = [i["key"] for i in self._collect_all_items(schema) if "title" not in i]
    if len(missing) > MAX_ALLOWED_MISSING_TITLES:
      pytest.fail(f"Items without titles ({len(missing)}): {missing[:10]}")

  def test_no_default_titles(self, schema):
    """No item should have title == key (forces human-readable titles)."""
    defaults = [i["key"] for i in self._collect_all_items(schema) if i.get("title") == i["key"]]
    assert not defaults, f"Items with default titles (title == key): {defaults}"

  def test_options_structure(self, schema):
    """Options must be list of {value, label} dicts."""
    for item in self._collect_all_items(schema):
      opts = item.get("options")
      if opts is None:
        continue
      assert isinstance(opts, list), f"{item['key']}: options must be a list"
      for opt in opts:
        assert isinstance(opt, dict), f"{item['key']}: each option must be a dict"
        assert "value" in opt, f"{item['key']}: option missing 'value': {opt}"
        assert "label" in opt, f"{item['key']}: option missing 'label': {opt}"

  def test_numeric_constraints(self, schema):
    """If min/max/step present, all three must be present and min < max."""
    for item in self._collect_all_items(schema):
      has_min = "min" in item
      has_max = "max" in item
      has_step = "step" in item
      if has_min or has_max or has_step:
        assert has_min and has_max and has_step, \
          f"{item['key']}: must have all of min/max/step or none"
        assert item["min"] < item["max"], \
          f"{item['key']}: min ({item['min']}) must be < max ({item['max']})"

  def test_known_param_has_options(self, schema):
    """LongitudinalPersonality should have 3 options."""
    cruise = next(p for p in schema["panels"] if p["id"] == "cruise")
    lp = next((i for i in _iter_panel_items(cruise) if i["key"] == "LongitudinalPersonality"), None)
    assert lp is not None
    assert "options" in lp
    assert len(lp["options"]) == 3
