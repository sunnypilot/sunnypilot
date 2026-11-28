import sys, time
import numpy as np
from tinygrad.device import Device, Buffer
from tinygrad.dtype import dtypes
from tinygrad.uop.ops import UOp, Ops, KernelInfo
from tinygrad.engine.realize import run_linear
from tinygrad.renderer.amd.dsl import s, v, ttmp, NULL
import tinygrad.runtime.autogen.amd.rdna4.ins as r4

SEED, LOCAL, WMMA_CASES = 1234, 256, 4096

def launch(name:str, body:list, n_wg:int, local:int, bufs:list[Buffer]) -> None:
  params = [UOp.param(i, dtypes.uint32, (b.nbytes // 4,)) for i, b in enumerate(bufs)]
  sink = UOp.sink(*params, UOp.special(local, "lidx0"), UOp.special(n_wg, "gidx0"), arg=KernelInfo(name))
  prg = UOp(Ops.PROGRAM, src=(sink, UOp(Ops.LINEAR, src=tuple(UOp(Ops.INS, arg=(x, dtypes.void)) for x in body + [r4.s_endpgm()]))))
  run_linear(UOp(Ops.LINEAR, src=(prg.call(*[UOp.from_buffer(b, dtypes.uint32) for b in bufs]),)), wait=True)

def gpu(data:np.ndarray) -> Buffer:
  return Buffer(Device.DEFAULT, data.nbytes, initial_value=np.ascontiguousarray(data).tobytes()).ensure_allocated()

def readback(b:Buffer) -> np.ndarray: return np.frombuffer(bytes(b.as_memoryview()), dtype=np.uint32).copy()

MODE = [r4.s_denorm_mode(simm16=0xF)]
PROLOGUE = MODE + [r4.s_load_b256(s[4:11], s[0:1], soffset=NULL), r4.s_wait_kmcnt(simm16=0), r4.s_lshl_b32(s[12], ttmp[9], 8),
            r4.v_add_nc_u32_e32(v[1], s[12], v[0]), r4.v_lshlrev_b32_e32(v[10], 2, v[1]), r4.v_mov_b32_e32(v[11], 0)]

def run_elementwise(name:str, op, n:int, base:int|None=None, inputs:tuple[np.ndarray, ...]=()) -> np.ndarray:
  out = Buffer(Device.DEFAULT, n * 4).ensure_allocated()
  ins = [gpu(np.array([base], np.uint32))] if base is not None else [gpu(x) for x in inputs]
  ins += [ins[0]] * (3 - len(ins))
  if base is not None:
    loads = [r4.s_load_b32(s[13], s[6:7], soffset=NULL), r4.s_wait_kmcnt(simm16=0), r4.v_add_nc_u32_e32(v[2], s[13], v[1])]
  else:
    loads = [r4.global_load_b32(vdst=v[r], vaddr=v[10:11], saddr=s[a:a+1]) for r, a in ((2, 6), (4, 8), (5, 10))] + [r4.s_wait_loadcnt(simm16=0)]
  body = PROLOGUE + loads + [r4.v_mov_b32_e32(v[3], 0), *op, r4.global_store_b32(vaddr=v[10:11], saddr=s[4:5], vsrc=v[3])]
  assert n % LOCAL == 0
  launch(name, body, n // LOCAL, LOCAL, [out, *ins])
  return readback(out)

def f32_delta(bits:np.ndarray, exact:np.ndarray) -> np.ndarray:
  ref = exact.astype(np.float32).view(np.uint32).astype(np.int64)
  def ordered(x): return np.where(x & 0x80000000, -(x & 0x7FFFFFFF), x)
  d = ordered(bits.astype(np.int64)) - ordered(ref)
  both_nan = np.isnan(bits.view(np.float32)) & np.isnan(exact)
  return np.where(both_nan, 0, np.clip(d, -127, 127)).astype(np.int8)

def unary_f32(name:str, inst, ranges:list[tuple[int, int]], exact) -> dict:
  out = {}
  for base, n in ranges:
    st = time.perf_counter()
    bits = run_elementwise(name, [inst(v[3], v[2])], n, base=base)
    x = (np.arange(n, dtype=np.uint64) + base).astype(np.uint32).view(np.float32).astype(np.float64)
    with np.errstate(all="ignore"): out[f"{name}_{base:08x}_{n}"] = f32_delta(bits, exact(x))
    d = out[f"{name}_{base:08x}_{n}"]
    print(f"{name} 0x{base:08x}+{n}: {np.count_nonzero(d)} not correctly rounded, delta range [{d.min()}, {d.max()}] "
          f"({time.perf_counter()-st:.1f}s)", flush=True)
  return out

def mant_sweep(exponent:int, sign:int=0) -> tuple[int, int]: return ((sign << 31) | (exponent << 23), 1 << 23)
def sample(exponent:int, sign:int=0, n:int=1 << 16) -> tuple[int, int]: return ((sign << 31) | (exponent << 23), n)

def probe_unary() -> dict:
  res = {}
  for name, inst in (("rcp_f16", r4.v_rcp_f16_e32), ("exp_f16", r4.v_exp_f16_e32), ("sqrt_f16", r4.v_sqrt_f16_e32), ("rsq_f16", r4.v_rsq_f16_e32),
                     ("log_f16", r4.v_log_f16_e32)):
    res[name] = (run_elementwise(name, [inst(v[3], v[2])], 1 << 16, base=0) & 0xFFFF).astype(np.uint16)  # every f16 input
    print(f"{name}: all 65536 inputs", flush=True)
  edge = [sample(0), sample(0, 1), sample(1), sample(2), sample(252), sample(253), sample(254), sample(254, 1)]
  res |= unary_f32("rcp_f32", r4.v_rcp_f32_e32, [mant_sweep(127), mant_sweep(127, 1), *edge], lambda x: 1.0 / x)
  res |= unary_f32("sqrt_f32", r4.v_sqrt_f32_e32, [mant_sweep(127), mant_sweep(128), sample(0), sample(1), sample(254)], np.sqrt)
  res |= unary_f32("rsq_f32", r4.v_rsq_f32_e32, [mant_sweep(127), mant_sweep(128)], lambda x: 1.0 / np.sqrt(x))
  res |= unary_f32("exp_f32", r4.v_exp_f32_e32, [mant_sweep(e, sg) for e in (125, 126, 127, 128, 129) for sg in (0, 1)] +
                   [sample(e, sg) for e in range(130, 134) for sg in (0, 1)] + [sample(e) for e in range(100, 125, 4)], np.exp2)
  res |= unary_f32("log_f32", r4.v_log_f32_e32, [mant_sweep(127), mant_sweep(126), sample(0), sample(1)], np.log2)
  return res

def f16_midpoint_cases(rng, n:int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
  h = rng.integers(0x0400, 0x7800, n).astype(np.uint16) | (rng.integers(0, 2, n).astype(np.uint16) << 15)
  hv = h.view(np.float16).astype(np.float64)
  mid = hv + np.copysign(np.spacing(np.abs(h.view(np.float16))).astype(np.float64) / 2, hv)
  a = rng.uniform(0.5, 2.0, n).astype(np.float32) * rng.choice([-1, 1], n).astype(np.float32)
  b = (mid / a.astype(np.float64) * rng.uniform(0.25, 1.0, n)).astype(np.float32)
  c = (mid - a.astype(np.float64) * b.astype(np.float64)).astype(np.float32)
  return a, b, c

def probe_fma() -> dict:
  rng, res, n = np.random.default_rng(SEED), {}, 1 << 18
  a16 = rng.integers(0, 0x7C00, n).astype(np.uint16) | (rng.integers(0, 2, n).astype(np.uint16) << 15)
  b16 = rng.integers(0x3000, 0x4800, n).astype(np.uint16)
  c16 = rng.integers(0, 0x7C00, n).astype(np.uint16) | (rng.integers(0, 2, n).astype(np.uint16) << 15)
  a16[n//2:] = rng.integers(0x3C00, 0x4400, n//2)
  b16[n//2:] = rng.integers(0x3C00, 0x4400, n//2)
  c16[n//2:] = rng.integers(0x0400, 0x1800, n//2)
  res["fma_f16"] = (run_elementwise("fma_f16", [r4.v_fma_f16(v[3], v[2], v[4], v[5])], n,
                                    inputs=(a16.astype(np.uint32), b16.astype(np.uint32), c16.astype(np.uint32))) & 0xFFFF).astype(np.uint16)
  a, b, c = f16_midpoint_cases(rng, n // 2)
  ra = rng.standard_normal(n // 2).astype(np.float32)
  rb = rng.standard_normal(n // 2).astype(np.float32)
  rc = rng.standard_normal(n // 2).astype(np.float32)
  fa, fb, fc = np.concatenate([a, ra]), np.concatenate([b, rb]), np.concatenate([c, rc])
  mix = r4.VOP3P(r4.VOP3POp.V_FMA_MIXLO_F16, vdst=v[3], src0=v[2], src1=v[4], src2=v[5], opsel=0, opsel_hi=0, opsel_hi2=0)
  res["fma_mixlo_f16"] = (run_elementwise("fma_mixlo_f16", [mix], n, inputs=(fa, fb, fc)) & 0xFFFF).astype(np.uint16)
  res["cvt_f16_f32"] = (run_elementwise("cvt_f16_f32", [r4.v_cvt_f16_f32_e32(v[3], v[2])], n, inputs=(fc,)) & 0xFFFF).astype(np.uint16)
  print("fma_f16, fma_mixlo_f16, cvt_f16_f32: done", flush=True)
  return res

def wmma_inputs() -> np.ndarray:
  rng = np.random.default_rng(SEED + 1)
  cases = np.zeros((WMMA_CASES, 32, 16), np.uint32)
  for i in range(WMMA_CASES):
    kind = i % 4
    if kind == 0: ab = rng.standard_normal((32, 8)).astype(np.float16)  # typical activations
    elif kind == 1: ab = (rng.standard_normal((32, 8)) * 2.0 ** rng.integers(-12, 12, (32, 8))).astype(np.float16)  # wide exponent spread
    elif kind == 2: ab = rng.choice([1.0, -1.0, 2.0 ** -11, -(2.0 ** -11), 2.0 ** -24, 1024.0], (32, 8)).astype(np.float16)  # cancellation, order
    else: ab = (rng.integers(-2048, 2048, (32, 8)) * 2.0 ** -10).astype(np.float16)
    bb = (rng.standard_normal((32, 8)) * (2.0 ** rng.integers(-6, 6, (32, 8)) if kind == 1 else 1)).astype(np.float16)
    c = (rng.standard_normal((32, 8)) * (0 if i % 8 < 2 else 2.0 ** rng.integers(-10, 10))).astype(np.float32)
    cases[i, :, 0:4] = ab.view(np.uint16).reshape(32, 4, 2).astype(np.uint32) @ np.array([1, 1 << 16], np.uint32)
    cases[i, :, 4:8] = bb.view(np.uint16).reshape(32, 4, 2).astype(np.uint32) @ np.array([1, 1 << 16], np.uint32)
    cases[i, :, 8:16] = c.view(np.uint32)
  return cases

def probe_wmma() -> dict:
  cases = wmma_inputs()
  out = Buffer(Device.DEFAULT, WMMA_CASES * 32 * 8 * 4).ensure_allocated()
  body = MODE + [r4.s_load_b128(s[4:7], s[0:1], soffset=NULL), r4.s_wait_kmcnt(simm16=0), r4.s_lshl_b32(s[12], ttmp[9], 5),
          r4.v_add_nc_u32_e32(v[20], s[12], v[0]), r4.v_lshlrev_b32_e32(v[22], 6, v[20]), r4.v_mov_b32_e32(v[23], 0),
          *[r4.global_load_b128(vdst=v[4*j:4*j+3], vaddr=v[22:23], saddr=s[6:7], ioffset=16*j) for j in range(4)], r4.s_wait_loadcnt(simm16=0),
          r4.v_wmma_f32_16x16x16_f16(v[8:15], v[0:3], v[4:7], v[8:15]),
          r4.v_lshlrev_b32_e32(v[22], 5, v[20]),
          r4.global_store_b128(vaddr=v[22:23], saddr=s[4:5], vsrc=v[8:11]),
          r4.global_store_b128(vaddr=v[22:23], saddr=s[4:5], vsrc=v[12:15], ioffset=16)]
  launch("wmma_probe", body, WMMA_CASES, 32, [out, gpu(cases)])
  print(f"wmma: {WMMA_CASES} cases", flush=True)
  return {"wmma_f32_16x16x16_f16": readback(out).reshape(WMMA_CASES, 32, 8)}

def run(path:str):
  dev = Device[Device.DEFAULT]
  arch = getattr(dev, "arch", "")
  print(f"device {Device.DEFAULT} arch {arch}", flush=True)
  st = time.perf_counter()
  res = probe_unary() | probe_fma() | probe_wmma()
  np.savez_compressed(path, device=np.array(Device.DEFAULT), arch=np.array(str(arch)), **res)
  print(f"wrote {path} in {time.perf_counter()-st:.0f}s", flush=True)

def compare(a_path:str, b_path:str):
  a, b = np.load(a_path), np.load(b_path)
  print(f"{a_path}: {a['device']} {a['arch']}  vs  {b_path}: {b['device']} {b['arch']}")
  for k in sorted(set(a.files) - {"device", "arch"}):
    if k not in b.files:
      print(f"{k}: missing in {b_path}")
      continue
    x, y = a[k], b[k]
    if x.dtype == np.uint16:  # f16 results: NaNs with different payloads count as equal
      nan = ((x & 0x7C00) == 0x7C00) & ((x & 0x3FF) != 0) & ((y & 0x7C00) == 0x7C00) & ((y & 0x3FF) != 0)
      diff = (x != y) & ~nan
    elif x.dtype == np.int8: diff = x != y
    else:
      xf, yf = x.view(np.float32), y.view(np.float32)
      diff = (x != y) & ~(np.isnan(xf) & np.isnan(yf))
    idx = np.flatnonzero(diff)
    print(f"{k:34s} {'MATCH' if idx.size == 0 else f'{idx.size} of {x.size} differ'}" +
          ("" if idx.size == 0 else f"  first at {idx[:4].tolist()}: {x.reshape(-1)[idx[:4]].tolist()} vs {y.reshape(-1)[idx[:4]].tolist()}"))

if __name__ == "__main__":
  if sys.argv[1] == "run": run(sys.argv[2])
  elif sys.argv[1] == "compare": compare(sys.argv[2], sys.argv[3])
  else: raise SystemExit("usage: probe_rounding.py run OUT.npz | compare A.npz B.npz")
