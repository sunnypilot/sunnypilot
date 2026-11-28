import ctypes, ctypes.util, functools, hashlib, math, mmap, os, struct, time
import numpy as np
from tinygrad.helpers import getenv, to_mv, cache_dir
from tinygrad.runtime.autogen import mesa
from test.mockgpu.qcom import emu
from test.mockgpu.qcom.emu import A0, P0, TYPES, HALF_TYPES, CAT1_HALF_TYPES, Cat0, Cat1, Cat2, Cat3, Cat4, Cat5, Cat7, Load, Store, Ldg, Stg, Ibo

O = mesa

class Unsupported(Exception): pass

PRELUDE = r"""
#include <metal_stdlib>
using namespace metal;
#define F(b) as_type<float>(b)
#define U(f) as_type<uint>(f)
struct XMap { ulong lo, hi; device uchar* p; ulong pad; };
inline uint ftz32(uint u) { return (u & 0x7fffffffu) < 0x00800000u ? (u & 0x80000000u) : u; }
inline uint ftz16(uint h) { return (h & 0x7fffu) < 0x0400u ? (h & 0x8000u) : h; }
inline bool nan32(uint u) { return (u & 0x7fffffffu) > 0x7f800000u; }
inline bool nan16(uint h) { return (h & 0x7fffu) > 0x7c00u; }
inline uint cnan32(uint u) { return nan32(u) ? 0x7fc00000u : u; }
inline uint cnan16(uint h) { return nan16(h) ? 0x7e00u : h; }
inline uint h2f(uint h) {  // the gpu converts f16 denormals exactly, but quiets NaN payloads
  return nan16(h) ? ((h & 0x8000u) << 16) | 0x7fc00000u | ((h & 0x3ffu) << 13) : U(float(as_type<half>((ushort)h)));
}
inline uint f2h(uint f) {
  uint s = (f & 0x80000000u) >> 16, fe = f & 0x7f800000u;
  if (fe >= 0x47800000u) {
    uint fs = f & 0x7fffffu;
    if (fe == 0x7f800000u && fs != 0u) return s | 0x7e00u | (fs >> 13);  // numpy converts with the cpu's instruction, which quiets NaN
    return s + 0x7c00u;
  }
  if (fe <= 0x38000000u) {
    if (fe < 0x33000000u) return s;
    uint e = fe >> 23, fs = 0x800000u + (f & 0x7fffffu);
    fs >>= (113u - e);
    if (((fs & 0x3fffu) != 0x1000u) || (f & 0x7ffu) != 0u) fs += 0x1000u;
    return s + (fs >> 13);
  }
  uint he = (fe - 0x38000000u) >> 13, fs = f & 0x7fffffu;
  if ((fs & 0x3fffu) != 0x1000u) fs += 0x1000u;
  return s + (fs >> 13) + he;
}
// (-1)^s * m * 2^e (m != 0) rounded to a float with p significand bits, minimum normal exponent emin and ew exponent bits
// mode: 0 toward zero, 1 nearest even, 2 toward +inf, 3 toward -inf; rounds onto the denormal grid, overflows by mode
inline uint round_fp(uint s, ulong m, int e, int mode, int p, int emin, int ew) {
  int E = 63 - (int)clz(m) + e;
  int q = max(E, emin) - (p - 1), sh = q - e;
  ulong k = 0; bool above = false, tie = false, nz = false;
  if (sh <= 0) k = m << (-sh);
  else if (sh < 64) { ulong rem = m & ((1ul << sh) - 1ul), hv = 1ul << (sh - 1); k = m >> sh; nz = rem != 0ul; above = rem > hv; tie = rem == hv; }
  else { nz = true; if (sh == 64) { above = m > (1ul << 63); tie = m == (1ul << 63); } }
  bool inc = mode == 1 ? (above || (tie && (k & 1ul))) : mode == 2 ? (nz && s == 0u) : mode == 3 ? (nz && s != 0u) : false;
  if (inc) k += 1ul;
  ulong one = 1ul << (p - 1);
  uint be = 0u, maxe = (1u << ew) - 1u, sb = s << (ew + p - 1);
  if (k >= one) { int b = q + (p - 1) + (1 << (ew - 1)) - 1; if (k >= (one << 1)) { k >>= 1; b += 1; } be = (uint)b; }
  if (be >= maxe) {
    bool inf = mode == 1 || (mode == 2 && s == 0u) || (mode == 3 && s != 0u);
    return sb | (inf ? (maxe << (p - 1)) : (((maxe - 1u) << (p - 1)) | (uint)(one - 1ul)));
  }
  return sb | (be << (p - 1)) | (uint)(k & (one - 1ul));
}
// m * 2^e rounded to an integer by mode (0 trunc, 1 rint, 2 ceil, 3 floor), magnitude capped at 2^40
inline long round_int(uint s, ulong m, int e, int mode) {
  ulong k = 0; bool above = false, tie = false, nz = false;
  if (e >= 0) k = (63 - (int)clz(m) + e >= 40) ? (1ul << 40) : (m << e);
  else { int sh = -e;
    if (sh < 64) { ulong rem = m & ((1ul << sh) - 1ul), hv = 1ul << (sh - 1); k = m >> sh; nz = rem != 0ul; above = rem > hv; tie = rem == hv; }
    else { nz = true; if (sh == 64) { above = m > (1ul << 63); tie = m == (1ul << 63); } } }
  bool inc = mode == 1 ? (above || (tie && (k & 1ul))) : mode == 2 ? (nz && s == 0u) : mode == 3 ? (nz && s != 0u) : false;
  if (inc) k += 1ul;
  return s ? -(long)k : (long)k;
}
inline bool dec32(uint u, thread ulong &m, thread int &e) { uint ef = (u >> 23) & 0xffu; m = u & 0x7fffffu; if (ef) { m |= 0x800000ul; e = (int)ef - 150; } else e = -149; return m != 0ul; }
inline bool dec16(uint h, thread ulong &m, thread int &e) { uint ef = (h >> 10) & 0x1fu; m = h & 0x3ffu; if (ef) { m |= 0x400ul; e = (int)ef - 25; } else e = -24; return m != 0ul; }
// f32 -> f16 toward zero (an f32 written to a half register: emu.cov_to_float), denormals flushed
inline uint rtz16(uint f) {
  if (nan32(f)) return f2h(f);
  uint s = f >> 31; ulong m; int e;
  if ((f & 0x7fffffffu) == 0x7f800000u) return (s << 15) | 0x7c00u;
  if (!dec32(f, m, e)) return s << 15;
  return ftz16(round_fp(s, m, e, 0, 11, -14, 5));
}
// f32 -> f16 image store (emu.to_texel): toward zero, denormals kept, NaN canonical
inline uint texel16(uint f) {
  if (nan32(f)) return 0x7e00u;
  uint s = f >> 31; ulong m; int e;
  if ((f & 0x7fffffffu) == 0x7f800000u) return (s << 15) | 0x7c00u;
  if (!dec32(f, m, e)) return s << 15;
  return round_fp(s, m, e, 0, 11, -14, 5);
}
inline uint covf16(uint f, int mode) {
  if (nan32(f)) return 0x7e00u;
  uint s = f >> 31; ulong m; int e;
  if ((f & 0x7fffffffu) == 0x7f800000u) return (s << 15) | 0x7c00u;
  if (!dec32(f, m, e)) return s << 15;
  uint r = round_fp(s, m, e, mode, 11, -14, 5);
  return (r & 0x7c00u) == 0u ? (r & 0x8000u) : r;
}
inline uint covi2f(long v, bool h, int mode) {
  if (v == 0) return 0u;
  uint s = v < 0 ? 1u : 0u; ulong m = s ? (ulong)(-v) : (ulong)v;
  return h ? round_fp(s, m, 0, mode, 11, -14, 5) : round_fp(s, m, 0, mode, 24, -126, 8);
}
inline long covf2i(uint b, bool h, int mode, long lo, long hi) {
  if (h ? nan16(b) : nan32(b)) return 0;
  uint s = h ? (b >> 15) & 1u : b >> 31; ulong m; int e;
  if ((h ? (b & 0x7fffu) : (b & 0x7fffffffu)) == (h ? 0x7c00u : 0x7f800000u)) return s ? lo : hi;
  if ((h ? (b & 0x7c00u) : (b & 0x7f800000u)) == 0u) return 0;
  if (h) dec16(b, m, e); else dec32(b, m, e);
  return clamp(round_int(s, m, e, mode), lo, hi);
}
inline uint covf2u8(uint raw, bool h, int mode) {
  uint mb = h ? 10u : 23u, eb = h ? 5u : 8u; int bias = h ? 15 : 127;
  uint e = (raw >> mb) & ((1u << eb) - 1u), m = raw & ((1u << mb) - 1u), neg = (raw >> (mb + eb)) & 1u;
  if (neg != 0u || e == (1u << eb) - 1u || e == 0u) return 0u;
  int sh = (int)e - bias - (int)mb;
  ulong mant = m | (1u << mb);
  if (sh >= 0) return (uint)((mant << (sh % 32)) & 0xfffffffful);
  return (uint)round_int(0u, mant, sh, mode);
}
// the gpu flushes f32 denormal inputs and results to signed zero like the a630, but flushes before rounding: a product whose exact
// value rounds up to 2^-126 comes out 0. both factors are then below 2, so a 2^64 scaled fma against the rounding midpoint
// (2^-126 - 2^-150, a tie rounds up to the even 2^-126) decides it exactly
inline uint mul32(uint a, uint b) {
  uint p = U(F(a) * F(b));
  if ((p & 0x7fffffffu) != 0u || (a & 0x7f800000u) == 0u || (b & 0x7f800000u) == 0u) return p;
  float r = fma(fabs(F(a)) * 0x1p64f, fabs(F(b)), -0x1.fffffep-63f);
  return ((a ^ b) & 0x80000000u) | (r >= 0.0f ? 0x00800000u : 0u);
}
inline uint fmax32(uint a, uint b) {
  bool na = nan32(a), nb = nan32(b);
  uint big = ((a & 0x7fffffffu) == 0u && (b & 0x7fffffffu) == 0u) ? (a & b & 0x80000000u) : (F(a) > F(b) ? a : b);
  return na ? (nb ? a : b) : (nb ? a : big);
}
inline uint fmax16(uint a, uint b) {
  bool na = nan16(a), nb = nan16(b);
  uint big = ((a & 0x7fffu) == 0u && (b & 0x7fffu) == 0u) ? (a & b & 0x8000u) : (F(h2f(a)) > F(h2f(b)) ? a : b);
  return na ? (nb ? a : b) : (nb ? a : big);
}
inline uint fmin32(uint a, uint b) { return fmax32(a ^ 0x80000000u, b ^ 0x80000000u) ^ 0x80000000u; }
inline uint fmin16(uint a, uint b) { return fmax16(a ^ 0x8000u, b ^ 0x8000u) ^ 0x8000u; }
inline uint sign32(uint a) { return nan32(a) ? 0u : (a & 0x7fffffffu) == 0u ? a : (a & 0x80000000u) | 0x3f800000u; }
inline uint sign16(uint a) { return nan16(a) ? 0u : (a & 0x7fffu) == 0u ? a : (a & 0x8000u) | 0x3c00u; }
inline float rndaz(float a) { float t = trunc(a); return fabs(a - t) >= 0.5f ? t + copysign(1.0f, a) : t; }
inline uint sat32(uint a) { return (nan32(a) || (a >> 31)) ? 0u : F(a) > 1.0f ? 0x3f800000u : a; }
inline uint sat16(uint a) { return (nan16(a) || (a >> 15)) ? 0u : F(h2f(a)) > 1.0f ? 0x3c00u : a; }
inline int s24(uint v) { return as_type<int>(v << 8) >> 8; }
inline uint sfu_rcp(uint x, device const int* T) {
  uint s = x & 0x80000000u, a = x & 0x7fffffffu;
  if (a > 0x7f800000u) return x;
  if (a == 0u) return s | 0x7f800000u;
  if (a == 0x7f800000u) return s;
  int e = (int)(a >> 23); uint m = a & 0x7fffffu;
  if ((m == 0u ? 127 : 126) + 127 - e <= 0) return s;
  return (uint)(T[m] + ((127 - e) << 23)) | s;
}
inline uint sfu_sqrt(uint x, device const int* Te, device const int* To) {
  uint a = x & 0x7fffffffu;
  if (a > 0x7f800000u || a == 0u) return x;
  if (x >> 31) return 0x7fc00000u;
  if (a == 0x7f800000u) return x;
  int e = (int)(x >> 23) - 127; uint m = x & 0x7fffffu;
  return (uint)(((e & 1) ? To[m] : Te[m]) + ((e >> 1) << 23));
}
inline uint sfu_rsq(uint x, device const int* Te, device const int* To) {
  uint a = x & 0x7fffffffu;
  if (a > 0x7f800000u) return x;
  if (a == 0u) return (x & 0x80000000u) | 0x7f800000u;
  if (x >> 31) return 0x7fc00000u;
  if (a == 0x7f800000u) return 0u;
  int e = (int)(x >> 23) - 127; uint m = x & 0x7fffffu;
  return (uint)(((e & 1) ? To[m] : Te[m]) - ((e >> 1) << 23));
}
inline uint sfu_exp2(uint x, device const int* Pt, device const int* Nt) {
  if (nan32(x)) return x;
  uint s = x >> 31, a = x & 0x7fffffffu, g = 0u; ulong k;
  if (a == 0x7f800000u) k = 1000000000ul;
  else { int ef = (int)(a >> 23); ulong M = (a & 0x7fffffu) | (ef ? 0x800000u : 0u), A; int sh = ef - 126;
    if (ef == 0) A = 0ul; else if (sh >= 24) A = 1ul << 50; else if (sh >= 0) A = M << sh; else A = (-sh >= 64) ? 0ul : (M >> (-sh));
    k = A >> 24; g = sh >= 24 ? 0u : (uint)(A & 0xfffffful); }
  long ki = (long)min(k, 1000000ul), bits;
  if (s) { long n = (long)Nt[g] - (ki << 23); bits = (n >> 23) <= 0 ? 0 : n; }
  else { long p = ((ki + 127) << 23) | (long)Pt[g]; bits = ki + 127 >= 255 ? 0x7f800000l : p; }
  return (uint)bits;
}
inline uint sfu_log2(uint x, device const int* Lp, device const int* Ln, device const int* L0, device const int* Lm) {
  uint a = x & 0x7fffffffu;
  if (a > 0x7f800000u) return x;
  if (a == 0u) return 0xff800000u;
  if (x >> 31) return 0x7fc00000u;
  if (a == 0x7f800000u) return x;
  int e2 = (int)(x >> 23) - 127; uint m = x & 0x7fffffu;
  if (e2 == 0) return (uint)L0[m];
  if (e2 == -1) return (uint)Lm[m];
  long S = ((long)e2 << 24) + (long)(e2 > 0 ? Lp[m] : Ln[m]);
  if (S == 0) return 0u;
  uint sg = S < 0 ? 1u : 0u;
  return round_fp(sg, sg ? (ulong)(-S) : (ulong)S, -24, 0, 24, -126, 8);
}
inline device uchar* G(ulong a, device uchar* MEM, constant uint* P, device const XMap* X) {
  ulong o = a - (((ulong)P[1] << 32) | P[0]);
  if (o < (((ulong)P[3] << 32) | P[2])) return MEM + o;
  for (uint j = 0; j < P[4]; j++) if (a >= X[j].lo && a < X[j].hi) return X[j].p + (a - X[j].lo);
  return MEM;
}
"""

