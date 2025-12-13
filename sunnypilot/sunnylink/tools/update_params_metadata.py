#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json
import os

from openpilot.common.params import Params

METADATA_PATH = os.path.join(os.path.dirname(__file__), "../params_metadata.json")


def main():
  params = Params()
  all_keys = params.all_keys()

  if os.path.exists(METADATA_PATH):
    with open(METADATA_PATH) as f:
      try:
        data = json.load(f)
      except json.JSONDecodeError:
        data = {}
  else:
    data = {}

  # Add new keys
  for key in all_keys:
    key_str = key.decode("utf-8")
    if key_str not in data:
      print(f"Adding new key: {key_str}")
      data[key_str] = {
        "title": key_str,
        "description": "",
      }

  # Remove deleted keys
  # keys_to_remove = [k for k in data.keys() if k.encode("utf-8") not in all_keys]
  # for k in keys_to_remove:
  #   print(f"Removing deleted key: {k}")
  #   del data[k]

  # Sort keys
  sorted_data = dict(sorted(data.items()))

  with open(METADATA_PATH, "w") as f:
    json.dump(sorted_data, f, indent=2)
    f.write("\n")

  print(f"Updated {METADATA_PATH}")


if __name__ == "__main__":
  main()
