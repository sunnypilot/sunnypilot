"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Sentinel tests for the capabilities payload contract. PROTOCOL_VERSION is the
wire-protocol version observable by the dashboard; bumping it is a breaking
change and must be intentional. KNOWN_PROTOCOL_VERSIONS pins the set we
explicitly support — when the constant is bumped, this list must be edited in
the same commit so the bump shows up in code review.
"""
from __future__ import annotations

import pytest

from openpilot.sunnypilot.sunnylink.capabilities import (
  CAPABILITY_DEFAULTS,
  CAPABILITY_FIELDS,
  CAPABILITY_LABELS,
  PROTOCOL_VERSION,
  generate_capabilities,
)


KNOWN_PROTOCOL_VERSIONS = (1,)
LATEST_KNOWN = max(KNOWN_PROTOCOL_VERSIONS)


@pytest.fixture(scope="module")
def caps():
  return generate_capabilities()


class TestProtocolVersion:
  def test_protocol_version_in_capability_fields(self):
    assert "protocol_version" in CAPABILITY_FIELDS

  def test_protocol_version_has_label(self):
    assert "protocol_version" in CAPABILITY_LABELS

  def test_protocol_version_default_is_set(self):
    assert CAPABILITY_DEFAULTS.get("protocol_version") == PROTOCOL_VERSION

  def test_protocol_version_emitted(self, caps):
    assert "protocol_version" in caps
    assert isinstance(caps["protocol_version"], int)
    assert caps["protocol_version"] >= 1

  def test_protocol_version_matches_constant(self, caps):
    assert caps["protocol_version"] == PROTOCOL_VERSION

  def test_protocol_version_is_known(self):
    """Sentinel against accidental bumps. If you intentionally bumped the
    protocol, edit KNOWN_PROTOCOL_VERSIONS in the same commit."""
    assert PROTOCOL_VERSION in KNOWN_PROTOCOL_VERSIONS, (
      f"PROTOCOL_VERSION={PROTOCOL_VERSION} is not in KNOWN_PROTOCOL_VERSIONS={KNOWN_PROTOCOL_VERSIONS}. "
      "If this bump is intentional, add it to KNOWN_PROTOCOL_VERSIONS."
    )

  def test_protocol_version_matches_latest_known(self):
    assert PROTOCOL_VERSION == LATEST_KNOWN, (
      "Test invariant: PROTOCOL_VERSION must equal max(KNOWN_PROTOCOL_VERSIONS)."
    )


class TestOpaquePerBrandFlags:
  def test_subaru_has_sng_field_present(self):
    assert "subaru_has_sng" in CAPABILITY_FIELDS

  def test_hyundai_alpha_long_available_field_present(self):
    assert "hyundai_alpha_long_available" in CAPABILITY_FIELDS

  def test_subaru_has_sng_default_false(self, caps):
    assert caps["subaru_has_sng"] is False

  def test_hyundai_alpha_long_available_default_false(self, caps):
    assert caps["hyundai_alpha_long_available"] is False


class TestCapabilitiesShape:
  def test_all_fields_present(self, caps):
    for field in CAPABILITY_FIELDS:
      assert field in caps, f"capabilities missing {field}"

  def test_all_fields_have_labels(self):
    for field in CAPABILITY_FIELDS:
      assert field in CAPABILITY_LABELS, f"CAPABILITY_LABELS missing {field}"

  def test_string_defaults_are_strings(self, caps):
    assert isinstance(caps["brand"], str)
    assert isinstance(caps["steer_control_type"], str)
    assert isinstance(caps["device_type"], str)