SFU32 = {O.OPC_RCP: ("rcp",), O.OPC_SQRT: ("sqrt_e", "sqrt_o"), O.OPC_RSQ: ("rsq_e", "rsq_o"), O.OPC_EXP2: ("exp2_p", "exp2_n"),
         O.OPC_LOG2: ("log2_p", "log2_n", "log2_0", "log2_m1")}
SFU16 = {O.OPC_RCP: "rcp", O.OPC_RSQ: "rsq", O.OPC_LOG2: "log2", O.OPC_EXP2: "exp2", O.OPC_SIN: "sin", O.OPC_COS: "cos", O.OPC_SQRT: "sqrt",
         O.OPC_HRSQ: "hrsq", O.OPC_HLOG2: "hlog2", O.OPC_HEXP2: "hexp2"}
TABLES = [t for v in SFU32.values() for t in v] + ["half"]

def _f32(bits:np.ndarray) -> np.ndarray: return bits.astype(np.uint32).view(np.float32)

@functools.cache
def sfu_table(name:str) -> np.ndarray:  # final result bits per mantissa, computed by the emulator itself
  path = os.path.join(cache_dir, "qcom_metal", f"{name}.npy")
  try: return np.load(path)
  except OSError: pass
  m = np.arange(1 << 23, dtype=np.int64)
  with np.errstate(all="ignore"):
    if name == "rcp":
      x = _f32((127 << 23) | m)
      out = emu.sfu_delta(O.OPC_RCP, x, np.reciprocal(x.astype(np.float64)).astype(np.float32)).view(np.uint32)
    elif name[:4] in ("sqrt", "rsq_"):
      op, fn = (O.OPC_SQRT, np.sqrt) if name.startswith("sqrt") else (O.OPC_RSQ, lambda v: 1 / np.sqrt(v))
      x = _f32(((127 if name.endswith("_e") else 128) << 23) | m)
      out = emu.sfu_delta(op, x, fn(x.astype(np.float64)).astype(np.float32)).view(np.uint32)
    elif name.startswith("exp2"):
      n, tab = 1 << 24, emu.sfu_tables()
      g = np.arange(n, dtype=np.int64)
      if name == "exp2_p": out = (np.exp2(g / float(n)).astype(np.float32).view(np.uint32).astype(np.int64) & 0x7FFFFF) + tab["exp2_f32_pos"][g]
      else: out = np.exp2(-g / float(n)).astype(np.float32).view(np.uint32).astype(np.int64) + tab["exp2_f32_neg"][g]
    elif name in ("log2_p", "log2_n"):
      tab = emu.sfu_tables()
      out = np.round(np.log2(1 + m / float(1 << 23)) * (1 << 24)).astype(np.int64) + tab["log2_f32_pos" if name == "log2_p" else "log2_f32_neg"][m]
    elif name in ("log2_0", "log2_m1"):
      out = emu.sfu_log2(_f32(((127 if name == "log2_0" else 126) << 23) | m)).view(np.uint32)
    elif name == "half":
      h = np.arange(1 << 16, dtype=np.uint16).view(np.float16)
      rows = []
      for op in SFU16:
        try: rows.append(emu.sfu_half(op, h).view(np.uint16))
        except RuntimeError: rows.append(np.zeros(1 << 16, np.uint16))
      out = np.concatenate(rows).view(np.uint16)
    else: raise KeyError(name)
  out = out.astype(np.uint16) if name == "half" else (out.astype(np.int64) & 0xFFFFFFFF).astype(np.uint32).view(np.int32)
  os.makedirs(os.path.dirname(path), exist_ok=True)
  np.save(tmp := f"{path}.{os.getpid()}.tmp.npy", out)
  os.replace(tmp, path)
  return out

