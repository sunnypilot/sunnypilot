import sys, os, glob, zlib, importlib.util
import numpy as np
here = os.path.dirname(os.path.abspath(__file__))
def _load(name):
  spec = importlib.util.spec_from_file_location(name, os.path.join(here, f"{name}.py"))
  m = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(m)
  return m
pa = _load("probe_all")
probe = pa.probe
from tinygrad.device import Device, Buffer
import tinygrad.runtime.autogen.amd.rdna4.ins as r4
from tinygrad.runtime.autogen.amd.rdna4.operands import OPERANDS
from tinygrad.renderer.amd.dsl import s, v, ttmp, NULL

CASES, WIN, WOUT = 2048, 24, 8
A, B, C, IDX = 0, 4, 12, 20

def elems(kind:str, key:str, stream:int, n:int, finite:bool=False) -> np.ndarray:
  u, u2 = pa.hashes(key, stream, n), pa.hashes(key, stream + 50, n)
  sel = pa._f(u2, 0, 6)
  if kind in ("F16", "BF16", "F32"):
    rnd = np.frombuffer(np.random.Generator(np.random.PCG64(zlib.crc32(f"{key}/{stream}".encode()))).standard_normal(n).tobytes(), np.float64)
    scale = 2.0 ** (pa._f(u2, 8, 5).astype(np.int64) - 16).astype(np.float64)
    vals = np.where(sel < 40, rnd, np.where(sel < 52, rnd * scale, (pa._f(u2, 16, 12).astype(np.float64) - 2048) * 2.0 ** -10))
    eb, mb = {"F16": (5, 10), "BF16": (8, 7), "F32": (8, 23)}[kind]
    if kind == "F16": bits = vals.astype(np.float16).view(np.uint16).astype(np.uint64)
    elif kind == "BF16": bits = (vals.astype(np.float32).view(np.uint32) >> 16).astype(np.uint64)
    else: bits = vals.astype(np.float32).view(np.uint32).astype(np.uint64)
    special = pa.floats(u, eb, mb)
    return bits if finite else np.where(sel >= 60, special, bits)
  if kind in ("FP8", "BF8"):
    if finite: return (pa._f(u, 8, 7) % np.uint64(0x7F if kind == "FP8" else 0x7C)) | (pa._f(u, 16, 1) << np.uint64(7))  # no NaN/inf codes
    return np.where(sel < 48, pa._f(u, 8, 7), pa._f(u, 8, 8))
  if kind == "IU8": return pa._f(u, 8, 8)
  if kind == "IU4": return pa._f(u, 8, 4)
  raise ValueError(kind)

def _pack(bits:np.ndarray, width:int) -> np.ndarray:
  per = 32 // width
  b = bits.reshape(-1, per).astype(np.uint64)
  return (b << (np.arange(per, dtype=np.uint64) * np.uint64(width))).sum(axis=1).astype(np.uint32)

def _fmt(fmtname:str) -> tuple[str, int]:
  t = fmtname.split("_")[-1]
  return t, {"F16": 16, "BF16": 16, "F32": 32, "I32": 32, "FP8": 8, "BF8": 8, "IU8": 8, "IU4": 4}[t]

def matrix_ops() -> list[str]:
  ops = [n for n in sorted(dir(r4)) if n.startswith(("v_wmma_", "v_swmmac_"))]
  return ops + [n + "|finite" for n in ops if "8" in n.split("_", 3)[-1] and "iu" not in n]  # fp8/bf8 forms on finite inputs too

