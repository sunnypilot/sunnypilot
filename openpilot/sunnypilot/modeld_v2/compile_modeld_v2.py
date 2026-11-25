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
  from examples.openpilot.compile_onnx import onnx_metadata
  from examples.openpilot.helpers import allocate_inputs, benchmark
  from tinygrad import Device, Tensor, TinyJit
  from tinygrad.dtype import _to_np_dtype
  from tinygrad.nn.onnx import OnnxRunner

  parser = argparse.ArgumentParser(description="Compile a native-architecture ONNX model into a plain tinygrad artifact")
  parser.add_argument('onnx')
  parser.add_argument('output')
  parser.add_argument('--device-input', action='append', default=[])
  parser.add_argument('--benchmark-runs', type=int, default=20)
  args = parser.parse_args()

  runner, (properties, output_shapes) = OnnxRunner(args.onnx), onnx_metadata(args.onnx)
  device_inputs = runner.graph_inputs.keys() if '*' in args.device_input else args.device_input
  metadata = {'metadata': properties} | {f'{kind}_shapes': {name: tuple(d if isinstance(d, int) else 0 for d in shape) for name, shape in shapes.items()}
                                         for kind, shapes in [('input', {name: spec.shape for name, spec in runner.graph_inputs.items()}),
                                                              ('output', output_shapes)]}
  input_specs = {name: (tuple(s if isinstance(s, int) else 1 for s in spec.shape), np.dtype(_to_np_dtype(spec.dtype)).str,
                        Device.DEFAULT if name in device_inputs else 'NPY') for name, spec in runner.graph_inputs.items()}

  def model(inputs):
    return {name: value.contiguous() for name, value in runner({name: value.to(Device.DEFAULT) for name, value in inputs.items()}).items()}
  output_specs = {name: (value.shape, np.dtype(_to_np_dtype(value.dtype)).name, Device.DEFAULT) for name, value in model(allocate_inputs(input_specs)).items()}

  @TinyJit(prune=True)
  def jit(output_buffers, **inputs):
    Tensor.realize(*(output_buffers[name].assign(value) for name, value in model(inputs).items()))

  check_inputs = allocate_inputs(input_specs, initialize_check_inputs) | {'output_buffers': allocate_inputs(output_specs)}
  with record_kernel_linear() as recorded:
    for i in range(2 + args.benchmark_runs):
      benchmark(jit, cb=lambda t, i=i: print(f"  [{i + 1}/{2 + args.benchmark_runs}] {t * 1e3:.2f} ms"), **check_inputs)
  assert len(recorded) == 1, f"expected one captured kernel list, got {len(recorded)}"

  frame, _ = capture_frame(jit, check_inputs, 'output_buffers')
  part = serialize_jit(jit, recorded[0], frame)
  PlainJit(part[0], memoryview(part[1]))
  write_bundle(args.output, {'run': part}, {'metadata': metadata, 'input_specs': input_specs, 'output_specs': output_specs})
  print(f"Saved model to {args.output} ({os.path.getsize(args.output) / 1e6:.2f} MB, {len(part[0]['calls'])} kernels)")
