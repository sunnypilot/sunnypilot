import sys, os, re, zlib, glob, copy, functools, importlib.util
import numpy as np
spec = importlib.util.spec_from_file_location("probe_rounding", os.path.join(os.path.dirname(os.path.abspath(__file__)), "probe_rounding.py"))
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)
from tinygrad.device import Device, Buffer
import tinygrad.runtime.autogen.amd.rdna4.ins as r4
from tinygrad.runtime.autogen.amd.rdna4.operands import OPERANDS
from tinygrad.renderer.amd.dsl import s, v, src, ttmp, NULL, VCC_LO, EXEC_LO, INV_2PI, DPP16 as DPP16_SRC

N_DEFAULT, N_MODS, N_CONSTS, LOCAL, WIN, WOUT = 1 << 16, 1 << 13, 1 << 11, 256, 9, 5
FLOAT = re.compile(r"_(f16|f32|f64|bf16|fp8|bf8)\b|_(f16|f32|f64|bf16)_|wmma|swmmac|_dot\d|_pk_")
SKIP_CLASSES = ("DS", "VBUFFER", "VFLAT", "VGLOBAL", "VIMAGE", "SOP1", "SOP2", "SOPC", "SOPK", "SOP2_LIT")
DST, SRC, VCCW = (40, 41), ((20, 21), (24, 25), (28, 29)), 32
K32, K16 = 0x3dcccccd, 0x2e66

def hashes(key:str, stream:int, n:int) -> np.ndarray:
  with np.errstate(over="ignore"):
    x = np.arange(n, dtype=np.uint64) + np.uint64(((zlib.crc32(key.encode()) << 24) ^ (stream << 16)) & 0xFFFFFFFFFFFF) * np.uint64(1 << 16)
    x = x * np.uint64(0x9E3779B97F4A7C15)
    x ^= x >> np.uint64(30)
    x *= np.uint64(0xBF58476D1CE4E5B9)
    x ^= x >> np.uint64(27)
    x *= np.uint64(0x94D049BB133111EB)
    x ^= x >> np.uint64(31)
  return x

def _f(u, lo, n): return ((u >> np.uint64(lo)) & np.uint64((1 << n) - 1)).astype(np.uint64)

def floats(u:np.ndarray, eb:int, mb:int) -> np.ndarray:
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
  raw = _f(u, 8, eb + mb + 1)
  return np.where(kind >= 13, raw, bits)

def f32s(u): return floats(u, 8, 23).astype(np.uint32)
def f16s(u): return floats(u, 5, 10).astype(np.uint32) | (_f(u, 40, 16).astype(np.uint32) << 16)
def bf16s(u): return (floats(u, 8, 23).astype(np.uint32) >> 16) | (_f(u, 40, 16).astype(np.uint32) << 16)
def pk_f16(u, u2): return (floats(u, 5, 10) | (floats(u2, 5, 10) << np.uint64(16))).astype(np.uint32)
def pk_bf16(u, u2): return ((floats(u, 8, 23) >> np.uint64(16)) | ((floats(u2, 8, 23) >> np.uint64(16)) << np.uint64(16))).astype(np.uint32)
def f64s(u, u2):
  b = floats(u, 11, 52)
  lowfix = np.where(_f(u2, 0, 2) == 0, b & np.uint64(0xFFFFFFFF00000000), b)
  return lowfix
def ints32(u):
  k = _f(u, 0, 2)
  small = (_f(u, 8, 10).astype(np.int64) - 512).astype(np.uint64)
  return np.where(k == 0, small, np.where(k == 1, _f(u, 8, 8), _f(u, 32, 32))).astype(np.uint32)

