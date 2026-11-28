import sys, os, zlib, glob
import numpy as np
from tinygrad import Tensor, dtypes
from tinygrad.helpers import Context

N = 1 << 16

def hashes(key:str, stream:int, n:int) -> np.ndarray:  # splitmix64 of (key, stream, index)
  with np.errstate(over="ignore"):
    x = (np.arange(n, dtype=np.uint64) + np.uint64(((zlib.crc32(key.encode()) << 24) ^ (stream << 16)) & 0xFFFFFFFFFFFF) * np.uint64(1 << 16))
    x = x * np.uint64(0x9E3779B97F4A7C15)
    x ^= x >> np.uint64(30)
    x *= np.uint64(0xBF58476D1CE4E5B9)
    x ^= x >> np.uint64(27)
    x *= np.uint64(0x94D049BB133111EB)
    x ^= x >> np.uint64(31)
  return x

def _f(u, lo, n): return ((u >> np.uint64(lo)) & np.uint64((1 << n) - 1)).astype(np.uint64)

def floats(u:np.ndarray, eb:int, mb:int) -> np.ndarray:  # normals near 1, all exponents, denormals, specials, raw bits
  emax, bias = (1 << eb) - 1, (1 << (eb - 1)) - 1
  kind, sign, mant = _f(u, 0, 4), _f(u, 4, 1), _f(u, 64 - mb, mb)
  e = np.where(kind < 4, 1 + _f(u, 8, 16) % np.uint64(emax - 1), bias - 8 + _f(u, 8, 4))
  edge = np.array([0, 1, 2, emax - 2, emax - 1, emax, bias - 1, bias, bias + 1], np.uint64)
  e = np.where(kind == 8, edge[_f(u, 8, 8) % np.uint64(len(edge))], e)
  e = np.where(kind == 9, 0, e)
  medge = np.array([0, 1, 2, (1 << mb) - 1, (1 << mb) - 2, 1 << (mb - 1), (1 << (mb - 1)) + 1, (1 << (mb - 1)) - 1], np.uint64)
  mant = np.where((kind == 8) | (kind == 10), medge[_f(u, 16, 8) % np.uint64(len(medge))], mant)
  e = np.where(kind == 10, np.array([emax, 0, bias], np.uint64)[_f(u, 24, 4) % np.uint64(3)], e)
  bits = (sign << np.uint64(eb + mb)) | (e << np.uint64(mb)) | mant
  return np.where(kind >= 13, _f(u, 8, eb + mb + 1), bits)

def f32s(key, s): return floats(hashes(key, s, N), 8, 23).astype(np.uint32).view(np.float32)
def f16s(key, s): return floats(hashes(key, s, N), 5, 10).astype(np.uint16).view(np.float16)
def i32s(key, s):
  u = hashes(key, s, N)
  return np.where(_f(u, 0, 2) == 0, _f(u, 8, 10).astype(np.int64) - 512, _f(u, 32, 32).astype(np.int64) - (1 << 31)).astype(np.int32)
def u8s(key, s): return _f(hashes(key, s, N), 8, 8).astype(np.uint8)

def T(x:np.ndarray) -> Tensor: return Tensor(x)

