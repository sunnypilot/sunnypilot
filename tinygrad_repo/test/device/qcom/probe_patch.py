import sys, os, glob, zlib, itertools, importlib.util
import numpy as np
here = os.path.dirname(os.path.abspath(__file__))
def _src(out:str, inp:str, expr:str="a[i] * b[i] + c[i]") -> str:
  return ("#pragma OPENCL EXTENSION cl_khr_fp16 : enable\n" if "half" in (out, inp) else "") + \
    f"__kernel void probe(__global {out}* out, __global const {inp}* a, __global const {inp}* b, __global const {inp}* c) {{\n" \
    f"  int i = get_group_id(0) * 64 + get_local_id(0); out[i] = {expr}; }}"
TEMPLATES = {  # source, slot, input / output element, src regs (a*b or a, b, c), dst reg, half registers, the original slot word
  "i32": (_src("int", "int"), 26, np.int32, np.int32, (2, 3, 4), 2, False, 0x42300002_00040002),
  "u16": (_src("ushort", "ushort"), 31, np.uint16, np.uint16, (0, 1, 2), 0, True, 0x71000000_00020001),
  "f2h": (_src("half", "float", "(half)(a[i] * b[i] + c[i])"), 32, np.uint32, np.uint16, (0, 1, 2), 0, False, 0x7380c000_00020000),
  "h2f": (_src("float", "half", "(float)(a[i] * b[i] + c[i])"), 32, np.uint16, np.uint32, (0, 1, 2), 0, True, 0x7300c000_00020000)}
TEMPLATE = os.getenv("PROBE_TEMPLATE", "u16" if int(os.getenv("PROBE_HALF", "0")) else "i32")
SRC, SLOT, IN_DT, OUT_DT, (R0Z, R0W, R1X), DST, HALF, ORIG = TEMPLATES[TEMPLATE]
N, LOCAL = 1 << 16, 64
SYNC = TEMPLATE != "i32"  # the other templates' slot follows its loads, so the patched word keeps (sy)

def field(word:int, lo:int, hi:int, val:int) -> int: return (word & ~(((1 << (hi - lo + 1)) - 1) << lo)) | ((val & ((1 << (hi - lo + 1)) - 1)) << lo)
def cat3(template:int, dst:int, s1:int, s2:int, s3:int, n1:int, n2:int, n3:int) -> int:  # field layout of emu.Cat3, sync/rpt flags cleared
  w = field(template, 0, 12, s1)
  for lo, hi, v in ((14, 14, n1), (47, 54, s2), (30, 30, n2), (16, 28, s3), (31, 31, n3), (32, 39, dst), (40, 41, 0), (43, 43, 0), (15, 15, 0),
                    (29, 29, 0), (44, 45, 0), (59, 60, 0)): w = field(w, lo, hi, v)
  return field(w, 60, 60, 1) if SYNC else w

SAD_WORD = 0x6787001c_8000000e  # a compiled sad.s32: the type/flag bits every 32-bit cat3 op below is built from
def cat3_op(op:int) -> int:  # cat3 opcode op (mesa opc_t numbering): opc in bits 55-58, values past 15 need the alt bit (13) and the full bit (42)
  lo = op & 0x7F
  w = field(field(SAD_WORD, 55, 58, lo if lo < 16 else lo - 8), 13, 13, int(lo >= 16))
  return field(w, 42, 42, 1) if lo >= 16 else w

ADD_S_WORD = 0x42300002_00040002  # the template's add.s r0.z, r0.z, r1.x: the cat2 encodings below start from it
def cat2(op:int, absneg1:int, absneg2:int, sat:int, cond:int) -> int:  # src1 r0.z (a*b), src2 r0.w (b), dst r0.z, 32-bit
  w = field(field(field(ADD_S_WORD, 53, 58, op & 0x3F), 0, 15, R0Z | (absneg1 << 14)), 16, 31, R0W | (absneg2 << 14))
  w = field(field(field(field(w, 42, 42, sat), 48, 50, cond), 52, 52, 0 if HALF else 1), 32, 39, DST)
  return field(w, 60, 60, 1) if SYNC else w

