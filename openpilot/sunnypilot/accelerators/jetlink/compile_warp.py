#!/usr/bin/env python3
"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Build the comma-side warp JIT. Invoked by accelerators/SConscript.

Mirrors upstream's compile_dm_warp.py and stays as thin: everything about what
gets captured lives in warp_cache, so jetlinkd's fallback builds the same pickle.
"""
import argparse

from openpilot.selfdrive.modeld.compile_modeld import _parse_size
from openpilot.sunnypilot.accelerators.jetlink.warp_cache import compile_warp

if __name__ == "__main__":
  p = argparse.ArgumentParser()
  p.add_argument('--camera-resolution', type=_parse_size, required=True, help='camera resolution WxH')
  p.add_argument('--model-size', type=_parse_size, required=True, help='model input WxH')
  p.add_argument('--output', required=True)
  args = p.parse_args()

  cam_w, cam_h = args.camera_resolution
  model_w, model_h = args.model_size
  print(f"Compiling jetlink warp for {cam_w}x{cam_h} -> {model_w}x{model_h}...")
  out = compile_warp(cam_w, cam_h, model_w, model_h, out=args.output)
  print(f"  Saved to {out}")