# value containers in the generated code: f32/f16/u32/u16/u8 in uint (16 bit kinds zero extended), i32/i16/i8 in int (sign extended), i64 in long
CTYPE = {"f32": "uint", "f16": "uint", "u32": "uint", "u16": "uint", "u8": "uint", "i32": "int", "i16": "int", "i8": "int", "i64": "long", "b": "bool"}
NP2T = {"f2": "f16", "f4": "f32", "u2": "u16", "u4": "u32", "i2": "i16", "i4": "i32", "u1": "u8", "i1": "i8"}
def tname(dt:np.dtype) -> str: return NP2T[f"{dt.kind}{dt.itemsize}"]
def vt(kind:str, half:bool) -> str: return f"{kind}{16 if half else 32}"
def width(t:str) -> int: return 8 if t in ("u8", "i8") else 64 if t == "i64" else 16 if t.endswith("16") else 32

COND_OPS = ["<", "<=", ">", ">=", "==", "!="]
HWFTZ = {O.OPC_ADD_F, O.OPC_MUL_F, O.OPC_MAD_F32, O.OPC_FLOOR_F, O.OPC_CEIL_F, O.OPC_TRUNC_F, O.OPC_RNDNE_F}
BRANCH_OPS = {O.OPC_JUMP, O.OPC_BR, O.OPC_BRAO, O.OPC_BRAA, O.OPC_PREDT, O.OPC_PREDF}

