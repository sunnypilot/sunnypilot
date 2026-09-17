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


def _enum_factory(enum_class):
  def factory(*args, **kwargs):
    try:
      return enum_class(*args, **kwargs)
    # OptOps and UOp objects in the .pkl are left over from the compilation phase,
    # reassignment does nothing because they aren't tied to the execution graph
    # It never executes or evaluates the UOp nodes again.
    except ValueError:
      return list(enum_class)[0]
  factory.__name__ = enum_class.__name__
  factory.__module__ = enum_class.__module__
  return factory


def _dynamic_factory(real_class):
  if isinstance(real_class, type) and issubclass(real_class, enum.Enum):
    return _enum_factory(real_class)

  def factory(*args, **kwargs):
    if real_class.__name__ == 'Buffer':
      # Tinygrad, before compile_modeld moved to tg, serialized lb_refcount at index 6. It has been removed.
      if len(args) >= 7 and isinstance(args[6], int):
        args = tuple(list(args[:6]) + list(args[7:]))

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
  def find_class(self, module, name):
    if module == "tinygrad.ops":
      try:
        importlib.import_module("tinygrad.uops")
        module = "tinygrad.uops"
      except ImportError:
        pass
    real_class = getattr(importlib.import_module(module), name)
    if module.startswith("tinygrad"):
      return _dynamic_factory(real_class)
    return real_class


def load_oob(f):
  opcodes = f.read(struct.unpack('<q', f.read(8))[0])
  def buffers():
    while (h := f.read(8)):
      pb = pickle.PickleBuffer(bytearray(struct.unpack('<q', h)[0]))
      f.readinto(pb)
      yield pb
  return DynamicTinygradUnpickler(io.BytesIO(opcodes), buffers=buffers()).load()


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


def patch_tinygrad_engine():
  from tinygrad.uop.ops import Ops
  from tinygrad.engine import realize
  if not getattr(realize, '_legacy_resolve_patched', False):
    old_resolve = realize._resolve
    def patched_resolve(b, inputs):
      if b.op == Ops.CUSTOM and isinstance(b.arg, int):
        return inputs[b.arg]
      return old_resolve(b, inputs)
    realize._resolve = patched_resolve
    old_get_runtime = realize.get_runtime

    def exec_legacy(ctx, call, ast):
      if getattr(call.arg, 'aux', None) != "LEGACY_EXEC":
        return None
      from tinygrad.engine.realize import resolve_params, unwrap_multi
      resolved = resolve_params(call, ctx.input_uops)
      device = call.src[1].device if len(call.src) > 1 else 'NPY'
      if isinstance(device, tuple):
        device = device[0]

      ets = []
      prg = old_get_runtime(device, ast)
      for _, (bufs, _device_vars) in zip([device], unwrap_multi(call, resolved), strict=False):
        real_bufs = [b.ensure_allocated() for b in bufs]
        try:
          et = prg(real_bufs, ctx.var_vals, wait=ctx.wait)
        except Exception:
          from tinygrad.shape.symbolic import sym_infer
          g = tuple(sym_infer(x, ctx.var_vals) if not isinstance(x, int) else x for x in ast.arg.global_size)\
            if hasattr(ast.arg, 'global_size') and ast.arg.global_size else None
          l = tuple(sym_infer(x, ctx.var_vals) if not isinstance(x, int) else x for x in ast.arg.local_size)\
            if hasattr(ast.arg, 'local_size') and ast.arg.local_size else None
          vals = tuple(ctx.var_vals[v.expr] for v in getattr(ast.arg, 'vars', []))
          et = prg.clprg(*[b._buf for b in real_bufs], global_size=g, local_size=l, vals=vals, wait=ctx.wait)\
            if hasattr(prg, 'clprg') else prg(*[b._buf for b in real_bufs], global_size=g, local_size=l, vals=vals, wait=ctx.wait)
        ets.append(et)
      return ets

    from tinygrad.uop.ops import UPat
    realize.pm_exec.patterns.insert(0, (UPat(Ops.CALL, src=(UPat(Ops.PROGRAM, name="ast"),), name="call", allow_any_len=True), exec_legacy))
    old_track_stats = realize.track_stats
    def patched_track_stats(ctx, call, st, ets):
      if ets is None:
        return
      return old_track_stats(ctx, call, st, ets)
    realize.track_stats = patched_track_stats
    realize._legacy_resolve_patched = True