def gen(fmt:str, bits:int, key:str, stream:int, n:int) -> list[np.ndarray]:
  u, u2 = hashes(key, stream, n), hashes(key, stream + 100, n)
  if fmt == "FMT_NUM_F64" or (bits == 64 and "F64" in fmt):
    x = f64s(u, u2)
    return [(x & np.uint64(0xFFFFFFFF)).astype(np.uint32), (x >> np.uint64(32)).astype(np.uint32)]
  if bits == 64: return [_f(u, 32, 32).astype(np.uint32), _f(u2, 32, 32).astype(np.uint32)]
  if fmt in ("FMT_NUM_F32",): return [f32s(u)]
  if fmt == "FMT_NUM_F16": return [f16s(u)]
  if fmt == "FMT_NUM_BF16": return [bf16s(u)]
  if fmt == "FMT_NUM_PK2_F16": return [pk_f16(u, u2)]
  if fmt == "FMT_NUM_PK2_BF16": return [pk_bf16(u, u2)]
  if fmt in ("FMT_NUM_I32", "FMT_NUM_U32"): return [ints32(u)]
  if fmt == "FMT_NUM_B32": return [np.where(_f(u2, 0, 1) == 0, f32s(u), pk_f16(u, u2))]
  return [_f(u, 32, 32).astype(np.uint32)]

def _fn_parts(name:str):
  fn = getattr(r4, name)
  return fn.func, (fn.args[0] if fn.args else None)

def targets() -> list[str]:
  out = []
  for n in sorted(dir(r4)):
    fn = getattr(r4, n)
    if not isinstance(fn, functools.partial) or not FLOAT.search(n) or not n.startswith("v_"): continue
    if fn.func.__name__ in SKIP_CLASSES or "wmma" in n or "swmmac" in n or n.startswith("v_dual_"): continue
    out.append(n)
  return out

def _operand_spec(op) -> dict[str, tuple[str, int]]:
  out = {}
  for k, (fmt, bits, _) in OPERANDS.get(op, {}).items():
    out[{"vsrc0": "src0", "ssrc0": "src0"}.get(k, k)] = (fmt.name, bits)
  return out

def _reg(base:tuple[int, int], bits:int): return v[base[0]:base[1]] if bits == 64 else v[base[0]]

def build(name:str, override:dict|None=None):
  cls, op = _fn_parts(name)
  spec = _operand_spec(op)
  fields = [f for f, _ in cls._fields]
  kw = {}
  if "vdst" in fields:
    if cls.__name__.startswith("VOP3_SDST") or "vdst" not in spec and "sdst" in spec: kw["vdst"] = s[20]
    elif cls.__name__ != "VOPC": kw["vdst"] = _reg(DST, spec.get("vdst", ("", 32))[1])
  if "sdst" in fields: kw["sdst"] = s[20]
  for i, f in enumerate(("src0", "src1", "src2")):
    key = f if f in fields else ("vsrc1" if f == "src1" and "vsrc1" in fields else None)
    if key is None: continue
    if f in spec or (f == "src1" and "vsrc1" in spec): kw[key] = _reg(SRC[i], spec.get(f, spec.get("vsrc1", ("", 32)))[1])
  if "literal" in fields or cls.__name__.endswith("_LIT"): kw["literal"] = K16 if "f16" in name else K32
  if name.startswith("v_s_"):  # valu ops on scalar operands: one lane at a time through s22 -> s23
    try: inst = cls(op, vdst=s[23], src0=s[22])
    except Exception: return None
    body = [x for lane in range(32) for x in (r4.v_readlane_b32(s[22], v[SRC[0][0]], lane), inst, r4.v_writelane_b32(v[DST[0]], s[23], lane))]
    return body, spec
  if "fmaak" in name or "fmamk" in name:
    lit = K16 if "f16" in name else K32
    kw.pop("literal", None)
    args = (kw["vdst"], kw["src0"], kw["vsrc1"], lit)
    try: inst = cls(op, *args)
    except Exception: return None
  else:
    if override: kw.update(override)
    try: inst = cls(op, **kw)
    except Exception: return None
  return [inst], spec

def signature(inst) -> str:
  from tinygrad.viz.serve import amd_decode
  import test.mockgpu.amd.emu as emu
  d = list(amd_decode(inst.to_bytes() + r4.s_endpgm().to_bytes(), "rdna4").values())[0]
  return emu.inst_signature(d)