class Gen:
  def __init__(self, key:tuple):
    (self.image, self.entry, self.merged, self.demote, self.localid_reg, self.wgid_reg, self.lmem_size, self.pvt_size, self.tex_dt, self.ibo_dt,
     self.test) = key
    self.prog = emu.decode(self.image)
    self.lines:list[str] = []
    self.ind, self.ntmp = 1, 0
    self.fregs:set[int] = set()
    self.hregs:set[int] = set()
    self.tables:set[str] = set()
    self.uses_lmem = self.uses_pvt = self.uses_bar = False
    self.dirty:set[int] = set()
    self.imms:list[int] = []

  # ***** registers
  def emit(self, s:str): self.lines.append("  " * self.ind + s)
  def tmp(self, e:str, t:str) -> tuple[str, str]:
    self.ntmp += 1
    self.emit(f"{CTYPE[t]} t{self.ntmp} = {e};")
    return f"t{self.ntmp}", t
  def freg(self, n:int, lazy:bool=False) -> str:
    if not 0 <= n < emu.NREGS: raise Unsupported(f"register r{n}")
    self.fregs.add(n)
    if n in self.dirty and not lazy:
      self.dirty.discard(n)
      self.emit(f"R{n} = cnan32(R{n});")
    return f"R{n}"
  # f32 add/mul/mad results skip NaN canonicalization until their bits are observed: arithmetic consumers make NaN of any NaN
  def settle(self):
    for n in sorted(self.dirty): self.emit(f"R{n} = cnan32(R{n});")
    self.dirty.clear()
  def hraw(self, n:int) -> str:  # t.h[n] as the emulator indexes it, no a0 redirect
    if self.merged: return f"(({self.freg(n >> 1)} >> {16 * (n & 1)}) & 0xFFFFu)"
    if not 0 <= n < emu.NREGS: raise Unsupported(f"register hr{n}")
    self.hregs.add(n)
    return f"H{n}"
  def set_half(self, n:int, bits16:str):
    if self.merged:
      r, sh = self.freg(n >> 1), 16 * (n & 1)
      self.emit(f"{r} = ({r} & {(~(0xFFFF << sh)) & 0xFFFFFFFF}u) | (({bits16}) << {sh});")
    else:
      self.hraw(n)
      self.emit(f"H{n} = {bits16};")

  # ***** emu.Threads.read / write
  def read(self, s:emu.Src, kind:str, lazy:bool=False) -> tuple[str, str]:
    t = vt(kind, s.half)
    if s.kind == "r":
      bits = self.hraw(s.val) if s.half and s.val < A0 else f"({self.freg(s.val)} & 0xFFFFu)" if s.half else self.freg(s.val, lazy)
    elif s.kind == "c<":
      if s.half: raise Unsupported("half relative const")
      bits = f"C[clamp(as_type<int>({self.freg(A0)}) + ({s.val}), 0, 4095)]"
    elif s.kind == "c":
      c = f"C[{s.val}]" if self.demote or not s.half else f"((C[{s.val >> 1}] >> {16 * (s.val & 1)}) & 0xFFFFu)"
      if s.half and kind == "f" and self.demote: c = f"f2h({c})"
      bits = f"({c} & 0xFFFFu)" if s.half else c
    else: bits = self.imm((s.val & 0xFFFF) if s.half else (s.val & 0xFFFFFFFF))
    e = bits if kind != "i" else f"((int)(short)({bits}))" if s.half else f"as_type<int>({bits})"
    v = self.tmp(e, t)
    if s.absneg & 2: v = self.tmp(self.abs_(v), t)
    if s.absneg & 1: v = self.tmp(self.neg(v), t)
    return v

  def imm(self, v:int) -> str:
    if v not in self.imms: self.imms.append(v)
    return f"IM[{self.imms.index(v)}]"

  def abs_(self, v:tuple[str, str]) -> str:
    e, t = v
    return {"f16": f"({e} & 0x7FFFu)", "f32": f"({e} & 0x7FFFFFFFu)", "u16": e, "u32": e, "i16": f"((int)(short)abs({e}))",
            "i32": f"({e} < 0 ? (int)(0u - (uint){e}) : {e})"}[t]
  def neg(self, v:tuple[str, str]) -> str:
    e, t = v
    return {"f16": f"({e} ^ 0x8000u)", "f32": f"({e} ^ 0x80000000u)", "u16": f"((0x10000u - {e}) & 0xFFFFu)", "u32": f"(0u - {e})",
            "i16": f"((int)(short)(-{e}))", "i32": f"(int)(0u - (uint){e})"}[t]
  def inv(self, v:tuple[str, str]) -> str:
    e, t = v
    return {"u16": f"((~{e}) & 0xFFFFu)", "u32": f"(~{e})", "i16": f"(~{e})", "i32": f"(~{e})"}[t]
  def wrap(self, e:str, t:str) -> str:  # an arithmetic result back into its container
    return {"u16": f"(({e}) & 0xFFFFu)", "u32": f"(uint)({e})", "i16": f"((int)(short)({e}))", "i32": f"as_type<int>((uint)({e}))", "u8": f"(({e}) & 0xFFu)",
            "i8": f"((int)(char)({e}))"}[t]

  def write(self, regid:int, half:bool, v:tuple[str, str]):
    e, t = v
    if regid >= A0: half = False
    if half and t == "f32": e, t = f"rtz16({e})", "f16"
    if half:
      bits = e if t in ("f16", "u16", "u8") else f"((uint)({e}) & 0xFFFFu)"
      self.set_half(regid, bits)
    else:
      bits = {"f32": e, "u32": e, "u16": e, "u8": e, "f16": f"h2f({e})"}.get(t, f"(uint)({e})")
      self.freg(regid, lazy=True)
      self.dirty.discard(regid)
      self.emit(f"R{regid} = {bits};")

  def ftz(self, v:tuple[str, str]) -> tuple[str, str]:
    return (f"ftz16({v[0]})", v[1]) if v[1] == "f16" else (f"ftz32({v[0]})", v[1]) if v[1] == "f32" else v

  # ***** instructions
  def inst(self, i):
    if isinstance(i, Cat1):
      if i.op != O.OPC_MOV:
        vals = [self.read(s, "u") for s in i.srcs]
        for d, v in zip(i.dsts, vals): self.write(d, i.dst_type in CAT1_HALF_TYPES, v)
        return
      for k in range(i.iterations): self.mov(i, k)
    elif isinstance(i, (Cat2, Cat3, Cat4)):
      for k in range(i.iterations): self.alu(i, k)
    elif isinstance(i, (Load, Store)):
      for k in range(i.iterations): self.mem(i)
    elif isinstance(i, Cat5):
      for k in range(i.iterations): self.isam(i)
    elif isinstance(i, Ibo):
      for k in range(i.iterations): self.ibo(i)
    elif isinstance(i, Cat7):
      if i.op == O.OPC_BAR:
        self.uses_bar = True
        self.emit("threadgroup_barrier(mem_flags::mem_threadgroup | mem_flags::mem_device);")
    else: raise Unsupported(f"{type(i).__name__}")

  def mov(self, i:Cat1, k:int):
    st, dt = i.src_type, i.dst_type
    sh, dh = st in CAT1_HALF_TYPES, dt in CAT1_HALF_TYPES
    raw, _ = self.read(i.repeat_srcs[k][0], "u")
    if st == dt: out = raw
    elif TYPES[dt].kind == "f":
      if st == 1: out = f"covf16({raw}, {i.round})"
      elif st == 0: out = f"(nan16({raw}) ? 0x7fc00000u : h2f({raw}))"
      else: out = f"covi2f({self.int_src(st, raw, True)}, {'true' if dt == 0 else 'false'}, {i.round})"
    elif st in (0, 1) and dt in (6, 7): out = f"covf2u8({raw}, {'true' if st == 0 else 'false'}, {i.round})"
    elif st in (0, 1):
      lo, hi = emu.CAT1_RANGE[dt]
      out = f"(uint)covf2i({raw}, {'true' if st == 0 else 'false'}, {i.round}, {lo}l, {hi}l)"
    else: out = f"(uint)({self.int_src(st, raw, False)})"
    self.write(i.dst + k, dh, (f"(({out}) & {0xFFFF if dh else 0xFFFFFFFF}u)", "u16" if dh else "u32"))

  def int_src(self, st:int, raw:str, to_float:bool) -> str:  # emu.cov_src for integer sources, as a long
    if st in (6, 7):
      if not to_float: return f"(long)(char)({raw} & 0xFFu)"
      s32 = f"(long)as_type<int>({raw})" if st == 7 else f"(long)({raw} & 0xFFFFu)"
      return f"(({raw} & 0x80u) ? -abs({s32}) : abs({s32}))"
    return {2: f"(long)({raw} & 0xFFFFu)", 3: f"(long)({raw})", 4: f"(long)(short)({raw} & 0xFFFFu)", 5: f"(long)as_type<int>({raw})"}[st]

  def fbin(self, op:str, a:tuple[str, str], b:tuple[str, str]) -> str:
    if a[1] == "f32": return f"mul32({a[0]}, {b[0]})" if op == "*" else f"U(F({a[0]}) {op} F({b[0]}))"
    return f"f2h(U(F(h2f({a[0]})) {op} F(h2f({b[0]}))))"
  def fun(self, fn:str, a:tuple[str, str]) -> str:
    if a[1] == "f32": return f"U({fn}(F({a[0]})))"
    return f"f2h(U({fn}(F(h2f({a[0]})))))"
  def fcmp(self, op:str, a:tuple[str, str], b:tuple[str, str]) -> str:
    if a[1] == "f32": return f"(F({a[0]}) {op} F({b[0]}))"
    return f"(F(h2f({a[0]})) {op} F(h2f({b[0]})))"

  def cmpv_int(self, i:Cat2, x:tuple[str, str], y:tuple[str, str]) -> str:
    bits = width(x[1])
    top, mask = 1 << (bits - 1), (1 << bits) - 1
    xe, ye = x[0], y[0]
    nx = f"((~{xe}) & {mask}u)"
    sx = f"(({xe} & {top}u) != 0u)"
    X = self.tmp({1: nx, 2: f"({sx} ? {nx} : {xe})", 3: f"({sx} ? {xe} : {nx})"}[i.cmpv_mod], "u32")[0]
    if emu.CMPS[i.op] == "u": lt = f"({X} < {ye})"
    else:
      low, sy = mask ^ top, f"(({ye} & {top}u) != 0u)"
      lt = f"({sx} != {sy} ? {sx} : (((({X} ^ {xe}) & {top}u) != 0u) ? (({X} & {low}u) >= ({ye} & {low}u)) : (({X} & {low}u) < ({ye} & {low}u))))"
    lt = self.tmp(lt, "b")[0]
    le = self.tmp(f"({lt} || {xe} == {ye})", "b")[0]
    return [lt, le, f"!{le}", f"!{lt}", f"({xe} == {ye})", f"({xe} != {ye})", "false", "false"][i.cond]

  def alu(self, i, k:int):
    srcs, op = i.repeat_srcs[k], i.op
    if isinstance(i, Cat2) and op in emu.CMPS:
      ot = vt("u", srcs[0].half)
      if i.cmpv_mod: b = self.cmpv_int(i, *[self.read(s, "u") for s in srcs])
      else:
        a, c = [self.read(s, emu.CMPS[op], lazy=emu.CMPS[op] == "f" and not s.half) for s in srcs]
        if a[1] != "f32": a, c = self.ftz(a), self.ftz(c)
        b = "false" if i.cond >= 6 else self.fcmp(COND_OPS[i.cond], a, c) if a[1].startswith("f") else f"({a[0]} {COND_OPS[i.cond]} {c[0]})"
      out = (f"({b} ? 1u : 0u)", ot)
      if i.sat: out = (f"({out[0]} ^ 1u)", ot)
      if op in emu.CMPV: out = (self.neg(out), ot)
    elif isinstance(i, Cat4) and srcs[0].half:
      if op not in SFU16: raise Unsupported("f16 sfu")
      x = self.read(srcs[0], "f")
      self.tables.add("half")
      out = (f"(uint)HALF[{list(SFU16).index(op) << 16} + {x[0]}]", "f16")
    elif isinstance(i, Cat4):
      x = self.ftz(self.read(srcs[0], "f"))
      if op not in SFU32: raise Unsupported(f"f32 {mesa.opc_t.get(op)}")
      names = SFU32[op]
      self.tables.update(names)
      fn = {O.OPC_RCP: "sfu_rcp", O.OPC_SQRT: "sfu_sqrt", O.OPC_RSQ: "sfu_rsq", O.OPC_EXP2: "sfu_exp2", O.OPC_LOG2: "sfu_log2"}[op]
      out = (f"{fn}({x[0]}, {', '.join('T_' + n for n in names)})", "f32")
    elif isinstance(i, Cat2) and op in emu.CAT2_MOD: out = self.cat2_mod(i, srcs)
    elif isinstance(i, Cat2) and i.sat and op in emu.SAT_INT:  # absneg.s: abs/neg taken in 64 bits before the clamp
      kind = emu.CAT2[op][0]
      s = srcs[0]
      v = self.read(emu.replace(s, absneg=0), kind)
      w = f"(long){v[0]}"
      if s.absneg & 2: w = f"abs({w})"
      if s.absneg & 1: w = f"(-{w})"
      lo, hi = self.trange(v[1])
      out = (f"({CTYPE[v[1]]})clamp({w}, {lo}l, {hi}l)", v[1])
    elif isinstance(i, Cat3) and op in (O.OPC_SEL_F32, O.OPC_SEL_F16):
      a, b, c = [self.read(s, "f") for s in srcs]
      fb = self.ftz(b)
      cond = f"(F({fb[0]}) >= 0.0f)" if fb[1] == "f32" else f"(F(h2f({fb[0]})) >= 0.0f)"
      out = (f"({cond} ? {a[0]} : {c[0]})", a[1])
    elif isinstance(i, Cat3) and op in emu.CAT3_NEG: out = self.cat3_neg(i, srcs)
    else:
      kind = (emu.CAT2 if isinstance(i, Cat2) else emu.CAT3)[op][0]
      hw = kind == "f" and not srcs[0].half and op in HWFTZ
      vals = [self.read(s, kind, lazy=hw) for s in srcs]
      if not hw: vals = [self.ftz(v) for v in vals]
      out = self.general(op, vals)
    out = self.tmp(*out)
    if out[1] == "f32" and op in HWFTZ and isinstance(i, (Cat2, Cat3)):
      if not i.dst_half and not i.sat:
        self.write(i.dst + k, False, out)
        self.dirty.add(i.dst + k)
        return
      out = self.tmp(f"cnan32({out[0]})", "f32")
    elif out[1] in ("f16", "f32") and not (isinstance(i, Cat3) and op in (O.OPC_SEL_F32, O.OPC_SEL_F16)) and not (isinstance(i, Cat4) and srcs[0].half):
      f = self.ftz(out)
      out = self.tmp(f[0] if op in (O.OPC_MIN_F, O.OPC_MAX_F, O.OPC_ABSNEG_F) else f"cnan{out[1][1:]}({f[0]})", out[1])
    sat = i.sat and not (isinstance(i, Cat2) and op in emu.CMPS) and op not in emu.SAT_INT and out[1] in ("f16", "f32") and not isinstance(i, Cat4)
    if sat: out = self.tmp(f"sat{out[1][1:]}({out[0]})", out[1])
    if isinstance(i, Cat2) and i.dst_conv and op in emu.DSTCONV_INF65536 and out[1] == "f16":
      out = self.tmp(f"((({out[0]}) & 0x7fffu) == 0x7c00u ? ((({out[0]}) & 0x8000u) << 16) | 0x47800000u : h2f({out[0]}))", "f32")
    self.write(i.dst + k, i.dst_half, out)

  def trange(self, t:str) -> tuple[int, int]:
    return {"u16": (0, 0xFFFF), "u32": (0, 0xFFFFFFFF), "i16": (-0x8000, 0x7FFF), "i32": (-0x80000000, 0x7FFFFFFF)}[t]

  def general(self, op:int, vals:list) -> tuple[str, str]:
    a = vals[0]
    t = a[1]
    if op == O.OPC_ADD_F: return self.fbin("+", a, vals[1]), t
    if op == O.OPC_MUL_F: return self.fbin("*", a, vals[1]), t
    if op == O.OPC_MAX_F: return f"fmax{t[1:]}({a[0]}, {vals[1][0]})", t
    if op == O.OPC_MIN_F: return f"fmin{t[1:]}({a[0]}, {vals[1][0]})", t
    if op == O.OPC_SIGN_F: return f"sign{t[1:]}({a[0]})", t
    if op == O.OPC_ABSNEG_F: return a[0], t
    if op in (O.OPC_FLOOR_F, O.OPC_TRUNC_F, O.OPC_CEIL_F, O.OPC_RNDNE_F, O.OPC_RNDAZ_F):
      return self.fun({O.OPC_FLOOR_F: "floor", O.OPC_TRUNC_F: "trunc", O.OPC_CEIL_F: "ceil", O.OPC_RNDNE_F: "rint", O.OPC_RNDAZ_F: "rndaz"}[op], a), t
    if op == O.OPC_ABSNEG_S: return a[0], t
    if op in (O.OPC_MAD_F32, O.OPC_MAD_F16):
      b, c = vals[1], vals[2]
      p = self.tmp(self.fbin('*', a, b) if t == "f32" else f"ftz16({self.fbin('*', a, b)})", t)
      return self.fbin("+", p, c), t
    raise Unsupported(f"alu {mesa.opc_t.get(op)}")

  def cat2_mod(self, i:Cat2, srcs) -> tuple[str, str]:
    op = i.op
    kind = emu.CAT2[op][0]
    vals = [self.read(s, kind) for s in srcs]
    mods = []
    for v, m in zip(vals, i.mods):
      if m == "not": v = self.tmp(self.inv(v), v[1])
      elif m == "neg": v = self.tmp(self.neg(v), v[1])
      elif m == "hi" and width(v[1]) == 32: v = self.tmp(f"({v[0]} >> 16)", v[1])
      mods.append(v)
    vals = mods
    a, t = vals[0], vals[0][1]
    bits = width(t)
    if op == O.OPC_BFREV_B and bits == 16: return ("0xFFFFu" if i.mods[0] == "not" else "0u"), t
    if i.sat and op in emu.SAT_INT:
      x, y = f"(long){a[0]}", f"(long){vals[1][0]}"
      e = {O.OPC_ADD_U: f"{x} + {y}", O.OPC_ADD_S: f"{x} + {y}", O.OPC_SUB_U: f"{x} - {y}", O.OPC_SUB_S: f"{x} - {y}",
           O.OPC_SHB: f"{x} + ({y} & 0xFFFFl)"}[op]
      lo, hi = self.trange(t)
      return f"({CTYPE[t]})clamp({e}, {lo}l, {hi}l)", t
    b = vals[1] if len(vals) > 1 else None
    ones = (1 << bits) - 1
    sh = f"({b[0]} & {bits - 1})" if b is not None else ""
    if op in (O.OPC_ADD_U, O.OPC_ADD_S): return self.wrap(f"(uint){a[0]} + (uint){b[0]}", t), t  # in uint: signed overflow is undefined in MSL
    if op in (O.OPC_SUB_U, O.OPC_SUB_S): return self.wrap(f"(uint){a[0]} - (uint){b[0]}", t), t
    if op in (O.OPC_MIN_U, O.OPC_MIN_S): return f"min({a[0]}, {b[0]})", t
    if op in (O.OPC_MAX_U, O.OPC_MAX_S): return f"max({a[0]}, {b[0]})", t
    if op == O.OPC_AND_B: return f"({a[0]} & {b[0]})", t
    if op == O.OPC_OR_B: return f"({a[0]} | {b[0]})", t
    if op == O.OPC_XOR_B: return f"({a[0]} ^ {b[0]})", t
    if op == O.OPC_NOT_B: return self.inv(a), t
    if op == O.OPC_MUL_S24: return f"as_type<int>((uint)s24((uint){a[0]}) * (uint)s24((uint){b[0]}))", "i32"
    if op == O.OPC_MUL_U24: return f"((((uint){a[0]}) & 0xFFFFFFu) * (((uint){b[0]}) & 0xFFFFFFu))", "u32"
    if op == O.OPC_MULL_U: return self.wrap(f"({a[0]} & 0xFFFFu) * ({b[0]} & 0xFFFFu)", t), t
    if op == O.OPC_CLZ_B: return f"({a[0]} == 0u ? {ones}u : clz({a[0]}){' - 16u' if bits == 16 else ''})", t
    if op == O.OPC_SETRM: return f"({a[0]} == 0u ? {ones}u : ctz({a[0]}))", t
    if op == O.OPC_CLZ_S:
      if bits == 16: return f"(({a[0]} & 0xFFFF) == 0 ? -1 : (int)clz((uint)({a[0]} & 0xFFFF)) - 16)", t
      w = self.tmp(f"({a[0]} < 0 ? ~{a[0]} : {a[0]})", t)[0]
      return f"({w} == 0 ? -1 : (int)clz((uint){w}))", t
    if op == O.OPC_SHL_B: return self.wrap(f"{a[0]} << {sh}", t), t
    if op == O.OPC_SHR_B: return f"({a[0]} >> {sh})", t
    if op == O.OPC_ASHR_B: return f"({a[0]} >> {sh})", t
    if op == O.OPC_GETBIT_B: return f"(({a[0]} >> {sh}) & 1u)", t
    if op == O.OPC_BFREV_B: return f"reverse_bits({a[0]})", t
    if op == O.OPC_CBITS_B: return f"popcount({a[0]} & 0xFFFFu)", t
    if op == O.OPC_MGEN_B: return self.wrap(f"(((1ul << ({a[0]} & 31u)) - 1ul) << ({b[0]} & 31u)) & 0xFFFFFFFFul", t), t
    if op == O.OPC_MSAD: return (a[0] if bits == 16 else f"((({a[0]} & 0xFFFFu) << 16) | ({b[0]} & 0xFFFFu))"), t
    if op == O.OPC_SHB: return self.wrap(f"{a[0]} + ({b[0]} & 0xFFFFu)", t), t
    raise Unsupported(f"cat2 {mesa.opc_t.get(op)}")

  def cat3_neg(self, i:Cat3, srcs) -> tuple[str, str]:
    op = i.op
    kind = emu.CAT3[op][0]
    raw = [self.read(s, kind) for s in srcs]
    vals = [self.tmp(self.neg(v), v[1]) if r == "neg" else self.tmp(self.inv(v), v[1]) if r == "not" else v for v, r in zip(raw, i.negs)]
    a, b, c = vals
    t = a[1]
    bits = width(t)
    if op in (O.OPC_SAD_S32, O.OPC_SAD_S16):
      ab = self.tmp(self.wrap(f"(uint){a[0]} + (uint){b[0]}", t), t)
      if i.negs[0] == "absab": ab = self.tmp(self.abs_(ab), t)
      if i.negs[2] == "negab": ab = self.tmp(self.neg(ab), t)
      return self.wrap(f"(uint){ab[0]} + (uint){raw[2][0]}", t), t
    sh = f"({a[0]} & {bits - 1})"
    if op in (O.OPC_MADSH_M16, O.OPC_MADSH_U16): return self.wrap(f"((({a[0]} & 0xFFFFu) * ({b[0]} >> 16)) << 16) + {c[0]}", t), t
    if op == O.OPC_MAD_U16: return self.wrap(f"({a[0]} & 0xFFFFu) * ({b[0]} & 0xFFFFu) + {c[0]}", t), t
    if op == O.OPC_MAD_S24: return f"((long)as_type<int>((uint)s24((uint){a[0]}) * (uint)s24((uint){b[0]})) + (long){c[0]})", "i64"
    if op == O.OPC_MAD_U24: return self.wrap(f"({a[0]} & 0xFFFFFFu) * ({b[0]} & 0xFFFFFFu) + {c[0]}", t), t
    if op in (O.OPC_SEL_S32, O.OPC_SEL_S16): return f"({b[0]} >= 0 ? {a[0]} : {c[0]})", t
    if op in (O.OPC_SEL_B32, O.OPC_SEL_B16): return f"({b[0]} != 0u ? {a[0]} : {c[0]})", t
    if op == O.OPC_SHRM: return f"(({b[0]} >> {sh}) & {c[0]})", t
    if op == O.OPC_SHRG: return f"(({b[0]} >> {sh}) | {c[0]})", t
    if op == O.OPC_SHLG: return self.wrap(f"({b[0]} << {sh}) | {c[0]}", t), t
    if op == O.OPC_SHLM: return self.wrap(f"({b[0]} << {sh}) & {c[0]}", t), t
    if op == O.OPC_ANDG: return f"(({b[0]} & {a[0]}) | {c[0]})", t
    if op == O.OPC_MAD_S16: return self.wrap(f"(uint){a[0]} * (uint){b[0]} + (uint){c[0]}", t), t
    raise Unsupported(f"cat3 {mesa.opc_t.get(op)}")

  # ***** memory
  def typed_load(self, ptr:str, dt:np.dtype) -> tuple[str, str]:
    t = tname(dt)
    space = ptr.split(":", 1)[0]
    p = ptr.split(":", 1)[1]
    c = {"f16": "ushort", "u16": "ushort", "i16": "short", "f32": "uint", "u32": "uint", "i32": "int", "u8": "uchar", "i8": "char"}[t]
    return self.tmp(f"({CTYPE[t]})(*({space} const {c}*)({p}))", t)

  def mem(self, i):
    dt, half = TYPES[i.type], i.type in HALF_TYPES
    n = dt.itemsize
    if isinstance(i, (Ldg, Stg)):
      a = f"(((ulong){self.freg(i.addr + 1)} << 32) | (ulong){self.freg(i.addr)})"
      a = f"({a} + {i.offset & 0xFFFFFFFFFFFFFFFF}ul)"
      if i.reg_off is not None:
        src2, shift, off = i.reg_off
        a = f"({a} + ((((ulong){self.freg(src2)}) << {shift}) + {off}ul) * {n}ul)"
      self.ntmp += 1
      base = f"t{self.ntmp}"
      self.emit(f"device uchar* {base} = G({a}, MEM, P, XM);")
      ptrs = [f"device:({base} + {c * n})" for c in range(i.size)]
      ok = None
    else:
      local = i.op in (O.OPC_LDL, O.OPC_STL)
      size = self.lmem_size if local else self.pvt_size
      if local: self.uses_lmem = True
      else: self.uses_pvt = True
      off = self.tmp(f"(long){self.freg(i.addr)} + ({i.offset})", "i64")[0]
      ok = self.tmp(f"({off} >= 0 && {off} + {n * i.size} <= {size})", "b")[0]
      space, arr = ("threadgroup", "LM") if local else ("thread", "PV")
      ptrs = [f"{space}:((({space} uchar*){arr}) + {off} + {c * n})" for c in range(i.size)]
    if isinstance(i, Load):
      if ok is not None:
        self.emit(f"if ({ok}) {{")
        self.ind += 1
      for c, p in enumerate(ptrs): self.write(i.dst + c, half, self.typed_load(p, dt))
      if ok is not None:
        self.ind -= 1
        if i.op == O.OPC_LDP:
          self.emit("} else {")
          self.ind += 1
          for c in range(i.size): self.write(i.dst + c, half, ("0u" if not tname(dt).startswith("i") else "0", tname(dt)))
          self.ind -= 1
        self.emit("}")
    else:
      if ok is not None:
        self.emit(f"if ({ok}) {{")
        self.ind += 1
      for c, p in enumerate(ptrs):
        row = self.hraw(i.val + c) if half else self.freg(i.val + c)
        space, q = p.split(":", 1)
        ct = {1: "uchar", 2: "ushort", 4: "uint"}[n]
        self.emit(f"*({space} {ct}*)({q}) = ({ct})({row});")
      if ok is not None:
        self.ind -= 1
        self.emit("}")

  def img_desc(self, kind:str, idx:int) -> tuple[str, str, str, str]:  # base pointer, width, height, pitch in elements
    o = 8 + 5 * (idx if kind == "tex" else len(self.tex_dt) + idx)
    return (f"(MEM + (((ulong)P[{o + 1}] << 32) | P[{o}]))", f"P[{o + 2}]", f"P[{o + 3}]", f"P[{o + 4}]")

  def isam(self, i:Cat5):
    if i.s2en: raise Unsupported("isam.s2en")
    if i.tex >= len(self.tex_dt): raise Unsupported(f"texture {i.tex} not bound")
    img_dt, dt, channels = self.tex_dt[i.tex], TYPES[i.type], emu.wrmask_channels(i.wrmask).tolist()
    if not channels: return
    kernel_path = not self.merged and img_dt in emu.TEX_DTYPES and dt in emu.TEX_DTYPES
    if kernel_path and i.dst + len(channels) > A0: raise Unsupported("isam into a0/p0")
    if kernel_path and img_dt == np.float32 and dt == np.float16: raise Unsupported("f32 texel into a half register")
    if dt not in (np.float16, np.float32) or img_dt not in (np.float16, np.float32): raise Unsupported("texel type")
    base, w, h, pitch = self.img_desc("tex", i.tex)
    x, y = self.freg(i.src1), self.freg(i.src1 + 1)
    ok = self.tmp(f"({x} < {w} && {y} < {h})", "b")[0]
    off = self.tmp(f"({ok} ? (ulong){y} * (ulong){pitch} + (ulong){x} * 4ul : 0ul)", "i64")[0]
    ct = "ushort" if img_dt == np.float16 else "uint"
    for n, c in enumerate(channels):
      v = self.tmp(f"({ok} ? (uint)((device const {ct}*){base})[{off} + {c}] : 0u)", "u32")[0]
      if img_dt == np.float16 and dt == np.float32: e = f"(nan16({v}) ? 0x7fc00000u : h2f({v}))" if kernel_path else f"h2f({v})"
      elif img_dt == np.float16: e = f"(nan16({v}) ? 0x7e00u : {v})" if kernel_path else v
      elif dt == np.float16: e = f"f2h({v})"
      else: e = v
      self.write(i.dst + n, dt == np.float16, (e, "f16" if dt == np.float16 else "f32"))

  def ibo(self, i:Ibo):
    if i.ssbo >= len(self.ibo_dt): raise Unsupported(f"ibo {i.ssbo} not bound")
    img_dt, dt = self.ibo_dt[i.ssbo], TYPES[i.type]
    if dt not in (np.float16, np.float32) or img_dt not in (np.float16, np.float32): raise Unsupported("ibo type")
    base, w, h, pitch = self.img_desc("ibo", i.ssbo)
    x, y = self.freg(i.coord), self.freg(i.coord + 1)
    self.emit(f"if ({x} < {w} && {y} < {h}) {{")
    self.ind += 1
    off = self.tmp(f"(ulong){y} * (ulong){pitch} + (ulong){x} * 4ul", "i64")[0]
    for c in range(i.ncomp):
      v = self.hraw(i.val + c) if dt == np.float16 else self.freg(i.val + c)
      if img_dt == dt: e = v
      elif img_dt == np.float32: e = f"h2f({v})"
      else: e = f"texel16({v})"
      ct = "ushort" if img_dt == np.float16 else "uint"
      self.emit(f"((device {ct}*){base})[{off} + {c}] = ({ct})({e});")
    self.ind -= 1
    self.emit("}")

  # ***** control flow
  def cond(self, i:Cat0) -> str:
    if i.op == O.OPC_JUMP: return "true"
    if i.op in (O.OPC_PREDT, O.OPC_PREDF): return f"({self.freg(P0)} {'!=' if i.op == O.OPC_PREDF else '=='} 0u)"
    c = f"(({self.freg(P0 + i.comp1)} != 0u) != {'true' if i.inv1 else 'false'})"
    if i.op == O.OPC_BRAO: c = f"({c} || (({self.freg(P0 + i.comp2)} != 0u) != {'true' if i.inv2 else 'false'}))"
    if i.op == O.OPC_BRAA: c = f"({c} && (({self.freg(P0 + i.comp2)} != 0u) != {'true' if i.inv2 else 'false'}))"
    return c

  def analyze(self):
    prog, seen, work = self.prog, set(), [self.entry]
    while work:
      pc = work.pop()
      if pc in seen: continue
      if pc >= len(prog) or pc < 0: raise Unsupported(f"pc {pc} outside the program")
      i = prog[pc]
      if isinstance(i, NotImplementedError): raise Unsupported(str(i))
      seen.add(pc)
      if isinstance(i, Cat0):
        if i.op in (O.OPC_CALL, O.OPC_RET): raise Unsupported("call/ret")
        if i.op == O.OPC_END: continue
        if i.op in BRANCH_OPS:
          work.append(i.target)
          if i.op == O.OPC_JUMP: continue
      work.append(pc + 1)
    self.reach = seen
    self.back:dict[int, int] = {}  # loop header -> last pc branching back to it
    for pc in seen:
      i = prog[pc]
      if isinstance(i, Cat0) and i.op in BRANCH_OPS and i.target <= pc: self.back[i.target] = max(self.back.get(i.target, -1), pc)
    if min(seen) < self.entry: raise Unsupported("code before the entry")

  def sese(self, pc:int, lo:int, hi:int, marks:dict[int, tuple[int, int]]) -> tuple[int, int]|None:  # smallest single entry/exit interval around pc
    branches = [(x, self.prog[x].target) for x in self.reach if isinstance(self.prog[x], Cat0) and self.prog[x].op in BRANCH_OPS]
    a, b = pc, pc + 1
    while True:
      na, nb = a, b
      for x, t in branches:
        if a <= x < b: na, nb = min(na, t), max(nb, t)
        elif a < t < b: na, nb = min(na, x), max(nb, x + 1)
      if (na, nb) == (a, b): break
      a, b = na, nb
    if a < lo or b > hi or a not in marks: return None
    if any(isinstance(self.prog[x], Cat7) and self.prog[x].op == O.OPC_BAR for x in range(a, b) if x in self.reach): return None
    return a, b

  def machine(self, a:int, b:int):  # [a, b) as a switch over block leaders; b is the only exit
    starts = {a} | {self.prog[x].target for x in range(a, b) if x in self.reach and isinstance(self.prog[x], Cat0) and self.prog[x].op in BRANCH_OPS}
    starts |= {x + 1 for x in range(a, b) if x in self.reach and isinstance(self.prog[x], Cat0) and self.prog[x].op in BRANCH_OPS | {O.OPC_END}}
    starts = sorted(x for x in starts if a <= x < b and x in self.reach)
    nxt = lambda x: x if x < b else -1
    self.settle()
    self.ntmp += 1
    pcv = f"t{self.ntmp}"
    self.emit(f"int {pcv} = {a};")
    self.emit(f"while ({pcv} >= 0) {{ switch ({pcv}) {{")
    self.ind += 1
    for k, s0 in enumerate(starts):
      end = starts[k + 1] if k + 1 < len(starts) else b
      self.emit(f"case {s0}: {{")
      self.ind += 1
      done = False
      for x in range(s0, end):
        i = self.prog[x]
        if x not in self.reach or (isinstance(i, Cat0) and i.op in (O.OPC_NOP, O.OPC_PREDE)): continue
        if not isinstance(i, Cat0): self.inst(i)
        elif i.op == O.OPC_END:
          self.dirty.clear()
          self.emit("return;")
          done = True
        elif i.op in BRANCH_OPS:
          self.settle()
          self.emit(f"{pcv} = {self.cond(i)} ? {nxt(i.target)} : {nxt(x + 1)}; break;")
          done = True
        else: raise Unsupported(f"cat0 {mesa.opc_t.get(i.op)}")
      if not done:
        self.settle()
        self.emit(f"{pcv} = {nxt(end)}; break;")
      self.ind -= 1
      self.emit("}")
    self.emit(f"default: {pcv} = -1;")
    self.ind -= 1
    self.emit("} }")

  def region(self, lo:int, hi:int, loops:list[tuple[int, int]], skip_header:int|None=None):
    pc, marks = lo, {}
    while pc < hi:
      if pc not in self.reach:
        pc += 1
        continue
      marks.setdefault(pc, (len(self.lines), self.ind, set(self.dirty)))
      try: pc = self.step(pc, lo, hi, loops, skip_header)
      except Unsupported as e:
        if (iv := self.sese(pc, lo, hi, marks)) is None: raise e
        n, self.ind, dirty = marks[iv[0]]
        self.dirty = set(dirty)
        del self.lines[n:]
        self.machine(*iv)
        pc = iv[1]
      skip_header = None
    self.settle()

  def step(self, pc:int, lo:int, hi:int, loops:list[tuple[int, int]], skip_header:int|None) -> int:
    if pc in self.back and pc != skip_header:
      q = self.back[pc]
      if q >= hi: raise Unsupported("loop leaves its region")
      self.settle()
      self.emit("while (true) {")
      self.ind += 1
      self.region(pc, q + 1, loops + [(pc, q + 1)], skip_header=pc)
      self.emit("break;")
      self.ind -= 1
      self.emit("}")
      return q + 1
    i = self.prog[pc]
    if not isinstance(i, Cat0):
      self.inst(i)
      return pc + 1
    if i.op in (O.OPC_NOP, O.OPC_PREDE): return pc + 1
    if i.op == O.OPC_END:
      if self.test: self.settle()
      self.emit("return;")
      return pc + 1
    if i.op not in BRANCH_OPS: raise Unsupported(f"cat0 {mesa.opc_t.get(i.op)}")
    self.settle()
    t, c = i.target, self.cond(i)
    if loops and t == loops[-1][0]:
      self.emit(f"if ({c}) continue;")
      return pc + 1
    elif loops and t == loops[-1][1]:
      self.emit(f"if ({c}) break;")
      return pc + 1
    elif any(t in (h, e) for h, e in loops): raise Unsupported("branch to an outer loop")
    elif pc < t <= hi:
      j = self.prog[t - 1]
      is_else = (t - 1 > pc and t - 1 in self.reach and isinstance(j, Cat0) and j.op in BRANCH_OPS and t < j.target <= hi
                 and not any(j.target in (h, e) for h, e in loops))
      if c == "true":
        if any(p in self.reach for p in range(pc + 1, t)): raise Unsupported("jump over reachable code")
        return t
      if is_else and j.op != O.OPC_JUMP:  # a conditional branch closing the block (predt/predf pairs): a flag says whether [t, target) runs
        self.ntmp += 1
        flag = f"t{self.ntmp}"
        self.emit(f"bool {flag} = true;")
        self.emit(f"if (!{c}) {{")
        self.ind += 1
        self.region(pc + 1, t - 1, loops)
        self.emit(f"{flag} = !{self.cond(j)};")
        self.ind -= 1
        self.emit(f"}}\n{'  ' * self.ind}if ({flag}) {{")
        self.ind += 1
        self.region(t, j.target, loops)
        self.ind -= 1
        self.emit("}")
        return j.target
      self.emit(f"if (!{c}) {{")
      self.ind += 1
      if is_else:
        self.region(pc + 1, t - 1, loops)
        self.ind -= 1
        self.emit("} else {")
        self.ind += 1
        self.region(t, j.target, loops)
        self.ind -= 1
        self.emit("}")
        return j.target
      self.region(pc + 1, t, loops)
      self.ind -= 1
      self.emit("}")
      return t
    raise Unsupported(f"unstructured branch {pc} -> {t}")

  def source(self) -> str:
    self.analyze()
    self.region(self.entry, max(self.reach) + 1, [])
    self.settle()
    self.emit("return;")
    body = self.lines
    head = []
    if self.test:
      for n in sorted(self.fregs): head.append(f"  uint R{n} = RF[{n} * NT + tid];")
      for n in sorted(self.hregs): head.append(f"  uint H{n} = HF[{n} * NT + tid];")
      tail = [f"  RF[{n} * NT + tid] = R{n};" for n in sorted(self.fregs)] + [f"  HF[{n} * NT + tid] = H{n};" for n in sorted(self.hregs)]
      body = [l.replace("return;", "goto_end;") for l in body]
    else:
      regs = sorted(self.fregs | {r + k for r in (self.localid_reg, self.wgid_reg) if r != 0xfc for k in range(3)})
      self.fregs = set(regs)
      if regs: head.append("  uint " + ", ".join(f"R{n} = 0u" for n in regs) + ";")
      if self.hregs: head.append("  uint " + ", ".join(f"H{n} = 0u" for n in sorted(self.hregs)) + ";")
      for reg, v in ((self.localid_reg, "lid"), (self.wgid_reg, "gid")):
        if reg != 0xfc: head += [f"  R{reg + k} = {v}.{c};" for k, c in enumerate("xyz")]
      tail = []
    if self.uses_lmem: head.insert(0, f"  threadgroup uint LM[{max(1, (self.lmem_size + 3) // 4)}];")
    if self.uses_pvt: head.insert(0, f"  uint PV[{max(1, (self.pvt_size + 3) // 4)}];")
    args = ["device uchar* MEM [[buffer(0)]]", "constant uint* C [[buffer(1)]]", "constant uint* P [[buffer(2)]]", "device const XMap* XM [[buffer(3)]]",
            "constant uint* IM [[buffer(28)]]"]
    for n in sorted(self.tables, key=TABLES.index):
      args.append(f"device const {'ushort* HALF' if n == 'half' else 'int* T_' + n} [[buffer({4 + TABLES.index(n)})]]")
    if self.test:
      args += ["device uint* RF [[buffer(30)]]", "device uint* HF [[buffer(29)]]"]
      args += ["uint tid [[thread_position_in_grid]]", "uint NT [[threads_per_grid]]"]
      code = head + ["  do {"] + ["  " + l.replace("goto_end;", "break;") for l in body] + ["  } while (false);"] + tail
    else:
      args += ["uint3 lid [[thread_position_in_threadgroup]]", "uint3 gid [[threadgroup_position_in_grid]]"]
      code = head + body
    return PRELUDE + "\nkernel void k(" + ", ".join(args) + ") {\n" + "\n".join(code) + "\n}\n"