def cat2_variants() -> dict[str, int]:
  from tinygrad.runtime.autogen import mesa
  out = {}
  for name, op in sorted((k[4:].lower(), v) for k, v in vars(mesa).items() if k.startswith("OPC_") and isinstance(v, int) and 256 <= v < 320):
    if name in ("bary_f", "flat_b"): continue  # need varyings
    conds = range(8) if name.startswith(("cmps", "cmpv")) else (0,)
    for cond, a1, a2, sat in itertools.product(conds, range(4), range(4), (0, 1)):
      out[f"c2_{name}|c{cond}a{a1}b{a2}s{sat}"] = cat2(op, a1, a2, sat, cond)
  return out

SS_NOP = 0x00001500_00000000  # (ss)(rpt5)nop: replaces the nop after the slot so the store waits for an SFU result
def cat4(op:int, absneg:int, sat:int) -> int:  # i32: src r1.x (c: an ALU result needs more delay before the SFU reads it); u16: hr0.x (every f16 value)
  w = (4 << 61) | ((op & 0x3F) << 53) | ((0 if HALF else 1) << 52) | (sat << 42) | (DST << 32) | (R0Z if HALF else R1X) | (absneg << 14)
  return field(w, 60, 60, 1) if SYNC else w

def cat4_variants() -> dict[str, tuple[int, int]]:
  from tinygrad.runtime.autogen import mesa
  ops = sorted((k[4:].lower(), v) for k, v in vars(mesa).items() if k.startswith("OPC_") and isinstance(v, int) and 512 <= v < 576)
  return {f"c4_{name}|a{an}s{sat}": (cat4(op, an, sat), SS_NOP) for name, op in ops for an in range(4) for sat in (0, 1)}

CAT1_TYPES = ("f16", "f32", "u16", "u32", "s16", "s32", "u8", "u8_32")  # mesa type_t order
HALF_TYPES = (0, 2, 4, 6)  # u8_32 is a full-register type
def cat1(src_type:int, dst_type:int, rnd:int) -> int:  # mov/cov from the template's a register to its dst register
  w = (1 << 61) | (rnd << 55) | (src_type << 50) | (dst_type << 46) | (DST << 32) | R0Z
  return field(w, 60, 60, 1) if SYNC else w

def cat1_variants() -> dict[str, int]:  # the type pairs whose source and destination widths match this template's registers
  src_half, dst_half = {"i32": (False, False), "u16": (True, True), "f2h": (False, True), "h2f": (True, False)}[TEMPLATE]
  return {f"c1_{CAT1_TYPES[s]}_{CAT1_TYPES[d]}|r{r}": cat1(s, d, r) for s in range(8) for d in range(8) for r in range(4)
          if (s in HALF_TYPES) == src_half and (d in HALF_TYPES) == dst_half}

def dstconv_variants() -> dict[str, int]:  # f2h / h2f: the op writes the other register width (dst_conv, bit 46), plain sources
  from tinygrad.runtime.autogen import mesa
  out = {}
  for name, op in sorted((k[4:].lower(), v) for k, v in vars(mesa).items() if k.startswith("OPC_") and isinstance(v, int) and 256 <= v < 320):
    if name in ("bary_f", "flat_b"): continue
    for cond, sat in itertools.product(range(8) if name.startswith(("cmps", "cmpv")) else (0,), (0, 1)):
      out[f"c2_{name}|c{cond}a0b0s{sat}d"] = field(cat2(op, 0, 0, sat, cond), 46, 46, 1)
  names = {v: k[4:].lower() for k, v in vars(mesa).items() if k.startswith("OPC_") and isinstance(v, int) and 384 <= v <= 404}
  for op, name in sorted(names.items()):
    if (name.endswith("16") or name in ("sel_f16", "sad_s16")) != HALF or name.startswith("madsh"): continue
    if name == "mad_u16": continue  # with a full dst it reads full registers, which hold addresses here; real sin/cos kernels verify it
    out[f"{name}|n000d"] = field(cat3(cat3_op(op), DST, R0Z, R0W, R1X, 0, 0, 0), 46, 46, 1)
  return out

