#!/usr/bin/env python3
import argparse
import os
import sys

import numpy as np

from openpilot.sunnypilot.modeld_v2.helpers import PlainJit, write_bundle
from openpilot.sunnypilot.modeld_v2.plain_artifact_compiler import capture_frame, record_kernel_linear, serialize_jit


def initialize_check_inputs(arrays: dict):
  rng = np.random.default_rng(7)
  for value in arrays.values():
    value[...] = rng.standard_normal(value.shape) if value.dtype.kind == "f" else rng.integers(0, 2 if value.dtype == np.bool_ else 16, value.shape)


if __name__ == "__main__":
  sys.path.insert(0, os.environ.get("TINYGRAD_PATH", "tinygrad_repo"))
  from examples.openpilot.compile_onnx import compile_onnx
  from examples.openpilot.helpers import allocate_inputs

  parser = argparse.ArgumentParser(description="Compile a native-architecture ONNX model into a plain tinygrad artifact")
  parser.add_argument('onnx')
  parser.add_argument('output')
  parser.add_argument('--device-input', action='append', default=[])
  parser.add_argument('--benchmark-runs', type=int, default=20)
  args = parser.parse_args()

  with record_kernel_linear() as recorded:
    artifact = compile_onnx(args.onnx, device_inputs=args.device_input, benchmark_runs=args.benchmark_runs)
  assert len(recorded) == 1, f"expected one captured kernel list, got {len(recorded)}"

  jit = artifact['run']
  check_inputs = allocate_inputs(artifact['input_specs'], initialize_check_inputs) | {'output_buffers': allocate_inputs(artifact['output_specs'])}
  frame, _ = capture_frame(jit, check_inputs, 'output_buffers')
  part = serialize_jit(jit, recorded[0], frame)
  PlainJit(part[0], memoryview(part[1]))
  write_bundle(args.output, {'run': part}, {key: artifact[key] for key in ('metadata', 'input_specs', 'output_specs')})
  print(f"Saved model to {args.output} ({os.path.getsize(args.output) / 1e6:.2f} MB, {len(part[0]['calls'])} kernels)")
