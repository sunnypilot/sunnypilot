"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import os
import unittest
from unittest.mock import patch
from openpilot.common.file_chunker import open_file_chunked
from openpilot.sunnypilot.modeld_v2.helpers import load_oob
from tinygrad.device import Device


class TestLegacyModels(unittest.TestCase):
  def test_legacy_model_load(self):
    base_name = os.environ.get("MODEL_BASE_NAME")
    if not base_name:
      raise unittest.SkipTest("MODEL_BASE_NAME env var not set, skipping integration test.")
    chunk_dir = os.environ.get("MODEL_CHUNK_DIR", "/tmp/model_chunks")
    base_path = os.path.join(chunk_dir, base_name)

    try:
      f = open_file_chunked(base_path)
    except Exception as error:
      self.fail(f"Failed to open chunked file {base_path}: {error}")
    self.addCleanup(f.close)

    real_getitem = Device.__class__.__getitem__

    def safe_getitem(device_self, ix):
      if ix == "QCOM" and not os.path.exists("/dev/kgsl-3d0"):
        return real_getitem(device_self, "CPU")
      if ix == "AMD" and not os.path.exists("/dev/kfd"):
        return real_getitem(device_self, "CPU")
      return real_getitem(device_self, ix)

    with patch.object(Device.__class__, "__getitem__", safe_getitem):
      obj = load_oob(f)

    assert isinstance(obj, dict), "Parsed object is not a dictionary"
    assert "metadata" in obj, "Metadata key is missing"
