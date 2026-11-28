import sys, os
import numpy as np
from tinygrad import Tensor, dtypes
from tinygrad.helpers import Context

def rtz_f16(x:np.ndarray) -> np.ndarray:  # model of the image store: f32 -> f16 rounding toward zero, NaN canonical
  with np.errstate(all="ignore"): r = x.astype(np.float32).astype(np.float16)
  r = np.where(np.abs(r.astype(np.float64)) > np.abs(x), np.nextafter(r, np.float16(0)), r).astype(np.float16)
  return np.where(np.isnan(x), np.uint16(0x7E00).view(np.float16), r)

REF = {"rcp": lambda x: 1.0 / x, "sqrt": np.sqrt, "exp2": np.exp2, "log2": np.log2, "img_f16": rtz_f16}
FN = {"rcp": lambda t: t.reciprocal(), "sqrt": lambda t: t.sqrt(), "exp2": lambda t: t.exp2(), "log2": lambda t: t.log2(),
      "img_f16": lambda t: t.reshape(2048, 4096).cast(dtypes.half).contiguous()}
M = 1 << 23

def sweep(op:str, sign:int, e:int) -> np.ndarray:  # inputs uploaded as f32 and outputs read back as f32: a bitcast in the graph moves it to the CPU
  x = Tensor((np.arange(M, dtype=np.uint64) + ((sign << 31) | (e << 23))).astype(np.uint32).view(np.float32))
  with Context(IMAGE=1 if op.startswith("img") else 0): out = FN[op](x).realize()
  assert out.device.startswith("QCOM"), out.device
  o = out.numpy()
  return o.reshape(-1).view(np.uint16).astype(np.uint32) if o.dtype == np.float16 else o.view(np.uint32)

def ref_bits(op:str, sign:int, e:int) -> np.ndarray:
  x = (np.arange(M, dtype=np.uint64) + ((sign << 31) | (e << 23))).astype(np.uint32).view(np.float32).astype(np.float64)
  with np.errstate(all="ignore"): r = REF[op](x)
  return r.view(np.uint16).astype(np.uint32) if r.dtype == np.float16 else r.astype(np.float32).view(np.uint32)

if __name__ == "__main__":
  outdir, op, sign, es = sys.argv[1], sys.argv[2], int(sys.argv[3]), [int(e) for e in sys.argv[4:]]
  os.makedirs(outdir, exist_ok=True)
  for e in es:
    f = os.path.join(outdir, f"{op}_s{sign}_e{e}.npz")
    if os.path.exists(f): continue
    hw = sweep(op, sign, e).astype(np.int64)
    np.savez_compressed(f + ".tmp.npz", d=(hw - ref_bits(op, sign, e).astype(np.int64)).astype(np.int32))
    os.replace(f + ".tmp.npz", f)
    print(f"{op} sign {sign} exponent {e}: done", flush=True)
