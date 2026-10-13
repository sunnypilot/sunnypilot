"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import builtins
import contextlib
import dataclasses
import functools
import hashlib
import io
import json
import math
import mmap
import os
import pickle
import struct

MAGIC = b"SPTGPLN1"
ALIGNMENT = 256
METADATA_TYPES = ("slice", "tuple", "list", "dict", "set", "frozenset", "complex")
RUNTIME_ENVIRONMENT = ("GMMU", "AMD_AQL", "AMD_DISABLE_SDMA", "GRAPH_ONE_KERNEL")


def _patch_system_flock_acquire():
  try:
    from tinygrad.runtime.support.system import System
    original_flock_acquire = System.flock_acquire
    acquired_locks: dict[str, int] = {}

    def flock_acquire(name: str) -> int:
      if name in acquired_locks:
        return acquired_locks[name]
      lock_file_descriptor = original_flock_acquire(name)
      acquired_locks[name] = lock_file_descriptor
      return lock_file_descriptor
    System.flock_acquire = flock_acquire
  except (ImportError, AttributeError):
    pass
_patch_system_flock_acquire()


class ArtifactMismatch(RuntimeError):
  pass


class Blob:
  def __init__(self):
    self.chunks: list[bytes] = []
    self.locations: dict[bytes, list[int]] = {}
    self.size = 0

  def add(self, data: bytes) -> list[int]:
    if data not in self.locations:
      start = self.size + -self.size % ALIGNMENT
      self.chunks += [bytes(start - self.size), data]
      self.locations[data], self.size = [start, start + len(data)], start + len(data)
    return self.locations[data]


class _MetadataUnpickler(pickle.Unpickler):
  def find_class(self, module, name):
    if module == "builtins" and name in METADATA_TYPES:
      return getattr(builtins, name)
    raise pickle.UnpicklingError(f"{module}.{name} is not allowed in model metadata")


def flatten(value) -> list:
  if isinstance(value, (tuple, list)):
    return [tensor for item in value for tensor in flatten(item)]
  return [] if value is None else [value]


def write_bundle(path: str, parts: dict, extras: dict | None = None):
  blob = Blob()
  entries = [{"key": list(key) if isinstance(key, tuple) else key, "blob": blob.add(bytes(part_blob)), "header": part_header}
             for key, (part_header, part_blob) in parts.items()]
  header = json.dumps({"parts": entries, "extras": blob.add(pickle.dumps(extras or {}, protocol=4))}).encode()
  with open(path, "wb") as file:
    file.write(MAGIC + struct.pack("<Q", len(header)) + header + bytes(-(len(MAGIC) + 8 + len(header)) % ALIGNMENT))
    file.writelines(blob.chunks)


def read_parts(path: str) -> tuple[dict, dict]:
  with open(path, "rb") as file:
    data = memoryview(mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ))
  if bytes(data[:len(MAGIC)]) != MAGIC:
    raise ValueError(f"{path} is not a plain tinygrad model, recompile it with compile_modeld.py")
  start = len(MAGIC) + 8 + struct.unpack_from("<Q", data, len(MAGIC))[0]
  header, blob = json.loads(bytes(data[len(MAGIC) + 8:start])), data[start + -start % ALIGNMENT:]
  parts = {tuple(e["key"]) if isinstance(e["key"], list) else e["key"]: (e["header"], blob[slice(*e["blob"])]) for e in header["parts"]}
  return parts, _MetadataUnpickler(io.BytesIO(bytes(blob[slice(*header["extras"])]))).load()


def load_model(path: str, device_map: dict | None = None, verify: bool = True, cache: bool = True) -> dict:
  parts, extras = read_parts(path)
  if cache and (cached := _read_cache(path, parts, device_map)) is not None:
    return extras | cached
  jits = {key: PlainJit(header, blob, device_map, verify) for key, (header, blob) in parts.items()}
  if cache:
    _write_cache(path, jits, device_map)
  return extras | jits


@functools.cache
def tinygrad_identity() -> str:
  import tinygrad
  root, digest = os.path.dirname(tinygrad.__file__), hashlib.sha256()
  for directory, _, files in sorted(os.walk(root)):
    for name in sorted(file for file in files if file.endswith(".py")):
      stat = os.stat(path := os.path.join(directory, name))
      digest.update(f"{os.path.relpath(path, root)}:{stat.st_size}:{stat.st_mtime_ns};".encode())
  return digest.hexdigest()


