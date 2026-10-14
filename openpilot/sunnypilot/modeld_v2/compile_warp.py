#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import argparse
import numpy as np

from openpilot.sunnypilot.modeld_v2.helpers import PlainJit, write_bundle
from openpilot.sunnypilot.modeld_v2.plain_artifact_compiler import capture_frame, record_kernel_linear, serialize_jit


def main():
  parser = argparse.ArgumentParser(description="Compile the two-frame yuv420 camera warp into a plain tinygrad artifact")
  parser.add_argument("--frame", required=True, help="width,height,stride,y_height,uv_height,buffer_size")
  parser.add_argument("--warp-to", required=True, help="model input WxH")
  parser.add_argument("--output", required=True)
  args = parser.parse_args()

  from examples.openpilot.compile_warp import make_frame_prepare, parse_frame, parse_size
  from tinygrad import Device, Tensor, TinyJit
  frame = parse_frame(args.frame)
  warp = make_frame_prepare(frame, *parse_size(args.warp_to))
  run = TinyJit(lambda input_frame, M_inv: Tensor.stack(*(warp(input_frame[i], M_inv[i]) for i in range(2))), prune=True)
  rng = np.random.default_rng(42)
  inputs = {"input_frame": Tensor(rng.integers(0, 256, (2, frame.size), dtype=np.uint8), device=Device.DEFAULT).realize(),
            "M_inv": Tensor((rng.standard_normal((2, 3, 3)) * 8).astype(np.float32), device=Device.DEFAULT).realize()}
  with record_kernel_linear() as recorded:
    run(**inputs)
    run(**inputs)
    check, _ = capture_frame(run, inputs)
  assert len(recorded) == 1, f"expected one captured kernel list, got {len(recorded)}"
  part = serialize_jit(run, recorded[0], check)
  PlainJit(*part)
  specs = {"input_frame": ((2, frame.size), "|u1", Device.DEFAULT), "M_inv": ((2, 3, 3), "<f4", Device.DEFAULT)}
  write_bundle(args.output, {"run": part}, {"input_specs": specs, "metadata": {}})
  print(f"Saved warp to {args.output} ({len(part[0]['calls'])} kernels)")


if __name__ == "__main__":
  main()
