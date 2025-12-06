"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json
import os
import pytest

from openpilot.common.params import Params
from openpilot.sunnypilot.sunnylink.athena.sunnylinkd import METADATA_PATH


def test_metadata_json_exists():
  """
  Test that the params_metadata.json file exists at the expected path.

  Why:
  The metadata file is the source of truth for parameter descriptions, options, and constraints.
  If it's missing, the UI will not be able to display rich information for parameters.

  Expected:
  The file should exist at sunnypilot/sunnylink/params_metadata.json.
  """
  assert os.path.exists(METADATA_PATH), f"Metadata file not found at {METADATA_PATH}"


def test_metadata_json_valid():
  """
  Test that the params_metadata.json file contains valid JSON.

  Why:
  Invalid JSON will cause the metadata loading to fail, potentially crashing the UI or
  resulting in missing metadata.

  Expected:
  The file content should be parseable as a JSON object (dictionary).
  """
  with open(METADATA_PATH) as f:
    try:
      data = json.load(f)
    except json.JSONDecodeError:
      pytest.fail("Metadata file is not valid JSON")

    assert isinstance(data, dict), "Metadata root must be a dictionary"


def test_all_params_have_metadata():
  """
  Test that every parameter in the codebase has a corresponding entry in params_metadata.json.

  Why:
  We want to ensure 100% coverage of parameter metadata. Any parameter added to the codebase
  should also be documented in the metadata file.

  Expected:
  There should be no parameters in Params() that are missing from the metadata file.
  If this fails, run 'python3 sunnypilot/sunnylink/tools/update_params_metadata.py'.
  """
  params = Params()
  all_keys = [k.decode('utf-8') for k in params.all_keys()]

  with open(METADATA_PATH) as f:
    metadata = json.load(f)

  missing_keys = [key for key in all_keys if key not in metadata]

  if missing_keys:
    pytest.fail(
      f"The following parameters are missing from metadata: {missing_keys}. "
      + "Please run 'python3 sunnypilot/sunnylink/tools/update_params_metadata.py' to update."
    )


def test_metadata_keys_exist_in_params():
  """
  Test that all keys in params_metadata.json actually exist in the codebase.

  Why:
  We want to avoid stale metadata for parameters that have been removed or renamed.
  This keeps the metadata file clean and relevant.

  Expected:
  There should be no keys in the metadata file that are not present in Params().
  This prints a warning rather than failing, as it's less critical than missing metadata.
  """
  params = Params()
  all_keys = {k.decode('utf-8') for k in params.all_keys()}

  with open(METADATA_PATH) as f:
    metadata = json.load(f)

  extra_keys = [key for key in metadata.keys() if key not in all_keys]

  if extra_keys:
    print(f"Warning: The following keys in metadata do not exist in Params: {extra_keys}")


def test_no_default_titles():
  """
  Test that no parameter has a title that is identical to its key.

  Why:
  The default behavior of the update script is to set the title equal to the key.
  We want to force developers to provide human-readable, descriptive titles for all parameters.

  Expected:
  No parameter metadata should have 'title' == 'key'.
  """
  with open(METADATA_PATH) as f:
    metadata = json.load(f)

  default_title_keys = [key for key, meta in metadata.items() if meta.get("title") == key]

  if default_title_keys:
    pytest.fail(
      f"The following parameters have default titles (title == key): {default_title_keys}. "
      + "Please update 'params_metadata.json' with descriptive titles."
    )


def test_options_structure():
  """
  Test that the 'options' field in metadata follows the correct structure.

  Why:
  The UI expects 'options' to be a list of objects with 'value' and 'label' keys.
  Incorrect structure will break the UI rendering for dropdowns/toggles.

  Expected:
  If 'options' is present, it must be a list of dicts, and each dict must have 'value' and 'label'.
  """
  with open(METADATA_PATH) as f:
    metadata = json.load(f)

  for key, meta in metadata.items():
    if "options" in meta:
      options = meta["options"]
      assert isinstance(options, list), f"Options for {key} must be a list"
      for option in options:
        assert isinstance(option, dict), f"Option in {key} must be a dictionary"
        assert "value" in option, f"Option in {key} must have a 'value' key"
        assert "label" in option, f"Option in {key} must have a 'label' key"


def test_numeric_constraints():
  """
  Test that numeric parameters have valid 'min', 'max', and 'step' constraints.

  Why:
  The UI uses these constraints to validate user input and render sliders/steppers.
  Missing or invalid constraints can lead to UI bugs or invalid parameter values.

  Expected:
  If any of min/max/step is present, ALL of them must be present.
  They must be numbers (int/float), and min must be less than max.
  """
  with open(METADATA_PATH) as f:
    metadata = json.load(f)

  for key, meta in metadata.items():
    if "min" in meta or "max" in meta or "step" in meta:
      assert "min" in meta, f"Numeric param {key} must have 'min'"
      assert "max" in meta, f"Numeric param {key} must have 'max'"
      assert "step" in meta, f"Numeric param {key} must have 'step'"

      assert isinstance(meta["min"], (int, float)), f"Min for {key} must be number"
      assert isinstance(meta["max"], (int, float)), f"Max for {key} must be number"
      assert isinstance(meta["step"], (int, float)), f"Step for {key} must be number"
      assert meta["min"] < meta["max"], f"Min must be less than max for {key}"


def test_known_params_metadata():
  """
  Test specific known parameters to ensure they have the expected rich metadata.

  Why:
  This acts as a spot check to ensure that our rich metadata population logic is working correctly
  and that critical parameters (like LongitudinalPersonality) have their options and constraints preserved.

  Expected:
  'LongitudinalPersonality' should have 3 options (Aggressive, Standard, Relaxed).
  'CustomAccLongPressIncrement' should have min=1, max=10, step=1.
  """
  with open(METADATA_PATH) as f:
    metadata = json.load(f)

  # Check an enum-like param
  lp = metadata.get("LongitudinalPersonality")
  assert lp is not None
  assert "options" in lp
  assert len(lp["options"]) == 3
  assert lp["options"][0]["label"] == "Aggressive"
  assert lp["options"][0]["value"] == 0

  # Check a numeric param
  acc_long = metadata.get("CustomAccLongPressIncrement")
  assert acc_long is not None
  assert acc_long["min"] == 1
  assert acc_long["max"] == 10
  assert acc_long["step"] == 1
