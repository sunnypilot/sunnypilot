"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import io
import struct
import pickle
import inspect
import importlib
import enum


def _pad_args(func, args, kwargs):
  try:
    sig = inspect.signature(func)
  except Exception:
    return args, kwargs
  params = list(sig.parameters.values())
  if inspect.isfunction(func) and params and params[0].name in ('cls', 'self'):
    params = params[1:]

  new_args = list(args)
  has_varargs = any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in params)
  if len(new_args) > len(params) and not has_varargs:
    new_args = new_args[:len(params)]

  for i in range(len(new_args), len(params)):
    param = params[i]
    if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
      continue
    val = param.default if param.default is not inspect.Parameter.empty else None
    new_args.append(val)
  return new_args, kwargs


# TODO: New models compiled via `compile_modeld.py` or upstream `compile_onnx.py`
# now natively serialize Ops as strings via FastEnum.__reduce_ex__ patching,
# bypassing this integer map entirely.
TG_e837e367_OP_CODE_MAP = {
  1: 'SPECIAL', 2: 'BUFFER', 3: 'NOOP', 4: 'REWRITE_ERROR', 5: 'PARAM', 6: 'CALL',
  7: 'PROGRAM', 8: 'LINEAR', 9: 'SOURCE', 10: 'BINARY', 11: 'SINK', 12: 'AFTER',
  13: 'GROUP', 14: 'STACK', 15: 'RETURNED', 16: 'GETADDR', 17: 'INDEX', 18: 'SHRINK',
  19: 'LOAD', 20: 'STORE', 21: 'WMMA', 22: 'CAST', 23: 'BITCAST', 24: 'EXP2', 25: 'LOG2',
  26: 'SIN', 27: 'SQRT', 28: 'RECIPROCAL', 29: 'NEG', 30: 'TRUNC', 31: 'ADD', 32: 'MUL',
  33: 'SHL', 34: 'SHR', 35: 'CDIV', 36: 'MAX', 37: 'CMOD', 38: 'CMPLT', 39: 'CMPNE',
  40: 'CMPEQ', 41: 'XOR', 42: 'OR', 43: 'AND', 44: 'THREEFRY', 45: 'SUB', 46: 'FDIV',
  47: 'POW', 48: 'FLOORDIV', 49: 'FLOORMOD', 50: 'WHERE', 51: 'MULACC', 52: 'BARRIER',
  53: 'RANGE', 54: 'IF', 55: 'END', 56: 'ENDIF', 57: 'CONST', 58: 'CUSTOM', 59: 'CUSTOMI',
  60: 'INS', 61: 'CONTIGUOUS', 62: 'CONTIGUOUS_BACKWARD', 63: 'DETACH', 64: 'STAGE',
  65: 'COPY', 66: 'MSELECT', 67: 'MSTACK', 68: 'CUSTOM_FUNCTION', 69: 'RESHAPE', 70: 'PERMUTE',
  71: 'EXPAND', 72: 'PAD', 73: 'FLIP', 74: 'UNSHARD', 75: 'REDUCE', 76: 'ALLREDUCE', 77: 'PYLITERAL'
}

def _enum_factory(enum_class, enum_offset=0, legacy_map=False):
  class EnumProxyMeta(type):
    def __getattr__(cls, name):
      return getattr(enum_class, name)

  class EnumProxy(metaclass=EnumProxyMeta):
    def __new__(cls, *args, **kwargs):
      if enum_class.__name__ == 'Ops' and args and isinstance(args[0], int):
        value = args[0] - enum_offset
        if legacy_map and value in TG_e837e367_OP_CODE_MAP:
          try:
            return getattr(enum_class, TG_e837e367_OP_CODE_MAP[value])
          except AttributeError:
            pass
        try:
          return enum_class(value)
        except ValueError:
          if not legacy_map:
            raise ValueError("LEGACY_MISMATCH") from None
          return list(enum_class)[0]
      try:
        return enum_class(*args, **kwargs)
    # OptOps and UOp objects in the .pkl are left over from the compilation phase,
    # reassignment does nothing because they aren't tied to the execution graph
    # It never executes or evaluates the UOp nodes again.
      except ValueError:
        return list(enum_class)[0]

  EnumProxy.__name__ = enum_class.__name__
  EnumProxy.__module__ = enum_class.__module__
  return EnumProxy