def inputs_for(key:str, spec:dict, n:int, exhaustive_f16:bool, hi16:bool=False) -> np.ndarray:
  cols = [np.zeros(n, np.uint32)] * WIN
  d = gen(*spec.get("vdst", ("FMT_ANY", 32)), key, 0, n)
  cols[0] = d[0]
  cols[1] = d[1] if len(d) > 1 else hashes(key, 9, n).astype(np.uint32)
  for i, f in enumerate(("src0", "src1", "src2")):
    sp = spec.get(f) or (spec.get("vsrc1") if f == "src1" else None)
    if sp is None:
      cols[2 + 2*i] = hashes(key, 10 + i, n).astype(np.uint32)
      cols[3 + 2*i] = hashes(key, 20 + i, n).astype(np.uint32)
      continue
    g = gen(*sp, key, 1 + i, n)
    cols[2 + 2*i] = g[0]
    cols[3 + 2*i] = g[1] if len(g) > 1 else hashes(key, 20 + i, n).astype(np.uint32)
  if exhaustive_f16: cols[2] = (np.arange(n, dtype=np.uint32) & 0xFFFF) | (hashes(key, 30, n).astype(np.uint32) << 16)
  cols[8] = (hashes(key, 40, n) & np.uint64(1)).astype(np.uint32)
  if hi16:  # the value a 16-bit operand reads moves to the high half
    for c, f in ((0, "vdst"), (2, "src0"), (4, "src1"), (6, "src2")):
      if (spec.get(f) or (spec.get("vsrc1") if f == "src1" else None) or ("", 32))[1] == 16: cols[c] = (cols[c] << 16) | (cols[c] >> 16)
  return np.stack(cols, axis=1)