def _cache_key(path: str, device_map: dict | None) -> bytes:
  stat = os.stat(path)
  return json.dumps({"format": MAGIC.decode(), "tinygrad": tinygrad_identity(), "size": stat.st_size, "mtime_ns": stat.st_mtime_ns,
                     "device_map": sorted((device_map or {}).items()), "env": [os.environ.get(name, "") for name in RUNTIME_ENVIRONMENT]}).encode()


def _cache_header_matches(file, path: str, device_map: dict | None) -> bool:
  return file.read(struct.unpack("<Q", file.read(8))[0]) == _cache_key(path, device_map)


def cache_is_fresh(path: str, device_map: dict | None = None) -> bool: # entry point for warmup proc
  try:
    with open(f"{path}.cache", "rb") as file:
      return _cache_header_matches(file, path, device_map)
  except (OSError, struct.error):
    return False


def _read_cache(path: str, parts: dict, device_map: dict | None) -> dict | None:
  try:
    with open(f"{path}.cache", "rb") as file:
      if not _cache_header_matches(file, path, device_map):
        return None
      buffers = {repr(key): _allocate_buffers(header, blob, device_map) for key, (header, blob) in parts.items()}
      return type("_Unpickler", (pickle.Unpickler,), {"persistent_load": lambda self, pid: buffers[pid[0]][pid[1]]})(file).load()
  except Exception:
    return None


def _write_cache(path: str, jits: dict, device_map: dict | None) -> None:
  from tinygrad.device import Buffer
  owners = {id(buffer): (repr(key), index) for key, jit in jits.items() for index, buffer in enumerate(jit.buffers)}

  class _Pickler(pickle.Pickler):
    def persistent_id(self, obj):
      return owners.get(id(obj)) if isinstance(obj, Buffer) else None

  key, tmp_path = _cache_key(path, device_map), f"{path}.cache.{os.getpid()}.tmp"
  with contextlib.suppress(Exception):
    with open(tmp_path, "wb") as file:
      file.write(struct.pack("<Q", len(key)) + key)
      _Pickler(file, protocol=5).dump({name: _Jit(jit.captured, jit.input_names, jit.buffers) for name, jit in jits.items()})
    os.replace(tmp_path, f"{path}.cache")


# Everything below this comment block calls tinygrad internals, so after a tinygrad bump this
# is the only code to update, and models are not recompiled. How to do this when discountchubbs is not available:
#   1. run modeld_v2/tests/test_plain_artifact.py on the new tinygrad and fix each failing call against the new API: Buffer,
#      UOp.from_buffer/param (ParamArg), ProgramInfo, Target, KernelInfo, compile_linear, graph_split_rewrite, CapturedJit and
#      _prepare_jit_inputs in tinygrad/engine/jit.py
#   2. load a real model with verify=True: ArtifactMismatch means the rebuilt graph still differs from the one that was compiled
# The boot cache is keyed on the tinygrad source, so it rebuilds itself. Only a change in how the device runs kernel binaries needs a recompile.
# Honestly, I would just have your clanker try it because you likely have zero idea what you are looking at lol..

def _dtype(text: str):
  from tinygrad.dtype import dtypes
  return eval(text, {"__builtins__": {}}, {"dtypes": dtypes})


def _device(recorded: str, device_map: dict | None) -> str:
  from tinygrad import Device
  device_map = device_map or {}
  return Device.canonicalize(device_map.get(recorded, device_map.get(recorded.split(":", 1)[0], recorded)))


