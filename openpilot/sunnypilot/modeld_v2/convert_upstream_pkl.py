#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import argparse
import dataclasses
import itertools
import mmap
import re
import struct
import tempfile
import numpy as np

from openpilot.sunnypilot.modeld_v2.helpers import ALIGNMENT, Blob, PlainJit, flatten, write_bundle
from openpilot.sunnypilot.modeld_v2.plain_artifact_compiler import capture_frame


def _root(u):
  from tinygrad.uop.ops import Ops
  while u.op in (Ops.AFTER, Ops.BITCAST, Ops.SHRINK, Ops.INDEX):
    u = u.src[0]
  return u


def _view(u) -> tuple[int, int | None]:
  from tinygrad.uop.ops import Ops
  start, size = 0, None
  while u.op in (Ops.AFTER, Ops.BITCAST, Ops.SHRINK):
    if u.op is Ops.SHRINK:
      start, size = start + u.src[1].arg, u.src[2].arg if size is None else size
    u = u.src[0]
  return start, size


def _address(v):
  from tinygrad.uop.ops import Ops
  add = 0
  while v.op is not Ops.GETADDR:
    add += v.src[1].arg if v.op is Ops.ADD else 0
    v = v.src[0]
  start, size = _view(v.src[0])
  return _root(v.src[0]), add + start, size


def _patched(buf, topo) -> tuple[bytearray, dict]:
  from tinygrad.uop.ops import Ops
  blob, rows = bytearray(buf.max_numel() * buf.dtype.itemsize), {}
  for u in topo:
    if u.op is not Ops.STORE or _root(u.src[0]) is not buf:
      continue
    if (value := u.src[1]).op is Ops.BINARY or value.src[0].op is Ops.BINARY:
      data = (value if value.op is Ops.BINARY else value.src[0]).arg
      blob[:len(data)] = data
    else:
      view, offsets = u.src[0].src
      rows |= {_view(view)[0] + o.arg * view.dtype.itemsize: w for o, w in zip(offsets.src, value.src, strict=True)}
  return blob, rows


def _evaluate(u, env):
  from tinygrad.uop.ops import GroupOp, Ops, exec_alu
  if u.op in (Ops.AFTER, Ops.CAST, Ops.BITCAST):
    return _evaluate(u.src[0], env)
  if u.op is Ops.CONST:
    return u.arg
  if u.op in (Ops.PARAM, Ops.RANGE):
    return env.get(u.arg.slot if u.op is Ops.PARAM else u)
  if u.op is Ops.LOAD:
    table, index = _root(u.src[0].src[0]), _evaluate(u.src[0].src[1], env)
    return struct.unpack_from(u.dtype.fmt, table.arg, index * u.dtype.itemsize)[0] if table.op is Ops.BINARY and index is not None else None
  if u.op in GroupOp.ALU and None not in (values := [_evaluate(x, env) for x in u.src]):
    return exec_alu(u.op, u.dtype, values, False)
  return None


def _input_pokes(submit, kernargs) -> dict[int, tuple[int, int]]:
  from tinygrad.uop.ops import Ops
  outer = dict(enumerate(submit.src[1:]))
  kernargs_params = {i for i, a in outer.items() if a.op is Ops.GETADDR and _root(a.src[0]) is kernargs}
  inputs = {i: _root(a.src[0]).arg.slot for i, a in outer.items() if a.op is Ops.GETADDR and _root(a.src[0]).op is Ops.PARAM}
  pokes = {}
  for call in (u for u in submit.src[0].src[0].toposort() if u.op is Ops.CALL and len(u.src) > 3):
    _, address, value, *_ = call.src[1:]
    used = list({x.arg.slot for x in value.toposort() if x.op is Ops.PARAM} & inputs.keys())
    if len(used) != 1 or not kernargs_params & {x.arg.slot for x in address.toposort() if x.op is Ops.PARAM}:
      continue
    ranges = list(dict.fromkeys(x for x in (*address.toposort(), *value.toposort()) if x.op is Ops.RANGE))
    for trip in itertools.product(*[range(int(r.vmax) + 1) for r in ranges]):
      env = dict.fromkeys(outer, 0) | dict(zip(ranges, trip, strict=True))
      if (offset := _evaluate(address, env)) % 8 == 0:
        pokes[offset] = (inputs[used[0]], _evaluate(value, env))
  return pokes


