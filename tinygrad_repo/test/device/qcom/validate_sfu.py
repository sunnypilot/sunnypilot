import sys, os, glob, re
import numpy as np
import test.mockgpu.qcom.emu as emu
from tinygrad.runtime.autogen import mesa
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import probe_sfu
OPS = {"rcp": mesa.OPC_RCP, "sqrt": mesa.OPC_SQRT, "exp2": mesa.OPC_EXP2, "log2": mesa.OPC_LOG2}

def model(op:str, x:np.ndarray) -> np.ndarray:
  if op == "img_f16": return emu.to_texel(x, np.dtype(np.float16)).view(np.uint16).astype(np.uint32)
  xf = emu.ftz(x)
  with np.errstate(all="ignore"): r = emu.CAT4[OPS[op]](xf.astype(np.float64)).astype(np.float32)
  out = emu.canonical_nan(emu.ftz(emu.sfu_delta(OPS[op], xf, r)))
  return out.view(np.uint32)

if __name__ == "__main__":
  bad, n = {}, 0
  for f in sorted(glob.glob(os.path.join(sys.argv[1], "*.npz"))):
    m = re.match(r"(.+)_s(\d)_e(\d+)\.npz$", os.path.basename(f))
    if m is None or m.group(1) not in list(OPS) + ["img_f16"]: continue
    op, sign, e = m.group(1), int(m.group(2)), int(m.group(3))
    x = (np.arange(probe_sfu.M, dtype=np.uint64) + ((sign << 31) | (e << 23))).astype(np.uint32).view(np.float32)
    hw = (probe_sfu.ref_bits(op, sign, e).astype(np.int64) + np.load(f)["d"]).astype(np.uint32)
    d = np.count_nonzero(model(op, x) != hw)
    n += 1
    if d: bad[f"{op} s{sign} e{e}"] = d
  print(f"{n} sweeps checked, {len(bad)} with mismatches: {dict(list(bad.items())[:20])}")
