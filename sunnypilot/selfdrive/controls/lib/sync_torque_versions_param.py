"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json
import os

from openpilot.common.basedir import BASEDIR
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog

VERSIONS_JSON_OUT = os.path.join(BASEDIR, "sunnypilot", "selfdrive", "controls", "lib", "latcontrol_torque_versions.json")


def update_torque_versions_param():
  with open(VERSIONS_JSON_OUT) as f:
    current_versions = json.load(f)

  params = Params()
  if params.get("TorqueControlTuneVersions") != current_versions:
    params.put("TorqueControlTuneVersions", current_versions)
    cloudlog.warning("Updated TorqueControlTuneVersions param with latest versions list")
  else:
    cloudlog.warning("TorqueControlTuneVersions param is up to date, no need to update")