def _elf(image: bytes, rodata: int) -> bytes:
  names, offset, data, headers = b"\0.text\0.rodata\0.shstrtab\0", 64, b"", []
  for name, kind, address, content in [(0, 0, 0, b""), (1, 1, ALIGNMENT, image[:rodata]), (7, 1, ALIGNMENT + rodata, image[rodata:]), (15, 3, 0, names)]:
    headers.append(struct.pack("<IIQQQQIIQQ", name, kind, 2 if kind == 1 else 0, address, offset, len(content), 0, 0, 1, 0))
    data, offset = data + content, offset + len(content)
  return b"\x7fELF\x02\x01\x01" + bytes(9) + struct.pack("<HHIQQQIHHHHHH", 1, 0xe0, 1, 0, 0, offset, 0, 64, 0, 0, 64, 4, 3) + data + b"".join(headers)


def convert(jit, kwargs: dict, frame: dict, target) -> tuple[dict, memoryview]:
  import tinygrad.runtime.autogen.am.pm4_nv as pm4
  import tinygrad.runtime.autogen.amd_gpu as amd_gpu
  from tinygrad.dtype import dtypes
  from tinygrad.engine.jit import _prepare_jit_inputs
  from tinygrad.helpers import unwrap
  from tinygrad.uop.ops import Ops
  submit = jit.captured._linear.src[0].without_after
  kernels, topo = submit.arg.aux.kernels, list(jit.captured._linear.toposort(enter_calls=True))
  allocs = {str(u.tag): u for u in topo if u.op is Ops.ALLOC and u.tag is not None}
  (commands, patched), kernargs = _patched(allocs["cmdbuf_compute_0"], topo), allocs["kernargs_compute_0"]
  argument_words, pokes = _patched(kernargs, topo)[1], _input_pokes(submit, kernargs)
  sh = {name: getattr(amd_gpu, f"reg{name}") + amd_gpu.GC_BASE__INST0_SEG0 - pm4.PACKET3_SET_SH_REG_START
        for name in ("COMPUTE_PGM_LO", "COMPUTE_USER_DATA_0", "COMPUTE_NUM_THREAD_X")} if hasattr(amd_gpu, "regCOMPUTE_PGM_LO") else \
       {"COMPUTE_PGM_LO": 0x20c, "COMPUTE_USER_DATA_0": 0x240, "COMPUTE_NUM_THREAD_X": 0x207}

  dispatches, registers, offset = [], {}, 0
  while offset < len(commands):
    word = lambda o: patched.get(o, struct.unpack_from("<I", commands, o)[0])  # noqa: E731
    if not isinstance(header := word(offset), int) or header >> 30 != 3:
      offset += 4
      continue
    count, opcode = ((header >> 16) & 0x3fff) + 1, (header >> 8) & 0xff
    body = [word(offset + 4 + 4 * i) for i in range(count)]
    if opcode == pm4.PACKET3_SET_SH_REG:
      registers |= {body[0] + i: v for i, v in enumerate(body[1:])}
    elif opcode == pm4.PACKET3_DISPATCH_DIRECT:
      local = [registers[sh["COMPUTE_NUM_THREAD_X"] + i] for i in range(3)]
      dispatches.append((registers[sh["COMPUTE_PGM_LO"]], registers[sh["COMPUTE_USER_DATA_0"]], local, body[:3]))
    offset += 4 + 4 * count
  assert len(dispatches) == len(kernels), f"decoded {len(dispatches)} dispatches, the JIT has {len(kernels)} kernels"

  sink = tempfile.TemporaryFile(dir=".")
  blob, buffers, programs = Blob(sink), {}, {}
  u8 = repr(dtypes.uint8)

  def store(array) -> dict:
    array = np.ascontiguousarray(array)
    return {"data": blob.add(array.tobytes()), "dtype": array.dtype.str, "shape": list(array.shape)}

  calls, written, needs_init = [], set(), set()
  for (program, arguments, local, grid), kernel in zip(dispatches, kernels, strict=True):
    image_alloc, entry, _ = _address(program)
    if image_alloc not in programs:
      image = bytes(_patched(image_alloc, topo)[0])
      rodata = next(r for r in range(0, len(image) - 24, 64) if r + struct.unpack_from("<q", image, r + 16)[0] == entry)
      programs[image_alloc] = blob.add(_elf(image, rodata))
    start, size = _view(arguments.src[0])
    args = []
    for slot in range(start, start + unwrap(size), 8):
      if slot in pokes:
        assert pokes[slot][1] == 0, "the plain format passes whole inputs, this kernel takes a view into one"
        args.append({"input": pokes[slot][0]})
      elif slot in argument_words:
        base, at, nbytes = _address(argument_words[slot])
        args.append({"buffer": buffers.setdefault(base, len(buffers)), "offset": at, "nbytes": nbytes or base.arg.buffer.nbytes, "dtype": u8})
    outs, ins = kernel[6]
    calls.append({"kind": "program", "name": re.sub(r"\x1b\[[0-9;]*m", "", kernel[1]), "lib": programs[image_alloc], "target": dataclasses.asdict(target),
                  "signature": [[f"data{i}", i, u8, [a.get("nbytes", 1)]] for i, a in enumerate(args)], "global_size": grid, "local_size": local,
                  "globals": list(range(len(args))), "outs": list(outs), "ins": list(ins), "args": args})
    needs_init |= {args[i]["buffer"] for i in ins if "buffer" in args[i] and args[i]["buffer"] not in written}
    written |= {args[i]["buffer"] for i in outs if "buffer" in args[i]}

  names = list(jit.captured.expected_names)
  inputs = [{"slot": slot, "name": names[slot] if slot < len(names) else None, "dtype": repr(u.dtype), "numel": int(u.max_numel()), "device": u.device}
            for slot, u in enumerate(_prepare_jit_inputs((), kwargs)[0])]
  header = {"input_names": names, "calls": calls, "returns": {"kind": "NoneType", "tensors": []}, "inputs": inputs,
            "buffers": [{"nbytes": b.arg.buffer.nbytes, "device": b.arg.buffer.device, "dtype": u8}
                        | ({"init": blob.add(b.arg.buffer.ensure_allocated().as_memoryview())} if i in needs_init else {}) for b, i in buffers.items()],
            "check": {"inputs": [[path, store(array), device] for path, array, device in frame["inputs"]],
                      "outputs": [store(array) for array in frame["outputs"]], "output_container": frame["output_container"]}}
  with sink:
    sink.flush()
    return header, memoryview(mmap.mmap(sink.fileno(), 0, access=mmap.ACCESS_READ))