def _allocate_buffers(header: dict, blob: memoryview, device_map: dict | None) -> list:
  from tinygrad.device import Buffer
  buffers = []
  for entry in header["buffers"]:
    dtype, initial = _dtype(entry["dtype"]), pickle.PickleBuffer(blob[slice(*entry["init"])]) if "init" in entry else None
    buffers.append(Buffer(_device(entry["device"], device_map), entry["nbytes"] // dtype.itemsize, dtype, initial_value=initial).ensure_allocated())
  return buffers


def _program_uop(call: dict, lib: bytes):
  from tinygrad.helpers import Target
  from tinygrad.uop.ops import KernelInfo, Ops, ProgramInfo, UOp
  parameters = []
  for name, compact_slot, dtype, shape in call["signature"]:
    parameter = UOp.param(call["globals"][compact_slot], _dtype(dtype), math.prod(shape))
    image = (shape[0], shape[1]) if len(shape) == 3 and shape[2] == 4 else None
    parameters.append(parameter.replace(arg=dataclasses.replace(parameter.arg, name=name, image=image)))
  info = ProgramInfo(global_size=tuple(call["global_size"]), local_size=tuple(call["local_size"]), vars=(), globals=tuple(call["globals"]),
                     outs=tuple(call["outs"]), ins=tuple(call["ins"]), target=Target(**call["target"]))
  return UOp(Ops.PROGRAM, src=(UOp(Ops.SINK, arg=KernelInfo(name=call["name"])), UOp(Ops.LINEAR, src=tuple(parameters)),
                               UOp(Ops.SOURCE, arg=""), UOp(Ops.BINARY, arg=lib)), arg=info)


class _Jit:
  def __init__(self, captured, input_names: list, buffers: list):
    self.captured, self.input_names, self.buffers = captured, input_names, buffers

  def __call__(self, *args, **kwargs):
    import tinygrad.engine.jit as jit
    input_uops, var_vals, names, _ = jit._prepare_jit_inputs(args, kwargs)
    if names != self.input_names:
      raise ValueError(f"expected inputs {self.input_names}, got {names}")
    return self.captured(input_uops, var_vals)


class PlainJit(_Jit):
  def __init__(self, header: dict, blob: memoryview, device_map: dict | None = None, verify: bool = True):
    import numpy as np
    import tinygrad.engine.jit as jit
    from tinygrad import Tensor
    from tinygrad.device import Buffer
    from tinygrad.dtype import dtypes
    from tinygrad.uop.ops import Ops, UOp

    inputs = {spec["slot"]: spec for spec in header["inputs"]}
    buffers = _allocate_buffers(header, blob, device_map)
    bases = [UOp.from_buffer(buffer) for buffer in buffers]

    def argument(described: dict):
      if "input" in described:
        spec = inputs[described["input"]]
        return UOp.param(described["input"], _dtype(spec["dtype"]), spec["numel"], _device(spec["device"], device_map))
      base, dtype, offset, nbytes = bases[described["buffer"]], _dtype(described["dtype"]), described["offset"], described["nbytes"]
      if offset == 0 and nbytes == header["buffers"][described["buffer"]]["nbytes"] and dtype == base.dtype:
        return base
      return (base if base.dtype.itemsize == 1 else base.bitcast(dtypes.uint8)).shrink(((offset, offset + nbytes),)).bitcast(dtype)

    calls = []
    for call in header["calls"]:
      arguments = [argument(described) for described in call["args"]]
      if call["kind"] == "program":
        calls.append(_program_uop(call, bytes(blob[slice(*call["lib"])])).call(*arguments))
      else:
        calls.append(arguments[1].copy_to_device(arguments[0].device).call(*arguments))
    # stand-ins for JIT inputs: copy staging to GPU is decided from the input buffers, the real ones bind per call
    stand_ins = {slot: UOp.from_buffer(Buffer(_device(spec["device"], device_map), spec["numel"], _dtype(spec["dtype"])).ensure_allocated())
                 for slot, spec in inputs.items()}
    input_uops = tuple(stand_ins.get(slot, next(iter(stand_ins.values()), None)) for slot in range(max(stand_ins, default=-1) + 1))
    linear = jit.compile_linear(UOp(Ops.LINEAR, src=tuple(calls)), beam=0, input_uops=input_uops, cache=False)
    if header["graph_batch_size"] is not None:
      linear = jit.graph_split_rewrite(linear, max_batch_size=header["graph_batch_size"])

    returned = [Tensor(argument(t)).reshape(tuple(t["shape"])) for t in header["returns"]["tensors"]]
    ret = {"NoneType": None, "Tensor": returned[0] if returned else None, "tuple": tuple(returned), "list": returned}[header["returns"]["kind"]]
    super().__init__(jit.CapturedJit(ret, linear, header["input_names"], []), header["input_names"], buffers)

    if not verify or not (check := header.get("check")):
      return
    def array(stored):
      return np.frombuffer(blob[slice(*stored["data"])], dtype=np.dtype(stored["dtype"])).reshape(stored["shape"]).copy()
    kwargs: dict = {}
    for path, stored, device in check["inputs"]:
      tensor = Tensor(array(stored), device=_device(device, device_map)).realize()
      kwargs[path[0]] = tensor if len(path) == 1 else {**kwargs.get(path[0], {}), path[1]: tensor}
    result = self(**kwargs)
    outputs = kwargs[check["output_container"]].values() if check["output_container"] else flatten(result)
    for index, (got, stored) in enumerate(zip([t.numpy() for t in outputs], check["outputs"], strict=True)):
      expected = array(stored)
      if got.shape != expected.shape or not np.allclose(got, expected, rtol=1e-3, atol=1e-3, equal_nan=True):
        raise ArtifactMismatch(f"output {index} differs from the compile-time reference frame; recompile the model")
