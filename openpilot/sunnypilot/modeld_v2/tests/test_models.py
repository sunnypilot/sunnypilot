"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import os

from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.modeld_v2.helpers import PlainJit, load_model


class TestRegistryModels(OpenpilotTestCase):
  def test_model_loads(self):
    if not (base_name := os.environ.get("MODEL_BASE_NAME")):
      self.skipTest("MODEL_BASE_NAME env var not set, skipping integration test.")
    bundle = load_model(os.path.join(os.environ.get("MODEL_DIR", "/tmp/models"), base_name), {"QCOM": "CPU", "AMD": "CPU"}, verify=False, cache=False)
    jits = [value for value in bundle.values() if isinstance(value, PlainJit)]
    assert "metadata" in bundle and jits and all(len(jit.captured.linear.src) > 0 for jit in jits)