def main():
  parser = argparse.ArgumentParser(description="Convert commaai's precompiled chestnut driving model into a plain tinygrad artifact")
  parser.add_argument("pkl", help="big_driving_tinygrad.pkl")
  parser.add_argument("output")
  args = parser.parse_args()

  from examples.openpilot.helpers import allocate_inputs, load_pickle
  from tinygrad import Device, Tensor
  from tinygrad.engine.realize import lower_and_compile
  artifact = load_pickle(args.pkl, out_of_band=True)
  artifact["run"].captured._linear = lower_and_compile(artifact["run"].captured._linear)
  rng = np.random.default_rng(7)

  def initialize(arrays: dict):
    for value in arrays.values():
      value[...] = rng.standard_normal(value.shape) if value.dtype.kind == "f" else rng.integers(0, 2 if value.dtype == np.bool_ else 16, value.shape)
  kwargs = allocate_inputs(artifact["input_specs"], initialize) | {"output_buffers": allocate_inputs(artifact["output_specs"])}
  frame, _ = capture_frame(artifact["run"], kwargs, "output_buffers")
  part = convert(artifact["run"], kwargs, frame, Device[Device.DEFAULT].renderer.target)

  plain = PlainJit(*part)  # replays the frame, within tolerance
  replay = {path[0]: Tensor(array, device=device).realize() for path, array, device in frame["inputs"] if len(path) == 1}
  replay["output_buffers"] = {path[1]: Tensor(array, device=device).realize() for path, array, device in frame["inputs"] if len(path) == 2}
  flatten(plain(**replay))
  for index, (got, expected) in enumerate(zip([t.numpy() for t in replay["output_buffers"].values()], frame["outputs"], strict=True)):
    assert np.array_equal(got, expected), f"output {index} of the plain artifact differs from the pickle"
  write_bundle(args.output, {"run": part}, {key: artifact[key] for key in ("metadata", "input_specs", "output_specs")})
  print(f"converted {len(part[0]['calls'])} kernels, bit-exact with the pickle: {args.output}")


if __name__ == "__main__":
  main()