def sfu_sweep_variants() -> dict[str, tuple[int, int]]:  # i32: rsq on every mantissa at an even and an odd exponent (2^24 inputs in 256 runs)
  from tinygrad.runtime.autogen import mesa
  return {f"c4s_rsq|e{e}m{m:03d}": (cat4(mesa.OPC_RSQ, 0, 0), SS_NOP) for e in (0, 1) for m in range((1 << 23) // N)}

def variants() -> dict[str, int|tuple[int, ...]]:
  from tinygrad.runtime.autogen import mesa
  out:dict[str, int|tuple[int, ...]] = {"orig": ORIG}  # the template's own word: the harness must agree with itself
  if TEMPLATE in ("f2h", "h2f"): return out | cat1_variants() | dstconv_variants()
  names = {v: k[4:].lower() for k, v in vars(mesa).items() if k.startswith("OPC_") and isinstance(v, int) and 384 <= v <= 404}
  for op, name in sorted(names.items()):
    if (name.endswith("16") or name in ("sel_f16", "sad_s16")) != HALF: continue  # 16-bit ops read half registers: PROBE_HALF=1 template
    for n1 in (0, 1):
      for n2 in (0, 1):
        for n3 in (0, 1): out[f"{name}|n{n1}{n2}{n3}"] = cat3(cat3_op(op), DST, R0Z, R0W, R1X, n1, n2, n3)
  return out | cat2_variants() | cat4_variants() | cat1_variants() | (sfu_sweep_variants() if TEMPLATE == "i32" else {})

def hashes(key, stream, n):
  spec = importlib.util.spec_from_file_location("pa", os.path.join(here, "probe_a630.py"))
  pa = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(pa)
  return pa.hashes(key, stream, n)

def inputs(name:str) -> list[np.ndarray]:
  if IN_DT == np.uint32 and TEMPLATE != "i32":  # f2h: half the lanes are f32 patterns (specials, denormals), the rest raw 32-bit words
    spec = importlib.util.spec_from_file_location("pa", os.path.join(here, "probe_a630.py"))
    pa = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pa)
    return [np.where((u := hashes(name, s, N)) & np.uint64(1), pa.floats(u, 8, 23), u >> np.uint64(32)).astype(np.uint32) for s in range(3)]
  if IN_DT == np.uint16:  # half the lanes are f16 patterns (specials, denormals), the rest raw 16-bit integers
    spec = importlib.util.spec_from_file_location("pa", os.path.join(here, "probe_a630.py"))
    pa = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pa)
    out = [np.where((u := hashes(name, s, N)) & np.uint64(1), pa.floats(u, 5, 10), u >> np.uint64(48)).astype(np.uint16) for s in range(3)]
    return [np.arange(N, dtype=np.uint16)] + out[1:] if name.startswith("c4_") else out  # sfu ops see every f16 value
  if name.startswith("c4s_"):  # c (r1.x) = 2^(127 + e - 127) * (1 + m / 2^23) for this run's mantissas
    e, m = int(name.split("|")[1][1]), int(name.split("|")[1][3:])
    c = (((127 + e) << 23) | (np.arange(N, dtype=np.int64) + m * N)).astype(np.uint32).view(np.int32)
    return [np.ones(N, np.int32), np.ones(N, np.int32), c]
  out = []
  for s in range(3):
    u = hashes(name, s, N)
    small = ((u >> np.uint64(8)) & np.uint64(0x3FF)).astype(np.int64) - 512
    out.append(np.where((u & np.uint64(3)) == 0, small, (u >> np.uint64(32)).astype(np.int64) - (1 << 31)).astype(np.int32))
  return out

