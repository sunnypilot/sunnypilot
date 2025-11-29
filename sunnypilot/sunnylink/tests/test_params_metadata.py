"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json

from openpilot.sunnypilot.sunnylink.athena.sunnylinkd import getParamsAllKeysV1, METADATA_PATH


def test_get_params_all_keys_v1():
  """
  Test the getParamsAllKeysV1 API endpoint.

  Why:
  This endpoint is used by the UI (and potentially external tools) to fetch the list of
  available parameters along with their metadata (titles, descriptions, options, constraints).
  We need to ensure it returns the correct structure and that the metadata from
  params_metadata.json is correctly merged into the response.

  Expected:
  - The response should contain a "keys" field which is a JSON string of a list of parameters.
  - Each parameter object should have "key", "type", "default_value", and optionally "_extra".
  - The "_extra" field should contain the rich metadata (title, options, min/max, etc.) matching
    the source of truth (params_metadata.json).
  """
  response = getParamsAllKeysV1()
  assert "keys" in response

  keys_json = response["keys"]
  params_list = json.loads(keys_json)

  assert isinstance(params_list, list)
  assert len(params_list) > 0

  # Check structure of first item
  first_param = params_list[0]
  assert "key" in first_param
  assert "type" in first_param
  assert "default_value" in first_param

  if "_extra" in first_param:
    assert isinstance(first_param["_extra"], dict)
    assert "default" not in first_param["_extra"]
    assert "type" not in first_param["_extra"]

  # Load the source of truth
  with open(METADATA_PATH) as f:
    metadata = json.load(f)

  # Verify that the API response matches the metadata file for a few sample keys
  # This ensures the plumbing is working without being brittle to content changes

  # 1. Check a key that should have metadata
  keys_with_metadata = [k for k in params_list if k["key"] in metadata]
  assert len(keys_with_metadata) > 0, "No parameters found that match metadata keys"

  for param in keys_with_metadata[:5]:  # Check first 5 matches
    key = param["key"]
    expected_meta = metadata[key]

    assert "_extra" in param, f"Parameter {key} should have _extra field"
    actual_meta = param["_extra"]

    # Verify all fields in JSON are present in the API response
    for meta_key, meta_val in expected_meta.items():
      assert meta_key in actual_meta, f"Missing {meta_key} in API response for {key}"
      assert actual_meta[meta_key] == meta_val, f"Mismatch for {key}.{meta_key}: expected {meta_val}, got {actual_meta[meta_key]}"

  # 2. Check that we are correctly serving options if they exist
  params_with_options = [k for k in keys_with_metadata if "options" in k.get("_extra", {})]
  if params_with_options:
    param = params_with_options[0]
    key = param["key"]
    assert isinstance(param["_extra"]["options"], list), f"Options for {key} should be a list"
    assert param["_extra"]["options"] == metadata[key]["options"]

  # 3. Check that we are correctly serving numeric constraints if they exist
  params_with_constraints = [k for k in keys_with_metadata if "min" in k.get("_extra", {})]
  if params_with_constraints:
    param = params_with_constraints[0]
    key = param["key"]
    assert param["_extra"]["min"] == metadata[key]["min"]
    assert param["_extra"]["max"] == metadata[key]["max"]
    assert param["_extra"]["step"] == metadata[key]["step"]