def run_one(body:list, inp:np.ndarray) -> np.ndarray:
  n = len(inp)
  out = Buffer(Device.DEFAULT, n * WOUT * 4).ensure_allocated()
  src = probe.gpu(inp.reshape(-1))
  regs = [DST[0], DST[1], SRC[0][0], SRC[0][1], SRC[1][0], SRC[1][1], SRC[2][0], SRC[2][1], VCCW]
  code = probe.MODE + [r4.s_load_b128(s[4:7], s[0:1], soffset=NULL), r4.s_wait_kmcnt(simm16=0), r4.s_lshl_b32(s[12], ttmp[9], 8),
          r4.v_add_nc_u32_e32(v[1], s[12], v[0]), r4.v_mul_u32_u24_e32(v[10], WIN * 4, v[1]), r4.v_mov_b32_e32(v[11], 0),
          r4.v_mul_u32_u24_e32(v[12], WOUT * 4, v[1]), r4.v_mov_b32_e32(v[13], 0),
          *[r4.global_load_b32(vdst=v[r], vaddr=v[10:11], saddr=s[6:7], ioffset=4 * j) for j, r in enumerate(regs)], r4.s_wait_loadcnt(simm16=0),
          r4.v_cmp_ne_u32_e32(0, v[VCCW]), r4.s_mov_b32(s[20], 0), r4.s_mov_b32(s[21], 0), r4.s_mov_b32(s[30], EXEC_LO), r4.v_mov_b32_e32(v[44], 0),
          *body,
          r4.v_mov_b32_e32(v[44], 1), r4.s_mov_b32(EXEC_LO, s[30]),
          r4.v_cndmask_b32_e64(v[42], 0, 1, VCC_LO), r4.v_cndmask_b32_e64(v[43], 0, 1, s[20]),
          *[r4.global_store_b32(vaddr=v[12:13], saddr=s[4:5], vsrc=v[r], ioffset=4 * j) for j, r in enumerate((40, 41, 42, 43, 44))]]
  probe.launch("probe_all", code, n // LOCAL, LOCAL, [out, src])
  return probe.readback(out).reshape(n, WOUT)

def _fname(sig:str) -> str: return re.sub(r"[^a-z0-9_=]", "+", sig) + ".npz"

def cases() -> list[tuple[str, list, dict, bool]]:  # (signature, body, spec, exhaustive f16)
  out, seen = [], set()
  for name in targets():
    b = build(name)
    if b is None:
      print(f"cannot build {name}", flush=True)
      continue
    body, spec = b
    sig = signature(body[1] if name.startswith("v_s_") else body[0])
    if sig in seen: continue
    seen.add(sig)
    srcs = [f for f in ("src0", "src1", "src2") if f in spec or (f == "src1" and "vsrc1" in spec)]
    ex = len(srcs) == 1 and spec[srcs[0]][0] == "FMT_NUM_F16"
    out.append((sig, body, spec, ex))
  return out + vopd_cases() + scalar_cases() + alias_cases()

def alias_cases() -> list[tuple[str, list, dict, bool]]:
  out = []
  for t in ("f32", "f64"):
    fn, wide = getattr(r4, f"v_div_scale_{t}"), t == "f64"
    def r(i, wide=wide): return v[SRC[i][0]:SRC[i][1]] if wide else v[SRC[i][0]]
    spec = _operand_spec(fn.args[0])
    for k, which in (("s0=s1", 1), ("s0=s2", 2)):
      inst = fn(vdst=v[DST[0]:DST[1]] if wide else v[DST[0]], sdst=s[20], src0=r(which), src1=r(1), src2=r(2))
      out.append((f"v_div_scale_{t}|{k}", [inst], spec, False))
  return out

def scalar_cases() -> list[tuple[str, list, dict, bool]]:
  out = []
  for n in sorted(dir(r4)):
    fn = getattr(r4, n)
    if not isinstance(fn, functools.partial) or not n.startswith("s_") or not FLOAT.search(n): continue
    cls, op = fn.func, fn.args[0]
    spec = {{"ssrc0": "src0", "ssrc1": "src1", "sdst": "vdst"}[k]: (fmt.name, bits) for k, (fmt, bits, _) in OPERANDS.get(op, {}).items()}
    fields = [f for f, _ in cls._fields]
    kw = {k: r for k, r in (("sdst", s[26]), ("ssrc0", s[22]), ("ssrc1", s[23])) if k in fields}
    try: inst = cls(op, **kw, literal=K16 if "f16" in n else K32) if cls.__name__.endswith("_LIT") else cls(op, **kw)
    except Exception:
      print(f"cannot build {n}", flush=True)
      continue
    body = [x for lane in range(32) for x in (
      r4.v_readlane_b32(s[22], v[SRC[0][0]], lane), r4.v_readlane_b32(s[23], v[SRC[1][0]], lane), r4.v_readlane_b32(s[26], v[DST[0]], lane),
      r4.s_cmp_lg_u32(s[22], s[22]), inst, r4.s_cselect_b32(s[25], 1, 0),
      r4.v_writelane_b32(v[DST[0]], s[26], lane), r4.v_writelane_b32(v[DST[1]], s[25], lane))]
    out.append((signature(inst), body, spec, False))
  return out

def vopd_cases() -> list[tuple[str, list, dict, bool]]:
  out, mov = [], r4.VOPDOp.V_DUAL_MOV_B32
  for op in r4.VOPDOp:
    name = op.name.lower()
    if not FLOAT.search(name): continue
    spec = {{"srcy0": "src0", "vsrcy1": "src1", "vdsty": "vdst"}[k]: (fmt.name, bits) for k, (fmt, bits, _) in OPERANDS.get(op, {}).items()}
    lit = {"literal": K32} if "fmaak" in name or "fmamk" in name else {}
    cls = r4.VOPD_LIT if lit else r4.VOPD
    if op.value < 16:
      x = cls(opx=op, opy=mov, vdstx=v[40], srcx0=v[20], vsrcx1=v[24], vdsty=v[41], srcy0=v[21], vsrcy1=v[25], **lit)
      out.append((f"{name}|x", [x], spec, False))
    y = cls(opx=mov, opy=op, vdstx=v[41], srcx0=v[21], vsrcx1=v[25], vdsty=v[40], srcy0=v[20], vsrcy1=v[24], **lit)
    out.append((f"{name}|y", [y], spec, False))
  return out

def _variant(inst, **fields):
  out = copy.copy(inst)
  for k, val in fields.items(): setattr(out, k, val)
  return out

COMBOS = 12
def mod_cases() -> list[tuple[str, list, dict, bool]]:
  out, seen = [], set()
  for sig, body, spec, _ in cases():
    if sig.startswith(("s_", "v_dual_")): continue
    inst = next(x for x in body if FLOAT.search(getattr(x, "op_name", "").lower() or "-"))
    cname, nsrc = type(inst).__name__, sum(1 for f in ("src0", "src1", "src2") if f in spec or (f == "src1" and "vsrc1" in spec))
    is16 = [spec.get(f, ("", 32))[1] == 16 for f in ("src0", "src1", "src2")] + [spec.get("vdst", ("", 32))[1] == 16]
    variants = []
    if cname in ("VOP1", "VOP2", "VOPC") and any(is16):
      hi = {}
      if is16[3] and cname != "VOPC": hi["vdst"] = v[DST[0] + 128]
      if is16[0]: hi["src0"] = v[SRC[0][0] + 128]
      if is16[1] and "vsrc1" in [f for f, _ in type(inst)._fields]: hi["vsrc1"] = v[SRC[1][0] + 128]
      try: variants.append((sig + "|hi16", _variant(inst, **hi), True))
      except Exception as e: print(f"cannot build hi16 {sig}: {e}", flush=True)
    names = [f for f, _ in type(inst)._fields]
    singles = []
    if cname.startswith(("VOP3", "VINTERP")) and cname != "VOP3P":
      singles += [{"neg": 1 << i} for i in range(nsrc)] + ([{"abs": 1 << i} for i in range(nsrc)] if "abs" in names else [])
      singles += [{"clmp": 1}] + ([{"omod": o} for o in (1, 2, 3)] if "omod" in names else [])
      if "opsel" in names: singles += [{"opsel": 1 << i} for i in range(4) if is16[i] or (i == 3 and is16[3])]
    elif cname == "VOP3P":
      singles += [{"neg": 1 << i} for i in range(nsrc)] + [{"neg_hi": 1 << i} for i in range(nsrc)] + [{"clmp": 1}]
      singles += [{"opsel": 1 << i} for i in range(nsrc)] + [{"opsel_hi": o} for o in (0, 1, 2)] + ([{"opsel_hi2": 0}] if nsrc == 3 else [])
    if singles:
      masks: dict[str, int] = {}
      for d in singles:
        for k, val in d.items(): masks[k] = masks.get(k, 0) | val
      masks.update({k: 3 for k in ("omod", "opsel_hi") if k in masks})
      if "opsel_hi2" in masks: masks["opsel_hi2"] = 1
      u = hashes(sig, 77, COMBOS)  # random multi-field combinations: the per-field gate trusts an op only if all of these match too
      for j in range(COMBOS): singles.append({k: int(_f(u[j:j+1], 6 * i, 6)[0]) & m for i, (k, m) in enumerate(masks.items())})
    for fields in singles:
      try: var = _variant(inst, **fields)
      except Exception: continue
      vsig = signature(var) + "".join(f"|{t}" for t in ("s0=s1", "s0=s2") if sig.endswith(f"|{t}"))  # an aliased base keeps its tag
      if vsig != sig: variants.append((vsig, var, False))
    for vsig, var, hi16 in variants:
      if vsig in seen: continue
      seen.add(vsig)
      out.append((vsig, [var if x is inst else x for x in body], spec, hi16))
  return out

def sig_cases(sigs:list[str]) -> list[tuple[str, list, dict, bool]]:
  base = {c[0].split("|")[0]: c for c in cases() if "|" not in c[0] or not c[0].split("|", 1)[1].startswith(("x", "y", "s0="))}
  out = []
  for sig in sigs:
    c = base.get(sig.split("|")[0])
    if c is None:
      print(f"no probe for {sig}", flush=True)
      continue
    inst = next(x for x in c[1] if FLOAT.search(getattr(x, "op_name", "").lower() or "-"))
    want = dict(f.split("=") for f in sig.split("|")[1:])
    names = [f for f, _ in type(inst)._fields]
    fields = {f: int(want.get(f, 0)) for f in ("clmp", "omod", "abs", "neg", "neg_hi", "opsel", "opsel_hi", "opsel_hi2") if f in names}
    try: var = _variant(inst, **fields)
    except Exception as e:
      print(f"cannot build {sig}: {e}", flush=True)
      continue
    if signature(var) != sig:
      print(f"cannot build {sig}: got {signature(var)}", flush=True)
      continue
    out.append((sig, [var if x is inst else x for x in c[1]], c[2], False))
  return out

CONSTS0 = [0, 1, 64, -1, -16, 0.5, -0.5, 1.0, -1.0, 2.0, -2.0, 4.0, -4.0, INV_2PI, 0x3DCCCCCD, 0xABCD3C00, 0xC0490FDB]
CONSTS1 = [1.0, -2.0, 0.5, -16, INV_2PI, 0x3DCCCCCD]

def const_cases() -> list[tuple[str, list[list], dict]]:
  out = []
  for name in targets():
    if name.startswith("v_s_"): continue
    b = build(name)
    if b is None: continue
    spec, cls = b[1], _fn_parts(name)[0]
    fields = [f for f, _ in cls._fields]
    variants = []
    for slot, consts in (("src0", CONSTS0), ("src1", CONSTS1)):
      if slot not in fields or slot not in spec: continue
      for k in consts:
        try: vb = build(name, {slot: k})
        except Exception: vb = None
        if vb is not None: variants.append(vb[0])
    if variants: out.append((signature(b[0][0]) + "|consts", variants, spec))
  return out

DPP16 = [(0xB1, 0, 0, 15, 15, 0, 0), (0x101, 0, 0, 15, 15, 0, 0), (0x113, 0, 0, 15, 15, 0, 0), (0x113, 1, 0, 15, 15, 0, 0),
         (0x125, 0, 0, 15, 15, 0, 0), (0x140, 0, 0, 15, 15, 0, 0), (0x141, 0, 1, 15, 15, 0, 0), (0x152, 0, 0, 15, 15, 0, 0),
         (0x165, 0, 0, 15, 15, 0, 0), (0x1B, 0, 0, 5, 10, 0, 0), (0xE4, 0, 0, 15, 15, 1, 0), (0x4E, 1, 0, 15, 15, 0, 1)]
DPP8 = [7, 6, 5, 4, 3, 2, 1, 0]

def dpp_cases() -> list[tuple[str, list[list], dict]]:
  out = []
  for name in targets():
    if name.startswith("v_s_") or "f64" in name: continue  # no dpp on f64 ops (the hardware faults)
    b = build(name)
    if b is None or "src0" not in b[1]: continue
    inst = b[0][0]
    c16, c8 = getattr(r4, type(inst).__name__ + "_DPP16", None), getattr(r4, type(inst).__name__ + "_DPP8", None)
    if c16 is None: continue
    variants = []
    for ctrl, bc, fi, rm, bm, neg, ab in DPP16:
      d = object.__new__(c16)
      d._raw = inst._raw
      d.src0, d.vsrc0, d.dpp, d.bc, d.fi, d.row_mask, d.bank_mask = DPP16_SRC, v[SRC[0][0]], ctrl, bc, fi, rm, bm
      if hasattr(c16, "src0_neg"): d.src0_neg, d.src0_abs = neg, ab
      elif neg or ab: continue
      variants.append([d])
    if c8 is not None:
      d = object.__new__(c8)
      d._raw = inst._raw
      d.src0, d.vsrc0 = src[233], v[SRC[0][0]]
      for i, lane in enumerate(DPP8): setattr(d, f"lane_sel_{i}", lane)
      variants.append([d])
    out.append((signature(inst) + "|dpp", variants, b[1]))
  return out

def run_consts(body_variants:list[list], inp:np.ndarray, per_kernel:int|None=None) -> np.ndarray:
  if per_kernel is None: per_kernel = 1 if os.environ.get("DEV", "").startswith("MOCK") else 64  # the mock truncates long hand-built kernels' code
  if len(body_variants) > per_kernel:
    return np.concatenate([run_consts(body_variants[i:i + per_kernel], inp) for i in range(0, len(body_variants), per_kernel)], axis=1)
  n, nv = len(inp), len(body_variants)
  out = Buffer(Device.DEFAULT, n * WOUT * nv * 4).ensure_allocated()
  src = probe.gpu(inp.reshape(-1))
  regs = [DST[0], DST[1], SRC[0][0], SRC[0][1], SRC[1][0], SRC[1][1], SRC[2][0], SRC[2][1], VCCW]
  code = probe.MODE + [r4.s_load_b128(s[4:7], s[0:1], soffset=NULL), r4.s_wait_kmcnt(simm16=0), r4.s_lshl_b32(s[12], ttmp[9], 8),
          r4.v_add_nc_u32_e32(v[1], s[12], v[0]), r4.v_mul_u32_u24_e32(v[10], WIN * 4, v[1]), r4.v_mov_b32_e32(v[11], 0),
          r4.v_mul_u32_u24_e32(v[12], WOUT * nv * 4, v[1]), r4.v_mov_b32_e32(v[13], 0),
          *[r4.global_load_b32(vdst=v[r], vaddr=v[10:11], saddr=s[6:7], ioffset=4 * j) for j, r in enumerate(regs)], r4.s_wait_loadcnt(simm16=0),
          r4.v_mov_b32_e32(v[46], v[DST[0]]), r4.v_mov_b32_e32(v[47], v[DST[1]]), r4.s_mov_b32(s[30], EXEC_LO)]
  for i, body in enumerate(body_variants):
    code += [r4.v_mov_b32_e32(v[DST[0]], v[46]), r4.v_mov_b32_e32(v[DST[1]], v[47]), r4.v_cmp_ne_u32_e32(0, v[VCCW]),
             r4.s_mov_b32(s[20], 0), r4.s_mov_b32(s[21], 0), r4.v_mov_b32_e32(v[44], 0), *body, r4.v_mov_b32_e32(v[44], 1),
             r4.s_mov_b32(EXEC_LO, s[30]), r4.v_cndmask_b32_e64(v[42], 0, 1, VCC_LO), r4.v_cndmask_b32_e64(v[43], 0, 1, s[20]),
             *[r4.global_store_b32(vaddr=v[12:13], saddr=s[4:5], vsrc=v[r], ioffset=4 * (WOUT * i + j)) for j, r in enumerate((40, 41, 42, 43, 44))]]
  probe.launch("probe_consts", code, n // LOCAL, LOCAL, [out, src])
  return probe.readback(out).reshape(n, nv * WOUT)

def run(outdir:str, limit:int, mods:bool=False, sigs:list[str]|None=None, consts:bool=False, dpp:bool=False):
  if consts or dpp:
    os.makedirs(outdir, exist_ok=True)
    todo = [c for c in (dpp_cases() if dpp else const_cases()) if not os.path.exists(os.path.join(outdir, _fname(c[0])))]
    for sig, variants, spec in todo[:limit]:
      inp = inputs_for(sig, spec, N_CONSTS, False)
      try: res = run_consts(variants, inp)
      except Exception as e:
        print(f"{sig}: FAILED {type(e).__name__}: {str(e)[:200]}", flush=True)
        np.savez(os.path.join(outdir, _fname(sig)), error=np.array(f"{type(e).__name__}: {e}"))
        if "hang" in str(e) or "failed with" in str(e):
          print(f"{len(todo) - 1 - todo.index((sig, variants, spec))} left", flush=True)
          os._exit(0)
        continue
      np.savez_compressed(os.path.join(outdir, _fname(sig)), out=res, inhash=np.array(zlib.crc32(inp.tobytes())))
      print(f"{sig}: done", flush=True)
    print(f"{max(0, len(todo) - limit)} left", flush=True)
    return
  os.makedirs(outdir, exist_ok=True)
  every = sig_cases(sigs) if sigs is not None else mod_cases() if mods else cases()
  todo = [c for c in every if not os.path.exists(os.path.join(outdir, _fname(c[0])))]
  for sig, body, spec, ex in todo[:limit]:
    inp = inputs_for(sig, spec, N_MODS, False, hi16=ex) if mods or sigs is not None else inputs_for(sig, spec, N_DEFAULT, ex)
    try: res = run_one(body, inp)
    except Exception as e:
      print(f"{sig}: FAILED {type(e).__name__}: {str(e)[:200]}", flush=True)
      np.savez(os.path.join(outdir, _fname(sig)), error=np.array(f"{type(e).__name__}: {e}"))
      continue
    np.savez_compressed(os.path.join(outdir, _fname(sig)), out=res, inhash=np.array(zlib.crc32(inp.tobytes())))
    print(f"{sig}: done", flush=True)
  print(f"{max(0, len(todo) - limit)} left", flush=True)

def compare(hw:str, emu:str):
  bad, ok, missing = [], 0, []
  for f in sorted(glob.glob(os.path.join(hw, "*.npz"))):
    a = np.load(f)
    g = os.path.join(emu, os.path.basename(f))
    if "error" in a.files or not os.path.exists(g):
      missing.append(os.path.basename(f))
      continue
    b = np.load(g)
    if "error" in b.files:
      bad.append((os.path.basename(f), "emulator error: " + str(b["error"])[:120]))
      continue
    if int(a["inhash"]) != int(b["inhash"]):
      bad.append((os.path.basename(f), "inputs differ"))
      continue
    x, y = a["out"], b["out"]
    d = np.flatnonzero((x != y).any(axis=1))
    if d.size:
      cols = sorted({c for i in d[:1000] for c in np.flatnonzero(x[i] != y[i])})
      bad.append((os.path.basename(f), f"{d.size} of {len(x)} lanes differ in cols {cols}, e.g. lane {d[0]}: hw {[hex(t) for t in x[d[0]]]} "
                                       f"emu {[hex(t) for t in y[d[0]]]}"))
    else: ok += 1
  for k, m in bad: print(f"DIFF {k}: {m}")
  print(f"{ok} match, {len(bad)} differ, {len(missing)} missing or failed on hw: {missing[:20]}")

if __name__ == "__main__":
  if sys.argv[1] == "run": run(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1 << 30)
  elif sys.argv[1] == "mods": run(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1 << 30, mods=True)
  elif sys.argv[1] == "sigs":  # OUTDIR SIGS.json [N]: a json list of exact signatures
    import json
    run(sys.argv[2], int(sys.argv[4]) if len(sys.argv) > 4 else 1 << 30, sigs=json.load(open(sys.argv[3])))
  elif sys.argv[1] == "consts": run(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1 << 30, consts=True)
  elif sys.argv[1] == "dpp": run(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1 << 30, dpp=True)
  elif sys.argv[1] == "runfile":  # SIG IN.npy OUT.npz: chosen per-lane inputs (N x 9 uint32, N a multiple of 256) through one signature
    c = next(c for c in cases() + mod_cases() if c[0] == sys.argv[2])
    inp = np.load(sys.argv[3]).astype(np.uint32)
    np.savez_compressed(sys.argv[4], out=run_one(c[1], inp), inhash=np.array(zlib.crc32(inp.tobytes())))
    print(f"{sys.argv[2]}: {len(inp)} lanes -> {sys.argv[4]}", flush=True)
  elif sys.argv[1] == "compare": compare(sys.argv[2], sys.argv[3])
  elif sys.argv[1] == "list":
    cs = cases()
    print("\n".join(c[0] for c in cs))
    print(f"{len(cs)} signatures")
