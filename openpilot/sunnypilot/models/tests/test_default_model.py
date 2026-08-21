"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from openpilot.sunnypilot import get_file_hash
from openpilot.sunnypilot.models import default_model
from openpilot.sunnypilot.models.model_name import DEFAULT_MODEL, DEFAULT_BIG_MODEL
import hashlib
from openpilot.common.test import OpenpilotTestCase


class TestDefaultModel(OpenpilotTestCase):
  def test_compare_onnx_hashes(self):
    supercombo_hash = get_file_hash(default_model.SUPERCOMBO_ONNX_PATH)

    combined_hash = hashlib.sha256(supercombo_hash.encode()).hexdigest()

    with open(default_model.MODEL_HASH_PATH) as f:
      current_hash = f.read().strip()

    assert combined_hash == current_hash, "Run openpilot/sunnypilot/models/default_model.py to update the default model name and hash"

  def test_default_model_follows_usbgpu(self, monkeypatch):
    monkeypatch.setattr(default_model, "usbgpu_present", lambda: True)
    assert default_model.get_default_model() == DEFAULT_BIG_MODEL

    monkeypatch.setattr(default_model, "usbgpu_present", lambda: False)
    assert default_model.get_default_model() == DEFAULT_MODEL
