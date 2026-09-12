"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import hashlib
import os

from openpilot.common.basedir import BASEDIR

# the scripts modeld/SConscript rebuilds the pkls for; default models are keyed on these next to tinygrad_ref
COMPILE_SCRIPTS = (
  'openpilot/selfdrive/modeld/compile_modeld.py',
  'openpilot/selfdrive/modeld/get_model_metadata.py',
  'openpilot/selfdrive/modeld/compile_dm_warp.py',
  'openpilot/system/camerad/cameras/nv12_info.py',
  'openpilot/common/hardware/hw.py',
)


def get_compile_ref() -> str:
  h = hashlib.sha256()
  for path in COMPILE_SCRIPTS:
    with open(os.path.join(BASEDIR, path), "rb") as f:
      h.update(f"{path}\n".encode())
      h.update(f.read())
  return h.hexdigest()


if __name__ == "__main__":
  print(get_compile_ref())
