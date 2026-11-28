import sys, os, zlib, glob, importlib.util, itertools
import numpy as np
from tinygrad import Tensor, dtypes
from tinygrad.helpers import Context
here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("probe_a630", os.path.join(here, "probe_a630.py"))
pa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pa)
N = 1 << 14

DT = {"f32": dtypes.float32, "f16": dtypes.half, "i32": dtypes.int32, "u32": dtypes.uint32, "i16": dtypes.int16, "u16": dtypes.uint16,
      "i8": dtypes.int8, "u8": dtypes.uint8, "bool": dtypes.bool}
NP = {"f32": np.float32, "f16": np.float16, "i32": np.int32, "u32": np.uint32, "i16": np.int16, "u16": np.uint16, "i8": np.int8, "u8": np.uint8,
      "bool": np.bool_}
FLOATS, INTS = ("f32", "f16"), ("i32", "u32", "i16", "u16", "i8", "u8")

def gen(dt:str, key:str, stream:int, n:int=N) -> np.ndarray:
  u = pa.hashes(key, stream, n)
  if dt == "f32": return pa.floats(u, 8, 23).astype(np.uint32).view(np.float32)
  if dt == "f16": return pa.floats(u, 5, 10).astype(np.uint16).view(np.float16)
  if dt == "bool": return (u & np.uint64(1)).astype(np.bool_)
  bits = np.dtype(NP[dt]).itemsize * 8
  small = ((u >> np.uint64(8)) & np.uint64(0xFF)).astype(np.int64) - 128
  raw = (u >> np.uint64(64 - bits)).astype(f"u{bits // 8}").view(NP[dt])
  return np.where((u & np.uint64(3)) == 0, small.astype(NP[dt]), raw)

UNARY_F = {"neg": lambda x: -x, "abs": lambda x: x.abs(), "recip": lambda x: x.reciprocal(), "sqrt": lambda x: x.sqrt(), "rsqrt": lambda x: x.rsqrt(),
           "exp2": lambda x: x.exp2(), "log2": lambda x: x.log2(), "exp": lambda x: x.exp(), "log": lambda x: x.log(), "sin": lambda x: x.sin(),
           "cos": lambda x: x.cos(), "trunc": lambda x: x.trunc(), "floor": lambda x: x.floor(), "ceil": lambda x: x.ceil(), "round": lambda x: x.round(),
           "relu": lambda x: x.relu(), "sigmoid": lambda x: x.sigmoid(), "tanh": lambda x: x.tanh(), "gelu": lambda x: x.gelu(), "silu": lambda x: x.silu(),
           "softplus": lambda x: x.softplus(), "elu": lambda x: x.elu(), "square": lambda x: x * x, "sign": lambda x: x.sign(),
           "isnan": lambda x: x.isnan().cast(dtypes.int32), "isinf": lambda x: x.isinf().cast(dtypes.int32)}
BINARY_F = {"add": lambda a, b: a + b, "sub": lambda a, b: a - b, "mul": lambda a, b: a * b, "div": lambda a, b: a / b,
            "max": lambda a, b: a.maximum(b), "min": lambda a, b: a.minimum(b), "lt": lambda a, b: (a < b).cast(dtypes.int32),
            "eq": lambda a, b: (a == b).cast(dtypes.int32), "ne": lambda a, b: (a != b).cast(dtypes.int32), "pow": lambda a, b: a.abs() ** b,
            "where": lambda a, b: (a > 0).where(a, b)}
UNARY_I = {"neg": lambda x: -x, "abs": lambda x: x.abs(), "not": lambda x: ~x if x.dtype != dtypes.bool else x.logical_not(), "relu": lambda x: x.relu()}
BINARY_I = {"add": lambda a, b: a + b, "sub": lambda a, b: a - b, "mul": lambda a, b: a * b, "idiv": lambda a, b: a // (b.abs() + 1),
            "mod": lambda a, b: a % (b.abs() + 1), "max": lambda a, b: a.maximum(b), "min": lambda a, b: a.minimum(b),
            "lt": lambda a, b: (a < b).cast(dtypes.int32), "eq": lambda a, b: (a == b).cast(dtypes.int32), "and": lambda a, b: a & b,
            "or": lambda a, b: a | b, "xor": lambda a, b: a ^ b, "shl": lambda a, b: a << (b & 7), "shr": lambda a, b: a >> (b & 7),
            "where": lambda a, b: (a > 0).where(a, b)}

