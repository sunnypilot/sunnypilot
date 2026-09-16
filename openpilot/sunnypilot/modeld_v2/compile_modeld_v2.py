#!/usr/bin/env python3
import runpy
import os

from openpilot.sunnypilot.modeld_v2.compile_modeld import _patch_fastenum_serialization


if __name__ == "__main__":
  _patch_fastenum_serialization()
  upstream_script = os.path.join(os.environ.get("TINYGRAD_PATH", "tinygrad_repo"), "examples/openpilot/compile_onnx.py")
  runpy.run_path(upstream_script, run_name="__main__")
