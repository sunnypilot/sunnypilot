#!/usr/bin/env python3
import json
import os
import pytest
from openpilot.common.params import Params
from openpilot.sunnypilot.sunnylink.athena.sunnylinkd import METADATA_PATH


def test_metadata_json_exists():
  assert os.path.exists(METADATA_PATH), f"Metadata file not found at {METADATA_PATH}"


def test_metadata_json_valid():
  with open(METADATA_PATH, "r") as f:
    try:
      data = json.load(f)
    except json.JSONDecodeError:
      pytest.fail("Metadata file is not valid JSON")

    assert isinstance(data, dict), "Metadata root must be a dictionary"


def test_all_params_have_metadata():
  params = Params()
  all_keys = [k.decode('utf-8') for k in params.all_keys()]

  with open(METADATA_PATH, "r") as f:
    metadata = json.load(f)

  missing_keys = [key for key in all_keys if key not in metadata]

  if missing_keys:
    pytest.fail(
      f"The following parameters are missing from metadata: {missing_keys}. "
      f"Please run 'python3 sunnypilot/sunnylink/tools/update_params_metadata.py' to update."
    )


def test_metadata_keys_exist_in_params():
  params = Params()
  all_keys = set([k.decode('utf-8') for k in params.all_keys()])

  with open(METADATA_PATH, "r") as f:
    metadata = json.load(f)

  extra_keys = [key for key in metadata.keys() if key not in all_keys]

  if extra_keys:
    print(f"Warning: The following keys in metadata do not exist in Params: {extra_keys}")


def test_no_default_titles():
  with open(METADATA_PATH, "r") as f:
    metadata = json.load(f)

  default_title_keys = [key for key, meta in metadata.items() if meta.get("title") == key]

  if default_title_keys:
    pytest.fail(
      f"The following parameters have default titles (title == key): {default_title_keys}. Please update 'params_metadata.json' with descriptive titles."
    )