def run_lib(lib:bytes, ins:list[np.ndarray]) -> np.ndarray:
  from tinygrad.device import Buffer, Device
  from tinygrad.dtype import dtypes
  from tinygrad.uop.ops import UOp, Ops
  from tinygrad.engine.realize import run_linear
  sys.path.insert(0, os.path.join(here, "..", "..", "..", ".."))
  from openpilot.sunnypilot.modeld_v2.helpers import _program_uop
  dts = {np.int32: dtypes.int32, np.uint32: dtypes.uint32, np.uint16: dtypes.ushort}
  odt, idt = dts[OUT_DT], dts[IN_DT]
  bufs = [Buffer(Device.DEFAULT, N * odt.itemsize).ensure_allocated()] + \
         [Buffer(Device.DEFAULT, N * idt.itemsize, initial_value=x.tobytes()).ensure_allocated() for x in ins]
  call = {"name": "probe", "signature": [[None, j, str(odt if j == 0 else idt), [N]] for j in range(4)], "global_size": [N // LOCAL, 1, 1],
          "local_size": [LOCAL, 1, 1],
          "globals": [0, 1, 2, 3], "outs": [0], "ins": [1, 2, 3], "target": {"device": "QCOM", "renderer": "", "arch": "a630", "interface": "", "indices": ""}}
  run_linear(UOp(Ops.LINEAR, src=(_program_uop(call, lib).call(*[UOp.from_buffer(b, odt if j == 0 else idt) for j, b in enumerate(bufs)]),)), wait=True)
  return np.frombuffer(bytes(bufs[0].as_memoryview()), OUT_DT).copy()

def patched(lib:bytes, word:int|tuple[int, ...]) -> bytes:  # a tuple patches consecutive words from the slot on
  from tinygrad.runtime.support.compiler_qcom import _read_lib
  off, words = _read_lib(lib, 0xc0) + SLOT * 8, word if isinstance(word, tuple) else (word,)
  return lib[:off] + b"".join(w.to_bytes(8, "little") for w in words) + lib[off + 8 * len(words):]

if __name__ == "__main__":
  if sys.argv[1] == "base":
    from tinygrad.runtime.support.compiler_qcom import QCOMCompiler, _read_lib
    from tinygrad.runtime.support.compiler_mesa import disas_adreno
    lib = QCOMCompiler("a630").compile(SRC)
    open(sys.argv[2], "wb").write(lib)
    disas_adreno(lib[(o := _read_lib(lib, 0xc0)):o + _read_lib(lib, 0x100)])
  elif sys.argv[1] == "run":
    lib, outdir = open(sys.argv[2], "rb").read(), sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    for name, word in variants().items():
      f = os.path.join(outdir, name.replace("|", "+") + ".npz")
      if os.path.exists(f): continue
      ins = inputs(name)
      try: np.savez_compressed(f, out=run_lib(patched(lib, word), ins), word=np.array(word[0] if isinstance(word, tuple) else word, np.uint64))
      except Exception as e: np.savez(f, error=np.array(f"{type(e).__name__}: {e}"))
      print(name, "done", flush=True)
  else:
    for f in sorted(glob.glob(os.path.join(sys.argv[2], "*.npz"))):
      a, b = np.load(f), np.load(os.path.join(sys.argv[3], os.path.basename(f)))
      if "error" in a.files or "error" in b.files: print(os.path.basename(f), "ERROR", a.get("error"), b.get("error")); continue
      d = np.flatnonzero(a["out"] != b["out"])
      ins = inputs(os.path.basename(f)[:-4].replace("+", "|"))
      ex = f"a={int(ins[0][d[0]]):#06x} b={int(ins[1][d[0]]):#06x} c={int(ins[2][d[0]]):#06x} hw={int(a['out'][d[0]]):#06x} emu={int(b['out'][d[0]]):#06x}" if TEMPLATE != "i32" and d.size else \
           f"a*b={int(ins[0][d[0]])*int(ins[1][d[0]]) & 0xffffffff:#x} b={int(ins[1][d[0]])} c={int(ins[2][d[0]])} hw={int(a['out'][d[0]])} emu={int(b['out'][d[0]])}" if d.size else ""
      print(f"{os.path.basename(f)[:-4]:22s} {'MATCH' if d.size == 0 else f'{d.size} differ'}" + ("" if d.size == 0 else "  e.g. " + ex))