def build(name:str):
  fn = getattr(r4, name)
  op = fn.args[0]
  spec = {k: (f.name, bits) for k, (f, bits, _) in OPERANDS[op].items()}
  def regs(base, bits): return v[base] if bits <= 32 else v[base:base + bits // 32 - 1]
  sparse = name.startswith("v_swmmac")
  inst = r4.VOP3P(op, vdst=regs(C, spec["vdst"][1]), src0=regs(A, spec["src0"][1]), src1=regs(B, spec["src1"][1]),
                  src2=v[IDX] if sparse else regs(C, spec["src2"][1]))
  return inst, spec, sparse

def inputs(name:str, spec:dict, sparse:bool, cases:int) -> np.ndarray:
  lanes = cases * 32
  out = np.zeros((lanes, WIN), np.uint32)
  for base, field, st in ((A, "src0", 1), (B, "src1", 2), (C, "vdst", 3)):
    kind, width = _fmt(spec[field][0])
    dw = spec[field][1] // 32
    if kind == "I32": col = pa.ints32(pa.hashes(name, st, lanes * dw))
    else: col = _pack(elems(kind, name, st, lanes * dw * (32 // width), name.endswith("|finite")), width)
    col = col.reshape(lanes, dw)
    if field == "vdst": col = np.where((np.arange(cases).repeat(32) % 8 < 2)[:, None], 0, col)
    out[:, base:base + dw] = col
  if sparse: out[:, IDX] = pa.hashes(name, 4, lanes).astype(np.uint32)
  return out

def run_one(inst, inp:np.ndarray, cases:int) -> np.ndarray:
  out = Buffer(Device.DEFAULT, cases * 32 * WOUT * 4).ensure_allocated()
  src = probe.gpu(inp.reshape(-1))
  body = probe.MODE + [r4.s_load_b128(s[4:7], s[0:1], soffset=NULL), r4.s_wait_kmcnt(simm16=0), r4.s_lshl_b32(s[12], ttmp[9], 5),
          r4.v_add_nc_u32_e32(v[30], s[12], v[0]), r4.v_mul_u32_u24_e32(v[32], WIN * 4, v[30]), r4.v_mov_b32_e32(v[33], 0),
          *[r4.global_load_b128(vdst=v[4*j:4*j+3], vaddr=v[32:33], saddr=s[6:7], ioffset=16*j) for j in range(WIN // 4)], r4.s_wait_loadcnt(simm16=0),
          inst,
          r4.v_lshlrev_b32_e32(v[32], 5, v[30]),
          r4.global_store_b128(vaddr=v[32:33], saddr=s[4:5], vsrc=v[C:C+3]),
          r4.global_store_b128(vaddr=v[32:33], saddr=s[4:5], vsrc=v[C+4:C+7], ioffset=16)]
  probe.launch("probe_matrix", body, cases, 32, [out, src])
  return probe.readback(out).reshape(cases, 32, WOUT)

def run(outdir:str, limit:int):
  os.makedirs(outdir, exist_ok=True)
  todo = [n for n in matrix_ops() if not os.path.exists(os.path.join(outdir, n.replace("|", "+") + ".npz"))]
  for name in todo[:limit]:
    inst, spec, sparse = build(name.split("|")[0])
    inp = inputs(name, spec, sparse, CASES)
    try: res = run_one(inst, inp, CASES)
    except Exception as e:
      print(f"{name}: FAILED {type(e).__name__}: {str(e)[:200]}", flush=True)
      np.savez(os.path.join(outdir, name.replace("|", "+") + ".npz"), error=np.array(f"{type(e).__name__}: {e}"))
      continue
    np.savez_compressed(os.path.join(outdir, name.replace("|", "+") + ".npz"), out=res, inhash=np.array(zlib.crc32(inp.tobytes())),
                        sig=np.array(pa.signature(inst) + ("|finite" if name.endswith("|finite") else "")))
    print(f"{name}: done", flush=True)
  print(f"{max(0, len(todo) - limit)} left", flush=True)

def compare(hw:str, emu:str):
  ok = 0
  for f in sorted(glob.glob(os.path.join(hw, "*.npz"))):
    a, g = np.load(f), os.path.join(emu, os.path.basename(f))
    b = np.load(g) if os.path.exists(g) else None
    if "error" in a.files or b is None or "error" in b.files:
      print(f"SKIP {os.path.basename(f)}: {'hw error' if 'error' in a.files else 'emulator missing or error'}")
      continue
    if int(a["inhash"]) != int(b["inhash"]):
      print(f"DIFF {os.path.basename(f)}: inputs differ")
      continue
    x, y = a["out"], b["out"]
    bad = np.flatnonzero((x != y).reshape(len(x), -1).any(axis=1))
    if bad.size: print(f"DIFF {os.path.basename(f)}: {bad.size} of {len(x)} cases differ, {int((x != y).sum())} dwords")
    else: ok += 1
  print(f"{ok} matrix ops match")

if __name__ == "__main__":
  if sys.argv[1] == "run": run(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1 << 30)
  elif sys.argv[1] == "compare": compare(sys.argv[2], sys.argv[3])