F32, F16 = (f32s,), (f16s,)
CASES = {
  "add_f32": ((f32s, f32s), lambda a, b: a + b), "sub_f32": ((f32s, f32s), lambda a, b: a - b), "mul_f32": ((f32s, f32s), lambda a, b: a * b),
  "mad_f32": ((f32s, f32s, f32s), lambda a, b, c: a * b + c), "max_f32": ((f32s, f32s), lambda a, b: a.maximum(b)),
  "min_f32": ((f32s, f32s), lambda a, b: a.minimum(b)), "lt_f32": ((f32s, f32s), lambda a, b: (a < b).cast(dtypes.int32)),
  "eq_f32": ((f32s, f32s), lambda a, b: (a == b).cast(dtypes.int32)), "where_f32": ((f32s, f32s, f32s), lambda a, b, c: (a < c).where(a, b)),
  "relu_f32": (F32, lambda a: a.relu()), "trunc_f32": (F32, lambda a: a.trunc()), "floor_f32": (F32, lambda a: a.floor()),
  "neg_f32": (F32, lambda a: -a), "abs_f32": (F32, lambda a: a.abs()),
  "recip_f32": (F32, lambda a: a.reciprocal()), "div_f32": ((f32s, f32s), lambda a, b: a / b), "sqrt_f32": (F32, lambda a: a.sqrt()),
  "exp2_f32": (F32, lambda a: a.exp2()), "log2_f32": (F32, lambda a: a.log2()), "sin_f32": (F32, lambda a: a.sin()),
  "exp_f32": (F32, lambda a: a.exp()), "sigmoid_f32": (F32, lambda a: a.sigmoid()), "tanh_f32": (F32, lambda a: a.tanh()),
  "add_f16": ((f16s, f16s), lambda a, b: a + b), "mul_f16": ((f16s, f16s), lambda a, b: a * b), "mad_f16": ((f16s, f16s, f16s), lambda a, b, c: a * b + c),
  "max_f16": ((f16s, f16s), lambda a, b: a.maximum(b)), "lt_f16": ((f16s, f16s), lambda a, b: (a < b).cast(dtypes.int32)),
  "recip_f16": (F16, lambda a: a.reciprocal()), "sqrt_f16": (F16, lambda a: a.sqrt()), "exp2_f16": (F16, lambda a: a.exp2()),
  "log2_f16": (F16, lambda a: a.log2()), "trunc_f16": (F16, lambda a: a.trunc()),
  "mix_f16_f32": ((f16s, f32s), lambda a, b: a.cast(dtypes.float32) * b), "mix_f32_f16": ((f32s, f16s), lambda a, b: (a * b.cast(dtypes.float32)).cast(dtypes.half)),
  "cast_f32_f16": (F32, lambda a: a.cast(dtypes.half)), "cast_f16_f32": (F16, lambda a: a.cast(dtypes.float32)),
  "cast_f32_i32": (F32, lambda a: a.cast(dtypes.int32)), "cast_f32_u8": (F32, lambda a: a.cast(dtypes.uint8)),
  "cast_f32_i16": (F32, lambda a: a.cast(dtypes.int16)), "cast_f16_i32": (F16, lambda a: a.cast(dtypes.int32)),
  "cast_i32_f32": ((i32s,), lambda a: a.cast(dtypes.float32)), "cast_i32_f16": ((i32s,), lambda a: a.cast(dtypes.half)),
  "cast_u8_f32": ((u8s,), lambda a: a.cast(dtypes.float32)), "cast_u8_f16": ((u8s,), lambda a: a.cast(dtypes.half)),
  "img_store_f32_f16": (F32, lambda a: a.reshape(128, 512).cast(dtypes.half).contiguous().float()),
  "img_store_f32_f16_rtz": ((f32s, f32s), lambda a, b: (a * b).reshape(128, 512).cast(dtypes.half).contiguous()),
  "img_read_f16": (F16, lambda a: a.reshape(128, 512).contiguous().float() * 1.0),
  "img_rt_f32": (F32, lambda a: (a.reshape(128, 512).contiguous() + 0.0).contiguous()),
  "img_mad_f16": ((f16s, f16s, f16s), lambda a, b, c: (a.reshape(128, 512) * b.reshape(128, 512) + c.reshape(128, 512)).contiguous()),
  "img_read_all_f16": ((lambda key, s: np.arange(N, dtype=np.uint32).astype(np.uint16).view(np.float16),),
                       lambda a: a.reshape(128, 512).contiguous().float() * 1.0),
  "idiv_i32": ((i32s, i32s), lambda a, b: a // (b.abs() + 1)), "imul_i32": ((i32s, i32s), lambda a, b: a * b),
  "shr_i32": ((i32s, i32s), lambda a, b: a >> (b & 31)), "imod_i32": ((i32s, i32s), lambda a, b: a % (b.abs() + 1)),
}

def run(outdir:str):
  os.makedirs(outdir, exist_ok=True)
  for name, (gens, fn) in CASES.items():
    f = os.path.join(outdir, name + ".npz")
    if os.path.exists(f): continue
    ins = [g(name, i) for i, g in enumerate(gens)]
    try:
      out = fn(*[T(x) for x in ins]).realize().numpy()
      np.savez_compressed(f, out=out, inhash=np.array(zlib.crc32(b"".join(x.tobytes() for x in ins))))
      print(f"{name}: done", flush=True)
    except Exception as e:
      np.savez(f, error=np.array(f"{type(e).__name__}: {e}"))
      print(f"{name}: FAILED {type(e).__name__}: {str(e)[:200]}", flush=True)

def compare(hw:str, emu:str):
  ok = 0
  for f in sorted(glob.glob(os.path.join(hw, "*.npz"))):
    a, g = np.load(f), os.path.join(emu, os.path.basename(f))
    if not os.path.exists(g) or "error" in a.files or "error" in np.load(g).files:
      print(f"SKIP {os.path.basename(f)}")
      continue
    b = np.load(g)
    x, y = a["out"], b["out"]
    if int(a["inhash"]) != int(b["inhash"]): print(f"DIFF {os.path.basename(f)}: inputs differ")
    elif x.shape != y.shape or x.dtype != y.dtype: print(f"DIFF {os.path.basename(f)}: shape/dtype {x.shape}{x.dtype} vs {y.shape}{y.dtype}")
    elif not np.array_equal(x.view(np.uint8), y.view(np.uint8)):
      xb, yb = x.reshape(-1).view(f"u{x.itemsize}"), y.reshape(-1).view(f"u{y.itemsize}")
      d = np.flatnonzero(xb != yb)
      print(f"DIFF {os.path.basename(f)}: {d.size} of {x.size}, e.g. idx {d[:3].tolist()} hw {[hex(int(v)) for v in xb[d[:3]]]} emu {[hex(int(v)) for v in yb[d[:3]]]}")
    else: ok += 1
  print(f"{ok} cases match")

if __name__ == "__main__":
  if sys.argv[1] == "run":
    with Context(**({"IMAGE": int(os.environ["PROBE_IMAGE"])} if "PROBE_IMAGE" in os.environ else {})): run(sys.argv[2])
  else: compare(sys.argv[2], sys.argv[3])
