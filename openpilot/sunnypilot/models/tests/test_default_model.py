"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import os
import subprocess

from openpilot.sunnypilot import get_file_hash
from openpilot.sunnypilot.models.default_model import MODEL_HASH_PATH, SUPERCOMBO_ONNX_PATH, BIG_MODEL_HASH_PATH, \
                                                      BIG_SUPERCOMBO_ONNX_PATH, _read_model_name_fields
import hashlib
from openpilot.common.test import OpenpilotTestCase


def _get_lfs_oid(path: str) -> str:
  """Extract the LFS OID (SHA256 of actual content) from git, works whether the file is smudged or not."""
  pointer = subprocess.check_output(["git", "show", f"HEAD:{path}"], text=True)
  for line in pointer.splitlines():
    if line.startswith("oid sha256:"):
      return line.split(":", 1)[1]
  raise ValueError(f"No LFS OID found for {path}")


class TestDefaultModel(OpenpilotTestCase):
  def test_compare_onnx_hashes(self):
    fields = _read_model_name_fields()
    supercombo_hash = get_file_hash(SUPERCOMBO_ONNX_PATH)
    fingerprint = f"{supercombo_hash}:{fields.get('DEFAULT_MODEL', '')}:{fields.get('DEFAULT_MODEL_REF', '')}"
    combined_hash = hashlib.sha256(fingerprint.encode()).hexdigest()

    with open(MODEL_HASH_PATH) as f:
      current_hash = f.read().strip()

    assert combined_hash == current_hash, "Run openpilot/sunnypilot/models/default_model.py to update the default model name and hash"

  def test_compare_big_onnx_hashes(self):
    if not os.path.exists(BIG_SUPERCOMBO_ONNX_PATH):
      self.skipTest("big_driving_supercombo.onnx not present")

    fields = _read_model_name_fields()
    oid = _get_lfs_oid(os.path.relpath(BIG_SUPERCOMBO_ONNX_PATH, os.getcwd()))
    big_fingerprint = f"{oid}:{fields.get('DEFAULT_BIG_MODEL', '')}:{fields.get('DEFAULT_BIG_MODEL_REF', '')}"
    combined_hash = hashlib.sha256(big_fingerprint.encode()).hexdigest()

    with open(BIG_MODEL_HASH_PATH) as f:
      current_hash = f.read().strip()

    assert combined_hash == current_hash, "Run openpilot/sunnypilot/models/default_model.py to update the default model name and hash"
