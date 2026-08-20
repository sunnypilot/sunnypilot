"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from openpilot.sunnypilot import get_file_hash
from openpilot.sunnypilot.models.default_model import (MODEL_HASH_PATH, BIG_MODEL_HASH_PATH,
                                                       SUPERCOMBO_ONNX_PATH, BIG_SUPERCOMBO_ONNX_PATH)
import hashlib
from openpilot.common.test import OpenpilotTestCase


class TestDefaultModel(OpenpilotTestCase):
  def test_compare_onnx_hash(self):
    supercombo_hash = get_file_hash(SUPERCOMBO_ONNX_PATH)

    expected_hash = hashlib.sha256(supercombo_hash.encode()).hexdigest()

    with open(MODEL_HASH_PATH) as f:
      current_hash = f.read().strip()

    assert expected_hash == current_hash, "Run sunnypilot/models/default_model.py to update the default model name and hash"

  def test_compare_big_onnx_hash(self):
    big_supercombo_hash = get_file_hash(BIG_SUPERCOMBO_ONNX_PATH)

    expected_hash = hashlib.sha256(big_supercombo_hash.encode()).hexdigest()

    with open(BIG_MODEL_HASH_PATH) as f:
      current_hash = f.read().strip()

    assert expected_hash == current_hash, "Run sunnypilot/models/default_model.py to update the default big model name and hash"
