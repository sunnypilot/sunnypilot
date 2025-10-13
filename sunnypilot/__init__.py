"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from enum import IntEnum
import hashlib

PARAMS_UPDATE_PERIOD = 3  # seconds


def get_file_hash(path: str) -> str:
  sha256_hash = hashlib.sha256()
  with open(path, "rb") as f:
    for byte_block in iter(lambda: f.read(4096), b""):
      sha256_hash.update(byte_block)
  return sha256_hash.hexdigest()


class IntEnumBase(IntEnum):
  @classmethod
  def min(cls):
    return min(cls)

  @classmethod
  def max(cls):
    return max(cls)


def get_sanitize_int_param(key: str, min_val: int, max_val: int, params) -> int:
  val: int = params.get(key, return_default=True)
  clipped_val = max(min_val, min(max_val, val))

  if clipped_val != val:
    params.put(key, clipped_val)

  return clipped_val
