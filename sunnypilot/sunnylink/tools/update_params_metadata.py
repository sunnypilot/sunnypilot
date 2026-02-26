#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json
import os

from openpilot.common.basedir import BASEDIR
from openpilot.common.params import Params

METADATA_PATH = os.path.join(os.path.dirname(__file__), "../params_metadata.json")
TORQUE_VERSIONS_JSON = os.path.join(BASEDIR, "sunnypilot", "selfdrive", "controls", "lib", "latcontrol_torque_versions.json")


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

  # update torque versions param
  update_torque_versions_param()

def update_torque_versions_param():
  with open(TORQUE_VERSIONS_JSON) as f:
    current_versions = json.load(f)

  try:
    with open(METADATA_PATH) as f:
      params_metadata = json.load(f)

    options = [{"value": "", "label": "Default"}]
    for version_key, version_data in current_versions.items():
      version_value = float(version_data["version"])
      options.append({"value": version_value, "label": str(version_key)})

    if "TorqueControlTune" in params_metadata:
      params_metadata["TorqueControlTune"]["options"] = options

      with open(METADATA_PATH, 'w') as f:
        json.dump(params_metadata, f, indent=2)
        f.write('\n')

      print(f"Updated TorqueControlTune options in params_metadata.json with {len(options)} options: \n{options}")

  except Exception as e:
    print(f"Failed to update TorqueControlTune versions in params_metadata.json: {e}")

if __name__ == "__main__":
  main()