# ***** Metal runtime

_libc, MADV_FREE_REUSABLE, MADV_FREE_REUSE = ctypes.CDLL(ctypes.util.find_library("c")), 7, 8

def _objc():
  import tinygrad.runtime.support.objc as objc
  from tinygrad.runtime.autogen import metal
  return objc, metal

class MetalQCOM:
  def __init__(self, arena_size:int):
    objc, metal = _objc()
    from tinygrad.runtime.ops_metal import MetalCompiler, checked, to_ns_str
    self.objc, self.metal, self.checked, self.to_ns_str = objc, metal, checked, to_ns_str
    self.compiler = MetalCompiler()
    self.dev = metal.MTLCreateSystemDefaultDevice()
    self.queue = self.dev.newCommandQueueWithMaxCommandBufferCount(1024)
    self.arena_mem = mmap.mmap(-1, arena_size, mmap.MAP_PRIVATE | mmap.MAP_ANON)
    self.nocopy = nocopy = objc.msg("newBufferWithBytesNoCopy:length:options:deallocator:", metal.MTLBuffer, [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_void_p])
    self.arena = nocopy(self.dev, ctypes.addressof(ctypes.c_char.from_buffer(self.arena_mem)), arena_size, metal.MTLResourceStorageModeShared, None)
    if self.arena.value is None: raise MemoryError(f"Metal could not wrap a {arena_size} byte arena")
    self.base, self.size = self.arena.contents(), arena_size
    self.free:list[tuple[int, int]] = [(0, arena_size)]
    self.used:dict[int, int] = {}
    self.high = 0
    self.pipes:dict[tuple, object] = {}
    self.tables:dict[str, object] = {}
    self.xbufs:dict[tuple[int, int], object] = {}
    self.xcache:dict[tuple, list] = {}
    self.xranges:list|None = None
    self.xout:list = []
    self.xdata = bytes(32)
    self.cb = self.enc = None
    self.deferred:list[tuple[int, int]] = []  # signal writes held until the kernels queued before them finish
    self.inflight:list = []
    self.ndisp = 0
    self.scratch = self.dev.newBufferWithLength_options(64 << 20, metal.MTLResourceStorageModeShared)
    self.scratch_off = 0
    self.stats = {"metal": 0, "cpu": 0, "compile_s": 0.0}
    self.fallback_reasons:dict[str, int] = {}
    self.scratch_ptr = self.scratch.contents()
    send, P, L = objc.lib["objc_msgSend"], ctypes.c_void_p, ctypes.c_ulong
    def fn(sel:str, *args):
      f = ctypes.CFUNCTYPE(None, P, P, *args)(ctypes.cast(send, P).value)
      s = objc.getsel(sel.encode()).value
      return lambda enc, *a: f(enc, s, *a)
    self.f_buffer = fn("setBuffer:offset:atIndex:", P, L, L)
    self.f_offset = fn("setBufferOffset:atIndex:", L, L)
    self.f_pso = fn("setComputePipelineState:", P)
    self.f_dispatch = fn("dispatchThreadgroups:threadsPerThreadgroup:", metal.MTLSize, metal.MTLSize)
    self.f_barrier = fn("memoryBarrierWithScope:", L)
    self.f_use = fn("useResource:usage:", P, L)
    self.est:dict = {}  # what the open encoder already has bound
    self.dmemo:dict[int, tuple] = {}

  def alloc(self, size:int) -> int:
    size = (size + 0x3FFF) & ~0x3FFF
    for k, (off, sz) in enumerate(self.free):
      if sz >= size:
        self.free[k:k + 1] = [(off + size, sz - size)] if sz > size else []
        self.used[off] = size
        self.high = max(self.high, off + size)
        self.sync()
        _libc.madvise(ctypes.c_void_p(self.base + off), ctypes.c_size_t(size), MADV_FREE_REUSE)
        ctypes.memset(self.base + off, 0, size)
        return self.base + off
    raise MemoryError(f"qcom metal arena of {self.size} bytes is full (QCOM_METAL_ARENA)")
  def owns(self, addr:int) -> bool: return self.base <= addr < self.base + self.size
  def release(self, addr:int):
    off = addr - self.base
    size = self.used.pop(off)
    _libc.madvise(ctypes.c_void_p(addr), ctypes.c_size_t(size), MADV_FREE_REUSABLE)  # hand the pages back: alloc zeroes them again
    self.free.append((off, size))
    self.free.sort()
    merged:list[tuple[int, int]] = []
    for o, s in self.free:
      if merged and merged[-1][0] + merged[-1][1] == o: merged[-1] = (merged[-1][0], merged[-1][1] + s)
      else: merged.append((o, s))
    self.free = merged

  def table(self, name:str):
    if name not in self.tables:
      path = os.path.join(cache_dir, "qcom_metal", f"{name}.bin")
      if not os.path.exists(path):
        t = sfu_table.__wrapped__(name).tobytes()
        with open(path + ".tmp", "wb") as f: f.write(t + bytes(-len(t) % 0x4000))
        os.replace(path + ".tmp", path)
      with open(path, "rb") as f: mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_COPY)
      buf = self.nocopy(self.dev, ctypes.addressof(ctypes.c_char.from_buffer(mm)), len(mm), self.metal.MTLResourceStorageModeShared, None)
      if buf.value is None: raise MemoryError(f"Metal could not wrap the {name} table")
      self.tables[name] = (buf, mm)
    return self.tables[name][0]

  def pipeline(self, key:tuple):
    if key in self.pipes: return self.pipes[key]
    st = time.perf_counter()
    try:
      g = Gen(key)
      src = g.source()
      path = os.path.join(cache_dir, "qcom_metal", "lib", hashlib.sha256(src.encode()).hexdigest() + ".metallib")
      try: lib = open(path, "rb").read()
      except OSError:
        lib = self.compiler.compile(src)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(tmp := f"{path}.{os.getpid()}.tmp", "wb") as f: f.write(lib)  # pid: parallel processes build the same kernels
        os.replace(tmp, path)
      library = self.checked(self.dev.newLibraryWithData_error, self.objc.dispatch_data_create(lib, len(lib), None, None))
      fn = library.newFunctionWithName(self.to_ns_str("k"))
      pso = self.checked(self.dev.newComputePipelineStateWithFunction_error, fn)
      samps = sorted({i.samp for i in g.prog if isinstance(i, Cat5) and not i.s2en})
      imms = np.array(g.imms or [0], np.uint32)
      imbuf = self.dev.newBufferWithLength_options(imms.nbytes, self.metal.MTLResourceStorageModeShared)
      ctypes.memmove(imbuf.contents(), imms.ctypes.data, imms.nbytes)
      ret = (pso, sorted(g.tables, key=TABLES.index), pso.maxTotalThreadsPerThreadgroup(), src, samps, imbuf)
    except Unsupported as e: ret = e
    self.stats["compile_s"] += time.perf_counter() - st
    self.pipes[key] = ret
    return ret

  def upload(self, data:bytes) -> int:
    n = (len(data) + 255) & ~255
    if self.scratch_off + n > 64 << 20: self.sync()
    off = self.scratch_off
    ctypes.memmove(self.scratch_ptr + off, data, len(data))
    self.scratch_off += n
    return off

  def upload_ptr(self, ptr:int, nbytes:int) -> int:
    n = (nbytes + 255) & ~255
    if self.scratch_off + n > 64 << 20: self.sync()
    off = self.scratch_off
    ctypes.memmove(self.scratch_ptr + off, ptr, nbytes)
    self.scratch_off += n
    return off

  def encoder(self):
    if self.enc is None:
      self.cb = self.queue.commandBuffer()
      self.enc = self.cb.computeCommandEncoder()
      self.est = {"tables": set(), "used": set()}
      e = self.enc.value
      self.f_buffer(e, self.arena.value, 0, 0)
      for i in (1, 2, 3): self.f_buffer(e, self.scratch.value, 0, i)
    return self.enc

  def flush(self):  # starts the queued kernels without waiting, so the gpu runs while the cp keeps encoding
    if self.enc is None: return
    self.enc.endEncoding()
    self.cb.commit()
    self.inflight.append(self.cb)
    self.cb = self.enc = None
    self.ndisp = 0

  def sync(self):
    self.flush()
    for cb in self.inflight:
      cb.waitUntilCompleted()
      if cb.status() == 5: raise RuntimeError(f"Metal command buffer failed: {cb.error()}")
    self.inflight.clear()
    self.scratch_off = 0
    for addr, val in self.deferred: to_mv(addr, 4).cast("I")[0] = val
    self.deferred.clear()

  def xmaps(self, d:emu.Dispatch) -> list[tuple[int, int, object]]:
    if d.ranges is self.xranges: return self.xout  # qcomgpu hands the same list until the mappings change
    key = tuple(d.ranges)
    if (hit := self.xcache.get(key)) is not None:
      self.xranges, self.xout = d.ranges, hit
      self.xdata = b"".join(struct.pack("QQQQ", lo, hi, buf.gpuAddress() + (lo - blo), 0) for lo, hi, buf, blo in hit) or bytes(32)
      return hit
    out = []
    for st, sz in d.ranges:
      if self.owns(st): continue
      lo, hi = st & ~0x3FFF, (st + sz + 0x3FFF) & ~0x3FFF
      if (lo, hi) not in self.xbufs:
        f = self.objc.msg("newBufferWithBytesNoCopy:length:options:deallocator:", self.metal.MTLBuffer,
                          [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_void_p])
        buf = f(self.dev, lo, hi - lo, self.metal.MTLResourceStorageModeShared, None)
        if buf.value is None: raise Unsupported(f"could not wrap host memory {st:#x}")
        self.xbufs[(lo, hi)] = buf
      out.append((st, st + sz, self.xbufs[(lo, hi)], lo))
    self.xcache, self.xranges, self.xout = {key: out}, d.ranges, out
    self.xdata = b"".join(struct.pack("QQQQ", lo, hi, buf.gpuAddress() + (lo - blo), 0) for lo, hi, buf, blo in out) or bytes(32)
    return out

  def prepare(self, d:emu.Dispatch) -> str|tuple:
    key = (d.image, d.entry, d.merged, d.demote, d.localid_reg, d.wgid_reg, d.lmem_size, d.pvt_size, tuple(t.dtype for t in d.textures),
           tuple(t.dtype for t in d.ibos), False)
    p = self.pipeline(key)
    if isinstance(p, Unsupported): return str(p)
    pso, tables, maxt, _, samps, imbuf = p
    nloc = math.prod(d.local_size)
    if nloc > maxt: return f"{nloc} threads per group > {maxt}"
    if d.lmem_size > 32768: return "local memory"
    if any(not self.owns(img.addr) for img in d.textures + d.ibos): return "image outside the arena"
    if any(k >= len(d.samplers) or not d.samplers[k] for k in samps): return "sampler"
    try: xm = self.xmaps(d)
    except Unsupported as e: return str(e)
    params = [self.base & 0xFFFFFFFF, self.base >> 32, self.size & 0xFFFFFFFF, self.size >> 32, len(xm), 0, 0, 0]
    for img in d.textures + d.ibos:
      off = img.addr - self.base
      params += [off & 0xFFFFFFFF, off >> 32, img.width, img.height, img.pitch // img.dtype.itemsize]
    return pso, tables, imbuf, struct.pack(f"{len(params)}I", *params), xm, self.xdata

  def run(self, d:emu.Dispatch) -> bool:
    if (m := self.dmemo.get(id(d))) is not None and m[0] is d: prep = m[1]
    else:
      prep = self.prepare(d)
      if len(self.dmemo) > 65536: self.dmemo.clear()
      self.dmemo[id(d)] = (d, prep)
    if isinstance(prep, str):
      self.fallback_reasons[prep] = self.fallback_reasons.get(prep, 0) + 1
      self.stats["cpu"] += 1
      self.sync()
      return False
    pso, tables, imbuf, pbytes, xm, xdata = prep
    e = self.encoder().value
    consts = np.ascontiguousarray(d.consts, np.uint32)
    poff = self.upload(pbytes)
    coff = self.upload_ptr(consts.ctypes.data, consts.nbytes)
    xoff = self.upload(xdata)
    if self.est.get("pso") is not pso: self.f_pso(e, pso.value); self.est["pso"] = pso
    self.f_offset(e, coff, 1)
    self.f_offset(e, poff, 2)
    self.f_offset(e, xoff, 3)
    if self.est.get("imbuf") is not imbuf: self.f_buffer(e, imbuf.value, 0, 28); self.est["imbuf"] = imbuf
    for _, _, buf, _ in xm:
      if buf.value not in self.est["used"]: self.f_use(e, buf.value, 3); self.est["used"].add(buf.value)
    for n in tables:
      if n not in self.est["tables"]: self.f_buffer(e, self.table(n).value, 0, 4 + TABLES.index(n)); self.est["tables"].add(n)
    m = self.metal
    self.f_dispatch(e, m.MTLSize(*d.groups), m.MTLSize(*d.local_size))
    self.f_barrier(e, m.MTLBarrierScopeBuffers)
    self.stats["metal"] += 1
    self.ndisp += 1
    if self.ndisp >= getenv("QCOM_METAL_BATCH", 8): self.flush()
    return True

_rt:MetalQCOM|None = None
def runtime() -> MetalQCOM:
  global _rt
  if _rt is None: _rt = MetalQCOM(getenv("QCOM_METAL_ARENA", 2 << 30))
  return _rt

def run(d:emu.Dispatch):
  rt = runtime()
  if getenv("QCOM_METAL") == 2: return crosscheck(rt, d)
  if not rt.run(d): emu.run(d)

def snapshot(rt:MetalQCOM, d:emu.Dispatch) -> list[tuple[int, bytes]]:
  out = [(rt.base, bytes(to_mv(rt.base, rt.high)))] if rt.high else []
  return out + [(st, bytes(to_mv(st, sz))) for st, sz in d.ranges if not rt.owns(st)]

def restore(snap:list[tuple[int, bytes]]):
  for addr, data in snap: ctypes.memmove(addr, data, len(data))

class Mismatch(RuntimeError): pass

def crosscheck(rt:MetalQCOM, d:emu.Dispatch):
  rt.sync()
  before = snapshot(rt, d)
  ok = rt.run(d)
  rt.sync()
  if not ok:
    emu.run(d)
    return
  gpu = snapshot(rt, d)
  restore(before)
  emu.run(d)
  cpu = snapshot(rt, d)
  for (addr, g), (_, c) in zip(gpu, cpu):
    if g != c:
      a, b = np.frombuffer(g, np.uint8), np.frombuffer(c, np.uint8)
      bad = np.nonzero(a != b)[0]
      key = hashlib.sha256(d.image).hexdigest()[:12]
      raise Mismatch(f"kernel {key}: metal differs from the emulator in {len(bad)} bytes, first at {addr + int(bad[0]):#x} "
                     f"(metal {a[bad[0]]:#x} emu {b[bad[0]]:#x})")