def cases() -> dict:
  out = {}
  for dt in FLOATS:
    for n, fn in UNARY_F.items(): out[f"{n}_{dt}"] = ((dt,), fn)
    for n, fn in BINARY_F.items(): out[f"{n}_{dt}"] = ((dt, dt), fn)
    out[f"mad_{dt}"] = ((dt, dt, dt), lambda a, b, c: a * b + c)
  for dt in INTS:
    for n, fn in UNARY_I.items(): out[f"{n}_{dt}"] = ((dt,), fn)
    for n, fn in BINARY_I.items(): out[f"{n}_{dt}"] = ((dt, dt), fn)
  for src, dst in itertools.product(DT, DT):
    if src != dst: out[f"cast_{src}_{dst}"] = ((src,), lambda x, d=DT[dst]: x.cast(d))
  for dt in FLOATS + ("i32",):
    out[f"sum_{dt}"] = ((dt,), lambda x: x.reshape(128, -1).sum(axis=1))
    out[f"max_red_{dt}"] = ((dt,), lambda x: x.reshape(128, -1).max(axis=1))
  out["conv_f16_img"] = (("f16", "f16"), lambda x, w: x[:2*8*32*32].reshape(2, 8, 32, 32).conv2d(w[:16*8*3*3].reshape(16, 8, 3, 3), padding=1).relu())
  out["matmul_f16_img"] = (("f16", "f16"), lambda a, b: (a[:64*128].reshape(64, 128) @ b[:128*96].reshape(128, 96)))
  out["softmax_f32"] = (("f32",), lambda x: (x.clip(-50, 50)).reshape(128, -1).softmax(axis=1))
  out["layernorm_f16"] = (("f16",), lambda x: x.clip(-100, 100).reshape(128, -1).layernorm())
  return out

def flags(name:str) -> dict: return {"IMAGE": 1, "FLOAT16": 1} if name.endswith("_img") else {}

def run(outdir:str):
  os.makedirs(outdir, exist_ok=True)
  for name, (dts, fn) in cases().items():
    f = os.path.join(outdir, name + ".npz")
    if os.path.exists(f): continue
    ins = [gen(dt, name, i) for i, dt in enumerate(dts)]
    try:
      with Context(**flags(name)): out = fn(*[Tensor(x) for x in ins]).realize().numpy()
      np.savez_compressed(f, out=out, inhash=np.array(zlib.crc32(b"".join(x.tobytes() for x in ins))))
    except Exception as e:
      np.savez(f, error=np.array(f"{type(e).__name__}: {str(e)[:300]}"))
      print(f"{name}: FAILED {type(e).__name__}: {str(e)[:160]}", flush=True)

def compare(hw:str, emu:str):
  ok, skipped = 0, []
  for f in sorted(glob.glob(os.path.join(hw, "*.npz"))):
    g = os.path.join(emu, os.path.basename(f))
    a = np.load(f)
    if "error" in a.files or not os.path.exists(g) or "error" in np.load(g).files:
      skipped.append(os.path.basename(f)[:-4] + (" (hw error)" if "error" in a.files else " (emu error/missing)"))
      continue
    b = np.load(g)
    x, y = a["out"], b["out"]
    if int(a["inhash"]) != int(b["inhash"]) or x.shape != y.shape or not np.array_equal(x.view(np.uint8), y.view(np.uint8)):
      d = np.flatnonzero(x.reshape(-1).view(np.uint8) != y.reshape(-1).view(np.uint8)) if x.nbytes == y.nbytes else []
      print(f"DIFF {os.path.basename(f)[:-4]}: {len(d)} bytes of {x.nbytes}")
    else: ok += 1
  print(f"{ok} cases match; skipped: {skipped}")

if __name__ == "__main__":
  if sys.argv[1] == "run": run(sys.argv[2])
  elif sys.argv[1] == "list": print(len(cases()), "cases")
  else: compare(sys.argv[2], sys.argv[3])
