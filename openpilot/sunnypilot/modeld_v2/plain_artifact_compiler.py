import dataclasses
from contextlib import contextmanager
from unittest import mock

import numpy as np

from openpilot.sunnypilot.modeld_v2.helpers import Blob, flatten

# Compile time only: turns a captured TinyJit into plain data that helpers.load_model rebuilds. It reads internals of the
# tinygrad that compiles the model, so a tinygrad bump that breaks it blocks new builds, never loading already built models.


@contextmanager
def record_kernel_linear():
  import tinygrad.engine.jit as jit
  import tinygrad.engine.realize as realize
  recorded, hcq_compile, compile_linear = [], realize.hcq_compile, jit.compile_linear

  def recording_compile_linear(*args, **kwargs):
    with mock.patch.object(realize, "hcq_compile", lambda linear, *a, **k: (recorded.append(linear), hcq_compile(linear, *a, **k))[1]):
      return compile_linear(*args, **kwargs)

  with mock.patch.object(jit, "compile_linear", recording_compile_linear):
    yield recorded


def capture_frame(jit, kwargs: dict, output_container: str | None = None):
  inputs = [([name] if key is None else [name, key], tensor.numpy().copy(), tensor.device)
            for name, value in kwargs.items() for key, tensor in (value.items() if isinstance(value, dict) else [(None, value)])]
  result = jit(**kwargs)
  outputs = kwargs[output_container].values() if output_container else flatten(result)
  return {"inputs": inputs, "outputs": [tensor.numpy().copy() for tensor in outputs], "output_container": output_container}, result


def serialize_jit(jit, kernel_linear, check: dict | None = None) -> tuple[dict, bytes]:
  from tinygrad.helpers import JIT, JIT_BATCH_SIZE
  from tinygrad.uop.ops import Ops

  blob, bases, input_specs = Blob(), {}, {}

  def store(array) -> dict:
    array = np.ascontiguousarray(array)
    return {"data": blob.add(array.tobytes()), "dtype": array.dtype.str, "shape": list(array.shape)}

  def describe(uop) -> dict:
    if uop.op is Ops.PARAM:
      input_specs.setdefault(uop.arg.slot, {"dtype": repr(uop.dtype), "numel": int(uop.max_numel()), "device": uop.device})
      return {"input": uop.arg.slot}
    buffer = uop.buffer
    root = buffer._base if buffer._base is not None else buffer
    base = bases.setdefault(id(root), (len(bases), root))
    return {"buffer": base[0], "offset": buffer.offset if buffer._base is not None else 0, "nbytes": buffer.nbytes, "dtype": repr(uop.dtype)}

  calls, written, needs_init = [], set(), set()
  for call in kernel_linear.src:
    ast, arguments = call.src[0], [describe(argument) for argument in call.src[1:]]
    if ast.op is Ops.PROGRAM:
      elf, info = ast.to_elf(), ast.arg
      global_size, local_size = info.launch_dims({})
      calls.append({"kind": "program", "name": elf.name, "lib": blob.add(bytes(elf.lib)), "target": dataclasses.asdict(elf.target),
                    "signature": [[name, slot, repr(dtype), [int(x) for x in shape]] for name, slot, dtype, shape in elf.signature],
                    "global_size": [int(x) for x in global_size], "local_size": [int(x) for x in local_size],
                    "globals": list(info.globals), "outs": list(info.outs), "ins": list(info.ins), "args": arguments})
      outs, ins = info.outs, info.ins
    elif ast.op is Ops.COPY:
      calls.append({"kind": "copy", "args": arguments})
      outs, ins = (0,), (1,)
    else:
      raise ValueError(f"unsupported call {ast.op} {ast.arg}")
    needs_init |= {arguments[i]["buffer"] for i in ins if "buffer" in arguments[i] and arguments[i]["buffer"] not in written}
    written |= {arguments[i]["buffer"] for i in outs if "buffer" in arguments[i]}

  ret = jit.captured.ret
  returns = {"kind": type(ret).__name__, "tensors": [describe(t.uop.base) | {"shape": [int(x) for x in t.shape]} for t in flatten(ret)]}
  buffers = [{"nbytes": base.nbytes, "device": base.device, "dtype": repr(base.dtype)}
             | ({"init": blob.add(bytes(base.as_memoryview()))} if index in needs_init else {}) for index, base in bases.values()]
  names = list(jit.captured.expected_names)
  if check is not None:
    check = {"inputs": [[path, store(array), device] for path, array, device in check["inputs"]], "outputs": [store(array) for array in check["outputs"]],
             "output_container": check["output_container"]}
  header = {"input_names": names, "buffers": buffers, "calls": calls, "returns": returns, "check": check,
            "graph_batch_size": JIT_BATCH_SIZE.value if JIT < 2 else None,
            "inputs": [{"slot": slot, "name": names[slot] if slot < len(names) else None} | input_specs[slot] for slot in sorted(input_specs)]}
  return header, b"".join(blob.chunks)
