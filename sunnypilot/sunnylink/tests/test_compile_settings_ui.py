"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Tests for the settings_ui_src/ -> settings_ui.json compiler. Covers:
  - Roundtrip: compiled output matches the checked-in settings_ui.json
  - $ref macro resolution semantics (list-splice, scalar-substitute, depth, cycles)
  - Per-page tree integrity (every page has id; vehicle page emits to vehicle_settings)

Does not cover device-side generator (test_settings_schema.py) or per-bug
regression (test_settings_changes.py); those continue to validate the
compiled output once the compiler has produced it.
"""
from __future__ import annotations

import json
import os

import pytest
import yaml

from openpilot.sunnypilot.sunnylink.tools.compile_settings_ui import (
  CompileError,
  DEFAULT_OUT,
  DEFAULT_SRC,
  _resolve_refs,
  compile_schema,
)


@pytest.fixture(scope="module")
def compiled() -> dict:
  return compile_schema(DEFAULT_SRC)


@pytest.fixture(scope="module")
def committed() -> dict:
  with open(DEFAULT_OUT) as f:
    return json.load(f)


class TestRoundtrip:
  def test_compiled_matches_committed(self, compiled, committed):
    """Compiled output must match the checked-in JSON."""
    assert compiled == committed

  def test_committed_file_is_canonical(self):
    """Compiled output must byte-match the checked-in file (including trailing newline).
    Drift means someone edited settings_ui.json by hand instead of editing settings_ui_src/."""
    schema = compile_schema(DEFAULT_SRC)
    rendered = json.dumps(schema, indent=2) + "\n"
    with open(DEFAULT_OUT) as f:
      current = f.read()
    assert current == rendered, "settings_ui.json out of sync — run compile_settings_ui.py"


class TestRefResolution:
  def test_list_context_splices(self):
    macros = {"a": [{"type": "offroad_only"}], "b": [{"type": "not_engaged"}]}
    out = _resolve_refs([{"$ref": "#/macros/a"}, {"$ref": "#/macros/b"}], macros)
    assert out == [{"type": "offroad_only"}, {"type": "not_engaged"}]

  def test_scalar_context_substitutes(self):
    macros = {"x": {"type": "capability", "field": "brand", "equals": "tesla"}}
    out = _resolve_refs({"condition": {"$ref": "#/macros/x"}}, macros)
    assert out == {"condition": {"type": "capability", "field": "brand", "equals": "tesla"}}

  def test_chained_ref_resolves(self):
    macros = {
      "leaf": [{"type": "offroad_only"}],
      "middle": [{"$ref": "#/macros/leaf"}],
    }
    out = _resolve_refs([{"$ref": "#/macros/middle"}], macros)
    assert out == [{"type": "offroad_only"}]

  def test_unknown_macro_raises(self):
    with pytest.raises(CompileError, match="unknown macro"):
      _resolve_refs([{"$ref": "#/macros/missing"}], {})

  def test_cycle_raises(self):
    macros = {"a": [{"$ref": "#/macros/b"}], "b": [{"$ref": "#/macros/a"}]}
    with pytest.raises(CompileError, match="cycle"):
      _resolve_refs([{"$ref": "#/macros/a"}], macros)

  def test_depth_limit(self):
    # Depth 4 chain should fail (limit is 3).
    macros = {
      "l1": [{"$ref": "#/macros/l2"}],
      "l2": [{"$ref": "#/macros/l3"}],
      "l3": [{"$ref": "#/macros/l4"}],
      "l4": [{"type": "offroad_only"}],
    }
    with pytest.raises(CompileError, match="depth"):
      _resolve_refs([{"$ref": "#/macros/l1"}], macros)

  def test_invalid_ref_scheme(self):
    with pytest.raises(CompileError, match="unsupported"):
      _resolve_refs([{"$ref": "https://example.com/x"}], {})

  def test_scalar_macro_in_list_context_raises(self):
    macros = {"x": {"type": "offroad_only"}}  # macro is a single rule (dict), not a list
    with pytest.raises(CompileError, match="must resolve to a list"):
      _resolve_refs([{"$ref": "#/macros/x"}], macros)


class TestCompiledShape:
  def test_panels_present(self, compiled):
    assert isinstance(compiled["panels"], list)
    assert len(compiled["panels"]) == 9
    panel_ids = {p["id"] for p in compiled["panels"]}
    assert {"steering", "cruise", "display", "visuals", "toggles",
            "device", "software", "developer", "models"} <= panel_ids

  def test_vehicle_settings_consistent_shape(self, compiled):
    """Each brand in vehicle_settings must have {title, description, items}."""
    for brand, data in compiled["vehicle_settings"].items():
      assert isinstance(data, dict), f"{brand}: expected object, got {type(data).__name__}"
      assert "title" in data, f"{brand}: missing title"
      assert "description" in data, f"{brand}: missing description"
      assert "items" in data, f"{brand}: missing items"

  def test_no_dangling_refs_after_compile(self, compiled):
    """All $ref objects must be resolved during compilation."""
    def walk(node):
      if isinstance(node, dict):
        if "$ref" in node:
          pytest.fail(f"unresolved $ref: {node}")
        for v in node.values():
          walk(v)
      elif isinstance(node, list):
        for x in node:
          walk(x)
    walk(compiled)


class TestSourceTreeIntegrity:
  def test_macros_yaml_well_formed(self):
    with open(os.path.join(DEFAULT_SRC, "_macros.yaml")) as f:
      doc = yaml.safe_load(f)
    assert "macros" in doc
    for name, body in doc["macros"].items():
      assert name.replace("_", "").isalnum(), f"macro name '{name}' must be alphanumeric_"
      assert body, f"macro '{name}' empty"

  def test_pages_dir_well_formed(self):
    pages_dir = os.path.join(DEFAULT_SRC, "pages")
    assert os.path.isdir(pages_dir), "pages/ directory missing"
    page_files = sorted(fn for fn in os.listdir(pages_dir) if fn.endswith(".yaml"))
    # 9 panels + 1 vehicle = 10
    assert len(page_files) == 10, f"expected 10 pages, found {len(page_files)}: {page_files}"

  def test_every_page_has_id(self):
    pages_dir = os.path.join(DEFAULT_SRC, "pages")
    for fn in sorted(os.listdir(pages_dir)):
      if not fn.endswith(".yaml"):
        continue
      path = os.path.join(pages_dir, fn)
      with open(path) as f:
        doc = yaml.safe_load(f)
      assert isinstance(doc, dict), f"{path}: top-level must be a mapping"
      assert "id" in doc, f"{path}: page missing 'id'"
      # File basename should match page id (modulo .yaml extension).
      expected_id = os.path.splitext(fn)[0]
      assert doc["id"] == expected_id, (
        f"{path}: page id '{doc['id']}' must match filename '{expected_id}'"
      )

  def test_vehicle_page_kind(self):
    """vehicle.yaml must declare kind: vehicle so it routes to vehicle_settings."""
    path = os.path.join(DEFAULT_SRC, "pages", "vehicle.yaml")
    with open(path) as f:
      doc = yaml.safe_load(f)
    assert doc.get("kind") == "vehicle", "vehicle.yaml must declare kind: vehicle"