def _dynamic_factory(real_class, enum_offset=0, legacy_map=False):
  if isinstance(real_class, type) and issubclass(real_class, enum.Enum):
    return _enum_factory(real_class, enum_offset, legacy_map)

  def factory(*args, **kwargs):
    if real_class.__name__ == 'Buffer':
      # Tinygrad, before compile_modeld moved to tg, serialized lb_refcount at index 6. It has been removed.
      if len(args) >= 7 and isinstance(args[6], int):
        args = tuple(list(args[:6]) + list(args[7:]))
    elif real_class.__name__ == 'UOp':
      # Legacy: (op, dtype, src, arg) -> Modern: (op, src, arg, tag)
      if len(args) >= 2 and type(args[1]).__name__ == 'DType':
        args = tuple([args[0]] + list(args[2:]))

      # august tg did this, which shifted the enums: class FastEnum(IntEnum):
      # def _generate_next_value_(_, __, ___, last_values):
      #     return 1 + max([0, *last_values, *[max(c) for c in FastEnum.__subclasses__()]])
      if getattr(args[0], 'name', None) == 'AFTER' and len(args) > 2 and isinstance(args[2], bytes):
        raise ValueError("OFFSET_2")

    try:
      return real_class(*args, **kwargs)
    except TypeError:
      new_args, new_kwargs = _pad_args(real_class, args, kwargs)
      return real_class(*new_args, **new_kwargs)

  class DynamicMeta(type(real_class)):
    def __call__(cls, *args, **kwargs):
      return factory(*args, **kwargs)

  class DynamicProxy(real_class, metaclass=DynamicMeta):
    __slots__ = ()

    def __new__(cls, *args, **kwargs):
      return factory(*args, **kwargs)

  DynamicProxy.__name__ = real_class.__name__
  DynamicProxy.__module__ = real_class.__module__
  return DynamicProxy


class DynamicTinygradUnpickler(pickle.Unpickler):
  def __init__(self, *args, enum_offset=0, legacy_map=False, **kwargs):
    self.enum_offset = enum_offset
    self.legacy_map = legacy_map
    super().__init__(*args, **kwargs)

  def find_class(self, module, name):
    if module == "tinygrad.ops":
      try:
        importlib.import_module("tinygrad.uops")
        module = "tinygrad.uops"
      except ImportError:
        pass
    real_class = getattr(importlib.import_module(module), name)
    if module.startswith("tinygrad"):
      return _dynamic_factory(real_class, self.enum_offset, self.legacy_map)
    return real_class


def load_oob(f):
  opcodes = f.read(struct.unpack('<q', f.read(8))[0])
  all_buffers_raw = []
  while (h := f.read(8)):
    size = struct.unpack('<q', h)[0]
    b = bytearray(size)
    f.readinto(b)
    all_buffers_raw.append(b)

  def try_load(offset=0, legacy_map=False):
    def buffers_gen():
      for b in all_buffers_raw:
        yield pickle.PickleBuffer(b)
    unpickler = DynamicTinygradUnpickler(io.BytesIO(opcodes), buffers=buffers_gen(), enum_offset=offset, legacy_map=legacy_map)
    return unpickler.load()
  try:
    return try_load(offset=0, legacy_map=False)
  except ValueError as e:
    if "LEGACY_MISMATCH" in str(e):
      try:
        return try_load(offset=0, legacy_map=True)
      except ValueError as e2:
        if "OFFSET_2" in str(e2):
          return try_load(offset=2, legacy_map=True)
        raise e2
    elif "OFFSET_2" in str(e):
      return try_load(offset=2, legacy_map=True)
    raise


def dump_oob(obj, f):
  buffers = []
  def buffer_cb(buffer):
    buffers.append(buffer)
    return False

  opcodes = pickle.dumps(obj, protocol=5, buffer_callback=buffer_cb)
  f.write(struct.pack('<q', len(opcodes)))
  f.write(opcodes)
  for b in buffers:
    f.write(struct.pack('<q', len(b.raw())))
    f.write(b.raw())
