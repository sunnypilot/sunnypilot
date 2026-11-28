# RDNA3 emulator v2 - compiles pcode to UOps executed via tinygrad CPU backend
# Each instruction is compiled to a kernel that operates on buffers:
#   arg=0: sgpr - sgpr[0-127], inline constants[128-255], SCC=258
#   arg=1: vgpr - vgpr[reg * 32 + lane]
#   arg=2: vmem - base address 0, INDEX offsets directly to host memory
#   arg=3: lds - local data share
#   arg=4: scratch - per-lane scratch memory
import os, ctypes, functools, hashlib, itertools, pathlib, pickle, re, platform, subprocess, tempfile, traceback
from typing import Callable

# Set/restore DAZ+FTZ (denormals-are-zero + flush-to-zero) to match RDNA3 default float mode
# x86: MXCSR bits DAZ(6)+FTZ(15), ARM64: FPCR bit FZ(24)
# Only applied during emulator execution, restored afterward to avoid breaking hypothesis tests
@functools.cache
def _get_ftz_lib():
  machine = platform.machine()
  if machine in ('x86_64', 'AMD64'):
    src = b'''
unsigned int get_fpcr(void){unsigned int m;__asm__ __volatile__("stmxcsr %0":"=m"(m));return m;}
void set_fpcr(unsigned int m){__asm__ __volatile__("ldmxcsr %0"::"m"(m));}
'''
    ftz_bits = 0x8040  # DAZ (bit 6) + FTZ (bit 15)
  elif machine in ('arm64', 'aarch64'):
    src = b'''
unsigned int get_fpcr(void){unsigned long long v;__asm__ __volatile__("mrs %0,fpcr":"=r"(v));return(unsigned int)v;}
void set_fpcr(unsigned int m){unsigned long long v=m;__asm__ __volatile__("msr fpcr,%0"::"r"(v));}
'''
    ftz_bits = 1 << 24  # FZ (bit 24)
  else: return None, 0
  try:
    with tempfile.NamedTemporaryFile(suffix='.so', delete=False) as f:
      subprocess.check_output(['clang', '-shared', '-O2', '-x', 'c', '-', '-o', f.name], input=src)
      lib = ctypes.CDLL(f.name)
      lib.get_fpcr.restype = ctypes.c_uint32
      lib.set_fpcr.argtypes = [ctypes.c_uint32]
      return lib, ftz_bits
  except Exception: return None, 0

class _MXCSRContext:
  """Context manager to set DAZ+FTZ during emulator execution and restore afterward."""
  __slots__ = ('_saved', '_ftz')
  def __init__(self, ftz:bool=True): self._ftz = ftz  # rdna4 model kernels run with f32 denormals kept, so they run without it
  def __enter__(self):
    lib, ftz_bits = _get_ftz_lib()
    if lib is None: return self
    self._saved = lib.get_fpcr()
    lib.set_fpcr((self._saved | ftz_bits) if self._ftz else (self._saved & ~ftz_bits))
    return self
  def __exit__(self, *args):
    lib, _ = _get_ftz_lib()
    if lib is None or not hasattr(self, '_saved'): return
    lib.set_fpcr(self._saved)

from tinygrad.uop.ops import UOp, Ops, KernelInfo, uopfunc, AxisType, rewrite_group
from tinygrad.dtype import dtypes, AddrSpace
from tinygrad.device import Buffer, BufferSpec, Device
from tinygrad.engine.realize import get_runtime
from tinygrad.codegen import to_program, to_program_config
from tinygrad.renderer import Renderer
import tinygrad.renderer.llvmir  # noqa: F401  # registers LLVM_STRICT_FP, which the emulator's kernels compile under
from tinygrad.helpers import Context, DEV, DEBUG, to_mv, ContextVar
from tinygrad.runtime.autogen import hsa
from tinygrad.viz.serve import amd_decode, get_cfg, COND_TAKEN, COND_NOT_TAKEN, UNCOND, get_elf_section

from tinygrad.runtime.autogen.amd.rdna3.str_pcode import PCODE as PCODE_RDNA3
from tinygrad.runtime.autogen.amd.rdna4.str_pcode import PCODE as PCODE_RDNA4
from tinygrad.runtime.autogen.amd.cdna.str_pcode import PCODE as PCODE_CDNA
from tinygrad.runtime.autogen.amd.rdna3 import ins as ir3
from tinygrad.runtime.autogen.amd.rdna4 import ins as ir4
from tinygrad.runtime.autogen.amd.cdna import ins as irc
from tinygrad.renderer.amd.dsl import VCC_LO, EXEC_LO, SCC, ttmp, Inst
from tinygrad.runtime.autogen.amd.common import Fmt, OpType
from test.amd.helpers import decode_dpp16
from test.mockgpu.amd.pcode import parse_pcode, _FUNCS, _set_bits, _to_bool, _to_u32, _val_to_bits, _ftz_f32, _bitreverse, _countbits

def _c(val, dtype=dtypes.uint32): return UOp.const(val, dtype)

def _u64(lo: UOp, hi: UOp) -> UOp:
  """Combine two 32-bit UOps into a 64-bit UOp."""
  return lo.cast(dtypes.uint64) | (hi.cast(dtypes.uint64) << _c(32, dtypes.uint64))

def _split64(val: UOp) -> tuple[UOp, UOp]:
  """Split a 64-bit value into (lo, hi) 32-bit values."""
  v64 = val.bitcast(dtypes.uint64) if val.dtype == dtypes.float64 else val.cast(dtypes.uint64)
  return v64.cast(dtypes.uint32), (v64 >> _c(32, dtypes.uint64)).cast(dtypes.uint32)

_SRC_MOD_TYPES = {16: (dtypes.uint16, dtypes.half, 0x7FFF), 32: (dtypes.uint32, dtypes.float32, 0x7FFFFFFF),
                  64: (dtypes.uint64, dtypes.float64, 0x7FFFFFFFFFFFFFFF)}
def _apply_src_mods(val: UOp, mod_bit: int, abs_bits: int, neg_bits: int, bits: int = 32) -> UOp:
  """Apply abs/neg modifiers to source value based on bit width (16, 32, or 64)."""
  if not (abs_bits & (1 << mod_bit)) and not (neg_bits & (1 << mod_bit)) or bits not in _SRC_MOD_TYPES: return val
  ut, ft, mask = _SRC_MOD_TYPES[bits]
  fv = val.cast(ut).bitcast(ft) if bits == 16 else val.bitcast(ft) if val.dtype == ut else val
  if abs_bits & (1 << mod_bit): fv = (fv.bitcast(ut) & _c(mask, ut)).bitcast(ft)
  # neg modifier is a pure sign-bit toggle (preserves NaN payloads), not an arithmetic negate
  if neg_bits & (1 << mod_bit): fv = (fv.bitcast(ut) ^ _c((mask + 1) & (1 << (bits - 1)), ut)).bitcast(ft)
  return fv.bitcast(ut).cast(dtypes.uint32) if bits == 16 else fv.bitcast(ut)

# Map VOPD ops to VOP2/VOP1 ops for pcode lookup (both RDNA3 and RDNA4 share these targets)
_VOPD_TARGETS = {
  'V_DUAL_FMAC_F32': ir3.VOP2Op.V_FMAC_F32_E32, 'V_DUAL_MUL_F32': ir3.VOP2Op.V_MUL_F32_E32,
  'V_DUAL_ADD_F32': ir3.VOP2Op.V_ADD_F32_E32, 'V_DUAL_SUB_F32': ir3.VOP2Op.V_SUB_F32_E32,
  'V_DUAL_SUBREV_F32': ir3.VOP2Op.V_SUBREV_F32_E32, 'V_DUAL_MAX_F32': ir3.VOP2Op.V_MAX_F32_E32,
  'V_DUAL_MIN_F32': ir3.VOP2Op.V_MIN_F32_E32, 'V_DUAL_ADD_NC_U32': ir3.VOP2Op.V_ADD_NC_U32_E32,
  'V_DUAL_LSHLREV_B32': ir3.VOP2Op.V_LSHLREV_B32_E32, 'V_DUAL_AND_B32': ir3.VOP2Op.V_AND_B32_E32,
  'V_DUAL_MOV_B32': ir3.VOP1Op.V_MOV_B32_E32, 'V_DUAL_CNDMASK_B32': ir3.VOP2Op.V_CNDMASK_B32_E32,
  'V_DUAL_FMAAK_F32': ir3.VOP2Op.V_FMAAK_F32_E32, 'V_DUAL_FMAMK_F32': ir3.VOP2Op.V_FMAMK_F32_E32,
  'V_DUAL_DOT2ACC_F32_F16': ir3.VOP2Op.V_DOT2ACC_F32_F16_E32,
}
# RDNA4 uses a _NUM_ suffix for min/max
VOPD_TO_VOP2 = {getattr(ir3.VOPDOp, n): t for n, t in _VOPD_TARGETS.items()}
def _vopd_rdna4(op):  # an rdna4 dual op runs the rdna4 VOP2/VOP1 op of the same name, so it gets rdna4's pcode
  n = op.name.replace('V_DUAL_', 'V_') + '_E32'
  return getattr(ir4.VOP2Op, n, None) or getattr(ir4.VOP1Op, n, None)
VOPD_TO_VOP2.update({op: t for op in ir4.VOPDOp if (t := _vopd_rdna4(op)) is not None})
_TINY_OPS = {'V_MUL_F32': 2, 'V_MUL_F16': 2, 'V_MUL_DX9_ZERO_F32': 2, 'V_MULLIT_F32': 2, 'V_FMA_F32': 3, 'V_FMA_F16': 3, 'V_FMAC_F32': 'D0',
             'V_FMAC_F16': 'D0', 'V_FMA_DX9_ZERO_F32': 3}
def _tiny_before_rounding(name:str, srcs:dict, val:UOp) -> UOp|None:
  # a result that rounded up to the smallest normal is a denormal to omod (so +0) when, rounded with an unbounded exponent, it stays below
  k = _TINY_OPS.get(re.sub(r'_E(32|64)$', '', name))
  if k is None or val.dtype not in (dtypes.float32, dtypes.half): return None
  rd = (lambda x: _ftz(_as(x, val.dtype)).cast(_F64)) if 'FMA_DX9' in name else (lambda x: _as(x, val.dtype).cast(_F64))
  ex = rd(srcs['S0']) * rd(srcs['S1']) + (rd(srcs['S2' if k == 3 else 'D0']) if k != 2 else _c(0.0, _F64))
  emin, mb = (-126, 23) if val.dtype == dtypes.float32 else (-14, 10)
  return val.abs().eq(_c(2.0 ** emin, val.dtype)) & (ex.abs() < _c(2.0 ** emin - 2.0 ** (emin - mb - 2), _F64))
def _omod(val:UOp, omod:int) -> UOp:
  # output modifier *2, *4, /2 as an exponent-field add: a denormal or zero result is +0, an exponent pushed to 0 or below is a signed
  # zero, one pushed to the top is a signed inf; inf and NaN pass through
  ut, eb, mb = {2: (dtypes.uint16, 5, 10), 4: (dtypes.uint32, 8, 23), 8: (dtypes.uint64, 11, 52)}[val.dtype.itemsize]
  i32, emax = dtypes.int32, (1 << eb) - 1
  b = val.bitcast(ut)
  sign = b & _c(1 << (eb + mb), ut)
  e = ((b >> _c(mb, ut)) & _c(emax, ut)).cast(i32)
  e2 = e + _c({1: 1, 2: 2, 3: -1}[omod], i32)
  scaled = (sign | (e2.cast(ut) << _c(mb, ut)) | (b & _c((1 << mb) - 1, ut)))
  r = (e2 <= _c(0, i32)).where(sign, (e2 >= _c(emax, i32)).where(sign | _c(emax << mb, ut), scaled))
  r = e.eq(_c(0, i32)).where(_c(0, ut), e.eq(_c(emax, i32)).where(b, r))
  return r.bitcast(val.dtype)
_RAW16 = {'FMT_NUM_I16', 'FMT_NUM_U16', 'FMT_NUM_B16', 'FMT_NUM_PK2_FP8', 'FMT_NUM_PK2_BF8', 'FMT_NUM_PK2_I16', 'FMT_NUM_PK2_U16'}
def _f16_const(inst, key:str) -> bool:  # rdna4: a float inline constant reaches a 16-bit integer or fp8 operand as its f32 bits, truncated
  if not (_hw_float() and isinstance(inst, (ir4.VOP1, ir4.VOP2, ir4.VOP3, ir4.VOPC))): return True
  fmt = inst.canonical_operands.get(key, (None,))[0]
  return getattr(fmt, 'name', '') not in _RAW16
def _pk_const(off:UOp, val:UOp, bf:bool, lo_only:bool=False) -> UOp:  # an inline constant in a packed 16-bit operand: its 16-bit form in both halves
  val = val.cast(dtypes.uint32) if val.dtype != dtypes.uint32 else val
  f = (off >= _c(240)) & (off <= _c(248))
  h16 = (val >> _c(16)) if bf else val.bitcast(dtypes.float32).cast(dtypes.half).bitcast(dtypes.uint16).cast(dtypes.uint32)
  h = f.where(h16, val & _c(0xFFFF))
  return ((off >= _c(128)) & (off < _c(255))).where(h if lo_only else h | (h << _c(16)), val)
def _clamp01(x:UOp) -> UOp: return (x > _c(0.0, x.dtype)).where(x.minimum(_c(1.0, x.dtype)), _c(0.0, x.dtype))  # -0 and NaN -> +0
def _h16(bits:UOp) -> UOp: return bits.cast(dtypes.uint16).bitcast(dtypes.half)
def _wave_size(arch: str) -> int: return 64 if arch.startswith("cdna") else 32
def _iattr(inst, name: str, default: int = 0) -> int:
  """Optional integer attribute of a decoded instruction (None/missing -> default)."""
  v = getattr(inst, name, default)
  return default if v is None else v
# SGPR buffer: 0-127 = SGPRs, 128-255 = inline constants
SGPR_COUNT = 256

def _op_name(inst) -> str:
  if hasattr(inst, 'opx'): return f"{inst.opx.name}_{inst.opy.name}"  # VOPD has opx/opy not op
  return inst.op.name

def _lane_active(exec_mask: UOp, lane: UOp) -> UOp:
  if exec_mask.dtype == dtypes.uint64: return ((exec_mask >> lane.cast(dtypes.uint64)) & _c(1, dtypes.uint64)).ne(_c(0, dtypes.uint64))
  return ((exec_mask >> lane.cast(dtypes.uint32)) & _c(1)).ne(_c(0))
def _hi16(v: UOp) -> UOp: return (v >> _c(16)) & _c(0xFFFF)
def _cond(cond, if_true, if_false):
  """Select between values based on condition (works with UOp or bool)."""
  return cond.where(if_true, if_false) if isinstance(cond, UOp) else if_true if cond else if_false
def _cond_hi16(cond, val: UOp) -> UOp: return _cond(cond, _hi16(val), val)
def _apply_opsel(val: UOp, sel_bit: int, opsel: int) -> UOp: return _hi16(val) if opsel & (1 << sel_bit) else val

def _val_to_u32(val: UOp) -> UOp:
  """Convert any value to uint32 for storage (bitcast floats, cast ints)."""
  if val.dtype == dtypes.float32: return val.bitcast(dtypes.uint32)
  if val.dtype == dtypes.half: return val.bitcast(dtypes.uint16).cast(dtypes.uint32)
  return val.cast(dtypes.uint32)

_pcode_fixes = {
  'V_RCP_F32': ('1.0F / S0.f32', 'hw_rcp(S0.f32)'), 'V_S_RCP_F32': ('1.0F / S0.f32', 'hw_rcp(S0.f32)'),
  'V_SQRT_F32': ('sqrt(S0.f32)', 'hw_sqrt(S0.f32)'), 'V_EXP_F16': ("pow(16'2.0, S0.f16)", 'hw_exp16(S0.f16)'),
  'V_EXP_F32': ('pow(2.0F, S0.f32)', 'hw_exp32(S0.f32)'), 'V_RSQ_F32': ('1.0F / sqrt(S0.f32)', 'hw_rsq32(S0.f32)'),
  'V_LOG_F32': ('log2(S0.f32)', 'hw_log32(S0.f32)'), 'V_RSQ_F16': ("16'1.0 / sqrt(S0.f16)", 'hw_rsq16(S0.f16)'),
  'V_RCP_F16': ("16'1.0 / S0.f16", 'hw_rcp16(S0.f16)'), 'V_SQRT_F16': ('sqrt(S0.f16)', 'hw_sqrt16(S0.f16)'),
  'V_LOG_F16': ('log2(S0.f16)', 'hw_log16(S0.f16)'),
  'V_S_EXP_F32': ('pow(2.0F, S0.f32)', 'hw_exp32(S0.f32)'), 'V_S_EXP_F16': ("pow(16'2.0, S0.f16)", 'hw_exp16(S0.f16)'),
  'V_S_LOG_F32': ('log2(S0.f32)', 'hw_log32(S0.f32)'), 'V_S_LOG_F16': ('log2(S0.f16)', 'hw_log16(S0.f16)'),
  'V_S_RSQ_F32': ('1.0F / sqrt(S0.f32)', 'hw_rsq32(S0.f32)'), 'V_S_RSQ_F16': ("16'1.0 / sqrt(S0.f16)", 'hw_rsq16(S0.f16)'),
  'V_S_SQRT_F32': ('sqrt(S0.f32)', 'hw_sqrt(S0.f32)'), 'V_S_SQRT_F16': ('sqrt(S0.f16)', 'hw_sqrt16(S0.f16)'),
  'V_S_RCP_F16': ("16'1.0 / S0.f16", 'hw_rcp16(S0.f16)'),
  'V_SUBREV_F32': ('S1.f32 - S0.f32', '-S0.f32 + S1.f32'), 'V_SUBREV_F16': ('S1.f16 - S0.f16', '-S0.f16 + S1.f16'),
  'V_PACK_B32_F16': ('D0[31 : 16].f16 = S1.f16;\nD0[15 : 0].f16 = S0.f16', 'D0[31 : 16].f16 = hw_quiet(S1.f16);\nD0[15 : 0].f16 = hw_quiet(S0.f16)'),
  'V_FMA_MIXLO_F16': ('D0[15 : 0].f16 = f32_to_f16(fma(in[0], in[1], in[2]))', 'D0[15 : 0].f16 = hw_fma_mix16(in[0], in[1], in[2])'),
  'V_FMA_MIXHI_F16': ('D0[31 : 16].f16 = f32_to_f16(fma(in[0], in[1], in[2]))', 'D0[31 : 16].f16 = hw_fma_mix16(in[0], in[1], in[2])'),
  'V_CVT_F32_FP8': ('VGPR[laneId][SRC0.u32]', 'S0'),
  'V_CVT_F32_BF8': ('VGPR[laneId][SRC0.u32]', 'S0'),
  'V_DIV_FMAS_F32': ('D0.f32 = 2.0F ** 32 * fma(S0.f32, S1.f32, S2.f32)',
    'D0.f32 = (exponent(S2.f32) > 127) ? (2.0F ** 64 * fma(S0.f32, S1.f32, S2.f32)) : (2.0F ** -64 * fma(S0.f32, S1.f32, S2.f32))'),
  'V_DIV_FMAS_F64': ('D0.f64 = 2.0 ** 64 * fma(S0.f64, S1.f64, S2.f64)',
    'D0.f64 = (exponent(S2.f64) > 1023) ? (2.0 ** 128 * fma(S0.f64, S1.f64, S2.f64)) : (2.0 ** -128 * fma(S0.f64, S1.f64, S2.f64))'),
  'V_DIV_FIXUP_F32': ('D0.f32 = sign_out ? -abs(S0.f32) : abs(S0.f32)',
    'D0.f32 = isNAN(S0.f32) ? (sign_out ? -INF.f32 : +INF.f32) : (sign_out ? -abs(S0.f32) : abs(S0.f32))'),
  'V_DIV_FIXUP_F64': ('D0.f64 = sign_out ? -abs(S0.f64) : abs(S0.f64)',
    'D0.f64 = isNAN(S0.f64) ? (sign_out ? -INF : +INF) : (sign_out ? -abs(S0.f64) : abs(S0.f64))'),
  'V_TRIG_PREOP_F64': ("result = 64'F((1201'B(2.0 / PI)[1200 : 0] << shift.u32) & 1201'0x1fffffffffffff)", "result = trig_preop_result(shift)"),
  'V_FREXP_EXP_I32_F32': ('D0.i32 = exponent(S0.f32) - 127 + 1', 'D0.i32 = frexp_exp(S0.f32)'),
  'V_FREXP_EXP_I32_F64': ('D0.i32 = exponent(S0.f64) - 1023 + 1', 'D0.i32 = frexp_exp(S0.f64)'),
  'V_LDEXP_F32': ('D0.f32 = S0.f32 * 2.0F ** S1.i32', 'D0.f32 = ldexp(S0.f32, S1.i32)'),
  'V_LDEXP_F64': ('D0.f64 = S0.f64 * 2.0 ** S1.i32', 'D0.f64 = ldexp(S0.f64, S1.i32)'),
  'S_MAX_I32': ('SCC = S0.i32 >= S1.i32', 'SCC = S0.i32 > S1.i32'),
  'S_MAX_U32': ('SCC = S0.u32 >= S1.u32', 'SCC = S0.u32 > S1.u32'),
  'S_ABSDIFF_I32': ('D0.i32 = S0.i32 - S1.i32;\nif D0.i32 < 0 then\nD0.i32 = -D0.i32\nendif',
                    'D0.u32 = S0.u32 - S1.u32;\nif D0.i32 < 0 then\nD0.u32 = -D0.u32\nendif'),
  'V_CMP_CLASS_F32': ('64\'F(abs(S0.f32)) > 0.0', '(64\'U(S0.u32 & 0x7FFFFFFF) != 0)'),
  'V_CMP_CLASS_F16': ('64\'F(abs(S0.f16)) > 0.0', '(64\'U(S0.u32 & 0x7FFF) != 0)'),
  'V_CMP_CLASS_F64': ('64\'F(abs(S0.f64)) > 0.0', '(64\'U(S0.u64 & 0x7FFFFFFFFFFFFFFF) != 0)'),
  'V_MUL_F32': ('D0.f32 = S0.f32 * S1.f32', 'D0.f32 = isNAN(S0.f32) ? cvtToQuietNAN(S0.f32) : isNAN(S1.f32) ? cvtToQuietNAN(S1.f32) : S0.f32*S1.f32'),
}

def _get_pcode_dict(op) -> dict:
  """Return the PCODE dictionary for the given opcode based on its architecture."""
  return PCODE_CDNA if 'cdna' in type(op).__module__ else PCODE_RDNA4 if 'rdna4' in type(op).__module__ else PCODE_RDNA3

# Pcode lookup with hardware errata fixes (the AMD-pdf pcode for these ops is subtly wrong)
@functools.cache
def get_pcode(op) -> str:
  op_name = op.name
  pcode_dict = _get_pcode_dict(op)
  if op not in pcode_dict and op_name.endswith('_E64'):
    # VOP3 ops ending in _E64 may share pcode with VOP1 _E32 equivalents
    import importlib
    enum_mod = importlib.import_module(type(op).__module__)
    vop1_cls, e32_name = getattr(enum_mod, 'VOP1Op', None), op_name.replace('_E64', '_E32')
    if vop1_cls and hasattr(vop1_cls, e32_name): op = vop1_cls[e32_name]
  pcode = pcode_dict[op]
  fix_name = op_name.replace('_E64', '').replace('_E32', '')
  if fix_name in _pcode_fixes: pcode = pcode.replace(*_pcode_fixes[fix_name])
  return _fix_div_scale(pcode, 'f32' if 'F32' in op_name else 'f64') if 'V_DIV_SCALE' in op_name else pcode

def _fix_div_scale(pcode: str, dt: str) -> str:
  """V_DIV_SCALE fixes: only the divWouldBeDenorm/exponent-overflow path may return the scaled value;
  all other paths must return S0 unchanged, and VCC is set exactly when scaling happened."""
  exp_lim, ldexp_val = ('23', '64') if dt == 'f32' else ('52', '128')
  for old, new in [(f'S2.{dt} / S1.{dt} == DENORM.{dt}', f'divWouldBeDenorm(S2.{dt}, S1.{dt})'), (f"1.0 / 64'F(S1.{dt}) == DENORM.f64", '0'),
                   (f'1.0 / S1.{dt} == DENORM.{dt}', '0'), (f'S1.{dt} == DENORM.{dt}', f'isDENORM(S1.{dt})'),
                   (f'D0.{dt} = NAN.{dt}', f'VCC = 0x1LL;\nD0.{dt} = NAN.{dt}'),
                   (f'elsif isDENORM(S1.{dt}) then\nD0.{dt} = ldexp(S0.{dt}, {ldexp_val})', f'elsif 1 == 0 then\nD0.{dt} = S0.{dt}'),
                    (f'elsif exponent(S2.{dt}) <= {exp_lim} then\n// Numerator is tiny\n'
                     f'D0.{dt} = ldexp(S0.{dt}, {ldexp_val})',
                     f'elsif exponent(S2.{dt}) <= {exp_lim} then\nVCC = 0x1LL;\n'
                     f'D0.{dt} = ldexp(S0.{dt}, {ldexp_val})'),
                    (f'elsif divWouldBeDenorm(S2.{dt}, S1.{dt}) then\nVCC = 0x1LL;\n'
                     f'if S0.{dt} == S2.{dt} then\n// Only scale the numerator\n'
                     f'D0.{dt} = ldexp(S0.{dt}, {ldexp_val})\nendif',
                     f'elsif divWouldBeDenorm(S2.{dt}, S1.{dt}) then\n'
                     f'VCC = 0x1LL;\nD0.{dt} = S0.{dt}'),
                    (f'D0.{dt} = ldexp(S0.{dt}, {ldexp_val})\nendif\nelsif',
                     f'D0.{dt} = ldexp(S0.{dt}, {ldexp_val})\nelse\n'
                     f'D0.{dt} = S0.{dt}\nendif\nelsif')]:
    pcode = pcode.replace(old, new)
  lines = pcode.rstrip().split('\n')
  for i in range(len(lines) - 1, -1, -1):
    if lines[i].strip() == 'endif':
      lines.insert(i, f'else\nD0.{dt} = S0.{dt}')
      break
  pcode = '\n'.join(lines) + f';\nif isDENORM(S1.{dt}) then\nD0.{dt} = NAN.{dt}\nendif'
  return pcode.replace('VCC = 0x0LL', 'VCC.u64[laneId] = 0').replace('VCC = 0x1LL', 'VCC.u64[laneId] = 1')

def _write_64bit(val: UOp, wfn, reg_or_addr, is_mem: bool, *args) -> list[UOp]:
  """Write a 64-bit value as two 32-bit writes. args passed to wfn after reg/addr and lo/hi value."""
  lo, hi = _split64(val)
  incr = 4 if is_mem else 1  # 4 bytes for memory addresses, 1 for register indices
  return [wfn(reg_or_addr, lo, *args), wfn(reg_or_addr + (_c(incr, reg_or_addr.dtype) if isinstance(reg_or_addr, UOp) else incr), hi, *args)]

def _write_val(bits: int, val: UOp, wfn, reg_or_addr, *args, is_mem: bool = False) -> list[UOp]:
  """Write value, splitting 64-bit if needed. bits=64 for 64-bit writes, otherwise 32-bit."""
  return _write_64bit(val, wfn, reg_or_addr, is_mem, *args) if bits == 64 else [wfn(reg_or_addr, _to_u32(val), *args)]

def _mem_store_bytes(mem: UOp, addr: UOp, val: UOp, active: UOp, data_bits: int = 32) -> list[UOp]:
  """Store to byte-addressable memory. addr is byte offset, mem is uint8 buffer."""
  stores = []
  val_u32 = val.cast(dtypes.uint32)
  for i in range(data_bits // 8):
    byte_val = (val_u32 >> _c(i * 8)) & _c(0xFF)
    stores.append(mem.index((addr + _c(i, dtypes.uint64)).valid(active)).store(byte_val.cast(dtypes.uint8)))
  return stores

def _collect_data_slices(assigns: list[tuple[str, UOp]], data_prefix: str, pcode_vars: dict | None = None, op_name: str = "") -> dict[int, UOp]:
  """Collect bit slices from assigns into {dword_idx: value} dict."""
  slices = {}
  for dest, val in assigns:
    if dest.startswith(f'{data_prefix}['):
      if (m := re.match(rf'{data_prefix}\[(\d+)\s*:\s*(\d+)\]', dest)):
        hi_bit, low_bit = int(m.group(1)), int(m.group(2))
        dword_idx = low_bit // 32
        # D16 loads preserve bits - use final value from pcode_vars which has hi bits preserved
        if pcode_vars and 'D16' in op_name and dword_idx == 0 and hi_bit < 32:
          slices[0] = _to_u32(pcode_vars.get(data_prefix, val))
        else: slices[dword_idx] = _to_u32(val)
    elif dest.startswith(data_prefix): slices[0] = _to_u32(val)
  return slices

# ═══════════════════════════════════════════════════════════════════════════════
# INSTRUCTION COMPILER - converts decoded instruction to UOp SINK
# ═══════════════════════════════════════════════════════════════════════════════

def _int_clamp(op_name: str, srcs: dict) -> UOp | None:
  """Integer clamp for V_*ADD/SUB/MAD* ops: compute in wide arithmetic and saturate to the narrow range. None if not applicable.
  NOTE: MUL_LO ops don't saturate - they always return the low bits."""
  s0, s1, s2 = srcs.get('S0'), srcs.get('S1'), srcs.get('S2')
  if not isinstance(s0, UOp) or not isinstance(s1, UOp): return None
  is_signed, is_16bit = '_I' in op_name and '_U' not in op_name, '16' in op_name
  if any(p in op_name for p in ('_NC_U', '_MAD_U', '_NC_I', '_MAD_I')):
    op_bits = 16 if '16' in op_name else (24 if '24' in op_name else 32)
    # D0 range: 16 for the *_U16/*_I16 result-narrow ops, else 32 (mad*32* D0 is u32/i32; mul operands have op-fmt width)
    narrow_dt = dtypes.uint16 if is_16bit and '32' not in op_name else (dtypes.int32 if is_signed else dtypes.uint32)
    wide_dt = dtypes.int64
    narrow_max, narrow_min = ((0xFFFF, 0) if narrow_dt == dtypes.uint16 else ((0x7FFFFFFF, -0x80000000) if is_signed else (0xFFFFFFFF, 0)))
    def to_mulin(x: UOp) -> UOp:  # mul-source: extract the op-fmt-width suboperand with sext for signed
      mask = (1 << op_bits) - 1
      if op_bits == 32: return x.bitcast(narrow_dt) if x.dtype.itemsize == 4 else x.cast(narrow_dt)
      m = (x & _c(mask)).cast(dtypes.int)
      if not is_signed: return m.cast(wide_dt)
      sign = (m >> _c(op_bits - 1)) & _c(1)
      return sign.ne(_c(0)).where(m - _c(1 << op_bits), m).cast(wide_dt)
    def to_wide(x: UOp) -> UOp: return (x.bitcast(narrow_dt) if x.dtype.itemsize == narrow_dt.itemsize else x.cast(narrow_dt)).cast(wide_dt)
    if isinstance(s2, UOp) and 'MAD' in op_name: full = to_mulin(s0) * to_mulin(s1) + to_wide(s2)
    elif 'SUBREV' in op_name: full = to_wide(s1) - to_wide(s0)
    elif 'SUB' in op_name: full = to_wide(s0) - to_wide(s1)
    else: full = to_wide(s0) + to_wide(s1)
    return full.clamp(narrow_min, narrow_max).cast(narrow_dt)
  # V_SUB_U32 / V_ADD_U32 with clamp: unsigned saturate (SUB underflow->0, ADD overflow->0xFFFFFFFF)
  if any(p in op_name for p in ('_SUB_U32', '_ADD_U32', '_SUB_U16', '_ADD_U16')):
    a, b = (s1.cast(dtypes.uint32), s0.cast(dtypes.uint32)) if 'SUBREV' in op_name else (s0.cast(dtypes.uint32), s1.cast(dtypes.uint32))
    if 'SUB' in op_name: return (a < b).where(_c(0), a - b)  # underflow -> 0
    return (a + b < a).where(_c(0xFFFFFFFF), a + b)  # overflow -> MAX
  return None

class _Ctx:
  """Context for instruction compilation - holds buffers and helpers."""
  __slots__ = ('dyn_fields', '_axis_id', 'wave_size', 'vgpr', 'accvgpr', 'branch_cond', 'sgpr_reads', 'dpp_keep')
  sgpr = UOp.param(0, dtypes.uint32, SGPR_COUNT, name="sgpr")
  vmem = UOp.param(2, dtypes.uint32, 1 << 46, name="vmem")
  lds = UOp.param(3, dtypes.uint32, 16384, name="lds")
  scratch = UOp.param(4, dtypes.uint8, 1 << 30, name="scratch")
  scratch_stride = UOp.param(9, dtypes.uint32, name="scratch_stride", addrspace=AddrSpace.ALU)

  def __init__(self, wave_size: int = 32):
    self._axis_id, self.wave_size, self.dpp_keep = 0, wave_size, None
    self.dyn_fields: list[tuple[int, int]] = []  # (lo, hi) of fields read dynamically
    self.vgpr = UOp.param(1, dtypes.uint32, 256 * wave_size, name="vgpr")
    self.accvgpr = UOp.param(5, dtypes.uint32, 256 * wave_size, name="accvgpr") if wave_size == 64 else self.vgpr
    self.branch_cond: UOp | None = None
    self.sgpr_reads: dict[UOp, UOp] = {}

  def range(self, n: int | None = None) -> UOp:
    """Create a lane range UOp with unique axis ID."""
    if n is None: n = self.wave_size
    self._axis_id += 1
    return UOp.range(n, self._axis_id, AxisType.LOOP, dtype=dtypes.int)

  def unroll_lanes(self, get_lane_bit, exec_mask: UOp, apply_exec: bool = True) -> UOp:
    """Combine lane bits into a mask using RANGE+REDUCE (32-bit for RDNA, 64-bit for CDNA)."""
    lane = self.range()
    dtype = dtypes.uint32 if self.wave_size <= 32 else dtypes.uint64
    bit = get_lane_bit(lane).cast(dtype) << lane.cast(dtype)
    result = bit.reduce(lane, arg=Ops.ADD)
    return result & exec_mask if apply_exec else result

  @staticmethod
  def inst_word(dword_idx: int) -> UOp: return UOp.param(-2-dword_idx, dtypes.uint32, name=f"inst_w{dword_idx}", addrspace=AddrSpace.ALU)

  def inst_field(self, field) -> UOp:
    """Extract field bits from instruction encoding. Tracks field for canonical key computation."""
    lo, hi = field.lo, field.hi
    self.dyn_fields.append((lo, hi))
    dword_idx = lo // 32
    lo_in_dword = lo % 32
    hi_in_dword = hi % 32
    word = self.inst_word(dword_idx)
    if lo // 32 == hi // 32:  # Same dword
      mask = (1 << (hi - lo + 1)) - 1
      shifted = word if lo_in_dword == 0 else word >> _c(lo_in_dword)
      return shifted & _c(mask)
    else:  # Spans two dwords
      lo_bits = 32 - lo_in_dword
      lo_mask = (1 << lo_bits) - 1
      hi_mask = (1 << (hi_in_dword + 1)) - 1
      lo_part = (word >> _c(lo_in_dword)) & _c(lo_mask)
      hi_part = self.inst_word(dword_idx + 1) & _c(hi_mask)
      return lo_part | (hi_part << _c(lo_bits))

  def optional_field(self, inst: Inst, name: str) -> UOp | None:
    """Extract a field that only exists on some instruction formats (e.g. 'literal', 'saddr'). None if absent."""
    return self.inst_field(getattr(type(inst), name)) if hasattr(type(inst), name) else None

  def inst_field_signed(self, field) -> UOp:
    """Extract field and sign-extend based on field width."""
    val = self.inst_field(field)
    width = field.hi - field.lo + 1
    sign_bit = 1 << (width - 1)
    return (val.cast(dtypes.int) ^ _c(sign_bit, dtypes.int)) - _c(sign_bit, dtypes.int)

  def canonical_mask(self, inst_bytes: bytes|memoryview) -> tuple[int, int]:
    """Compute canonical (base, mask) for cache lookup.
    base = instruction bits with dynamic fields zeroed
    mask = bitmask with 1s for static bits, 0s for dynamic bits"""
    base = int.from_bytes(inst_bytes, 'little')
    mask = (1 << (len(inst_bytes) * 8)) - 1  # all 1s initially
    for lo, hi in self.dyn_fields:
      field_mask = ((1 << (hi - lo + 1)) - 1) << lo
      base &= ~field_mask  # zero dynamic bits in base
      mask &= ~field_mask  # zero dynamic bits in mask
    return base, mask

  def rexec(self) -> UOp:
    """Read full EXEC mask (32-bit for RDNA, 64-bit for CDNA)."""
    return self.rmask(_c(EXEC_LO.offset))

  # Dynamic register access (takes UOp index instead of int)
  def rsgpr_dyn(self, reg: UOp, valid: UOp | None = None) -> UOp:
    index = reg.valid(valid) if valid is not None else reg
    if index not in self.sgpr_reads: self.sgpr_reads[index] = UOp.param(SGPR_COUNT+len(self.sgpr_reads), dtypes.uint32, addrspace=AddrSpace.ALU)
    return self.sgpr_reads[index]

  def wsgpr_dyn(self, reg: UOp, val: UOp) -> UOp:
    """Write SGPR with dynamic register index. On RDNA, index 124 = NULL (writes discarded). On CDNA, index 124 = M0 (read/write)."""
    # RDNA: NULL (124) discards writes. CDNA: M0 (124) is writable.
    return self.sgpr.index(reg if self.wave_size == 64 else reg.valid(reg.ne(_c(124)))).store(val.cast(dtypes.uint32))

  def wmask(self, reg: UOp, val: UOp) -> list[UOp]:
    """Write a lane mask (VCC/EXEC). Splits into lo/hi for wave64."""
    if self.wave_size > 32:
      lo, hi = _split64(val)
      return [self.wsgpr_dyn(reg, lo), self.wsgpr_dyn(reg + _c(1), hi)]
    return [self.wsgpr_dyn(reg, val)]

  def wmask_lane_bit(self, reg: UOp, lane: UOp, val: UOp, exec_mask: UOp) -> list[UOp]:
    """Set/clear bit `lane` of the mask at `reg` from val for exec-active lanes, preserving memory for inactive lanes"""
    active, bit, mask32 = _lane_active(exec_mask, lane), _to_u32(val), _c(0xFFFFFFFF)
    if self.wave_size <= 32:
      old = self.rsgpr_dyn(reg)
      mask = _c(1) << lane.cast(dtypes.uint32)
      return [self.wsgpr_dyn(reg, active.where((old & (mask ^ mask32)) | (bit << lane.cast(dtypes.uint32)), old))]
    off = (lane & _c(31, dtypes.int)).cast(dtypes.uint32)
    mask = _c(1) << off
    def half(old: UOp, sel: UOp) -> UOp: return sel.where(active.where((old & (mask ^ mask32)) | (bit << off), old), old)
    return [self.wsgpr_dyn(reg, half(self.rsgpr_dyn(reg), lane < _c(32, dtypes.int))),
            self.wsgpr_dyn(reg + _c(1), half(self.rsgpr_dyn(reg + _c(1)), _c(32, dtypes.int) <= lane))]

  def rmask(self, reg: UOp) -> UOp:
    """Read a lane mask (VCC/EXEC). Combines lo/hi for wave64."""
    if self.wave_size > 32: return _u64(self.rsgpr_dyn(reg), self.rsgpr_dyn(reg + _c(1)))
    return self.rsgpr_dyn(reg)

  def rvgpr_dyn(self, reg: UOp, lane: UOp, valid: UOp | None = None) -> UOp:
    """Read VGPR with dynamic register index."""
    idx = reg.cast(dtypes.int) * _c(self.wave_size, dtypes.int) + lane.cast(dtypes.int)
    return self.vgpr.index(idx.valid(valid)).load() if valid is not None else self.vgpr.index(idx).load()

  def wvgpr_dyn(self, reg: UOp, lane: UOp, val: UOp, exec_mask: UOp, after: UOp | None = None) -> UOp:
    """Write VGPR with dynamic register index."""
    buf = self.vgpr.after(after) if after is not None else self.vgpr
    offset = reg.cast(dtypes.int) * _c(self.wave_size, dtypes.int) + lane.cast(dtypes.int)
    return buf.index(offset.valid(_lane_active(exec_mask, lane))).store(val.cast(dtypes.uint32))

  def raccvgpr_dyn(self, reg: UOp, lane: UOp, valid: UOp | None = None) -> UOp:
    """Read ACCVGPR with dynamic register index (CDNA only)."""
    idx = reg.cast(dtypes.int) * _c(self.wave_size, dtypes.int) + lane.cast(dtypes.int)
    return self.accvgpr.index(idx.valid(valid)).load() if valid is not None else self.accvgpr.index(idx).load()

  def waccvgpr_dyn(self, reg: UOp, lane: UOp, val: UOp, exec_mask: UOp) -> UOp:
    """Write ACCVGPR with dynamic register index (CDNA only)."""
    offset = reg.cast(dtypes.int) * _c(self.wave_size, dtypes.int) + lane.cast(dtypes.int)
    return self.accvgpr.index(offset.valid(_lane_active(exec_mask, lane))).store(val.cast(dtypes.uint32))

  def rsrc_dyn(self, off: UOp, lane: UOp | None, bits: int = 32, literal: UOp | None = None, is_f64: bool = False, do_cast: bool = True) -> UOp:
    """Read source operand with dynamic offset. Handles SGPR/inline constants (<256), VGPR (>=256).
    If lane is None, only scalar access is supported (off must be < 256).
    is_f64: True for F64 operations where 64-bit literals go in high 32 bits."""
    is_float_const = (off >= _c(240)) & (off <= _c(248))
    is_vgpr = off >= _c(256)
    is_sgpr = is_vgpr.ne(True)
    sgpr_lo = self.rsgpr_dyn(off, is_sgpr)

    if lane is not None:
      vgpr_reg = off - _c(256)
      vgpr_lo = self.rvgpr_dyn(vgpr_reg, lane, is_vgpr)
      vgpr_val = _u64(vgpr_lo, self.rvgpr_dyn(vgpr_reg + _c(1), lane, is_vgpr)) if bits == 64 else vgpr_lo

    if bits == 64:
      sgpr_hi = self.rsgpr_dyn(off + _c(1), is_sgpr)
      sgpr_val = _u64(sgpr_lo, sgpr_hi)
      # Integer inline constants: sign-extend 32-bit value from buffer to 64-bit
      # Float constants: cast F32 to F64
      int_inline = sgpr_lo.cast(dtypes.int32).cast(dtypes.int64)
      float_inline = sgpr_lo.bitcast(dtypes.float32).cast(dtypes.float64)
      # compute inline
      inline = is_float_const.where(float_inline.bitcast(dtypes.uint64), int_inline.bitcast(dtypes.uint64))
      # Literal handling: F64 VOP puts literal in high 32 bits; B64/I64/U64 VOP and SOP zero-extend
      if literal is not None:
        lit_val = literal.cast(dtypes.uint64) << _c(32, dtypes.uint64) if is_f64 else literal.cast(dtypes.uint64)
        inline = off.eq(_c(255)).where(lit_val, inline)
      scalar_val = (off < _c(128)).where(sgpr_val, inline)
    else:
      scalar_val = sgpr_lo
      if literal is not None: scalar_val = off.eq(_c(255)).where(literal, scalar_val)
      if bits == 16 and do_cast:  # Float constants: cast F32 to F16
        scalar_val = is_float_const.where(scalar_val.bitcast(dtypes.float32).cast(dtypes.half).bitcast(dtypes.uint16).cast(dtypes.uint32), scalar_val)

    return is_vgpr.where(vgpr_val, scalar_val) if lane is not None else scalar_val

  def scalar_stores(self, assigns: list[tuple[str, UOp]], sdst_reg: UOp, sdst_size: int = 1) -> list[UOp]:
    """Generate stores for scalar assigns with dynamic destination register (D0, SCC, EXEC, VCC)."""
    stores: list[UOp] = []
    for dest, val in assigns:
      if dest.startswith('D0'):
        if sdst_size == 2:
          lo, hi = _split64(val)
          stores.extend([self.wsgpr_dyn(sdst_reg, lo), self.wsgpr_dyn(sdst_reg + _c(1), hi)])
        else: stores.append(self.wsgpr_dyn(sdst_reg, _val_to_u32(val)))
      elif dest.startswith('SCC'): stores.append(self.wsgpr_dyn(_c(SCC.offset), _to_u32(val)))
      elif dest.startswith('EXEC'):
        if self.wave_size > 32 and val.dtype in (dtypes.uint64, dtypes.int64):
          lo, hi = _split64(val)
          stores.extend([self.wsgpr_dyn(_c(EXEC_LO.offset), lo), self.wsgpr_dyn(_c(EXEC_LO.offset + 1), hi)])
        else: stores.append(self.wsgpr_dyn(_c(EXEC_LO.offset), _to_u32(val)))
      elif dest.startswith('VCC'): stores.extend(self.wmask(_c(VCC_LO.offset), val))
      elif dest.startswith('PC'): raise NotImplementedError("AMD lifter does not support direct PC writes")
    return stores

  def compile_sop_pcode(self, op, srcs: dict[str, UOp | int], sdst_reg: UOp, sdst_size: int) -> UOp:
    """Compile a scalar instruction with dynamic destination register."""
    pcode = get_pcode(op)
    srcs.update(self.base_srcs(self.rexec()), VCC=self.rmask(_c(VCC_LO.offset)))
    if 'D0' not in srcs: srcs['D0'] = self.rsgpr_dyn(sdst_reg)  # D0 is current dest value for read-modify-write ops
    _, assigns = parse_pcode(pcode, srcs)
    return UOp.sink(*self.scalar_stores(assigns, sdst_reg, sdst_size))

  def compile_lane_pcode(self, op, inst) -> UOp:
    """Compile cross-lane ops (READLANE/WRITELANE/PERMLANE) using pcode parser."""
    pcode = get_pcode(op)
    op_name = op.name
    src0_off, vdst_off = self.inst_field(type(inst).src0), self.inst_field(type(inst).vdst)
    src0_reg = (src0_off >= _c(256)).where(src0_off - _c(256), _c(0))  # VGPR index or 0
    src1_off, src2_off = self.optional_field(inst, 'src1'), self.optional_field(inst, 'src2')
    src1_reg = (src1_off >= _c(256)).where(src1_off - _c(256), src1_off) if src1_off is not None else _c(0)
    src2_reg = (src2_off >= _c(256)).where(src2_off - _c(256), src2_off) if src2_off is not None else _c(0)
    exec_val = self.rexec()
    exec_lo = exec_val.cast(dtypes.uint32)
    srcs = {
      'SRC0': src0_reg, 'VDST': vdst_off, 'EXEC_LO': exec_lo, 'EXEC': exec_val.cast(dtypes.uint64),
      '_vgpr': self.vgpr, '_wave_size': self.wave_size, 'SRC1': src1_reg, 'SRC2': src2_reg,
      'S0': self.rsrc_dyn(src0_off, _c(0, dtypes.int)) if 'WRITELANE' in op_name else src0_reg,
      'S1': self.rsrc_dyn(src1_off, _c(0, dtypes.int)) if src1_off is not None else _c(0),
      'S2': self.rsrc_dyn(src2_off, _c(0, dtypes.int)) if src2_off is not None else _c(0),
    }
    _, assigns = parse_pcode(pcode, srcs)
    stores = []
    for dest, val in assigns:
      if dest.startswith('D0'): stores.append(self.wsgpr_dyn(vdst_off, val.cast(dtypes.uint32)))
      elif dest.startswith('VGPR['): stores.append(self.vgpr.index(val[0]).store(val[1].cast(dtypes.uint32)))
    return UOp.sink(*stores)

  def base_srcs(self, exec_mask: UOp, lane: UOp | None = None) -> dict[str, UOp | int]:
    """Pcode environment entries shared by all instructions: EXEC/SCC, rounding mode (emulator always rounds-nearest-even),
    and CDNA SDWA byte/word select defaults (E32 encodings always use BYTE0/WORD0)."""
    srcs: dict[str, UOp | int] = {'EXEC': exec_mask, 'SCC': self.rsgpr_dyn(_c(SCC.offset)), '_vgpr': self.vgpr, '_wave_size': self.wave_size,
                                  'ROUND_MODE': _c(0), 'ROUND_TOWARD_ZERO': _c(0), 'ROUND_NEAREST_EVEN': _c(0),
                                  'SDWA_SRC0_SEL': _c(0), 'BYTE0': _c(0), 'BYTE1': _c(1), 'BYTE2': _c(2), 'BYTE3': _c(3),
                                  'WORD0': _c(0), 'WORD1': _c(1)}
    if lane is not None: srcs['laneId'] = lane
    return srcs

  def compile_vop_pcode(self, op, srcs: dict[str, UOp | int], lane: UOp, vdst_reg: UOp, exec_mask: UOp,
                        opsel_dst_hi: bool | UOp = False, sdst_reg: int | None = None, clmp: int = 0,
                        src0_off: UOp | None = None, omod: int = 0) -> UOp:
    """Compile VOP instruction to a sink of stores."""
    keep, self.dpp_keep = self.dpp_keep, None  # lanes a dpp control leaves unwritten
    pcode = get_pcode(op)
    vcc_reg = sdst_reg if sdst_reg is not None else VCC_LO.offset
    if 'VCC' not in srcs: srcs['VCC'] = self.rmask(_c(vcc_reg))
    srcs.update(self.base_srcs(exec_mask, lane), VDST=vdst_reg, MAX_FLOAT_F32=_c(3.4028234663852886e38, dtypes.float32))
    # f32 min/max/median ops flush denormal inputs to signed zero (select-style ops: results propagate inputs bitwise)
    # (RDNA4 calls them _NUM_: V_MIN_NUM_F32 etc.)
    if not _hw_float() and any(p in op.name for p in ('MIN_F32', 'MAX_F32', 'MIN3_F32', 'MAX3_F32', 'MED3_F32', 'MIN_NUM_F32', 'MAX_NUM_F32')):
      srcs = {k: _ftz_f32(v) if k in ('S0', 'S1', 'S2') and isinstance(v, UOp) else v for k, v in srcs.items()}
    _, assigns = parse_pcode(pcode, srcs)

    # For integer ops with clamp, pre-compute the saturated result; floats clamp to [0,1] at write time
    int_saturate = _int_clamp(op.name, srcs) if clmp else None

    lane_stores, scalar_stores, slice_stores = [], [], []
    vcc_val, exec_val = None, None
    for dest, val in assigns:
      # VGPR bit-slice assignment: VGPR[lane][reg][hi:lo] -> read-modify-write with optional condition
      if dest.startswith('VGPR[') and re.search(r'\[\d+:\d+\]', dest):
        hi_bit, lo_bit = int(val[2]), int(val[3])
        new_val = _set_bits(self.vgpr.index(val[0]).load(), _val_to_bits(val[1]), hi_bit - lo_bit + 1, lo_bit).cast(dtypes.uint32)
        active = _lane_active(exec_mask, lane) & _to_bool(val[4]) if len(val) > 4 else _lane_active(exec_mask, lane)
        if keep is not None: active = active & ~keep
        lane_stores.append(self.vgpr.index(val[0].valid(active)).store(new_val))
      elif 'D0' in dest and '[laneId]' in dest: continue  # per-lane mask bits are written via VCC/EXEC assigns instead
      elif dest.startswith('D0'):
        if (dest_suffix := re.match(r'D0\.(\w+)', dest)) is not None:
          target_dt = {'u16': dtypes.uint16, 'i16': dtypes.int16, 'f16': dtypes.half}.get(dest_suffix.group(1))
          if target_dt is not None: val = val.cast(target_dt)
        if (slice_match := re.match(r'D0\[(\d+)\s*:\s*(\d+)\]', dest)) and (int(slice_match.group(1)), int(slice_match.group(2))) != (31, 0):
          if clmp and _hw_float() and val.dtype == dtypes.half: val = _clamp01(val)
          slice_stores.append((int(slice_match.group(2)), int(slice_match.group(1)) - int(slice_match.group(2)) + 1, _val_to_bits(val)))
          continue
        if (omod or clmp) and 'DIV_SCALE' in op.name and val.dtype in (dtypes.uint32, dtypes.uint64) and _hw_float():  # bits -> float for the mods
          val = val.bitcast(dtypes.float32 if val.dtype == dtypes.uint32 else dtypes.float64)
        if omod and val.dtype in (dtypes.float32, dtypes.half, dtypes.float64):  # output modifier: *2, *4 or /2, before the clamp
          if _hw_float() and (tiny := _tiny_before_rounding(op.name, srcs, val)) is not None: val = tiny.where(_c(0.0, val.dtype), val)
          val = _omod(val, omod)
        if int_saturate is not None: val = int_saturate
        elif clmp and _hw_float() and val.dtype == dtypes.uint32 and op.name.startswith('V_PK_') and op.name.endswith('_F16'):
          val = _clamp01(_h16(val & _c(0xFFFF))).bitcast(dtypes.uint16).cast(dtypes.uint32) | \
                (_clamp01(_h16(val >> _c(16))).bitcast(dtypes.uint16).cast(dtypes.uint32) << _c(16))
        elif clmp and val.dtype in (dtypes.float32, dtypes.half, dtypes.float64):
          # hardware clamp: -0 becomes +0 and NaN becomes 0 (hardware verified)
          val = (val > _c(0.0, val.dtype)).where(val.minimum(_c(1.0, val.dtype)), _c(0.0, val.dtype))
        if val.dtype in (dtypes.uint64, dtypes.int64, dtypes.float64):
          lo, hi = _split64(val)
          if keep is not None: lo, hi = keep.where(self.rvgpr_dyn(vdst_reg, lane), lo), keep.where(self.rvgpr_dyn(vdst_reg + _c(1), lane), hi)
          lane_stores.extend([self.wvgpr_dyn(vdst_reg, lane, lo, exec_mask), self.wvgpr_dyn(vdst_reg + _c(1), lane, hi, exec_mask)])
        elif val.dtype in (dtypes.half, dtypes.uint16, dtypes.int16):
          result, old_val = _val_to_u32(val), self.rvgpr_dyn(vdst_reg, lane)
          hi_result = (old_val & _c(0xFFFF)) | (result << _c(16, dtypes.uint32))
          # GFX9/CDNA zeroes upper 16 bits on lo-half write; RDNA preserves them
          lo_result = (result & _c(0xFFFF)) if self.wave_size == 64 else (old_val & _c(0xFFFF0000)) | (result & _c(0xFFFF))
          result = opsel_dst_hi.where(hi_result, lo_result) if isinstance(opsel_dst_hi, UOp) else hi_result if opsel_dst_hi else lo_result
          if keep is not None: result = keep.where(old_val, result)
          lane_stores.append(self.wvgpr_dyn(vdst_reg, lane, result, exec_mask))
        else:
          v32 = _val_to_u32(val)
          if keep is not None: v32 = keep.where(self.rvgpr_dyn(vdst_reg, lane), v32)
          lane_stores.append(self.wvgpr_dyn(vdst_reg, lane, v32, exec_mask))
      elif dest.startswith('S0') and src0_off is not None:
        # Write back to src0 VGPR (e.g. v_swap_b32). src0_off is raw encoding (256+ = VGPR)
        lane_stores.append(self.wvgpr_dyn(src0_off - _c(256), lane, _val_to_u32(val), exec_mask))
      elif dest.startswith('VCC'): vcc_val = val
      elif dest.startswith('EXEC'): exec_val = val
      elif dest.startswith('SCC'): scalar_stores.append(self.wsgpr_dyn(_c(SCC.offset), _to_u32(val)))

    # VCC/EXEC mask writes must be computed BEFORE VGPR stores to avoid reading modified VGPRs.
    # When vdst overlaps with src operands (e.g. v_add_co_u32 v[0], vcc, s[8], v[0]), the carry
    # computation reads the original source values only if its range loop runs before the VGPR write loop.
    stores: list[UOp] = []
    for mask_val, reg in [(vcc_val, vcc_reg), (exec_val, EXEC_LO.offset)]:
      if mask_val is None: continue
      # hardware zeroes the inactive lane bits of per-lane VCC writes (VCC = mask & EXEC), it never preserves them
      stores.extend(self.wmask(_c(reg), self.unroll_lanes(lambda l, v=mask_val: (_to_u32(v.substitute({lane: l})) & _c(1)).cast(dtypes.uint32),
                                                          exec_mask, apply_exec=reg != EXEC_LO.offset)))
    if slice_stores:  # merge D0[hi:lo] slices into one read-modify-write of the destination VGPR
      result = old = self.rvgpr_dyn(vdst_reg, lane)
      for lo_bit, width, val_bits in slice_stores: result = _set_bits(result, val_bits, width, lo_bit)
      lane_stores.append(self.wvgpr_dyn(vdst_reg, lane, result if keep is None else keep.where(old, result), exec_mask))
    if lane_stores: stores.append(UOp.sink(*lane_stores).end(lane))
    stores.extend(scalar_stores)
    return UOp.sink(*stores)

# ═══════════════════════════════════════════════════════════════════════════════
# INSTRUCTION HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

HW_FLOAT = ContextVar("HW_FLOAT", 1)
_lift_arch = [""]
def _hw_float() -> bool: return bool(HW_FLOAT.value) and _lift_arch[0] == "rdna4"
_HW_TABLE_BASE = 0x200000000000  # a fixed address, so a lifted program reads the tables wherever it was lifted
@functools.cache
def _hw_tables() -> dict[str, int]:
  import mmap, numpy as np
  here = os.path.dirname(os.path.abspath(__file__))
  arrays = {k: np.ascontiguousarray(t[k]).view(np.uint8).reshape(-1) for f in ("gfx1200_rounding.npz", "gfx1200_sincos.npz", "gfx1200_f64core.npz")
            for t in [np.load(os.path.join(here, f))] for k in t.files}
  sizes = {k: (a.nbytes + 0xFFFF) & ~0xFFFF for k, a in arrays.items()}
  libc = ctypes.CDLL(None)
  libc.mmap.restype, libc.mmap.argtypes = ctypes.c_void_p, [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_long]
  ptr = libc.mmap(_HW_TABLE_BASE, sum(sizes.values()), mmap.PROT_READ | mmap.PROT_WRITE, mmap.MAP_PRIVATE | mmap.MAP_ANON, -1, 0)
  if ptr != _HW_TABLE_BASE: raise RuntimeError(f"could not map the rdna4 rounding tables at 0x{_HW_TABLE_BASE:x}")
  offs, off = {}, 0
  for k, a in arrays.items():
    ctypes.memmove(ptr + off, a.ctypes.data, a.nbytes)
    offs[k], off = _HW_TABLE_BASE + off, off + sizes[k]
  return offs

@functools.cache
def _hw_table_len(name:str) -> int:
  import numpy as np
  here = os.path.dirname(os.path.abspath(__file__))
  for f in ("gfx1200_rounding.npz", "gfx1200_sincos.npz", "gfx1200_f64core.npz"):
    t = np.load(os.path.join(here, f))
    if name in t.files: return t[name].nbytes
  raise KeyError(name)
def _tab_bits(name:str, byte_idx:UOp, nbytes:int) -> UOp:
  addr = _c(_hw_tables()[name], dtypes.uint64) + byte_idx.cast(dtypes.uint64)
  word = _Ctx.vmem.index((addr >> _c(2, dtypes.uint64)).cast(dtypes.int64)).load()
  return (word >> ((addr.cast(dtypes.uint32) & _c(3)) * _c(8))) & _c((1 << (8 * nbytes)) - 1)

def _with_ulp_delta(r:UOp, table:str, idx:UOp, use:UOp) -> UOp:
  delta = (_tab_bits(table, idx, 1).cast(dtypes.int32) << _c(24, dtypes.int32)) >> _c(24, dtypes.int32)
  return use.where((r.bitcast(dtypes.uint32).cast(dtypes.int32) + delta).cast(dtypes.uint32).bitcast(dtypes.float32), r)

def _uint_of(x:UOp): return {2: dtypes.uint16, 4: dtypes.uint32, 8: dtypes.uint64}[x.dtype.itemsize]
_FLOATS = (dtypes.half, dtypes.float32, dtypes.float64)
_QUIET = {dtypes.half: 0x200, dtypes.float32: 0x400000, dtypes.float64: 0x8000000000000}
_DEFAULT_NAN = {dtypes.half: 0xFE00, dtypes.float32: 0xFFC00000, dtypes.float64: 0xFFF8000000000000}
def _quiet_bits(x:UOp) -> UOp:  # NaN selection stays on the raw bits: a NaN float constant would lose its sign and payload
  ut = _uint_of(x)
  b = x.bitcast(ut)
  return x.ne(x).where(b | _c(_QUIET[x.dtype], ut), b)
def _quiet(x:UOp) -> UOp:
  if x.dtype not in _FLOATS: return x
  return _quiet_bits(x).bitcast(x.dtype)
def _amd_nan(result:UOp, operands:list[UOp]) -> UOp:
  if result.dtype not in _FLOATS: return result
  ut = _uint_of(result)
  out = _c(_DEFAULT_NAN[result.dtype], ut)
  for o in reversed(operands):
    o = o.cast(result.dtype) if o.dtype != result.dtype else o
    out = o.ne(o).where(_quiet_bits(o), out)
  return result.ne(result).where(out, result.bitcast(ut)).bitcast(result.dtype)
def _flush_denorm(x:UOp) -> UOp:  # signed zero for a denormal f32
  b = x.bitcast(dtypes.uint32)
  return ((b & _c(0x7F800000)).eq(_c(0)) & (b & _c(0x7FFFFF)).ne(_c(0))).where((b & _c(0x80000000)).bitcast(dtypes.float32), x)

def _hw_rcp(a:UOp) -> UOp:
  if not _hw_float(): return _c(1.0, dtypes.float32) / a
  a = _flush_denorm(a)  # rcp, sqrt and exp ignore the denormal mode: denormal inputs and results are signed zero
  r = _c(1.0, dtypes.float32) / a
  bits = a.bitcast(dtypes.uint32)
  e = (bits >> _c(23)) & _c(0xFF)
  r = _with_ulp_delta(r, "rcp_f32", bits & _c(0x7FFFFF), (e >= _c(1)) & (e <= _c(252)))  # the hardware result is normal there
  return _amd_nan(_flush_denorm(r), [a])

def _hw_sqrt(a:UOp) -> UOp:
  if not _hw_float(): return UOp(Ops.SQRT, src=(a,))
  a = _flush_denorm(a)
  r = UOp(Ops.SQRT, src=(a,))
  bits = a.bitcast(dtypes.uint32)
  e = (bits >> _c(23)) & _c(0xFF)
  use = (bits < _c(0x80000000)) & (e >= _c(1)) & (e <= _c(254))
  return _amd_nan(_with_ulp_delta(r, "sqrt_f32", ((e & _c(1)) << _c(23)) | (bits & _c(0x7FFFFF)), use), [a])

def _f16_table(name:str, a:UOp) -> UOp:
  return _tab_bits(name, a.bitcast(dtypes.uint16).cast(dtypes.uint32) * _c(2), 2).cast(dtypes.uint16).bitcast(dtypes.half)
def _hw_exp16(a:UOp) -> UOp: return _f16_table("exp_f16", a) if _hw_float() else UOp(Ops.EXP2, src=(a,))
def _hw_rsq16(a:UOp) -> UOp: return _f16_table("rsq_f16", a) if _hw_float() else _c(1.0, dtypes.half) / UOp(Ops.SQRT, src=(a,))
def _hw_rcp16(a:UOp) -> UOp: return _f16_table("rcp_f16", a) if _hw_float() else _c(1.0, dtypes.half) / a
def _hw_sqrt16(a:UOp) -> UOp: return _f16_table("sqrt_f16", a) if _hw_float() else UOp(Ops.SQRT, src=(a,))
def _hw_log16(a:UOp) -> UOp: return _f16_table("log_f16", a) if _hw_float() else UOp(Ops.LOG2, src=(a,))

def _tab_code2(name:str, idx:UOp) -> UOp:  # 2-bit delta codes, 4 per byte: 0, 1, 2 -> -1, 0, +1
  byte = _tab_bits(name, idx >> _c(2), 1)
  return ((byte >> ((idx & _c(3)) * _c(2))) & _c(3)).cast(dtypes.int32) - _c(1, dtypes.int32)

def _hw_exp32(a:UOp) -> UOp:
  r = UOp(Ops.EXP2, src=(a.cast(dtypes.float64),)).cast(dtypes.float32)
  if not _hw_float(): return UOp(Ops.EXP2, src=(a,))
  bits = a.bitcast(dtypes.uint32)
  sign, e, m = bits >> _c(31), (bits >> _c(23)) & _c(0xFF), bits & _c(0x7FFFFF)
  in_frac = (e >= _c(127)) & (e <= _c(133))
  jpos = (m << (e - _c(127)).maximum(_c(0)).minimum(_c(6))) & _c(0x7FFFFF)
  j = sign.eq(_c(1)).where((_c(0x800000) - jpos) & _c(0x7FFFFF), jpos)
  d_frac = _tab_code2("exp_f32_frac", (sign << _c(23)) | j)
  in_small = (e >= _c(102)) & (e <= _c(126))
  d_small = _tab_code2("exp_f32_small", ((sign * _c(25) + (e - _c(102)).maximum(_c(0)).minimum(_c(24))) << _c(23)) | m)
  delta = in_frac.where(d_frac, in_small.where(d_small, _c(0, dtypes.int32)))
  rb = r.bitcast(dtypes.uint32)
  normal = ((rb >> _c(23)) & _c(0xFF)) >= _c(1)
  return _amd_nan(_flush_denorm(normal.where((rb.cast(dtypes.int32) + delta).cast(dtypes.uint32).bitcast(dtypes.float32), r)), [a])

def _hw_rsq32(a:UOp) -> UOp:
  if not _hw_float(): return _c(1.0, dtypes.float32) / UOp(Ops.SQRT, src=(a,))
  a = _flush_denorm(a)
  r = (_c(1.0, dtypes.float64) / UOp(Ops.SQRT, src=(a.cast(dtypes.float64),))).cast(dtypes.float32)
  bits = a.bitcast(dtypes.uint32)
  e = (bits >> _c(23)) & _c(0xFF)
  r = _with_ulp_delta(r, "rsq_f32", ((e & _c(1)) << _c(23)) | (bits & _c(0x7FFFFF)), (bits < _c(0x80000000)) & (e >= _c(1)) & (e <= _c(254)))
  return _amd_nan(r, [a])

def _tab_code2_raw(name:str, idx:UOp) -> UOp:  # 2-bit codes 0..3, 4 per byte
  byte = _tab_bits(name, idx >> _c(2), 1)
  return ((byte >> ((idx & _c(3)) * _c(2))) & _c(3)).cast(dtypes.int32)

def _hw_log32(a:UOp) -> UOp:
  if not _hw_float(): return UOp(Ops.LOG2, src=(a,))
  f64, i32 = dtypes.float64, dtypes.int32
  a = _flush_denorm(a)
  bits = a.bitcast(dtypes.uint32)
  e, m = (bits >> _c(23)) & _c(0xFF), bits & _c(0x7FFFFF)
  x = (_c(0x3FF0000000000000, dtypes.uint64) | (m.cast(dtypes.uint64) << _c(29, dtypes.uint64))).bitcast(f64)
  lg = UOp(Ops.LOG2, src=(x,))
  e2 = e.cast(i32) - _c(127, i32)
  n = (lg * _c(2.0 ** 24, f64) + _c(0.5, f64)).cast(i32) + _tab_code2_raw("log_f32_L", m) - _c(2, i32)
  s_ = e2.cast(f64) + n.cast(f64) * _c(2.0 ** -24, f64)  # exact
  r = s_.cast(dtypes.float32)
  rb = r.bitcast(dtypes.uint32)
  above = r.cast(f64) > s_  # one step toward -inf: down in magnitude for a positive result, up for a negative one
  rd = above.where((s_ < _c(0.0, f64)).where(rb + _c(1), rb - _c(1)), rb)
  def near(off:float, table:str):
    ref = (lg + _c(off, f64)).cast(dtypes.float32).bitcast(dtypes.uint32).cast(i32)
    return (ref + _tab_code2_raw(table, m) - _c(1, i32)).cast(dtypes.uint32)
  out = e2.eq(_c(0, i32)).where(near(0.0, "log_f32_e0"), e2.eq(_c(-1, i32)).where(near(-1.0, "log_f32_em1"), rd)).bitcast(dtypes.float32)
  normal = (e >= _c(1)) & (e <= _c(254))
  negative = (bits >= _c(0x80000000)) & (bits & _c(0x7FFFFFFF)).ne(_c(0))
  nan = _c(0x7FC00000).bitcast(dtypes.float32)
  return _amd_nan(negative.where(nan, normal.where(out, UOp(Ops.LOG2, src=(a,)))), [a])

def _hw_ldexp32(a:UOp, e:UOp) -> UOp:
  if a.dtype == dtypes.uint32: a = a.bitcast(dtypes.float32)
  k = e.cast(dtypes.int32).maximum(_c(-400, dtypes.int32)).minimum(_c(400, dtypes.int32))
  half = k // _c(2, dtypes.int32)
  def p2(x): return ((x + _c(1023, dtypes.int32)).cast(dtypes.uint64) << _c(52, dtypes.uint64)).bitcast(dtypes.float64)
  return _amd_nan((a.cast(dtypes.float64) * p2(half) * p2(k - half)).cast(dtypes.float32), [a])

def _invalid_product(a:UOp, b:UOp) -> UOp:
  ia, ib = a.abs().eq(_c(float("inf"), a.dtype)), b.abs().eq(_c(float("inf"), b.dtype))
  za, zb = a.eq(_c(0.0, a.dtype)), b.eq(_c(0.0, b.dtype))
  return (ia & zb) | (za & ib)

def _hw_fma_mix16(a:UOp, b:UOp, c:UOp) -> UOp:
  if not _hw_float(): return _pcode._fma(a, b, c).cast(dtypes.half)
  f64, u64 = dtypes.float64, dtypes.uint64
  p, cc = a.cast(f64) * b.cast(f64), c.cast(f64)  # an f32 product is exact in f64
  s_ = p + cc
  bb = s_ - p
  err = (p - (s_ - bb)) + (cc - bb)               # two-sum: p + cc == s_ + err exactly
  # round to odd before narrowing, so f64 -> f16 rounds once: step a rounded-away sum back toward zero, then set its last bit
  sb = s_.bitcast(u64)
  inexact = err.ne(_c(0.0, f64)) & err.eq(err) & (s_.abs() < _c(float('inf'), f64))
  away = inexact & ((err < _c(0.0, f64)).ne(s_ < _c(0.0, f64)))
  sb = away.where(sb - _c(1, u64), sb)
  odd = inexact.where(sb | _c(1, u64), sb).bitcast(f64)
  r = odd.cast(dtypes.half)
  r32 = s_.cast(dtypes.float32)
  n32 = _amd_nan(r32, [a, b, c]).bitcast(dtypes.uint32)
  n16 = (((n32 >> _c(16)) & _c(0x8000)) | _c(0x7E00) | ((n32 >> _c(13)) & _c(0x3FF))).cast(dtypes.uint16)
  nan = _invalid_product(a, b).where(_c(0xFE00, dtypes.uint16), n16).bitcast(dtypes.half)
  return (s_.ne(s_) | _invalid_product(a, b)).where(nan, r)

def _hw_fma(a:UOp, b:UOp, c:UOp) -> UOp:
  r = _pcode._fma(a, b, c)
  if not _hw_float() or r.dtype not in _FLOATS: return r
  ut = _uint_of(r)
  inv = _invalid_product(a, b) & a.eq(a) & b.eq(b)
  return inv.where(_c(_DEFAULT_NAN[r.dtype], ut), _amd_nan(r, [a, b, c]).bitcast(ut)).bitcast(r.dtype)

def _hw_minmax(is_max:bool, *xs:UOp) -> UOp:
  def two(a:UOp, b:UOp) -> UOp:
    ut = _uint_of(a)
    ab, bb = a.bitcast(ut), b.bitcast(ut)
    sgn = _c(1 << (8 * a.dtype.itemsize - 1), ut)
    both_zero = a.eq(_c(0.0, a.dtype)) & b.eq(_c(0.0, b.dtype))
    zero = ((ab | bb) if not is_max else (ab & bb)) & sgn
    pick = (a > b).where(a, b) if is_max else (a < b).where(a, b)
    v = both_zero.where(zero.bitcast(a.dtype), pick)
    an, bn = a.ne(a), b.ne(b)
    return (an & bn).where(_quiet(a), an.where(b, bn.where(a, v)))
  x = xs[0]
  for y in xs[1:]: x = two(x, y)
  return x

def _hw_binop(left:UOp, right:UOp, op:str, result:UOp) -> UOp:
  if not _hw_float() or result.dtype not in _FLOATS: return result
  return _amd_nan(result, [left, right.neg() if op == '-' else right])

import test.mockgpu.amd.pcode as _pcode
_pcode._float_binop_hook = _hw_binop
_orig_ldexp = _FUNCS['ldexp']
_orig_minmax = {k: _FUNCS[k] for k in ('v_min_num_f32', 'v_max_num_f32', 'v_min3_num_f32', 'v_max3_num_f32')}
def _minmax_fn(name:str, is_max:bool):
  def fn(*a):
    if not _hw_float(): return _orig_minmax[name](*a)
    return _hw_minmax(is_max, *[x.bitcast(dtypes.float32) if x.dtype == dtypes.uint32 else x.cast(dtypes.float32) for x in a])
  return fn
_FUNCS.update({k: _minmax_fn(k, "max" in k) for k in _orig_minmax})
_FUNCS.update(fma=_hw_fma, ldexp=lambda a, e: _hw_ldexp32(a, e) if _hw_float() and a.dtype in (dtypes.float32, dtypes.uint32) else _orig_ldexp(a, e),
              hw_quiet=lambda x: _quiet(x) if _hw_float() else x)
_FUNCS.update(hw_rcp=_hw_rcp, hw_sqrt=_hw_sqrt, hw_exp16=_hw_exp16, hw_exp32=_hw_exp32, hw_rsq32=_hw_rsq32, hw_log32=_hw_log32, hw_rsq16=_hw_rsq16,
              hw_rcp16=_hw_rcp16, hw_sqrt16=_hw_sqrt16, hw_log16=_hw_log16, hw_ldexp32=_hw_ldexp32, hw_fma_mix16=_hw_fma_mix16)

_F64 = dtypes.float64
def _as(a:UOp, dt) -> UOp:  # pcode hands some operands over as raw bits
  if a.dtype == dt: return a
  if dt == dtypes.half and a.dtype.itemsize == 4: return (a.bitcast(dtypes.uint32) & _c(0xFFFF)).cast(dtypes.uint16).bitcast(dtypes.half)
  if a.dtype.itemsize == dt.itemsize: return a.bitcast(dt)
  return a.cast(dt)
def _k(x, dt=_F64) -> UOp: return _c(x, dt)
def _rne64(x:UOp) -> UOp:  # round half to even, exact for |x| < 2^52
  f = _pcode._floor(x + _k(0.5))
  odd = (_pcode._floor(f * _k(0.5)) * _k(2.0)).ne(f)
  return ((f - x).eq(_k(0.5)) & odd).where(f - _k(1.0), f)
def _sat(x:UOp, lo:int, hi:int, dt, nan:int=0) -> UOp:  # x: an integral f64; clamp, NaN -> nan
  r = (x < _k(lo)).where(_k(lo), (x > _k(hi)).where(_k(hi), x))
  return x.ne(x).where(_c(nan, dt), r.cast(dt))
def _trunc(x:UOp) -> UOp: return UOp(Ops.TRUNC, src=(x,))
def _clampf(x:UOp, lo:float, hi:float) -> UOp: return (x < _k(lo)).where(_k(lo), (x > _k(hi)).where(_k(hi), x))
def _f(dt): return lambda a: _as(a, dt).cast(_F64)
_h64, _s64 = _f(dtypes.half), _f(dtypes.float32)
_HW_CONV = {
  'f16_to_i16': lambda a: _sat(_trunc(_h64(a)), -32768, 32767, dtypes.int16),
  'f16_to_u16': lambda a: _sat(_trunc(_h64(a)), 0, 65535, dtypes.uint16),
  'v_cvt_i16_f32': lambda a: _sat(_trunc(_s64(a)), -32768, 32767, dtypes.int16),
  'f16_to_snorm': lambda a: _sat(_rne64(_clampf(_h64(a), -1.0, 1.0) * _k(32767.0)), -32768, 32767, dtypes.int16),
  'f16_to_unorm': lambda a: _sat(_rne64(_clampf(_h64(a), 0.0, 1.0) * _k(65535.0)), 0, 65535, dtypes.uint16),
  'f32_to_snorm': lambda a: _sat(_rne64(_clampf(_s64(a), -1.0, 1.0) * _k(32767.0)), -32768, 32767, dtypes.int16),
  'f32_to_unorm': lambda a: _sat(_rne64(_clampf(_s64(a), 0.0, 1.0) * _k(65535.0)), 0, 65535, dtypes.uint16),
  'f32_to_u8': lambda a: _sat(_rne64(_s64(a)), 0, 255, dtypes.uint8),
  'i32_to_i16': lambda a: _sat(a.bitcast(dtypes.int32).cast(_F64) if a.dtype == dtypes.uint32 else a.cast(_F64), -32768, 32767, dtypes.int16),
  'u32_to_u16': lambda a: _sat(a.cast(dtypes.uint32).cast(_F64), 0, 65535, dtypes.uint16),
}
def _hw_cvt_sat_nan(x:UOp, src:UOp) -> UOp:  # a NaN source saturates by its own sign: arithmetic on the way may change a NaN's sign by host
  ut = _uint_of(src)
  neg = (src.bitcast(ut) >> _c(8 * src.dtype.itemsize - 1, ut)).ne(_c(0, ut))
  nan = neg.where(_c(-0x80000000, dtypes.int32), _c(0x7FFFFFFF, dtypes.int32))
  return src.ne(src).where(nan, _pcode._f_to_i32(x))
def _hw_frexp(x:UOp, mant:bool) -> UOp:
  ut, (eb, mb) = _uint_of(x), {2: (5, 10), 4: (8, 23), 8: (11, 52)}[x.dtype.itemsize]
  b, bias = x.bitcast(ut), (1 << (eb - 1)) - 2
  e = ((b >> _c(mb, ut)) & _c((1 << eb) - 1, ut)).cast(dtypes.int32)
  m = b & _c((1 << mb) - 1, ut)
  sh = _c(mb + 1, dtypes.int32) - _pcode._msb(m, mb).cast(dtypes.int32) - _c(1, dtypes.int32)
  den = e.eq(_c(0, dtypes.int32)) & m.ne(_c(0, ut))
  ee = den.where(_c(1, dtypes.int32) - sh, e)
  mm = den.where((m << sh.cast(ut)) & _c((1 << mb) - 1, ut), m)
  special = e.eq(_c((1 << eb) - 1, dtypes.int32))
  zero = e.eq(_c(0, dtypes.int32)) & m.eq(_c(0, ut))
  if not mant: return (special | zero).where(_c(0, dtypes.int32), ee - _c(bias, dtypes.int32))
  out = ((b & _c(1 << (eb + mb), ut)) | _c(bias << mb, ut) | mm).bitcast(x.dtype)
  return special.where(_quiet(x), zero.where(x, out))
def _hw_fract(x:UOp) -> UOp:  # x - floor(x), below 1.0 by at least one ulp; NaN quieted, inf -> default NaN
  ut, one_minus = _uint_of(x), {2: 0x3BFF, 4: 0x3F7FFFFF, 8: 0x3FEFFFFFFFFFFFFF}[x.dtype.itemsize]
  r = x - _pcode._floor(x)
  lim = _c(one_minus, ut).bitcast(x.dtype)
  r = (r > lim).where(lim, r)
  dnan = _c({2: 0xFE00, 4: 0xFFC00000, 8: 0xFFF8000000000000}[x.dtype.itemsize], ut).bitcast(x.dtype)
  return _amd_nan(x.abs().eq(_c(float('inf'), x.dtype)).where(dnan,
                                                                  r), [x])
def _hw_ldexp(x:UOp, k:UOp) -> UOp:  # exact scaling, one rounding at the end; denormal inputs kept
  dt = x.dtype
  ut, (eb, mb) = _uint_of(x), {2: (5, 10), 8: (11, 52)}[dt.itemsize]
  k = k.cast(dtypes.int32)
  if dt == dtypes.half:  # an f16 times 2^k with |k| <= 64 is exact in f64; anything larger saturates the same way
    kk = (k < _c(-64, dtypes.int32)).where(_c(-64, dtypes.int32), (k > _c(64, dtypes.int32)).where(_c(64, dtypes.int32), k))
    r = (x.cast(_F64) * UOp(Ops.EXP2, src=(kk.cast(_F64),))).cast(dt)
  else:
    i32 = dtypes.int32
    b = x.bitcast(ut)
    e = ((b >> _c(52, ut)) & _c(0x7FF, ut)).cast(i32)
    m = b & _c((1 << 52) - 1, ut)
    sh = _c(52, i32) - _pcode._msb(m, 52).cast(i32)
    den = e.eq(_c(0, i32))
    E = den.where(_c(1 - 1023, i32) - sh, e - _c(1023, i32))
    mm = den.where((m << sh.cast(ut)) & _c((1 << 52) - 1, ut), m)
    mn = ((b & _c(1 << 63, ut)) | _c(1023 << 52, ut) | mm).bitcast(dt)
    T = E + (k < _c(-4000, i32)).where(_c(-4000, i32), (k > _c(4000, i32)).where(_c(4000, i32), k))
    lo = (T + _c(200, i32) < _c(-1022, i32)).where(_c(-1022, i32), T + _c(200, i32))
    A = (T > _c(1023, i32)).where(_c(1023, i32), (T >= _c(-1022, i32)).where(T, lo))
    B = (T > _c(1023, i32)).where(T - _c(1023, i32), (T >= _c(-1022, i32)).where(_c(0, i32), _c(-200, i32)))
    r = (mn * UOp(Ops.EXP2, src=(A.cast(_F64),))) * UOp(Ops.EXP2, src=(B.cast(_F64),))
  b = x.bitcast(ut)
  special = (b & _c(((1 << eb) - 1) << mb, ut)).eq(_c(((1 << eb) - 1) << mb, ut)) | (b & _c((1 << (eb + mb)) - 1, ut)).eq(_c(0, ut))
  return special.where(_quiet(x), r)
def _hw_cvt_off(a:UOp) -> UOp: return ((a.cast(dtypes.uint32) & _c(0xF)).cast(dtypes.int32) ^ _c(8, dtypes.int32)) \
                                         .__sub__(_c(8, dtypes.int32)).cast(dtypes.float32) * _c(0.0625, dtypes.float32)
def _hw_rtz16(x:UOp) -> UOp:
  r = x.cast(dtypes.half)
  rb = r.bitcast(dtypes.uint16)
  inf = r.abs().eq(_c(float('inf'), dtypes.half)) & x.abs().ne(_c(float('inf'), dtypes.float32))
  past = r.cast(dtypes.float32).abs() > x.abs()
  stepped = (inf | past).where(rb - _c(1, dtypes.uint16), rb)
  return x.ne(x).where(_quiet(x).cast(dtypes.half).bitcast(dtypes.uint16) | _c(0x200, dtypes.uint16), stepped)
def _hw_pk_rtz(a:UOp, b:UOp) -> UOp:
  lo, hi = _hw_rtz16(_as(a, dtypes.float32)), _hw_rtz16(_as(b, dtypes.float32))
  return lo.cast(dtypes.uint32) | (hi.cast(dtypes.uint32) << _c(16))
for _n, _fn in _HW_CONV.items():
  _FUNCS[_n] = (lambda hw, orig: lambda *a: hw(*a) if _hw_float() else orig(*a))(_fn, _FUNCS[_n])
_FUNCS.update(hw_cvt_floor=lambda x: _hw_cvt_sat_nan(_pcode._floor(_as(x, dtypes.float32)), _as(x, dtypes.float32)),
              hw_cvt_nearest=lambda x: _hw_cvt_sat_nan(_pcode._floor(_as(x, dtypes.float32).cast(_F64) + _c(0.5, _F64)), _as(x, dtypes.float32)),
              hw_frexp_mant=lambda x: _hw_frexp(x, True), hw_frexp_exp=lambda x: _hw_frexp(x, False), hw_fract=_hw_fract,
              hw_ldexp=_hw_ldexp, hw_cvt_off=_hw_cvt_off, hw_pk_rtz=_hw_pk_rtz)
def _hw_maximum(is_max:bool, *xs:UOp) -> UOp:
  out = _hw_minmax(is_max, *xs)
  for x in reversed(xs): out = x.ne(x).where(_quiet(x), out)
  return out
def _hw_rndne(x:UOp) -> UOp:
  r = _rne64(x.cast(_F64)).cast(x.dtype)
  big = x.abs() >= _c({2: 1024.0, 4: 8388608.0, 8: 4503599627370496.0}[x.dtype.itemsize], x.dtype)
  ut = _uint_of(x)
  r = (r.bitcast(ut) | (x.bitcast(ut) & _c(1 << (8 * x.dtype.itemsize - 1), ut))).bitcast(x.dtype)
  return _amd_nan((big | x.ne(x)).where(x, r), [x])
def _hw_med3(a:UOp, b:UOp, c:UOp) -> UOp:
  anynan = a.ne(a) | b.ne(b) | c.ne(c)
  med = _hw_minmax(True, _hw_minmax(False, a, b), _hw_minmax(False, _hw_minmax(True, a, b), c))
  return anynan.where(_hw_minmax(False, a, b, c), med)
_DT = {'f16': dtypes.half, 'f32': dtypes.float32, 'f64': dtypes.float64}
for _t, _dt in _DT.items():
  for _mx in (False, True):
    _nm, _full = ('max' if _mx else 'min'), ('maximum' if _mx else 'minimum')
    def _wrap(fn, dt, orig): return lambda *a: fn(*[_as(x, dt) for x in a]) if _hw_float() else orig(*a)
    for _n in (f'v_{_full}_{_t}', f'v_{_full}3_{_t}'):
      if _n in _FUNCS or _t == 'f64': _FUNCS[_n] = _wrap(functools.partial(_hw_maximum, _mx), _dt, _FUNCS.get(_n, lambda *a: a[0]))
    if _t == 'f16':
      for _n in (f'v_{_nm}_num_f16', f'v_{_nm}3_num_f16'): _FUNCS[_n] = _wrap(functools.partial(_hw_minmax, _mx), _dt, _FUNCS[_n])
_FUNCS.update(hw_rndne=lambda x: _hw_rndne(x), hw_med3=lambda a, b, c: _hw_med3(a, b, c))
def _hw_div_fmas_scaled(a:UOp, b:UOp, c:UOp) -> UOp:  # fma scaled by 2^+-64 (f32) or 2^+-128 (f64): up when c's exponent field is in the upper half
  ut, (eb, mb) = _uint_of(c), {4: (8, 23), 8: (11, 52)}[c.dtype.itemsize]
  up = ((c.bitcast(ut) >> _c(mb, ut)) & _c((1 << eb) - 1, ut)) >= _c(1 << (eb - 1), ut)
  k = {4: 64.0, 8: 128.0}[c.dtype.itemsize]
  sc = up.where(_c(2.0 ** k, _F64), _c(2.0 ** -k, _F64))
  if c.dtype == dtypes.float64:  # an fma that overflows before a down-scale is redone with the scale folded into a and c
    big_a = a.abs() >= b.abs()  # scale the larger factor so it stays exact
    f = _hw_fma(a, b, c)
    a2, b2 = big_a.where(a * sc, a), big_a.where(b, b * sc)
    r1 = f * sc
    def split(x:UOp) -> tuple[UOp, UOp]:
      hi = (x.bitcast(dtypes.uint64) & _c(0xFFFFFFFFF8000000, dtypes.uint64)).bitcast(_F64)
      return hi, x - hi
    (ah, al), (bh, bl) = split(a2), split(b2)
    ph = a2 * b2
    pl, cs = ((ah * bh - ph) + ah * bl + al * bh) + al * bl, c * sc
    s1 = ph + cs
    bb = s1 - ph
    e1 = (ph - (s1 - bb)) + (cs - bb)
    lo = pl + e1
    bl = lo - pl
    el = (pl - (lo - bl)) + (e1 - bl)
    el = el.ne(_c(0.0, _F64)).where(el, c - cs / sc)
    r2, r3 = _hw_fma(a2, b2, cs), s1 + _rto64(lo, el)
    (ah, al), (bh, bl) = split(a), split(b)  # a denormal result: the exact unscaled a*b + c rounded to odd, so the scale rounds once
    qh = (a * (b * _c(2.0, _F64))) * _c(0.5, _F64)  # fl(a*b) without an a*b node: one shared with the plain fma would stop it fusing
    ql = ((ah * bh - qh) + ah * bl + al * bh) + al * bl
    t1 = qh + c
    tb = t1 - qh
    te = (qh - (t1 - tb)) + (c - tb)
    tl = ql + te
    tlb = tl - ql
    tle = (ql - (tl - tlb)) + (te - tlb)
    t2 = t1 + tl
    t2b = t2 - t1
    ok = (qh.abs() >= _c(2.0 ** -960, _F64)) & (qh.abs() < _c(2.0 ** 1000, _F64)) & (c.abs() < _c(2.0 ** 1000, _F64)) & \
         (a.abs() >= _c(2.0 ** -940, _F64)) & (b.abs() >= _c(2.0 ** -940, _F64))  # every partial product of the split stays exact
    err = ((t1 - (t2 - t2b)) + (tl - t2b)) + tle
    u64 = dtypes.uint64
    mb, neg_ = t2.abs().bitcast(u64), t2 < _c(0.0, _F64)
    em = neg_.where(-err, err)  # > 0: the true magnitude is above |t2|
    m53 = (mb & _c((1 << 52) - 1, u64)) | _c(1 << 52, u64)
    q = m53 >> _c(1, u64)  # |t2| * 2^-128 just under 2^-1022 keeps 52 bits: round the one dropped bit by hand (round to odd needs two)
    up1 = (m53 & _c(1, u64)).ne(_c(0, u64)) & ((em > _c(0.0, _F64)) | (em.eq(_c(0.0, _F64)) & (q & _c(1, u64)).ne(_c(0, u64))))
    d52 = ((q + up1.cast(u64)) | neg_.where(_c(1 << 63, u64), _c(0, u64))).bitcast(_F64)
    r2 = ok.where(((mb >> _c(52, u64)).eq(_c(128, u64)) & ~up).where(d52, _rto64(t2, err) * sc), r2)
    over = r1.abs().eq(_c(float('inf'), _F64)) & a.abs().ne(_c(float('inf'), _F64)) & b.abs().ne(_c(float('inf'), _F64)) & \
           c.abs().ne(_c(float('inf'), _F64))
    tiny = (r1.abs() < _c(2.0 ** -1022, _F64)) & f.ne(_c(0.0, _F64))    # a denormal result rounds once from the folded form
    return ((over & ~up) & r3.ne(_c(0.0, _F64)) & r3.eq(r3)).where(r3, (tiny & r2.ne(_c(0.0, _F64)) & r2.eq(r2)).where(r2, r1))
  p, cc = a.cast(_F64) * b.cast(_F64), c.cast(_F64)    # exact product; two-sum keeps the sum exact, rounding to odd makes the f32 rounding single
  s_ = p + cc
  bb = s_ - p
  err = (p - (s_ - bb)) + (cc - bb)
  s2, e2 = s_ * sc, err * sc
  sb = s2.bitcast(dtypes.uint64)
  odd = e2.ne(_c(0.0, _F64)) & s2.eq(s2) & (s2.abs() < _c(float('inf'), _F64))
  away = (e2 < _c(0.0, _F64)).ne(s2 < _c(0.0, _F64)) & s2.ne(_c(0.0, _F64))     # s2 rounded away from zero: step it back
  sb = (odd & away).where(sb - _c(1, dtypes.uint64), sb)
  sb = odd.where(sb | _c(1, dtypes.uint64), sb)
  r = sb.bitcast(_F64).cast(dtypes.float32)
  return _amd_nan(r, [a, b, c])
_FUNCS.update(hw_div_fmas_scaled=_hw_div_fmas_scaled)
def _fma_exact(a:UOp, b:UOp, c:UOp) -> tuple[UOp, UOp]:  # f32/f16 fma as an exact f64 pair s + err
  p, cc = a.cast(_F64) * b.cast(_F64), c.cast(_F64)
  s_ = p + cc
  bb = s_ - p
  return s_, (p - (s_ - bb)) + (cc - bb)
def _rto64(s_:UOp, err:UOp) -> UOp:  # the exact s + err rounded to odd in f64
  sb = s_.bitcast(dtypes.uint64)
  odd = err.ne(_c(0.0, _F64)) & s_.eq(s_) & (s_.abs() < _c(float('inf'), _F64))
  away = (err < _c(0.0, _F64)).ne(s_ < _c(0.0, _F64)) & s_.ne(_c(0.0, _F64))
  sb = (odd & away).where(sb - _c(1, dtypes.uint64), sb)
  return odd.where(sb | _c(1, dtypes.uint64), sb).bitcast(_F64)
def _rtz32(x:UOp) -> UOp:  # an f64 (already rounded to odd) to f32 toward zero; overflow gives the largest finite
  r = x.cast(dtypes.float32)
  rb = r.bitcast(dtypes.uint32)
  past = r.cast(_F64).abs() > x.abs()
  rb = past.where(rb - _c(1), rb)
  return x.ne(x).where(x.cast(dtypes.float32), rb.bitcast(dtypes.float32))
def _ftz(x:UOp) -> UOp:  # dx9 and cube ops flush f32 denormals to +0
  b = x.bitcast(dtypes.uint32)
  return ((b & _c(0x7F800000)).eq(_c(0)) & (b & _c(0x7FFFFF)).ne(_c(0))).where(_c(0.0, dtypes.float32), x)
def _hw_fma_dx9(a:UOp, b:UOp, c:UOp) -> UOp:
  a, b, c = _ftz(_as(a, dtypes.float32)), _ftz(_as(b, dtypes.float32)), _ftz(_as(c, dtypes.float32))
  z = a.eq(_c(0.0, dtypes.float32)) | b.eq(_c(0.0, dtypes.float32))   # 0 * x is +0, then the addend joins as in IEEE
  return _flush_denorm(z.where(c.eq(_c(0.0, dtypes.float32)).where(_c(0.0, dtypes.float32), _quiet(c)), _hw_fma(a, b, c)))
def _hw_mullit(a:UOp, b:UOp, c:UOp) -> UOp:  # denormals kept; dx9 zero rule on exact zeros
  a, b, c = _as(a, dtypes.float32), _as(b, dtypes.float32), _as(c, dtypes.float32)
  bad = b.eq(_c(-3.4028234663852886e38, dtypes.float32)) | b.eq(_c(float('-inf'), dtypes.float32)) | b.ne(b)
  bad = bad | (c <= _c(0.0, dtypes.float32)) | c.ne(c)
  z = a.eq(_c(0.0, dtypes.float32)) | b.eq(_c(0.0, dtypes.float32))
  return bad.where(_c(-3.4028234663852886e38, dtypes.float32), z.where(_c(0.0, dtypes.float32), _amd_nan(a * b, [a, b])))
def _f3(a, b, c): return _as(a, dtypes.float32), _as(b, dtypes.float32), _as(c, dtypes.float32)
def _ftz0(x:UOp) -> UOp:
  x = _as(x, dtypes.float32)
  return (x.bitcast(dtypes.uint32) & _c(0x7F800000)).eq(_c(0)).where(_c(0.0, dtypes.float32), x)
def _fma_rtz32(a, b, c): return _amd_nan(_rtz32(_rto64(*_fma_exact(*_f3(a, b, c)))), list(_f3(a, b, c)))
def _fma_rtz16(a, b, c): return _amd_nan(_hw_rtz16(_rto32(_rto64(*_fma_exact(*_f3(a, b, c))))).bitcast(dtypes.half), list(_f3(a, b, c)))
def _fma16_once(a, b, c): return _amd_nan(_rto32(_rto64(*_fma_exact(*_f3(a, b, c)))).cast(dtypes.half), list(_f3(a, b, c)))
_FUNCS.update(hw_ftz0=_ftz0, hw_fma_dx9=_hw_fma_dx9, hw_mullit=_hw_mullit, hw_ftz=lambda x: _ftz(_as(x, dtypes.float32)),
              hw_quietf=lambda x: _quiet(_as(x, dtypes.float32)), hw_fma_rtz32=_fma_rtz32, hw_fma_rtz16=_fma_rtz16, hw_fma16_once=_fma16_once)
_FUNCS.update(hw_sin16=lambda a: _f16_table('sin_f16', _as(a, dtypes.half)), hw_cos16=lambda a: _f16_table('cos_f16', _as(a, dtypes.half)))
_SC_NA = (1 << 24) + 6 * (1 << 23)  # table entries: every R < 2^24, then multiples of 2^j in [2^(23+j), 2^(24+j)), j = 1..6
def _tab_word(name:str, i:UOp) -> UOp: return _tab_bits(name, i.cast(dtypes.uint64) * _c(4, dtypes.uint64), 4).cast(dtypes.uint32)
def _sc_coef(s:UOp, k:int) -> UOp:
  return _tab_i64("sc_coefs", s * _c(6, dtypes.int64) + _c(k, dtypes.int64)).bitcast(_F64)
def _sc_core(R0:UOp, cos:bool) -> UOp:
  # R0 = trunc(frac|x| * 2^31) -> core bits (uint32). core(R + 2^30) = -core(R), cos = core(R + 2^29). per 2^-7 segment a degree-5
  # f64 Horner on R quantised as the hardware does (seg 0 exact, seg 1 to 4, else to 16; segs 0 and 63 times the distance to the zero),
  # rounded to f32, plus a measured 2-bit delta per R (code 3: one of 79 escapes)
  i64 = dtypes.int64
  def c(v): return _c(v, i64)
  negh = R0 >= c(1 << 30)
  Rh = negh.where(R0 - c(1 << 30), R0)
  Rx = Rh + c(1 << 29) if cos else Rh
  neg = Rx >= c(1 << 30)
  Rf = neg.where(Rx - c(1 << 30), Rx)
  s = Rf >> c(24)
  q = s.eq(c(0)).where(Rf, s.eq(c(1)).where(((Rf + c(2)) >> c(2)) << c(2), ((Rf + c(8)) >> c(4)) << c(4)))
  u = (c(2) * (q - (s << c(24)))).cast(_F64) * _c(2.0 ** -24, _F64) - _c(1.0, _F64)
  f = _sc_coef(s, 0)
  for k in range(1, 6): f = f * u + _sc_coef(s, k)
  near = s.eq(c(0)).where(Rf, c(1 << 30) - Rf).cast(_F64) * _c(2.0 ** -31, _F64)
  f = (s.eq(c(0)) | s.eq(c(63))).where(f * near, f)
  m = f.cast(dtypes.float32).bitcast(dtypes.int32).cast(i64)
  j = functools.reduce(lambda acc, b: acc + (Rh >= c(1 << (23 + b))).cast(i64), range(1, 7), c(0))
  idx = (Rh < c(1 << 24)).where(Rh, c(1 << 24) + (j - c(1)) * c(1 << 23) + ((Rh >> j) - c(1 << 23)))
  code = _tab_code2("sc_cos" if cos else "sc_sin", idx.cast(dtypes.uint32)).cast(i64)
  key = idx + c(_SC_NA if cos else 0)
  pos = c(0)
  for step in (64, 32, 16, 8, 4, 2, 1): pos = (_tab_word("sc_esck", pos + c(step - 1)).cast(i64) <= key).where(pos + c(step), pos)
  esc = _tab_word("sc_escv", (pos - c(1)).maximum(c(0))).bitcast(dtypes.int32).cast(i64)
  v = m + code.eq(c(2)).where(esc, code)
  v = neg.ne(negh).where(v ^ c(0x80000000), v)
  return (v & c(0x7FFFFFFF)).eq(c(0)).where(c(0), v & c(0xFFFFFFFF)).cast(dtypes.uint32)
def _hw_sin32(a:UOp, cos:bool) -> UOp:
  # gfx1200 v_sin/v_cos f32 (revolutions), exact on every |x| < 2 and the large-|x| edge probes: sin = sign(x) * core(R0),
  # cos = core'(R0), R0 = trunc(frac|x| * 2^31), an exact zero is +0; sin with |x| < 1.5*2^-12 (denormals, +-0 too) is
  # |x| * 0xC90FD5 * 2^-21 rounded to nearest even onto the f32 grid, sign kept; inf -> negative default NaN, NaN -> quieted
  i64, u32 = dtypes.int64, dtypes.uint32
  def c(v): return _c(v, i64)
  xb = _as(a, dtypes.float32).bitcast(u32).cast(i64)
  sign, ex, man = xb >> c(31), (xb >> c(23)) & c(255), xb & c(0x7FFFFF)
  mi = ex.eq(c(0)).where(man, man | c(1 << 23))
  e2 = ex.eq(c(0)).where(c(-149), ex - c(150))
  sh = e2 + c(31)
  R0 = (sh >= c(0)).where(mi << sh.maximum(c(0)).minimum(c(40)), mi >> (c(0) - sh).maximum(c(0)).minimum(c(63)))
  R0 = (sh >= c(32)).where(c(0), R0) & c((1 << 31) - 1)
  out = _sc_core(R0, cos).cast(i64)
  if not cos:
    out = (sign.eq(c(1)) & out.ne(c(0))).where(out ^ c(0x80000000), out)
    tiny = (ex < c(115)) | (ex.eq(c(115)) & (man < c(1 << 22)))
    p = mi * c(0xC90FD5)
    k = e2 - c(21)
    nb = ((p.maximum(c(1)).cast(_F64).bitcast(dtypes.uint64) >> _c(52, dtypes.uint64)).cast(i64) & c(0x7FF)) - c(1022)
    L = (nb - c(1) + k - c(23)).maximum(c(-149))
    shv = L - k
    sp = shv.maximum(c(0))
    q0 = p >> sp
    rem = p - (q0 << sp)
    half = (shv > c(0)).where(c(1) << (shv - c(1)).maximum(c(0)), c(0))
    up = (rem > half) | (rem.eq(half) & (q0 & c(1)).eq(c(1)))
    q = (shv > c(0)).where(q0 + up.cast(i64), p << (c(0) - shv).maximum(c(0)).minimum(c(40)))
    tb = (q.cast(_F64) * ((L + c(1023)) << c(52)).bitcast(_F64)).cast(dtypes.float32).bitcast(u32).cast(i64)
    out = tiny.where(sign.eq(c(1)).where(tb | c(0x80000000), tb), out)
  out = ex.eq(c(255)).where(man.ne(c(0)).where(xb | c(0x400000), c(0xFFC00000)), out)
  return out.cast(u32).bitcast(dtypes.float32)
_FUNCS.update(hw_sin32=lambda a: _hw_sin32(a, False), hw_cos32=lambda a: _hw_sin32(a, True))

def _exp_of(x:UOp, emin:int) -> UOp:  # unbiased exponent of a finite f32-held value, zero -> -4000, denormals of the source type -> emin
  i32 = dtypes.int32
  e = ((x.cast(_F64).bitcast(dtypes.uint64) >> _c(52, dtypes.uint64)) & _c(0x7FF, dtypes.uint64)).cast(i32) - _c(1023, i32)
  return x.eq(_c(0.0, x.dtype)).where(_c(-4000, i32), e.maximum(_c(emin, i32)))
def _pow2(e:UOp) -> UOp: return ((e + _c(1023, dtypes.int32)).cast(dtypes.uint64) << _c(52, dtypes.uint64)).bitcast(_F64)  # 2^e, -1022 <= e <= 1023
def _floor_sum(ps:list[UOp], q:UOp, iq:UOp) -> UOp:  # floor((p0 + p1) / q) of an exactly held pair sum, the low part kept by two-sum
  if len(ps) == 1: return _pcode._floor(ps[0] * iq)
  s = ps[0] + ps[1]
  bb = s - ps[0]
  err = (ps[0] - (s - bb)) + (ps[1] - bb)
  f = _pcode._floor(s * iq)
  return ((f * q).eq(s) & (err < _c(0.0, _F64))).where(f - _c(1.0, _F64), f)
def _grid_dot(a:list[UOp], b:list[UOp], c:UOp, emin:int, cmin:int) -> UOp:
  i32 = dtypes.int32
  ps = [x.cast(_F64) * y.cast(_F64) for x, y in zip(a, b)]
  ep = functools.reduce(lambda x, y: x.maximum(y), [_exp_of(x, emin) + _exp_of(y, emin) for x, y in zip(a, b)])
  ec = _exp_of(c, cmin)  # a denormal accumulator counts at its type's smallest exponent
  e = (ep - _c(24, i32)).maximum(ec - _c(26, i32)).maximum(_c(-1000, i32))
  q, iq = _pow2(e), _pow2(-e)
  cf = c.cast(_F64)
  c_al = (ec < e).where(_c(0.0, _F64), _pcode._floor(cf * iq))
  terms = [_floor_sum(ps[i:i+2], q, iq) for i in range(0, len(ps), 2)]
  return (functools.reduce(lambda x, y: x + y, terms) + c_al) * q
EMU_NATIVE = ContextVar("EMU_NATIVE", 1)
_WMMA_C = r"""
#include <stdint.h>
#include <string.h>
static inline double bd(uint64_t u) { double d; memcpy(&d, &u, 8); return d; }
static inline float bf(uint32_t u) { float f; memcpy(&f, &u, 4); return f; }
static inline uint32_t fb(float f) { uint32_t u; memcpy(&u, &f, 4); return u; }
static inline double p2(int e) { return bd((uint64_t)(e + 1023) << 52); }
static inline double fsum(double p0, double p1, double q, double iq) {
  double s = p0 + p1, bb = s - p0, err = (p0 - (s - bb)) + (p1 - bb), f = __builtin_floor(s * iq);
  return (f * q == s && err < 0.0) ? f - 1.0 : f;
}
static inline int expo32(uint32_t x) {
  int ex = (int)((x >> 23) & 0xFF), e = ex == 255 ? 1024 : ex - 127; e = e < -126 ? -126 : e; return (x & 0x7FFFFFFF) == 0 ? -4000 : e;
}
static inline double h2d(uint32_t h) {
  uint32_t s = (h & 0x8000) << 16, e5 = (h >> 10) & 0x1F, m = h & 0x3FF;
  uint32_t nb = s | ((e5 + 112) << 23) | (m << 13), db = s | fb((float)m * 0x1p-24f);
  return (double)bf(e5 ? nb : db);
}
static inline int h2e(uint32_t h) { int e5 = (int)((h >> 10) & 0x1F); return (h & 0x7FFF) == 0 ? -4000 : e5 ? e5 - 15 : -14; }
static inline double b2d(uint32_t h) { return (double)bf(h << 16); }
static inline int b2e(uint32_t h) { int e8 = (int)((h >> 7) & 0xFF); return (h & 0x7FFF) == 0 ? -4000 : e8 ? e8 - 127 : -126; }
int emu_wmma_rdna4(uint32_t *v, uint32_t s0, uint32_t s1, uint32_t s2, uint32_t vd, uint32_t exec, uint32_t cc, int cvgpr, int bf16) {
  uint32_t bad = 0, cb[16][16];
  for (int j = 0; j < 4; j++) for (int l = 0; l < 32; l++) {
    uint32_t wa = v[(s0 + j) * 32 + l], wb = v[(s1 + j) * 32 + l];
    bad |= bf16 ? (((wa & 0x7FFF) >= 0x7F00) | (((wa >> 16) & 0x7FFF) >= 0x7F00) | ((wb & 0x7FFF) >= 0x7F00) | (((wb >> 16) & 0x7FFF) >= 0x7F00))
                : (((wa & 0x7C00) == 0x7C00) | ((wa & 0x7C000000) == 0x7C000000) | ((wb & 0x7C00) == 0x7C00) | ((wb & 0x7C000000) == 0x7C000000));
  }
  for (int j = 0; j < 8; j++) for (int l = 0; l < 32; l++) {
    uint32_t x = cvgpr ? v[(s2 + j) * 32 + l] : cc;
    cb[j + (l >> 4) * 8][l & 15] = x; bad |= (x & 0x7FFFFFFF) >= 0x7F000000;
  }
  if (bad) return 0;
  double at[16][16], bt[16][16]; int ea[16][16], eb[16][16];
  uint32_t ha[16][16], hb[16][16];
  for (int j = 0; j < 4; j++) for (int h = 0; h < 2; h++) for (int hl = 0; hl < 2; hl++) {
    int el = 2 * j + h, k = (el & 3) | (hl << 2) | ((el >> 2) << 3);
    for (int i = 0; i < 16; i++) {
      ha[k][i] = (v[(s0 + j) * 32 + hl * 16 + i] >> (16 * h)) & 0xFFFF;
      hb[k][i] = (v[(s1 + j) * 32 + hl * 16 + i] >> (16 * h)) & 0xFFFF;
    }
  }
  if (bf16) for (int k = 0; k < 16; k++) for (int i = 0; i < 16; i++) {
    at[k][i] = b2d(ha[k][i]); ea[k][i] = b2e(ha[k][i]); bt[k][i] = b2d(hb[k][i]); eb[k][i] = b2e(hb[k][i]);
  } else for (int k = 0; k < 16; k++) for (int i = 0; i < 16; i++) {
    at[k][i] = h2d(ha[k][i]); ea[k][i] = h2e(ha[k][i]); bt[k][i] = h2d(hb[k][i]); eb[k][i] = h2e(hb[k][i]);
  }
  for (int r = 0; r < 16; r++) {
    float acc[16];
    for (int n = 0; n < 16; n++) acc[n] = bf(cb[r][n]);
    for (int g = 0; g < 16; g += 4) {
      double a0 = at[g][r], a1 = at[g+1][r], a2 = at[g+2][r], a3 = at[g+3][r];
      int e0 = ea[g][r], e1 = ea[g+1][r], e2 = ea[g+2][r], e3 = ea[g+3][r];
      for (int n = 0; n < 16; n++) {
        double p0 = a0 * bt[g][n], p1 = a1 * bt[g+1][n], p2_ = a2 * bt[g+2][n], p3 = a3 * bt[g+3][n];
        int ep = e0 + eb[g][n], s1_ = e1 + eb[g+1][n], s2_ = e2 + eb[g+2][n], s3 = e3 + eb[g+3][n];
        ep = ep > s1_ ? ep : s1_; ep = ep > s2_ ? ep : s2_; ep = ep > s3 ? ep : s3;
        int ec = expo32(fb(acc[n]));
        int e = ep - 24; e = e > ec - 26 ? e : ec - 26; e = e > -1000 ? e : -1000;
        double q = p2(e), iq = p2(-e);
        double c_al = ec < e ? 0.0 : __builtin_floor((double)acc[n] * iq);
        acc[n] = (float)(((fsum(p0, p1, q, iq) + fsum(p2_, p3, q, iq)) + c_al) * q);
      }
    }
    for (int n = 0; n < 16; n++) cb[r][n] = fb(acc[n]);
  }
  for (int j = 0; j < 8; j++) for (int l = 0; l < 32; l++) {
    uint32_t *d = &v[(vd + j) * 32 + l];
    *d = ((exec >> l) & 1) ? cb[j + (l >> 4) * 8][l & 15] : *d;
  }
  return 1;
}
"""
@functools.cache
def _wmma_native() -> bool:
  if not EMU_NATIVE.value: return False
  try:
    so = os.path.join(tempfile.mkdtemp(), "emu_wmma.so")
    cpu = "-march=native" if platform.machine() in ('x86_64', 'AMD64') else "-mcpu=native"
    subprocess.check_output(['clang', '-shared', '-fPIC', '-O3', '-ffp-contract=off', '-fno-math-errno', cpu, '-x', 'c', '-', '-o', so],
                            input=_WMMA_C.encode(), stderr=subprocess.DEVNULL)
    from tinygrad.runtime.support.c import DLL
    return DLL("emu_wmma", [so]).nm in DLL._loaded_
  except Exception: return False
def _grid_dot8(a:list[UOp], b:list[UOp], c:UOp, emin_a:int, emin_b:int) -> UOp:
  i32 = dtypes.int32
  def p2(e): return ((e.maximum(_c(-1000, i32)) + _c(1023, i32)).cast(dtypes.uint64) << _c(52, dtypes.uint64)).bitcast(_F64)
  subs, eps = [], []
  for j in range(0, len(a), 4):
    ps = [x.cast(_F64) * y.cast(_F64) for x, y in zip(a[j:j+4], b[j:j+4])]
    ep = functools.reduce(lambda x, y: x.maximum(y), [_exp_of(x, emin_a) + _exp_of(y, emin_b) for x, y in zip(a[j:j+4], b[j:j+4])])
    qp = p2(ep - _c(24, i32))
    subs.append(functools.reduce(lambda x, y: x + y, [_pcode._floor(x / qp) for x in ps]) * qp)
    eps.append(ep)
  ep, ec = functools.reduce(lambda x, y: x.maximum(y), eps), _exp_of(c, -126)
  e = (ep - _c(24, i32)).maximum(ec - _c(26, i32))
  q = p2(e)
  c_al = (ec < e.maximum(_c(-1000, i32))).where(_c(0.0, _F64), _pcode._floor(c.cast(_F64) / q))
  return (functools.reduce(lambda x, y: x + y, [_pcode._floor(x / q) for x in subs]) + c_al) * q
_DOT8 = {f'V_DOT4_F32_{a.upper()}_{b.upper()}': (a, b) for a in ('fp8', 'bf8') for b in ('fp8', 'bf8')}
def _hw_dot8(inst, ctx, lane:UOp, op_name:str) -> UOp:
  literal = ctx.optional_field(inst, 'literal')
  s = [ctx.rsrc_dyn(ctx.inst_field(getattr(type(inst), f)), lane, 32, literal=literal).cast(dtypes.uint32) for f in ('src0', 'src1', 'src2')]
  s[0] = _dpp_src0(ctx, inst, lane, s[0]).cast(dtypes.uint32)
  opsel, opsel_hi, neg, neg_hi = _iattr(inst, 'opsel'), _iattr(inst, 'opsel_hi', 3), _iattr(inst, 'neg'), _iattr(inst, 'neg_hi')
  def pick(x:UOp, i:int) -> UOp:
    lo, hi = x & _c(0xFFFF), x >> _c(16)
    return (hi if opsel & (1 << i) else lo) | ((hi if opsel_hi & (1 << i) else lo) << _c(16))
  ta, tb = _DOT8[op_name]
  a = [_FUNCS[f'{ta}_to_f32']((pick(s[0], 0) >> _c(8 * k)) & _c(0xFF)) for k in range(4)]
  b = [_FUNCS[f'{tb}_to_f32']((pick(s[1], 1) >> _c(8 * k)) & _c(0xFF)) for k in range(4)]
  c = s[2]
  if neg_hi & 4: c = c & _c(0x7FFFFFFF)
  if neg & 4: c = c ^ _c(0x80000000)
  cf = c.bitcast(dtypes.float32)
  r = _grid_dot8(a, b, cf, -6 if ta == 'fp8' else -14, -6 if tb == 'fp8' else -14)
  prods = functools.reduce(lambda x, y: x + y, [x.cast(_F64) * y.cast(_F64) for x, y in zip(a, b)])
  ieee = prods + cf.cast(_F64)
  big = ieee.abs().eq(_c(float('inf'), _F64))
  res = big.where(ieee, r).cast(dtypes.float32).bitcast(dtypes.uint32)
  res = ((res & _c(0x7FFFFFFF)).eq(_c(0)) & r.ne(_c(0.0, _F64))).where(_c(0), res)
  abnan = functools.reduce(lambda x, y: x | y, [x.ne(x) for x in a + b])
  pinv = functools.reduce(lambda x, y: x | y, [(x.cast(_F64) * y.cast(_F64)).ne(x.cast(_F64) * y.cast(_F64)) for x, y in zip(a, b)])  # inf*0
  invalid = prods.ne(prods) | (prods.abs().eq(_c(float('inf'), _F64)) & ieee.ne(ieee) & cf.eq(cf))
  return (abnan | pinv | invalid).where(_c(0xFFC00A3D), cf.ne(cf).where(_quiet(cf).bitcast(dtypes.uint32), (
                     ieee.ne(ieee).where(_c(0xFFC00A3D), res))))
def _rto32(x:UOp) -> UOp:  # f64 -> f32 rounding to odd, so a following f32 -> f16 rounds once
  r = x.cast(dtypes.float32)
  rb = r.bitcast(dtypes.uint32)
  rb = (r.cast(_F64).abs() > x.abs()).where(rb - _c(1), rb)
  return (rb.bitcast(dtypes.float32).cast(_F64).ne(x)).where(rb | _c(1), rb).bitcast(dtypes.float32)
_DOT_NAN = {'f32': 0xFFC00A3D, 'f16': 0xFE3D, 'bf16': 0xFFFD}
def _hw_dot(a:list[UOp], b:list[UOp], c:UOp, emin:int, out:str, cmin:int) -> UOp:
  ut = {'f32': dtypes.uint32, 'f16': dtypes.uint16, 'bf16': dtypes.uint16}[out]
  r = _grid_dot(a, b, c, emin, cmin)
  prods = functools.reduce(lambda x, y: x + y, [x.cast(_F64) * y.cast(_F64) for x, y in zip(a, b)])
  ieee = prods + c.cast(_F64)
  big = ieee.abs().eq(_c(float('inf'), _F64))
  if out == 'f32': res = big.where(ieee, r).cast(dtypes.float32).bitcast(ut)
  elif out == 'f16': res = big.where(ieee.cast(dtypes.float32), _rto32(r)).cast(dtypes.half).bitcast(ut)
  else:  # bf16: the f32 result truncated
    r32 = big.where(ieee, r).cast(dtypes.float32).bitcast(dtypes.uint32)
    r32 = ((r32 & _c(0x7FFFFFFF)).eq(_c(0)) & r.ne(_c(0.0, _F64))).where(_c(0), r32)
    res = (r32 >> _c(16)).cast(ut)
  if out != 'bf16':  # a nonzero sum that underflows is +0
    sign = _c({'f32': 0x80000000, 'f16': 0x8000}[out], ut)
    res = ((res & ~sign).eq(_c(0, ut)) & r.ne(_c(0.0, _F64))).where(_c(0, ut), res)
  abnan = functools.reduce(lambda x, y: x | y, [x.ne(x) for x in a + b])
  cq = {'f32': lambda: _quiet(c).bitcast(ut), 'f16': lambda: _quiet(c.cast(dtypes.half)).bitcast(ut),
        'bf16': lambda: (c.bitcast(dtypes.uint32) >> _c(16)).cast(ut) | _c(0x40, ut)}[out]()
  dnan = _c({'f32': 0xFFC00000, 'f16': 0xFE00, 'bf16': 0xFFC0}[out], ut)
  invalid = prods.ne(prods) | (prods.abs().eq(_c(float('inf'), _F64)) & ieee.ne(ieee) & c.eq(c))
  return abnan.where(_c(_DOT_NAN[out], ut), invalid.where(dnan, c.ne(c).where(cq, ieee.ne(ieee).where(dnan, res))))
def _h2f(x:UOp) -> UOp: return _as(x, dtypes.half).cast(dtypes.float32)
def _b2f(x:UOp) -> UOp: return ((x.cast(dtypes.uint32) if x.dtype != dtypes.uint32 else x) & _c(0xFFFF)).__lshift__(_c(16)).bitcast(dtypes.float32)
def _halves(x:UOp, conv) -> list[UOp]:
  u = x.bitcast(dtypes.uint32) if x.dtype.itemsize == 4 else x.cast(dtypes.uint32)
  return [conv(u & _c(0xFFFF)), conv(u >> _c(16))]
_FUNCS.update(
  hw_dot2_f32_f16=lambda a, b, c: _hw_dot(_halves(a, _h2f), _halves(b, _h2f), _as(c, dtypes.float32), -14, 'f32', -126).bitcast(dtypes.float32),
  hw_dot2_f32_bf16=lambda a, b, c: _hw_dot(_halves(a, _b2f), _halves(b, _b2f), _as(c, dtypes.float32), -126, 'f32', -126).bitcast(dtypes.float32),
  hw_dot2_f16_f16=lambda a, b, c: _hw_dot(_halves(a, _h2f), _halves(b, _h2f), _h2f(c), -14, 'f16', -14).bitcast(dtypes.half),
  hw_dot2_bf16_bf16=lambda a, b, c: _hw_dot(_halves(a, _b2f), _halves(b, _b2f), _b2f(c.cast(dtypes.uint32) if c.dtype.itemsize < 4 else c),
                                            -126, 'bf16', -126))
_HW_PCODE = {
  **{f'{p}_{f.upper()}_{t.upper()}': f'D0.{t} = v_{f}_{t}(S0.{t}, S1.{t})' for p in ('V', 'S') for f in ('maximum', 'minimum') for t in _DT
     if not (p == 'S' and t == 'f64')},
  **{f'V_{f.upper()}_NUM_F16': f'D0.f16 = v_{f}_num_f16(S0.f16, S1.f16)' for f in ('max', 'min')},
  **{f'{p}_RNDNE_{t.upper()}': f'D0.{t} = hw_rndne(S0.{t})' for p in ('V', 'S') for t in _DT if not (p == 'S' and t == 'f64')},
  **{f'V_MED3_NUM_{t.upper()}': f'D0.{t} = hw_med3(S0.{t}, S1.{t}, S2.{t})' for t in ('f16', 'f32')},
  'V_CVT_FLOOR_I32_F32': 'D0.i32 = hw_cvt_floor(S0.f32)', 'V_CVT_NEAREST_I32_F32': 'D0.i32 = hw_cvt_nearest(S0.f32)',
  **{f'V_FREXP_MANT_{t.upper()}': f'D0.{t} = hw_frexp_mant(S0.{t})' for t in ('f16', 'f32', 'f64')},
  'V_FREXP_EXP_I32_F32': 'D0.i32 = hw_frexp_exp(S0.f32)', 'V_FREXP_EXP_I16_F16': 'D0.i16 = 16\'I(hw_frexp_exp(S0.f16))',
  'V_FREXP_EXP_I32_F64': 'D0.i32 = hw_frexp_exp(S0.f64)',
  **{f'V_FRACT_{t.upper()}': f'D0.{t} = hw_fract(S0.{t})' for t in ('f16', 'f32', 'f64')},
  'V_LDEXP_F16': 'D0.f16 = hw_ldexp(S0.f16, S1.i16)', 'V_LDEXP_F64': 'D0.f64 = hw_ldexp(S0.f64, S1.i32)',
  'V_SIN_F16': 'D0.f16 = hw_sin16(S0.f16)', 'V_COS_F16': 'D0.f16 = hw_cos16(S0.f16)',
  'V_SIN_F32': 'D0.f32 = hw_sin32(S0.f32)', 'V_COS_F32': 'D0.f32 = hw_cos32(S0.f32)',
  'V_CVT_OFF_F32_I4': 'D0.f32 = hw_cvt_off(S0.u32)',
  **{f'V_DIV_FMAS_{t.upper()}': f'if VCC.u64[laneId] then\nD0.{t} = hw_div_fmas_scaled(S0.{t}, S1.{t}, S2.{t})\nelse\n'
                                 f'D0.{t} = fma(S0.{t}, S1.{t}, S2.{t})\nendif' for t in ('f32', 'f64')},
  'S_CVT_PK_RTZ_F16_F32': 'D0.b32 = hw_pk_rtz(S0.f32, S1.f32)',
  'V_DOT2_F32_F16': 'D0.f32 = hw_dot2_f32_f16(S0.b32, S1.b32, S2.f32)', 'V_DOT2_F32_BF16': 'D0.f32 = hw_dot2_f32_bf16(S0.b32, S1.b32, S2.f32)',
  'V_DOT2_F16_F16': 'D0.f16 = hw_dot2_f16_f16(S0.b32, S1.b32, S2.f16)', 'V_DOT2_BF16_BF16': 'D0.u16 = hw_dot2_bf16_bf16(S0.b32, S1.b32, S2.u16)',
  'V_CVT_PK_RTZ_F16_F32': 'D0.b32 = hw_pk_rtz(S0.f32, S1.f32)',
}
_VOPD_HW_PCODE = {ir4.VOPDOp.V_DUAL_DOT2ACC_F32_F16: 'D0.f32 = hw_dot2_f32_f16(S0.b32, S1.b32, D0.f32)',  # no rdna4 VOP2 form to borrow
                   ir4.VOPDOp.V_DUAL_DOT2ACC_F32_BF16: 'D0.f32 = hw_dot2_f32_bf16(S0.b32, S1.b32, D0.f32)'}
_get_pcode_isa = get_pcode
def _hw_div_fixup_pcode(t:str) -> str:  # the isa text with gfx1200's underflow (a signed zero, not the smallest denormal)
  op = getattr(ir4.VOP3Op, f'V_DIV_FIXUP_{t.upper()}')
  p = _get_pcode_isa(op).replace(f'-UNDERFLOW_{t.upper()} : UNDERFLOW_{t.upper()}', '-0.0 : 0.0')
  for k, t in (("64'F(0xfff8000000000000LL)", 'f64'), ("16'F(0xfe00)", 'f16'), ("32'F(0xffc00000)", 'f32')): p = p.replace(k, f'hw_dnan(S1.{t})')
  return p
_HW_PCODE.update({f'V_DIV_FIXUP_{t.upper()}': _hw_div_fixup_pcode(t) for t in ('f16', 'f32', 'f64')})
_FUNCS['hw_dnan'] = lambda x: ((x.bitcast(_uint_of(x)) | _c(_DEFAULT_NAN[x.dtype], _uint_of(x))) &  # tied to x: a folded NaN constant loses its sign
                               _c(_DEFAULT_NAN[x.dtype], _uint_of(x))).bitcast(x.dtype)
def _hw_div_fixup16(a:UOp, b:UOp, c:UOp) -> UOp:  # isa order, with a NaN quotient guess becoming a signed inf (as f32/f64)
  a, b, c = _as(a, dtypes.half), _as(b, dtypes.half), _as(c, dtypes.half)
  u = dtypes.uint16
  sgn = (b.bitcast(u) ^ c.bitcast(u)) & _c(0x8000, u)
  inf, zero, dn = (sgn | _c(0x7C00, u)), sgn, (b.bitcast(u) & _c(0, u)) | _c(0xFE00, u)
  ia, ib = b.abs().eq(_c(float('inf'), dtypes.half)), c.abs().eq(_c(float('inf'), dtypes.half))
  zb, zc = b.eq(_c(0.0, dtypes.half)), c.eq(_c(0.0, dtypes.half))
  q = a.ne(a).where(inf, sgn | (a.bitcast(u) & _c(0x7FFF, u)))
  r = (zb | ib).where(inf, (ia | zc).where(zero, q))
  r = ((zb & zc) | (ia & ib)).where(dn, r)
  r = b.ne(b).where(_quiet(b).bitcast(u), r)
  return c.ne(c).where(_quiet(c).bitcast(u), r).bitcast(dtypes.half)
_FUNCS['hw_div_fixup16'] = _hw_div_fixup16
_HW_PCODE['V_DIV_FIXUP_F16'] = 'D0.f16 = hw_div_fixup16(S0.f16, S1.f16, S2.f16)'
def _fp8_nan_in(orig, is_bf8:bool):
  def fn(v):
    b = v.cast(dtypes.uint32) & _c(0xFF) if v.dtype != dtypes.uint32 else v & _c(0xFF)
    nan = ((b & _c(0x7C)).eq(_c(0x7C)) & (b & _c(3)).ne(_c(0))) if is_bf8 else (b & _c(0x7F)).eq(_c(0x7F))
    r = orig(v)
    return nan.where((r.bitcast(dtypes.uint32) & _c(0)) | _c(0xFFC00000), r.bitcast(dtypes.uint32)).bitcast(dtypes.float32) if _hw_float() else r
  return fn
def _fp8_nan_out(orig, code:int):
  def fn(v):
    r = orig(v)
    if not _hw_float(): return r
    x = _as(v, dtypes.float32)
    return x.ne(x).where(_c(code, r.dtype), r)
  return fn
_FUNCS.update(fp8_to_f32=_fp8_nan_in(_FUNCS['fp8_to_f32'], False), bf8_to_f32=_fp8_nan_in(_FUNCS['bf8_to_f32'], True),
              f32_to_fp8=_fp8_nan_out(_FUNCS['f32_to_fp8'], 0xFF), f32_to_bf8=_fp8_nan_out(_FUNCS['f32_to_bf8'], 0xFE),
              float32=lambda s_, e, m: ((s_.cast(dtypes.uint32) << _c(31)) | ((e.cast(dtypes.uint32) & _c(0xFF)) << _c(23)) |
                                        (m.cast(dtypes.uint32) & _c(0x7FFFFF))).bitcast(dtypes.float32))
def _hw_pk8(t:UOp, fn:str) -> UOp:  # two fp8/bf8 bytes -> two f32 in one 64-bit result
  u = t.cast(dtypes.uint32) if t.dtype != dtypes.uint32 else t
  lo, hi = _FUNCS[fn](u & _c(0xFF)).bitcast(dtypes.uint32), _FUNCS[fn]((u >> _c(8)) & _c(0xFF)).bitcast(dtypes.uint32)
  return lo.cast(dtypes.uint64) | (hi.cast(dtypes.uint64) << _c(32, dtypes.uint64))
_FUNCS.update(hw_pk_fp8=lambda t: _hw_pk8(t, 'fp8_to_f32'), hw_pk_bf8=lambda t: _hw_pk8(t, 'bf8_to_f32'),
              hw_mant_bits=lambda x: _as(x, dtypes.float32).bitcast(dtypes.uint32) & _c(0x7FFFFF))
_HW_PCODE.update({f'V_CVT_PK_F32_{k}': f'tmp = OPSEL[0].u1 ? S0[31 : 16] : S0[15 : 0];\nD0.b64 = hw_pk_{k.lower()}(tmp.u32)' for k in ('FP8', 'BF8')})
def _hw_sr8(x:UOp, r:UOp, bf8:bool) -> UOp:
  x, r = _as(x, dtypes.float32), r.cast(dtypes.uint32) if r.dtype != dtypes.uint32 else r
  i32 = dtypes.int32
  mb, emin, kb, maxf = (2, -14, 11, 57344.0) if bf8 else (3, -6, 12, 448.0)
  ax = x.abs().cast(_F64)
  e = (((ax.bitcast(dtypes.uint64) >> _c(52, dtypes.uint64)) & _c(0x7FF, dtypes.uint64)).cast(i32) - _c(1023, i32)).maximum(_c(emin, i32))
  ulp = ((e - _c(mb, i32) + _c(1023, i32)).cast(dtypes.uint64) << _c(52, dtypes.uint64)).bitcast(_F64)
  frac = (r >> _c(kb)).cast(_F64) * _c(2.0 ** -(32 - kb), _F64)
  v = _pcode._floor(ax / ulp + frac) * ulp
  y = v.cast(dtypes.float32)
  y = (x.bitcast(dtypes.uint32) & _c(0x80000000)).ne(_c(0)).where(-y, y)
  q = _FUNCS['f32_to_bf8' if bf8 else 'f32_to_fp8'](y).cast(dtypes.uint32) & _c(0xFF)
  sgn = (x.bitcast(dtypes.uint32) >> _c(24)) & _c(0x80)
  over = sgn | _c(0x7C if bf8 else 0x7F)
  q = (v > _c(maxf, _F64)).where(over, q)
  return x.ne(x).where(_c(0xFE if bf8 else 0xFF), (x.abs().eq(_c(float('inf'), dtypes.float32))).where(over, q))
_FUNCS.update(hw_sr_fp8=lambda x, r: _hw_sr8(x, r, False), hw_sr_bf8=lambda x, r: _hw_sr8(x, r, True))
def _hw_sr_pcode(k:str) -> str:
  def put(hi:int, lo:int) -> str: return f"VGPR[laneId][VDST.u32][{hi} : {lo}].{k.lower()} = hw_sr_{k.lower()}(S0.f32, S1.u32)"
  return '\n'.join(f"{'if' if i == 0 else 'elsif'} OPSEL[3 : 2].u2 == 2'{i}U then\n{put(8*i+7, 8*i)}" for i in range(3)) + \
    f"\nelse\n{put(31, 24)}\nendif"
_HW_PCODE.update({f'V_CVT_SR_{k}_F32': _hw_sr_pcode(k) for k in ('FP8', 'BF8')})
def _hw_qsad(a:UOp, b:UOp, c:UOp, clmp:UOp, masked:bool) -> UOp:
  # four byte SADs of S0's sliding 32-bit windows against S1, each into a 16-bit lane of S2 (masked: S1 zero bytes count 0); clamp saturates
  u64 = dtypes.uint64
  a, b, c = a.bitcast(u64) if a.dtype.itemsize == 8 else a.cast(u64), b.cast(u64), c.bitcast(u64) if c.dtype.itemsize == 8 else c.cast(u64)
  out = _c(0, u64)
  for j in range(4):
    acc = (c >> _c(16 * j, u64)) & _c(0xFFFF, u64)
    for i in range(4):
      x, y = (a >> _c(8 * (i + j), u64)) & _c(0xFF, u64), (b >> _c(8 * i, u64)) & _c(0xFF, u64)
      d = (x > y).where(x - y, y - x)
      acc = acc + (y.eq(_c(0, u64)).where(_c(0, u64), d) if masked else d)
    acc = (clmp.cast(u64).ne(_c(0, u64)) & (acc > _c(0xFFFF, u64))).where(_c(0xFFFF, u64), acc)
    out = out | ((acc & _c(0xFFFF, u64)) << _c(16 * j, u64))
  return out
_FUNCS['hw_amdnan64'] = lambda r, a: _amd_nan(_as(r, _F64), [_as(a, _F64)])  # an invalid op's NaN is the host's otherwise (arm +, x86 -)
_F64C = {"rcp": dict(rb=24, ts=0, nR=32, sh=18, unit=64, neg=True), "rsq": dict(rb=24, ts=0, nR=32, sh=17, unit=128, neg=True),
        "sqrt": dict(rb=25, ts=1, nR=16, sh=17, unit=128, neg=False)}
def _i64(v): return _c(v, dtypes.int64)
def _tab_i64(name:str, i:UOp) -> UOp:
  lo, hi = _tab_word(name, i * _i64(2)).cast(dtypes.uint64), _tab_word(name, i * _i64(2) + _i64(1)).cast(dtypes.uint64)
  return (lo | (hi << _c(32, dtypes.uint64))).bitcast(dtypes.int64)
def _tab_i32(name:str, i:UOp) -> UOp: return _tab_word(name, i).bitcast(dtypes.int32).cast(dtypes.int64)
def _fshr(x:UOp, k) -> UOp:  # floor(x / 2^k) on signed int64 using only shifts of non-negative values
  k = k if isinstance(k, UOp) else _i64(k)
  return (x >= _i64(0)).where(x >> k, _i64(0) - ((_i64(0) - x + (_i64(1) << k) - _i64(1)) >> k))
def _rne_pos(x:UOp, s) -> UOp:  # x >= 0 rounded to nearest even at bit s (s >= 0), returned >> s
  s = s if isinstance(s, UOp) else _i64(s)
  q = x >> s
  r, h = x - (q << s), (s > _i64(0)).where(_i64(1) << (s - _i64(1)).maximum(_i64(0)), _i64(0))
  return q + ((s > _i64(0)) & ((r > h) | (r.eq(h) & (q & _i64(1)).eq(_i64(1))))).cast(dtypes.int64)
def _rne_s(x:UOp, s) -> UOp:
  n = x < _i64(0)
  v = _rne_pos(n.where(_i64(0) - x, x), s)
  return n.where(_i64(0) - v, v)
def _bitlen64(x:UOp) -> UOp:  # x >= 0, exact
  n = _i64(0)
  for b in (32, 16, 8, 4, 2, 1): n = (x >> (n + _i64(b))).ne(_i64(0)).where(n + _i64(b), n)
  return x.eq(_i64(0)).where(_i64(0), n + _i64(1))
def _tab_find(name_k:str, name_v:str, n:int, key:UOp, wide:bool) -> tuple[UOp, UOp]:  # sorted pow2-padded int64 keys
  pos, step = _i64(0), n // 2
  while step:
    pos = (_tab_i64(name_k, pos + _i64(step - 1)) <= key).where(pos + _i64(step), pos)
    step //= 2
  pos = (_tab_i64(name_k, pos + _i64(n - 1)) <= key).where(_i64(n), pos) if n == 1 else pos
  i = (pos - _i64(1)).maximum(_i64(0))
  found = (pos > _i64(0)) & _tab_i64(name_k, i).eq(key)
  return found, (_tab_i64(name_v, i) if wide else _tab_i32(name_v, i))
def _f64_core(op:str, m29:UOp, pidx:UOp) -> UOp:
  sp = _F64C[op]
  ng = 1 << 20
  R, t = m29 >> _i64(sp["rb"]), m29 & _i64((1 << sp["rb"]) - 1)
  tp = t >> _i64(sp["ts"])
  u = tp >> _i64(4)
  ri = pidx * _i64(sp["nR"]) + R
  g = {k: _tab_i64(f"f_{op}_{k}", ri) for k in ("S2", "Z", "R0", "E", "C0", "K", "C1", "C2", "C3")}
  P = g["S2"] * tp
  r = (P >= (_i64(1) << (g["R0"] + _i64(24)))).where(g["R0"] + _i64(1), g["R0"])
  nr, k = _rne_pos(P, r), (g["Z"] - r).maximum(_i64(0))
  lam = (_i64(0) - ((nr + (_i64(1) << k) - _i64(1)) >> k)) if sp["neg"] else nr >> k
  q = u >> _i64(3)
  Q2 = ((q * q) >> _i64(10)) << _i64(10)
  Mq = _rne_s(g["C2"] - g["C3"] * u, 19)
  PP = Q2 * Mq
  an = PP < _i64(0)
  aa = an.where(_i64(0) - PP, PP)
  shv = (_bitlen64(aa) - _i64(24)).maximum(_i64(33))
  rm = _rne_pos(aa, shv) << shv
  A = g["C0"] + _fshr(g["C1"] * u, 20) + _fshr(g["K"] + an.where(_i64(0) - rm, rm), 33)
  nck = _hw_table_len(f"f_{op}_ck") // 8
  found, cv = _tab_find(f"f_{op}_ck", f"f_{op}_cv", nck, (pidx << _i64(40)) + R * _i64(ng) + u, False)
  A = found.where(A + cv, A)
  if op == "rsq":
    b = tp >> _i64(6)
    qb = b >> _i64(3)
    Ad = g["C0"] + _fshr(g["C1"] * b, 20) + _fshr(qb * qb * _fshr(g["C2"] - g["C3"] * b, 19), 33)
    Ad = Ad + _tab_i32("f_rsq_dense", pidx * _i64(ng // 4) + b) + _tab_i32("f_rsq_dA", pidx * _i64(ng) + u)
    pat = _tab_i32("f_rsq_pat", pidx * _i64(1024) + _tab_i32("f_rsq_pidx", pidx * _i64(ng // 4) + b) * _i64(64) + (tp & _i64(63)))
    dense = R.eq(_i64(31))
    A, lam = dense.where(Ad, A), dense.where(pat, lam)
  V = A + _i64(sp["unit"]) * lam
  mant = (V.cast(dtypes.uint64) << _c(sp["sh"], dtypes.uint64)) & _c((1 << 52) - 1, dtypes.uint64)
  out = (g["E"].cast(dtypes.uint64) << _c(52, dtypes.uint64)) | mant
  nei = _hw_table_len(f"f_{op}_ei") // 8
  if nei:
    found, eh = _tab_find(f"f_{op}_ei", f"f_{op}_eh", nei, (pidx << _i64(40)) + m29, True)
    out = found.where(eh.bitcast(dtypes.uint64), out)
  return out
def _hw_f64op(a:UOp, op:str) -> UOp:
  i64, u64 = dtypes.int64, dtypes.uint64
  M52 = (1 << 52) - 1
  xb = _as(a, _F64).bitcast(u64)
  s = (xb >> _c(63, u64)).cast(i64)
  e = ((xb >> _c(52, u64)) & _c(0x7FF, u64)).cast(i64)
  m = (xb & _c(M52, u64)).cast(i64)
  den = e.eq(_i64(0)) & m.ne(_i64(0))
  lz = den.where(_i64(53) - _bitlen64(m), _i64(0))
  mn = den.where((m << lz) & _i64(M52), m)
  ee = den.where(_i64(1) - lz, e)
  m29, low = mn >> _i64(23), mn & _i64((1 << 23) - 1)
  par = ee & _i64(1)
  if op == "rcp": core, ce = _f64_core(op, m29, _i64(0)), _i64(1023)
  else: core, ce = _f64_core(op, m29, _i64(1) - par), par.eq(_i64(1)).where(_i64(1023), _i64(1024))
  E = (core >> _c(52, u64)).cast(i64) & _i64(0x7FF)
  cm = (core & _c(M52, u64)).cast(i64)
  if op != "sqrt":
    dec = m29.eq(_i64(0)) & low.ne(_i64(0))
    if op == "rsq": dec = dec & par.eq(_i64(1))
    E, cm = dec.where(E - _i64(1), E), dec.where(_i64(M52), cm)
  up = mn.eq(_i64(M52)) if op == "rcp" else None
  if up is not None: cm = up.where(_i64(1), cm)
  de = (ce - ee) if op == "rcp" else _fshr((ee - ce) if op == "sqrt" else (ce - ee), 1)
  pe = E + de
  full = cm | _i64(1 << 52)
  k = (_i64(1) - pe).maximum(_i64(0)).minimum(_i64(63))
  dn = full >> k
  if up is not None: dn = dn + (up & (full & ((_i64(1) << k) - _i64(1))).ne(_i64(0))).cast(i64)
  out = (pe >= _i64(2047)).where(_i64(0x7FF << 52), (pe <= _i64(0)).where(dn, (pe.maximum(_i64(0)).minimum(_i64(2046)) << _i64(52)) | cm)).cast(u64)
  S = s.cast(u64) << _c(63, u64)
  if op == "rcp": out = out | S
  zero, inf, nan = e.eq(_i64(0)) & m.eq(_i64(0)), e.eq(_i64(2047)) & m.eq(_i64(0)), e.eq(_i64(2047)) & m.ne(_i64(0))
  INF, DN, Z0 = _c(0x7FF0000000000000, u64), _c(0xFFF8000000000000, u64), _c(0, u64)
  if op == "rcp": out = zero.where(S | INF, inf.where(S, out))
  elif op == "rsq": out = zero.where(S | INF, (inf & s.eq(_i64(0))).where(Z0, s.eq(_i64(1)).where(DN, out)))
  else: out = zero.where(S, (inf & s.eq(_i64(0))).where(INF, s.eq(_i64(1)).where(DN, out)))
  return nan.where(xb | _c(1 << 51, u64), out).bitcast(_F64)
_FUNCS.update(hw_rcp64=lambda a: _hw_f64op(a, "rcp"), hw_rsq64=lambda a: _hw_f64op(a, "rsq"), hw_sqrt64=lambda a: _hw_f64op(a, "sqrt"))
_HW_PCODE.update({'V_SQRT_F64': 'D0.f64 = hw_sqrt64(S0.f64)', 'V_RSQ_F64': 'D0.f64 = hw_rsq64(S0.f64)', 'V_RCP_F64': 'D0.f64 = hw_rcp64(S0.f64)'})
_FUNCS['hw_trig_preop'] = lambda sh: _pcode._trig_preop(sh, low=18)  # gfx1200 keeps 2/pi down to bit 18 of the 1201
_FUNCS['hw_mqsad'] = lambda a, b, c, clmp: _hw_qsad(a, b, c, clmp, True)
_FUNCS['hw_qsad'] = lambda a, b, c, clmp: _hw_qsad(a, b, c, clmp, False)
_HW_PCODE.update({'V_MQSAD_PK_U16_U8': 'D0.b64 = hw_mqsad(S0.b64, S1.u32, S2.b64, CLMP)',
                  'V_QSAD_PK_U16_U8': 'D0.b64 = hw_qsad(S0.b64, S1.u32, S2.b64, CLMP)',
                  'V_RCP_IFLAG_F32': 'D0.f32 = hw_rcp(S0.f32)',
                  'V_TRIG_PREOP_F64': _get_pcode_isa(ir4.VOP3Op.V_TRIG_PREOP_F64).replace('D0.f64 = ldexp(result, scale)',
                                                                                          'D0.f64 = hw_ldexp(result, scale)')
                                                                                          .replace('trig_preop_result(shift)', 'hw_trig_preop(shift)')
})
def _div_scale_fields(x:UOp) -> tuple[UOp, int, int]:
  ut, mb = (dtypes.uint64, 52) if x.dtype == _F64 else (dtypes.uint32, 23)
  return ((x.bitcast(ut) >> _c(mb, ut)) & _c(0x7FF if x.dtype == _F64 else 0xFF, ut)).cast(dtypes.int32), mb, 0
def _hw_div_scale(s0:UOp, s1:UOp, s2:UOp) -> UOp:
  f64 = s0.dtype == _F64
  i32, ut = dtypes.int32, (dtypes.uint64 if f64 else dtypes.uint32)
  lim, tiny, big, sc, mb = (768, 53, 2045, 128, 52) if f64 else (96, 24, 253, 64, 23)
  e0, e1, e2 = (_div_scale_fields(x)[0] for x in (s0, s1, s2))
  d = e2 - e1
  den = s0.bitcast(ut).eq(s1.bitcast(ut))
  up = s0 * _c(2.0 ** sc, s0.dtype)
  sinf = ((s0.bitcast(ut) & _c(1 << (mb + (11 if f64 else 8)), ut)) | _c((0x7FF if f64 else 0xFF) << mb, ut)).bitcast(s0.dtype)
  emax = _c(0x7FF if f64 else 0xFF, i32)  # f64 with an inf / NaN s1: a small s0 saturates only up to exponent 116 (measured)
  thr = e1.eq(emax).where(_c(116, i32), _c(sc, i32)) if f64 else _c(sc, i32)
  dn = ((e0 <= thr) & s0.ne(_c(0.0, s0.dtype))).where(sinf, s0 * _c(2.0 ** -sc, s0.dtype))
  r = (e2 <= _c(tiny, i32)).where(up, s0)
  r = (d <= _c(-lim, i32)).where(den.where(s0, up), r)
  r = (e1 >= _c(big, i32)).where((den | (d > _c(-lim, i32))).where(dn, s0), r)
  r = e1.eq(_c(0, i32)).where(up, r)
  r = (d >= _c(lim, i32)).where(den.where(up, s0), r)
  zero = s1.eq(_c(0.0, s1.dtype)) | s2.eq(_c(0.0, s2.dtype))
  return zero.where(_c(_DEFAULT_NAN[s0.dtype], ut), s0.ne(s0).where(_quiet(s0), r).bitcast(ut))  # raw bits: a NaN float constant loses its sign
def _hw_div_scale_vcc(s1:UOp, s2:UOp) -> UOp:
  d = _div_scale_fields(s2)[0] - _div_scale_fields(s1)[0]
  lim = 768 if s1.dtype == _F64 else 96
  return ((d >= _c(lim, dtypes.int32)) | (d <= _c(-lim, dtypes.int32))).cast(dtypes.uint32)
_FUNCS.update(hw_div_scale=_hw_div_scale, hw_div_scale_vcc=_hw_div_scale_vcc)
_HW_PCODE.update({f'V_DIV_SCALE_{t.upper()}': f'VCC.u64[laneId] = hw_div_scale_vcc(S1.{t}, S2.{t});\nD0.{b} = hw_div_scale(S0.{t}, S1.{t}, S2.{t})'
                  for t, b in (('f32', 'b32'), ('f64', 'b64'))})
_HW_PCODE.update({'V_FMA_DX9_ZERO_F32': 'D0.f32 = hw_fma_dx9(S0.f32, S1.f32, S2.f32)', 'V_MULLIT_F32': 'D0.f32 = hw_mullit(S0.f32, S1.f32, S2.f32)'})
def _hw_cube_pcode(name:str) -> str:  # the isa text on flushed inputs, NaN results quieted and denormal results flushed
  p = _get_pcode_isa(getattr(ir4.VOP3Op, name))
  pre = 'X0 = hw_ftz(S0.f32);\nX1 = hw_ftz(S1.f32);\nX2 = hw_ftz(S2.f32);\n'
  lines = [l.replace('S0.f32', 'X0').replace('S1.f32', 'X1').replace('S2.f32', 'X2') if l.startswith(('if', 'elsif')) or name == 'V_CUBEMA_F32' else l
           for l in p.split('\n')]
  return pre + '\n'.join(lines) + (';\nD0.f32 = hw_ftz0(hw_quietf(D0.f32))' if name == 'V_CUBEMA_F32' else ';\nD0.f32 = hw_quietf(D0.f32)')
_HW_PCODE.update({n: _hw_cube_pcode(n) for n in ('V_CUBEID_F32', 'V_CUBEMA_F32', 'V_CUBESC_F32', 'V_CUBETC_F32')})
def _hw_interp_pcode(name:str) -> str:
  p = _get_pcode_isa(getattr(ir4.VINTERPOp, name))
  if name == 'V_INTERP_P2_F16_F32': return p.replace("D0.f16 = 16'F(fma(", 'D0.f16 = hw_fma16_once(').replace('S2.f32))', 'S2.f32)')
  if name == 'V_INTERP_P2_RTZ_F16_F32': return p.replace('D0.f32 = fma(', 'D0.f16 = hw_fma_rtz16(')
  return p.replace('D0.f32 = fma(', 'D0.f32 = hw_fma_rtz32(')
_HW_PCODE.update({n: _hw_interp_pcode(n) for n in ('V_INTERP_P2_F16_F32', 'V_INTERP_P2_RTZ_F16_F32', 'V_INTERP_P10_RTZ_F16_F32')})
def _hw_pk_fma16(a:UOp, b:UOp, c:UOp) -> UOp:  # one rounding even for a shared product; inf*0 outranks a NaN addend (default NaN)
  a, b, c = _as(a, dtypes.half), _as(b, dtypes.half), _as(c, dtypes.half)
  inf, zero = _c(float('inf'), dtypes.half), _c(0.0, dtypes.half)
  inf0 = (a.abs().eq(inf) & b.eq(zero)) | (b.abs().eq(inf) & a.eq(zero))
  dn = ((a.bitcast(dtypes.uint16) | _c(0xFE00, dtypes.uint16)) & _c(0xFE00, dtypes.uint16)).bitcast(dtypes.half)  # tied to a: no folded NaN constant
  return inf0.where(dn, _fma16_once(a, b, c))
_FUNCS['hw_pk_fma16'] = _hw_pk_fma16
_HW_PCODE['V_PK_FMA_F16'] = _get_pcode_isa(ir4.VOP3POp.V_PK_FMA_F16).replace('= fma(', '= hw_pk_fma16(')
def _hw_interp_neg(p:str) -> str:  # neg applies to the cross-lane operands too: wrap the VGPR reads of src0/src2
  def rep(m):
    v = f"VGPR[{m.group(1)}][SRC{m.group(2)}.u32]"
    v = f"hw_hisel({v}.u32, OPSEL, {m.group(2)})" if m.group(3) == 'f16' else f"{v}.f32"   # opsel picks an f16 operand's high half
    return f"hw_negsel({v}, NEG, {m.group(2)})"
  return re.sub(r"VGPR\[([^\]]*)\]\[SRC(\d)\.u32\]\.(f16|f32)", rep, p)
for _n in ('V_INTERP_P10_F32', 'V_INTERP_P2_F32', 'V_INTERP_P10_F16_F32', 'V_INTERP_P2_F16_F32', 'V_INTERP_P10_RTZ_F16_F32',
           'V_INTERP_P2_RTZ_F16_F32'):
  _HW_PCODE[_n] = _hw_interp_neg(_HW_PCODE.get(_n) or _get_pcode_isa(getattr(ir4.VINTERPOp, _n)))
def _negsel(x:UOp, neg:UOp, bit:UOp) -> UOp:
  ut = _uint_of(x)
  on = ((neg.cast(dtypes.uint32) >> bit.cast(dtypes.uint32)) & _c(1)).ne(_c(0))
  return on.where((x.bitcast(ut) ^ _c(1 << (8 * x.dtype.itemsize - 1), ut)).bitcast(x.dtype), x)
_FUNCS['hw_negsel'] = _negsel
def _hisel(v:UOp, sel:UOp, bit:UOp) -> UOp:
  hi = ((sel.cast(dtypes.uint32) >> bit.cast(dtypes.uint32)) & _c(1)).ne(_c(0))
  return (hi.where(v >> _c(16), v) & _c(0xFFFF)).cast(dtypes.uint16).bitcast(dtypes.half)
_FUNCS['hw_hisel'] = _hisel
def get_pcode(op) -> str:  # type: ignore[no-redef]
  if HW_FLOAT.value and 'rdna4' in type(op).__module__:
    if (p := _HW_PCODE.get(op.name.replace('_E64', '').replace('_E32', ''))) is not None: return p
  return _get_pcode_isa(op)

HW_FLOAT_MODE = 0xF0
_FLOAT_OP = re.compile(r"_(f16|f32|f64|bf16|fp8|bf8)\b|_(f16|f32|f64|bf16)_|wmma|swmmac|_dot\d|_pk_")
_SIG_FIELDS = ("clmp", "omod", "abs", "neg", "neg_hi", "opsel", "opsel_hi", "opsel_hi2")
@functools.cache
def _hw_sigs() -> tuple[frozenset[str], dict[str, dict[str, int]]]:
  with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gfx1200_verified.sigs")) as f:
    lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
  bases = {(b:=l.split(" ", 1)[1]).split("|")[0]: _sig_fields(b) for l in lines if l.startswith("fields ")}
  return frozenset(l for l in lines if not l.startswith("fields ")), bases
def hw_verified() -> frozenset[str]: return _hw_sigs()[0]
def _sig_fields(sig:str) -> dict[str, int]: return {k: int(v) for k, v in (f.split("=") for f in sig.split("|")[1:])}
def _make_sig(op:str, fields:dict[str, int]) -> str: return "|".join([op] + [f"{f}={fields[f]}" for f in _SIG_FIELDS if fields.get(f, 0)])
_BIT_FIELDS = ("abs", "neg", "neg_hi", "opsel")
def sig_verified(sig:str) -> bool:
  verified, bases = _hw_sigs()
  if sig in verified: return True
  op, fields = sig.split("|")[0], _sig_fields(sig)
  if (base := bases.get(op)) is None: return False
  atoms = []
  for f in _SIG_FIELDS:
    q, b = fields.get(f, 0), base.get(f, 0)
    if q == b: continue
    atoms += [{**base, f: b ^ bit} for bit in (1 << i for i in range(8)) if (q ^ b) & bit] if f in _BIT_FIELDS else [{**base, f: q}]
  return all(_make_sig(op, a) in verified for a in atoms)
def inst_signature(inst) -> str: return _make_sig(inst.op_name.lower(), {f: getattr(inst, f, 0) or 0 for f in _SIG_FIELDS})
EMU_CACHE = ContextVar("EMU_CACHE", 1)
@functools.cache
def _emu_digest() -> str:
  import tinygrad
  h = hashlib.sha256()
  here = pathlib.Path(__file__).parent
  for f in sorted([*pathlib.Path(tinygrad.__file__).parent.rglob("*.py"), *here.glob("*.py"), *here.glob("*.sigs"), *here.glob("gfx1200_*.npz")]):
    h.update(str(f.relative_to(f.parents[1])).encode() + b"\0" + f.read_bytes() + b"\0")
  try:
    from tinygrad.runtime.autogen import llvm
    st = os.stat(path:=llvm.dll._name)
    h.update(f"{path}:{st.st_size}:{st.st_mtime_ns}".encode())
  except Exception as e: h.update(f"no llvm: {e}".encode())
  return h.hexdigest()
@functools.cache
def _host_cpu() -> str:
  from tinygrad.runtime.autogen import llvm
  return ctypes.string_at(llvm.LLVMGetHostCPUName()).decode() + ":" + ctypes.string_at(llvm.LLVMGetHostCPUFeatures()).decode()
def _cache_key(*parts) -> str: return hashlib.sha256(pickle.dumps((_emu_digest(), *parts))).hexdigest()
def _cached(table:str, key:str, fn:Callable):
  from tinygrad.helpers import diskcache_get, diskcache_put
  if not EMU_CACHE.value: return fn()
  if (ret:=diskcache_get(table, key)) is None:
    ret = fn()
    try: diskcache_put(table, key, ret)
    except Exception as e:
      if DEBUG >= 1: print(f"emu cache: {table} not stored: {type(e).__name__}: {e}")
  return ret

def hw_unverified(elf:bytes) -> dict[str, int]:
  return dict(_cached("emu_hw_unverified", _cache_key(elf, HW_FLOAT_MODE), lambda: _hw_unverified(elf)))
def _hw_unverified(elf:bytes) -> dict[str, int]:
  out:dict[str, int] = {}
  mode = (int.from_bytes(get_elf_section(elf, ".rodata").content[48:52], "little") >> 12) & 0xFF
  if mode != HW_FLOAT_MODE: out[f"float_mode=0x{mode:02x}"] = 1
  for inst in amd_decode(get_elf_section(elf, ".text").content, "rdna4").values():
    if isinstance(inst, ir4.VOPD):  # dual issue: two ops and no modifiers, each half is its own signature
      sigs = [o.name.lower() for o in (inst.opx, inst.opy)]
    elif hasattr(inst, "op_name"): sigs = [inst_signature(inst)]
    else: continue
    for sig in sigs:
      if _FLOAT_OP.search(sig.split("|")[0]) and not sig_verified(sig): out[sig] = out.get(sig, 0) + 1
  return out

def _compile_sopp(inst: ir3.SOPP | ir4.SOPP, ctx: _Ctx) -> UOp:
  simm16 = ctx.inst_field_signed(type(inst).simm16).cast(dtypes.int16)
  if inst.op in (ir3.SOPPOp.S_ENDPGM, ir4.SOPPOp.S_ENDPGM, irc.SOPPOp.S_ENDPGM):
    return UOp.sink()
  # barriers are represented by block boundaries in the lifter.
  if inst.op in _BARRIER_OPS: return UOp.sink()
  # S_NOP and S_WAITCNT are no-ops in emulator (no pipeline/cache to wait on)
  if inst.op in (ir3.SOPPOp.S_NOP, ir4.SOPPOp.S_NOP, irc.SOPPOp.S_NOP, irc.SOPPOp.S_WAITCNT): return UOp.sink()
  # NOTE: we ignore SOPPs without PCODE
  if inst.op in _get_pcode_dict(inst.op):
    pcode = get_pcode(inst.op)
    vcc, exec_val = ctx.rmask(_c(VCC_LO.offset)), ctx.rexec()
    srcs = {'PC': _c(0, dtypes.uint32), 'SIMM16': simm16, 'SCC': ctx.rsgpr_dyn(_c(SCC.offset)), 'VCC': vcc,
            'VCCZ': vcc.eq(_c(0, vcc.dtype)).cast(dtypes.uint32), 'EXECZ': exec_val.eq(_c(0, exec_val.dtype)).cast(dtypes.uint32)}
    for dest, val in parse_pcode(pcode, srcs)[1]:
      if dest.startswith('PC') and val.op is Ops.WHERE: ctx.branch_cond = val.src[0]
  return UOp.sink()

def _compile_smem(inst: ir3.SMEM | ir4.SMEM, ctx: _Ctx) -> UOp:
  # Dynamic sbase field (bits 5:0) - SGPR pair, field value * 2 = register offset
  sbase = ctx.inst_field(type(inst).sbase) * _c(2)
  # Dynamic sdata field (bits 12:6) - destination SGPR
  sdata_reg = ctx.inst_field(type(inst).sdata)
  # RDNA4 uses 'ioffset', RDNA3 uses 'offset' - use type(inst) to get correct field
  offset_field = type(inst).ioffset if hasattr(type(inst), 'ioffset') else type(inst).offset  # type: ignore[union-attr]
  offset = ctx.inst_field_signed(offset_field)  # signed immediate
  # Dynamic soffset field - SGPR for additional offset (NULL=124 reads as 0, CDNA soffset_en=0 means no soffset)
  soffset_val = _c(0).cast(dtypes.uint64)
  if not (isinstance(inst, irc.SMEM) and not inst.soffset_en):
    soffset_val = ctx.rsgpr_dyn(ctx.inst_field(type(inst).soffset)).cast(dtypes.uint64)
  base = _u64(ctx.rsgpr_dyn(sbase), ctx.rsgpr_dyn(sbase + _c(1)))
  byte_offset = offset.cast(dtypes.uint64) + soffset_val
  srcs = {'ADDR': base + byte_offset, 'sgpr_base': base, 'offset': byte_offset,
          'SBASE': base, 'SOFFSET': soffset_val, 'OFFSET': offset, '_vmem': ctx.vmem}
  funcs = {'CalcScalarGlobalAddr': lambda _base, soffset, offset: base + soffset.cast(dtypes.uint64) + offset.cast(dtypes.uint64)}
  _, assigns = parse_pcode(get_pcode(inst.op), srcs, funcs)
  stores = [ctx.wsgpr_dyn(sdata_reg + _c(i), val) for i, val in _collect_data_slices(assigns, 'SDATA').items()]
  return UOp.sink(*stores)

def _compile_sop(inst: ir3.SOP1|ir3.SOP2|ir3.SOPC|ir3.SOPK|ir4.SOP1|ir4.SOP2|ir4.SOPC|ir4.SOPK|irc.SOP1|irc.SOP2|irc.SOPC|irc.SOPK, ctx: _Ctx) -> UOp:
  bits = inst.canonical_op_bits
  literal = ctx.optional_field(inst, 'literal')

  if isinstance(inst, (ir3.SOPK, ir4.SOPK, irc.SOPK)):
    sdst_off = ctx.inst_field(type(inst).sdst)
    simm16 = ctx.inst_field(type(inst).simm16)
    # Sign-extend simm16
    simm16_sext = simm16.cast(dtypes.int16).cast(dtypes.int32)
    # RDNA4 pcodes use S0.i16 for the immediate (e.g., S_MULK_I32), RDNA3 uses S0 for the register (e.g., S_CMPK_*)
    # CDNA pcode uses S0 for the immediate in MOVK/MULK/ADDK/CMOVK, but S0 = register for CMPK/SETREG
    op_name = _op_name(inst)
    if isinstance(inst, ir4.SOPK): s0 = simm16
    elif isinstance(inst, irc.SOPK) and 'CMPK' not in op_name and 'SETREG' not in op_name: s0 = simm16_sext
    else: s0 = ctx.rsgpr_dyn(sdst_off)
    srcs: dict[str, UOp|int] = {'S0': s0, 'S1': simm16_sext, 'SIMM16': simm16_sext, 'D0': ctx.rsgpr_dyn(sdst_off)}
    dst_off, dst_size = sdst_off, 1
    # S_GETREG_B32: extract bits from HW register. Handle as special case since HW_REGISTERS is not a normal variable.
    # HW register values are stored at SGPR[SGPR_COUNT-16 + hwRegId] by init_wave.
    if 'GETREG' in op_name:
      hw_reg_id = simm16.cast(dtypes.uint32) & _c(0x3F)
      offset = (simm16.cast(dtypes.uint32) >> _c(6)) & _c(0x1F)
      size = ((simm16.cast(dtypes.uint32) >> _c(11)) & _c(0x1F)) + _c(1)
      hw_val = ctx.rsgpr_dyn(_c(SGPR_COUNT - 16) + hw_reg_id)
      mask = (_c(1) << size) - _c(1)
      result = (hw_val >> offset) & mask
      return UOp.sink(ctx.wsgpr_dyn(sdst_off, result))
  elif isinstance(inst, (ir3.SOP1, ir4.SOP1, irc.SOP1)):
    # S_BARRIER_SIGNAL: no-op in emulator, barrier sync handled by execution loop
    if isinstance(inst, ir4.SOP1) and inst.op in _BARRIER_SOP1_OPS: return UOp.sink()
    sdst_off = ctx.inst_field(type(inst).sdst)
    ssrc0_off = ctx.inst_field(type(inst).ssrc0)
    srcs = {'S0': ctx.rsrc_dyn(ssrc0_off, None, bits['s0'], literal)}
    dst_off, dst_size = sdst_off, bits['d'] // 32
  elif isinstance(inst, (ir3.SOP2, ir4.SOP2, irc.SOP2)):
    sdst_off = ctx.inst_field(type(inst).sdst)
    ssrc0_off = ctx.inst_field(type(inst).ssrc0)
    ssrc1_off = ctx.inst_field(type(inst).ssrc1)
    srcs = {'S0': ctx.rsrc_dyn(ssrc0_off, None, bits['s0'], literal), 'S1': ctx.rsrc_dyn(ssrc1_off, None, bits['s1'], literal)}
    if literal is not None: srcs['SIMM32'] = literal
    dst_off, dst_size = sdst_off, bits['d'] // 32
  elif isinstance(inst, (ir3.SOPC, ir4.SOPC, irc.SOPC)):
    ssrc0_off = ctx.inst_field(type(inst).ssrc0)
    ssrc1_off = ctx.inst_field(type(inst).ssrc1)
    srcs = {'S0': ctx.rsrc_dyn(ssrc0_off, None, bits['s0'], literal), 'S1': ctx.rsrc_dyn(ssrc1_off, None, bits['s1'], literal)}
    dst_off, dst_size = _c(0), 0  # SOPC writes to SCC, not sdst
  else:
    raise RuntimeError(f"unknown SOP type: {type(inst).__name__}")

  return ctx.compile_sop_pcode(inst.op, srcs, dst_off, dst_size)

def _sdwa_select(val: UOp, sel: UOp, sext: UOp) -> UOp:
  """Apply SDWA byte/word selection and optional sign extension to a 32-bit value."""
  # sel: 0-3=BYTE_0..3, 4=WORD_0, 5=WORD_1, 6=DWORD
  b0 = val & _c(0xFF)
  b1 = (val >> _c(8)) & _c(0xFF)
  b2 = (val >> _c(16)) & _c(0xFF)
  b3 = (val >> _c(24)) & _c(0xFF)
  w0 = val & _c(0xFFFF)
  w1 = (val >> _c(16)) & _c(0xFFFF)
  selected = sel.eq(_c(1)).where(b1, sel.eq(_c(2)).where(b2, sel.eq(_c(3)).where(b3,
    sel.eq(_c(4)).where(w0, sel.eq(_c(5)).where(w1, sel.eq(_c(6)).where(val, b0))))))
  # Sign extend when sext=1
  is_byte = sel < _c(4)
  byte_sext = (selected & _c(0x80)).ne(_c(0)).where(selected | _c(0xFFFFFF00), selected)
  word_sext = (selected & _c(0x8000)).ne(_c(0)).where(selected | _c(0xFFFF0000), selected)
  return sext.ne(_c(0)).where(is_byte.where(byte_sext, word_sext), selected)

def _sdwa_write(old: UOp, val: UOp, dst_sel: UOp, dst_unused: UOp) -> UOp:
  """Apply SDWA destination selection: write selected byte/word, handle unused bits."""
  # dst_unused: 0=PAD(zero), 1=SEXT, 2=PRESERVE
  # dst_sel: 0-3=BYTE, 4=WORD_0, 5=WORD_1, 6=DWORD
  is_byte = dst_sel < _c(4)
  is_word = (dst_sel >= _c(4)) & (dst_sel < _c(6))
  shift = is_byte.where(dst_sel * _c(8), (dst_sel - _c(4)) * _c(16))
  mask = is_byte.where(_c(0xFF), is_word.where(_c(0xFFFF), _c(0xFFFFFFFF)))
  placed = (val & mask) << shift
  preserve_mask = (mask << shift) ^ _c(0xFFFFFFFF)
  preserved = (old & preserve_mask) | placed
  # For PAD and SEXT, unused bits are zero (PAD) or sign-extended (SEXT). For DWORD, just return val.
  return dst_sel.eq(_c(6)).where(val, dst_unused.eq(_c(2)).where(preserved, placed))

def _dpp_quad_sel(quad_lane: UOp, sels: tuple[int, int, int, int]) -> UOp:
  sel = _c(sels[0], dtypes.int)
  for i, src in enumerate(sels[1:], start=1): sel = quad_lane.eq(_c(i, dtypes.int)).where(_c(src, dtypes.int), sel)
  return sel

def _dpp16_ctrl(lane: UOp, dpp: int, row_mask: int, bank_mask: int, wave_size: int) -> tuple[UOp, UOp, UOp]:
  """Return (src_lane, row/bank enabled, in-bounds) for a DPP16 swizzle."""
  lane_i = lane.cast(dtypes.int)
  row_base, lane_in_row = lane_i & _c(~15, dtypes.int), lane_i & _c(15, dtypes.int)
  row = lane_i // _c(16, dtypes.int)
  bank = lane_in_row >> _c(2, dtypes.int)
  enabled = (((_c(row_mask) >> row.cast(dtypes.uint32)) & _c(1)).ne(_c(0)) & (((_c(bank_mask) >> bank.cast(dtypes.uint32)) & _c(1)).ne(_c(0))))
  op, arg = decode_dpp16(dpp)
  src_lane, valid = lane_i, UOp.const(True)

  if op == 'quad_perm':
    assert isinstance(arg, tuple)
    src_lane = (lane_i & _c(~3, dtypes.int)) + _dpp_quad_sel(lane_i & _c(3, dtypes.int), arg)
  else:
    assert isinstance(arg, int)
    if op == 'row_shl': src_lane, valid = row_base + lane_in_row + _c(arg, dtypes.int), lane_in_row <= _c(15 - arg, dtypes.int)
    elif op == 'row_shr': src_lane, valid = row_base + lane_in_row - _c(arg, dtypes.int), lane_in_row >= _c(arg, dtypes.int)
    elif op == 'row_ror': src_lane = row_base + ((lane_in_row - _c(arg, dtypes.int)) & _c(15, dtypes.int))
    elif op == 'row_mirror': src_lane = row_base + (_c(15, dtypes.int) - lane_in_row)
    elif op == 'row_half_mirror': src_lane = row_base + ((lane_in_row & _c(8, dtypes.int)) | (_c(7, dtypes.int) - (lane_in_row & _c(7, dtypes.int))))
    elif op == 'row_bcast': src_lane = row_base
    elif op == 'row_newbcast' and wave_size == 32: src_lane = row_base + _c(arg, dtypes.int)
    elif op == 'row_share' and wave_size == 32: src_lane = row_base + (lane_in_row ^ _c(arg, dtypes.int))
    elif op == 'wave_shl': src_lane, valid = lane_i + _c(arg, dtypes.int), lane_i < _c(wave_size - arg, dtypes.int)
    elif op == 'wave_rol': src_lane = (lane_i + _c(arg, dtypes.int)) % _c(wave_size, dtypes.int)
    elif op == 'wave_shr': src_lane, valid = lane_i - _c(arg, dtypes.int), lane_i >= _c(arg, dtypes.int)
    elif op == 'wave_ror': src_lane = (lane_i - _c(arg, dtypes.int)) % _c(wave_size, dtypes.int)
    else: raise NotImplementedError(f"DPP16 control {dpp:#x} ({op}:{arg}) not implemented in emulator")
  return src_lane, enabled, valid

def _hw_dpp_src0(ctx: _Ctx, inst, lane: UOp) -> tuple[UOp, UOp]:
  lane_i = lane.cast(dtypes.int)
  if not hasattr(type(inst), 'lane_sel_0') and getattr(getattr(inst, 'src0', None), 'offset', 0) in (233, 234):
    d8 = object.__new__(getattr(ir4, type(inst).__name__.replace('_DPP16', '_DPP8')))
    d8._raw = inst._raw
    inst = d8
  if hasattr(type(inst), 'lane_sel_0'):
    sels = [_iattr(inst, f'lane_sel_{i}') for i in range(8)]
    sel = _c(sels[7], dtypes.int)
    for i in range(6, -1, -1): sel = (lane_i & _c(7, dtypes.int)).eq(_c(i, dtypes.int)).where(_c(sels[i], dtypes.int), sel)
    return ctx.rvgpr_dyn(ctx.inst_field(type(inst).vsrc0), (lane_i & _c(~7, dtypes.int)) + sel), UOp.const(False, dtypes.bool)
  src_lane, enabled, valid = _dpp16_ctrl(lane, _iattr(inst, 'dpp'), _iattr(inst, 'row_mask', 0xf), _iattr(inst, 'bank_mask', 0xf), ctx.wave_size)
  v = ctx.rvgpr_dyn(ctx.inst_field(type(inst).vsrc0), (enabled & valid).where(src_lane, _c(0, dtypes.int)))
  bc = bool(_iattr(inst, 'bc'))
  return valid.where(v, _c(0, v.dtype)), ~enabled | (~valid & UOp.const(not bc, dtypes.bool))

def _dpp_src0(ctx: _Ctx, inst, lane: UOp, val: UOp) -> UOp:  # a vop3 / vop3p / vop3sd dpp src0 is the swizzled vsrc0; records the kept lanes
  if not (_hw_float() and isinstance(inst, (ir4.VOP3, ir4.VOP3P, ir4.VOP3SD)) and hasattr(type(inst), 'vsrc0')): return val
  v, ctx.dpp_keep = _hw_dpp_src0(ctx, inst, lane)
  return _pk_dpp_lo(ctx, inst, lane, v)
def _pk_dpp_lo(ctx: _Ctx, inst, lane: UOp, v: UOp) -> UOp:  # v_pk_* (two 16-bit lanes): only the high half comes through the swizzle
  if not _op_name(inst).startswith('V_PK_'): return v
  own = ctx.rvgpr_dyn(ctx.inst_field(type(inst).vsrc0), lane.cast(dtypes.int))
  return (v.cast(dtypes.uint32) & _c(0xFFFF0000)) | (own & _c(0xFFFF))
def _dpp_store(ctx: _Ctx, vdst_reg: UOp, lane: UOp, val: UOp, exec_mask: UOp) -> UOp:
  keep, ctx.dpp_keep = ctx.dpp_keep, None
  return ctx.wvgpr_dyn(vdst_reg, lane, val if keep is None else keep.where(ctx.rvgpr_dyn(vdst_reg, lane), val), exec_mask)

def _load_dpp16_src0(ctx: _Ctx, inst, lane: UOp, fallback: UOp) -> UOp:
  """Load a DPP16-swizzled src0 value from vsrc0."""
  src_lane, enabled, valid = _dpp16_ctrl(lane, _iattr(inst, 'dpp'), _iattr(inst, 'row_mask', 0xf), _iattr(inst, 'bank_mask', 0xf), ctx.wave_size)
  safe_src_lane = (enabled & valid).where(src_lane, _c(0, dtypes.int))
  swizzled = ctx.rvgpr_dyn(ctx.inst_field(type(inst).vsrc0), safe_src_lane)
  invalid = _c(0, fallback.dtype) if _iattr(inst, 'bc') else fallback
  return enabled.where(valid.where(swizzled, invalid), fallback)

def _compile_sdwa(inst: irc.VOP1_SDWA | irc.VOP2_SDWA | irc.VOP2_SDWA_SDST | irc.VOPC_SDWA_SDST, ctx: _Ctx) -> UOp:
  """Compile CDNA SDWA (Sub-Dword Access) VOP1/VOP2/VOPC instructions."""
  is_vopc = isinstance(inst, irc.VOPC_SDWA_SDST)
  exec_mask = ctx.rexec()
  # sd=1 means use sdst register, sd=0 means use VCC (for VOPC_SDWA_SDST and VOP2_SDWA_SDST)
  if isinstance(inst, (irc.VOP2_SDWA_SDST, irc.VOPC_SDWA_SDST)):
    sdst_off = _c(inst.sdst.offset) if _iattr(inst, 'sd') else _c(VCC_LO.offset)
  else:
    sdst_off = _c(VCC_LO.offset)
  # Read SDWA fields (these are dynamic but shared across lanes)
  src0_sel = ctx.inst_field(type(inst).src0_sel)
  src0_sext = ctx.inst_field(type(inst).src0_sext)
  vsrc0_reg = ctx.inst_field(type(inst).vsrc0)
  pcode = get_pcode(inst.op)
  if isinstance(inst, (irc.VOP2_SDWA, irc.VOP2_SDWA_SDST, irc.VOPC_SDWA_SDST)):
    src1_sel = ctx.inst_field(type(inst).src1_sel)
    src1_sext = ctx.inst_field(type(inst).src1_sext)
    vsrc1_reg = ctx.inst_field(type(inst).vsrc1)

  # For VOPC: use unroll_lanes to build the bitmask from scratch (no read-modify-write on stale data)
  if is_vopc:
    def get_cmp_bit(lane: UOp) -> UOp:
      lc = lane.cast(dtypes.int)
      s0_raw = ctx.rsgpr_dyn(vsrc0_reg) if inst.s0 else ctx.rvgpr_dyn(vsrc0_reg, lc)
      s0 = _sdwa_select(s0_raw, src0_sel, src0_sext)
      s1_raw = ctx.rsgpr_dyn(vsrc1_reg) if inst.s1 else ctx.rvgpr_dyn(vsrc1_reg, lc)
      s1 = _sdwa_select(s1_raw, src1_sel, src1_sext)
      for dest, val in parse_pcode(pcode, {'S0': s0, 'S1': s1, 'laneId': lc})[1]:
        if '[laneId]' in dest and ('D0' in dest or 'EXEC' in dest): return val.cast(dtypes.uint32)
      return _c(0)
    new_result = ctx.unroll_lanes(get_cmp_bit, exec_mask)
    stores = ctx.wmask(sdst_off, new_result)
    return UOp.sink(*stores)

  # Non-VOPC path: VOP1_SDWA, VOP2_SDWA, VOP2_SDWA_SDST — uses lane loop
  lane = ctx.range()
  vdst_reg = ctx.inst_field(type(inst).vdst)  # type: ignore[union-attr]
  s0_raw = ctx.rsgpr_dyn(vsrc0_reg) if inst.s0 else ctx.rvgpr_dyn(vsrc0_reg, lane)
  s0 = _sdwa_select(s0_raw, src0_sel, src0_sext)
  if isinstance(inst, (irc.VOP2_SDWA, irc.VOP2_SDWA_SDST)):
    s1_raw = ctx.rsgpr_dyn(vsrc1_reg) if inst.s1 else ctx.rvgpr_dyn(vsrc1_reg, lane)
    s1 = _sdwa_select(s1_raw, src1_sel, src1_sext)
    srcs:dict[str, UOp | int] = {'S0': s0, 'S1': s1, 'D0': ctx.rvgpr_dyn(vdst_reg, lane)}
  else:
    srcs = {'S0': s0}
  # dst_sel and dst_unused
  has_dst_sel = hasattr(type(inst), 'dst_sel')
  if has_dst_sel:
    dst_sel = ctx.inst_field(type(inst).dst_sel)  # type: ignore[union-attr]
    dst_unused = ctx.inst_field(type(inst).dst_unused)  # type: ignore[union-attr]
  srcs.update(ctx.base_srcs(exec_mask, lane), VCC=ctx.rmask(_c(VCC_LO.offset)), VDST=vdst_reg)
  _, assigns = parse_pcode(pcode, srcs)
  stores = []
  vcc_val = None
  for dest, val in assigns:
    if 'D0' in dest and '[laneId]' in dest:
      vcc_val = val
    elif dest.startswith('D0'):
      result = _val_to_u32(val)
      if has_dst_sel:
        old = ctx.rvgpr_dyn(vdst_reg, lane)
        result = _sdwa_write(old, result, dst_sel, dst_unused)
      stores.append(ctx.wvgpr_dyn(vdst_reg, lane, result, exec_mask))
    elif dest.startswith('VCC'): vcc_val = val
  if vcc_val is not None:
    mask = ctx.unroll_lanes(lambda l: (_to_u32(vcc_val.substitute({lane:l})) & _c(1)).cast(dtypes.uint32), exec_mask)
    return UOp.sink(*ctx.wmask(sdst_off, mask), UOp.sink(*stores).end(lane))
  if stores:
    return UOp.sink(UOp.sink(*stores).end(lane))
  return UOp.sink()

def _load_vsrc0(ctx: _Ctx, inst: ir3.VOP1 | ir3.VOP1_SDST | ir3.VOP1_DPP16 | ir3.VOP2 | ir3.VOP2_DPP16 |
                ir4.VOP1 | ir4.VOP1_SDST | ir4.VOP1_DPP16 | ir4.VOP2 | ir4.VOP2_DPP16 |
                irc.VOP1 | irc.VOP1_DPP16 | irc.VOP2 | irc.VOP2_DPP16,
                lane: UOp, bits: dict, literal: UOp | None, is_f64: bool, is_float: bool, fallback: UOp) -> tuple[UOp, UOp | None]:
  """Load VOP src0: DPP16 swizzle (with abs/neg mods for floats), 16-bit VGPR hi-half (src0 >= 384), or plain operand.
  Returns (value, src0_offset) - offset is None for DPP16."""
  if _hw_float() and isinstance(inst, (ir4.VOP1, ir4.VOP2)) and hasattr(type(inst), 'vsrc0'):
    s0, ctx.dpp_keep = _hw_dpp_src0(ctx, inst, lane)
    s0 = _pk_dpp_lo(ctx, inst, lane, s0)
    if bits['s0'] == 16: s0 = s0 & _c(0xFFFF)
    if _op_name(inst).startswith('V_PK_FMAC_F16'):  # dpp neg / abs are neg_lo / neg_hi here: each negates one half
      s0 = s0.cast(dtypes.uint32)
      if _iattr(inst, 'src0_neg'): s0 = s0 ^ _c(0x8000)
      if _iattr(inst, 'src0_abs'): s0 = s0 ^ _c(0x80000000)
    elif _op_name(inst).startswith('V_SAT_PK_U8_I16'):  # dpp abs / neg act on both i16 halves
      s0 = s0.cast(dtypes.uint32)
      if _iattr(inst, 'src0_abs'): s0 = s0 & _c(0x7FFF7FFF)
      if _iattr(inst, 'src0_neg'): s0 = s0 ^ _c(0x80008000)
    elif is_float: s0 = _apply_src_mods(s0, 0, 1 if _iattr(inst, 'src0_abs') else 0, 1 if _iattr(inst, 'src0_neg') else 0, bits['s0'])
    return s0, None
  if hasattr(type(inst), 'dpp') and hasattr(type(inst), 'vsrc0'):
    s0 = _load_dpp16_src0(ctx, inst, lane, fallback)
    if is_float: s0 = _apply_src_mods(s0, 0, 1 if _iattr(inst, 'src0_abs') else 0, 1 if _iattr(inst, 'src0_neg') else 0, bits['s0'])
    return s0, None
  src0_off = ctx.inst_field(type(inst).src0)
  s0 = ctx.rsrc_dyn(src0_off, lane, bits['s0'], literal, is_f64, do_cast=_f16_const(inst, 's0'))
  if _hw_float() and isinstance(inst, ir4.VOP2) and inst.op.name == 'V_PK_FMAC_F16_E32': s0 = _pk_const(src0_off, s0, False)
  if bits['s0'] == 16 and not isinstance(inst, (irc.VOP1, irc.VOP2)):  # src0 >= 384 means hi half of v[src0-384]. Guard index against OOB access.
    src0_hi = src0_off >= _c(384)
    s0 = src0_hi.where(_hi16(ctx.rvgpr_dyn(src0_hi.where(src0_off - _c(384), _c(0)), lane)), s0)
  return s0, src0_off

def _compile_vop12(inst: ir3.VOP1 | ir3.VOP1_SDST | ir3.VOP1_DPP16 | ir3.VOP2 | ir3.VOP2_DPP16 |
                   ir4.VOP1 | ir4.VOP1_SDST | ir4.VOP1_DPP16 | ir4.VOP2 | ir4.VOP2_DPP16 |
                   irc.VOP1 | irc.VOP1_DPP16 | irc.VOP2 | irc.VOP2_DPP16, ctx: _Ctx) -> UOp:
  op_name = _op_name(inst)
  if op_name in ('V_READFIRSTLANE_B32_E32', 'V_PERMLANE64_B32_E32'): return ctx.compile_lane_pcode(inst.op, inst)
  # v_accvgpr_mov_b32: ACCVGPR[vdst] = ACCVGPR[src0] (VOP1 encoding, no pcode)
  if 'ACCVGPR_MOV' in op_name:
    lane, exec_mask = ctx.range(), ctx.rexec()
    vdst_reg = ctx.inst_field(type(inst).vdst)  # VGPRField: raw ACCVGPR index (0-255)
    acc_src0_off = ctx.inst_field(type(inst).src0)  # SrcField: raw 256 + ACCVGPR index
    val = ctx.raccvgpr_dyn(acc_src0_off - _c(256), lane)
    return UOp.sink(ctx.waccvgpr_dyn(vdst_reg, lane, val, exec_mask).end(lane))
  lane, exec_mask, bits = ctx.range(), ctx.rexec(), inst.canonical_op_bits
  literal = ctx.optional_field(inst, 'literal')
  is_f64 = 'F64' in op_name and 'B64' not in op_name
  is_float = any(x in op_name for x in ('F16', 'F32', 'F64'))
  is_dpp16 = hasattr(type(inst), 'dpp') and hasattr(type(inst), 'vsrc0')
  vdst_reg = ctx.inst_field(type(inst).vdst)
  write_hi_half = bits['d'] == 16 and not isinstance(inst, (irc.VOP1, irc.VOP2)) and (vdst_reg >= _c(128))
  if isinstance(write_hi_half, UOp): vdst_reg = write_hi_half.where(vdst_reg - _c(128), vdst_reg)
  if isinstance(inst, (ir3.VOP1, ir4.VOP1, irc.VOP1)):
    d0 = _cond_hi16(write_hi_half, ctx.rvgpr_dyn(vdst_reg, lane))
    s0, src0_off = _load_vsrc0(ctx, inst, lane, bits, literal, is_f64, is_float, d0)
    srcs: dict[str, UOp | int] = {'S0': s0, 'D0': d0, 'OPSEL': _c(0)}
  else:
    vsrc1_reg = ctx.inst_field(type(inst).vsrc1)
    vsrc1_hi = bits['s0'] == 16 and not isinstance(inst, irc.VOP2) and (vsrc1_reg >= _c(128))
    if bits['s1'] == 64:
      s1 = _u64(ctx.rvgpr_dyn(vsrc1_reg, lane), ctx.rvgpr_dyn(vsrc1_reg + _c(1), lane))
      d0 = _u64(ctx.rvgpr_dyn(vdst_reg, lane), ctx.rvgpr_dyn(vdst_reg + _c(1), lane))
    else:
      s1 = _cond_hi16(vsrc1_hi, ctx.rvgpr_dyn(_cond(vsrc1_hi, vsrc1_reg - _c(128), vsrc1_reg), lane))
      d0 = _cond_hi16(write_hi_half, ctx.rvgpr_dyn(vdst_reg, lane))  # FMAC/FMAMK hi-half dest needs hi-half accumulator
    s0, src0_off = _load_vsrc0(ctx, inst, lane, bits, literal, is_f64, is_float, d0)
    if is_dpp16 and is_float:
      s1 = _apply_src_mods(s1, 0, 1 if _iattr(inst, 'src1_abs') else 0, 1 if _iattr(inst, 'src1_neg') else 0, bits['s1'])
    srcs = {'S0': s0, 'S1': s1, 'D0': d0}
    # FMAAK_(DTYPE)_E32 series
    if 'V_FMAA' in op_name or 'V_FMAM' in op_name:
      assert literal is not None
      srcs['SIMM32'] = literal
  return ctx.compile_vop_pcode(inst.op, srcs, lane, vdst_reg, exec_mask, opsel_dst_hi=write_hi_half, src0_off=src0_off)

def _compile_vopc(inst: ir3.VOPC|ir3.VOPC_DPP16|ir3.VOP3|ir4.VOPC|ir4.VOPC_DPP16|ir4.VOP3|irc.VOPC|irc.VOP3, ctx: _Ctx,
                  opsel: int = 0, abs_bits: int = 0, neg_bits: int = 0) -> UOp:
  exec_mask, op_name, bits = ctx.rexec(), _op_name(inst), inst.canonical_op_bits
  is_cmpx, is_vopc = 'CMPX' in op_name, hasattr(inst, 'vsrc1')  # is_vopc: e32 vs e64
  is_dpp16 = hasattr(type(inst), 'dpp') and hasattr(type(inst), 'vsrc0')

  # Handle both VOPC (vsrc1) and VOP3 (src1) instruction formats - read operands dynamically
  src0_off = ctx.inst_field(type(inst).src0)
  if is_vopc:
    vsrc1_off = ctx.inst_field(type(inst).vsrc1)  # type: ignore[union-attr]
    # For 16-bit ops, vsrc1 >= 128 means hi-half of v[vsrc1-128]
    if bits['s0'] == 16 and not isinstance(inst, irc.VOPC):
      vsrc1_hi = vsrc1_off >= _c(128)
      src1_off = _c(256) + vsrc1_hi.where(vsrc1_off - _c(128), vsrc1_off)
    else:
      vsrc1_hi = False
      src1_off = _c(256) + vsrc1_off
  else:
    src1_off = ctx.inst_field(type(inst).src1)  # type: ignore[union-attr]
    dst_off = ctx.inst_field(type(inst).vdst)  # type: ignore[union-attr]
    vsrc1_hi = False
  literal = ctx.optional_field(inst, 'literal')

  is_float, is_f64, pcode = any(x in op_name for x in ('_F32', '_F64', '_F16')), '_F64' in op_name, get_pcode(inst.op)
  def get_cmp_bit(lane: UOp) -> UOp:
    lc = lane.cast(dtypes.int)
    s0 = _load_dpp16_src0(ctx, inst, lc, _c(0)) if is_dpp16 else ctx.rsrc_dyn(src0_off, lc, bits['s0'], literal, is_f64)
    off = UOp.const(False, dtypes.bool)
    if _hw_float() and isinstance(inst, ir4.VOPC) and (is_dpp16 or hasattr(type(inst), 'lane_sel_0')): s0, off = _hw_dpp_src0(ctx, inst, lc)
    if is_vopc and not isinstance(inst, irc.VOPC) and bits['s0'] == 16 and not is_dpp16:
      src0_hi = src0_off >= _c(384)
      s0 = src0_hi.where(_hi16(ctx.rvgpr_dyn(src0_hi.where(src0_off - _c(384), _c(0)), lc)), s0)
    s1 = _cond_hi16(vsrc1_hi, ctx.rsrc_dyn(src1_off, lc, bits['s1'], literal, is_f64)) if bits['s0'] == 16 \
      else ctx.rsrc_dyn(src1_off, lc, bits['s1'], literal, is_f64)
    if bits['s0'] == 16 and opsel: s0, s1 = _apply_opsel(s0, 0, opsel), _apply_opsel(s1, 1, opsel)
    if is_float and is_dpp16:
      s0 = _apply_src_mods(s0, 0, 1 if _iattr(inst, 'src0_abs') else 0, 1 if _iattr(inst, 'src0_neg') else 0, bits['s0'])
      s1 = _apply_src_mods(s1, 0, 1 if _iattr(inst, 'src1_abs') else 0, 1 if _iattr(inst, 'src1_neg') else 0, bits['s1'])
    s0 = _apply_src_mods(s0, 0, abs_bits, neg_bits, bits['s0'])
    s1 = _apply_src_mods(s1, 1, abs_bits, neg_bits, bits['s1'])
    for dest, val in parse_pcode(pcode, {'S0': s0, 'S1': s1, 'laneId': lc, 'D0': _c(0, dtypes.uint64)})[1]:
      if '[laneId]' in dest and ('D0' in dest or 'EXEC' in dest): return off.where(_c(0), val.cast(dtypes.uint32))  # a lane dpp turns off writes 0
    return _c(0)

  # Both VOPC and VOP3 clear inactive lane bits (hardware verified)
  new_result = ctx.unroll_lanes(get_cmp_bit, exec_mask)

  # CMPX writes EXEC only (hardware verified: e64 CMPX does not write SDST); non-CMPX writes SDST/VCC
  if is_cmpx: stores = ctx.wmask(_c(EXEC_LO.offset), new_result)
  else: stores = ctx.wmask(dst_off, new_result) if not is_vopc else ctx.wmask(_c(VCC_LO.offset), new_result)
  return UOp.sink(*stores)


def _compile_bitop3(inst, ctx: _Ctx, exec_mask: UOp, bits: dict, op_name: str) -> UOp:
  """BITOP3: 3-input truth table. abs/neg/omod encode the truth table, not source modifiers."""
  lane = ctx.range()
  vdst_reg = ctx.inst_field(type(inst).vdst)
  ops = inst.canonical_operands
  src0 = ctx.rsrc_dyn(ctx.inst_field(type(inst).src0), lane, bits['s0'], None, 's0' in ops and ops['s0'][0] == Fmt.FMT_NUM_F64)
  src1 = ctx.rsrc_dyn(ctx.inst_field(type(inst).src1), lane, bits['s1'], None, 's1' in ops and ops['s1'][0] == Fmt.FMT_NUM_F64)
  src2 = ctx.rsrc_dyn(ctx.inst_field(type(inst).src2), lane, bits['s2'], None, 's2' in ops and ops['s2'][0] == Fmt.FMT_NUM_F64)
  # Truth table: TTBL = { omod[1:0], abs[2:0], neg[2:0] } = 8-bit LUT
  ttbl = ((_iattr(inst, 'omod')) << 6) | ((_iattr(inst, 'abs')) << 3) | (_iattr(inst, 'neg'))
  is_16 = 'B16' in op_name
  dt, mask = (dtypes.uint16, 0xFFFF) if is_16 else (dtypes.uint32, 0xFFFFFFFF)
  s0, s1, s2 = src0.cast(dt), src1.cast(dt), src2.cast(dt)
  def bnot(v): return v ^ _c(mask, dt)
  result = _c(0, dt)
  for i in range(8):
    if not (ttbl & (1 << i)): continue
    result = result | ((s0 if i & 4 else bnot(s0)) & (s1 if i & 2 else bnot(s1)) & (s2 if i & 1 else bnot(s2)))
  return UOp.sink(ctx.wvgpr_dyn(vdst_reg, lane, result.cast(dtypes.uint32), exec_mask).end(lane))

def _compile_vop3(inst: ir3.VOP3 | ir4.VOP3 | irc.VOP3, ctx: _Ctx) -> UOp:
  exec_mask = ctx.rexec()
  bits = inst.canonical_op_bits
  opsel, op_name = _iattr(inst, 'opsel'), _op_name(inst)

  # Lane operations
  if op_name in ('V_READLANE_B32', 'V_READFIRSTLANE_B32', 'V_READFIRSTLANE_B32_E64', 'V_WRITELANE_B32'):
    return ctx.compile_lane_pcode(inst.op, inst)

  # V_PERMLANE16_B32 / V_PERMLANEX16_B32: cross-lane swizzle via pcode
  if 'PERMLANE16' in op_name or 'PERMLANEX16' in op_name:
    return ctx.compile_lane_pcode(inst.op, inst)

   # VOP3 VOPC (v_cmp_*_e64) - delegate to unified VOPC handler
  if 'V_CMP' in op_name:
    return _compile_vopc(inst, ctx, opsel=opsel, abs_bits=_iattr(inst, 'abs'), neg_bits=_iattr(inst, 'neg'))

  # BITOP3: abs/neg/omod encode truth table, not source modifiers
  if 'BITOP3' in op_name:
    return _compile_bitop3(inst, ctx, exec_mask, bits, op_name)

  # VOP3 specific fields
  vdst_reg = ctx.inst_field(type(inst).vdst)
  literal = ctx.optional_field(inst, 'literal')
  abs_bits, neg_bits = _iattr(inst, 'abs'), _iattr(inst, 'neg')

  # VOP3_SDST: v_s_* instructions goes to SGPR
  if 'V_S_' in op_name:
    src0 = ctx.rsrc_dyn(ctx.inst_field(type(inst).src0), _c(0, dtypes.int), bits['s0'], literal)
    if bits['s0'] == 16: src0 = _apply_opsel(src0, 0, opsel)
    src0 = _apply_src_mods(src0, 0, abs_bits, neg_bits, bits['s0'])
    srcs = {**ctx.base_srcs(exec_mask, _c(0, dtypes.int)), 'S0': src0}
    pcode_vars, _ = parse_pcode(get_pcode(inst.op), srcs)
    d = pcode_vars['D0']
    if _hw_float() and op_name.endswith('F16') and d.dtype != dtypes.half: d = (_val_to_u32(d) & _c(0xFFFF)).cast(dtypes.uint16).bitcast(dtypes.half)
    if _hw_float() and d.dtype in (dtypes.float32, dtypes.half):  # output modifier, then clamp, as for vector destinations
      if (om := _iattr(inst, 'omod')): d = _omod(d, om)
      if _iattr(inst, 'clmp'): d = (d > _c(0.0, d.dtype)).where(d.minimum(_c(1.0, d.dtype)), _c(0.0, d.dtype))
    return UOp.sink(ctx.wsgpr_dyn(vdst_reg, _val_to_u32(d)))

  # Regular VOP3 - read operands dynamically
  lane = ctx.range()
  ops = inst.canonical_operands
  src0, src1, src2 = (ctx.rsrc_dyn(ctx.inst_field(getattr(type(inst), f)), lane, bits[k], literal, k in ops and ops[k][0] == Fmt.FMT_NUM_F64,
                                   do_cast=_f16_const(inst, k)) for f, k in (('src0', 's0'), ('src1', 's1'), ('src2', 's2')))
  if _hw_float() and isinstance(inst, ir4.VOP3) and hasattr(type(inst), 'vsrc0'):  # vop3 dpp16 / dpp8: src0 is a lane swizzle of vsrc0
    src0, ctx.dpp_keep = _hw_dpp_src0(ctx, inst, lane)
  if _hw_float() and isinstance(inst, ir4.VOP3) and inst.op.name in ('V_DOT2_F16_F16', 'V_DOT2_BF16_BF16'):
    ab_, ng = _iattr(inst, 'abs'), _iattr(inst, 'neg')
    def pk(x:UOp, i:int) -> UOp:
      x = x.cast(dtypes.uint32) if x.dtype != dtypes.uint32 else x
      if ab_ & (1 << i): x = x & _c(0x7FFF7FFF)
      return x ^ _c(0x80008000) if ng & (1 << i) else x
    bf = 'BF16' in inst.op.name
    dpp = hasattr(type(inst), 'vsrc0')  # src0 is then the swizzled vsrc0, not an operand encoding
    src0, src1 = (pk(x if f == 'src0' and dpp else _pk_const(ctx.inst_field(getattr(type(inst), f)), x, bf), i)
                  for i, (f, x) in enumerate((('src0', src0), ('src1', src1))))
    c16 = (src2.cast(dtypes.uint32) >> _c(16)) if _iattr(inst, 'opsel') & 4 else src2.cast(dtypes.uint32) & _c(0xFFFF)
    if ab_ & 4: c16 = c16 & _c(0x7FFF)
    if ng & 4: c16 = c16 ^ _c(0x8000)
    srcs = {'S0': src0, 'S1': src1, 'S2': c16, 'OPSEL': _c(_iattr(inst, 'opsel'), dtypes.uint32)}
    return ctx.compile_vop_pcode(inst.op, srcs, lane, vdst_reg, exec_mask, opsel_dst_hi=bool(_iattr(inst, 'opsel') & 8))
    if bits['s0'] == 16: src0 = src0 & _c(0xFFFF)
  fp8_in = _hw_float() and op_name.startswith(('V_CVT_F32_FP8', 'V_CVT_F32_BF8', 'V_CVT_PK_F32_FP8', 'V_CVT_PK_F32_BF8'))
  if bits['s0'] == 16 and not fp8_in:
    src0 = _apply_opsel(src0, 0, opsel)
    src1 = _apply_opsel(src1, 1, opsel)
    src2 = _apply_opsel(src2, 2, opsel)
  if _hw_float() and op_name.startswith('V_SAT_PK_U8_I16'):  # abs / neg act on the sign bit of each i16 half
    src0 = src0.cast(dtypes.uint32) if src0.dtype != dtypes.uint32 else src0
    if abs_bits & 1: src0 = src0 & _c(0x7FFF7FFF)
    if neg_bits & 1: src0 = src0 ^ _c(0x80008000)
  elif not fp8_in: src0 = _apply_src_mods(src0, 0, abs_bits, neg_bits, bits['s0'])  # fp8 / bf8 sources take no abs, neg or clamp
  src1 = _apply_src_mods(src1, 1, abs_bits, neg_bits, bits['s1'])
  src2 = _apply_src_mods(src2, 2, abs_bits, neg_bits, bits['s2'])
  srcs = {'S0': src0, 'S1': src1, 'S2': src2, 'OPSEL': _c(opsel, dtypes.uint32), 'CLMP': _c(_iattr(inst, 'clmp'), dtypes.uint32)}
  if 'CNDMASK' in op_name: srcs['VCC'] = src2
  # FMAC instructions need D0 (accumulator) from destination register
  if 'FMAC' in op_name: srcs['D0'] = ctx.rvgpr_dyn(vdst_reg, lane)
  opsel_dst_hi = bool(opsel & 0b1000) and bits['d'] == 16
  if 'FMAC' in op_name and opsel_dst_hi and _hw_float() and isinstance(inst, ir4.VOP3): srcs['D0'] = _hi16(srcs['D0'])  # accumulates the high half
  return ctx.compile_vop_pcode(inst.op, srcs, lane, vdst_reg, exec_mask, opsel_dst_hi=opsel_dst_hi, clmp=0 if fp8_in else _iattr(inst, 'clmp'),
                               omod=_iattr(inst, 'omod') if _hw_float() and not any(k in inst.op.name for k in ('FP8', 'BF8')) else 0)

def _compile_vinterp(inst: ir3.VINTERP | ir4.VINTERP, ctx: _Ctx) -> UOp:
  lane, exec_mask = ctx.range(), ctx.rexec()
  inst_type = type(inst)
  vdst_reg = ctx.inst_field(inst_type.vdst)
  src0_off, src1_off, src2_off = ctx.inst_field(inst_type.src0), ctx.inst_field(inst_type.src1), ctx.inst_field(inst_type.src2)
  if _hw_float() and isinstance(inst, ir4.VINTERP):  # vinterp sources are VGPRs only: any other encoding reads v0
    src0_off, src1_off, src2_off = [(o >= _c(256)).where(o, _c(256)) for o in (src0_off, src1_off, src2_off)]
  src0_reg = (src0_off >= _c(256)).where(src0_off - _c(256), src0_off)
  src2_reg = (src2_off >= _c(256)).where(src2_off - _c(256), src2_off)
  srcs = {
    'SRC0': src0_reg, 'SRC2': src2_reg,
    'S0': ctx.rsrc_dyn(src0_off, lane), 'S1': ctx.rsrc_dyn(src1_off, lane), 'S2': ctx.rsrc_dyn(src2_off, lane),
  }
  if _hw_float() and isinstance(inst, ir4.VINTERP):  # neg on each source, then clamp on the result
    neg, opsel = _iattr(inst, 'neg'), _iattr(inst, 'opsel')
    srcs.update(NEG=_c(neg), OPSEL=_c(opsel), S1=_apply_src_mods(srcs['S1'], 1, 0, neg), S2=_apply_src_mods(srcs['S2'], 2, 0, neg))
    return ctx.compile_vop_pcode(inst.op, srcs, lane, vdst_reg, exec_mask, clmp=_iattr(inst, 'clmp'), opsel_dst_hi=bool(opsel & 8))
  return ctx.compile_vop_pcode(inst.op, srcs, lane, vdst_reg, exec_mask)

def _compile_vop3sd(inst: ir3.VOP3SD | ir4.VOP3SD | irc.VOP3SD, ctx: _Ctx) -> UOp:
  exec_mask = ctx.rexec()
  bits, pcode, ops = inst.canonical_op_bits, get_pcode(inst.op), inst.canonical_operands

  # Read operands dynamically from instruction encoding
  vdst_reg, sdst_off = ctx.inst_field(type(inst).vdst), ctx.inst_field(type(inst).sdst)
  src0_off, src1_off, src2_off = ctx.inst_field(type(inst).src0), ctx.inst_field(type(inst).src1), ctx.inst_field(type(inst).src2)
  literal = ctx.optional_field(inst, 'literal')

  has_carry_in = 's2' in ops and ops['s2'][2] == OpType.OPR_SREG
  vcc_in_off = src2_off if has_carry_in else sdst_off

  def load_srcs(lane_uop):
    ret = {**ctx.base_srcs(exec_mask, lane_uop), 'VCC': ctx.rmask(vcc_in_off)}
    ret['S0'] = _dpp_src0(ctx, inst, lane_uop, ctx.rsrc_dyn(src0_off, lane_uop, bits['s0'], literal, ops['s0'][0] == Fmt.FMT_NUM_F64))
    ret['S1'] = ctx.rsrc_dyn(src1_off, lane_uop, bits['s1'], literal, ops['s1'][0] == Fmt.FMT_NUM_F64)
    if 's2' in ops: ret['S2'] = ctx.rsrc_dyn(src2_off, lane_uop, bits['s2'], literal, ops['s2'][0] == Fmt.FMT_NUM_F64)
    if _hw_float() and isinstance(inst, ir4.VOP3SD) and 'DIV_SCALE' in inst.op.name:  # neg flips each float source's sign
      for i, k in enumerate(('S0', 'S1', 'S2')): ret[k] = _apply_src_mods(ret[k], i, 0, _iattr(inst, 'neg'), bits[f's{i}'])
    return ret

  lane = ctx.range()
  srcs = load_srcs(lane)
  _, assigns = parse_pcode(pcode, srcs)

  has_per_lane_vcc = any('[laneId]' in dest for dest, _ in assigns if dest.startswith('VCC') or dest.startswith('D0.u64'))
  clmp = _iattr(inst, 'clmp')
  if has_per_lane_vcc:
    # VCC computation: RANGE+REDUCE gets axis ID first (lower ID = runs first)
    # This ensures VCC reads source values BEFORE VGPR stores modify them
    def get_vcc_bit(lane_uop) -> UOp:
      vcc_bit, lsrcs = _c(0), load_srcs(lane_uop)
      keep, ctx.dpp_keep = ctx.dpp_keep, None
      for dest, val in parse_pcode(pcode, lsrcs)[1]:
        if dest.startswith('VCC') or (dest.startswith('D0.u64') and '[laneId]' in dest): vcc_bit = val.cast(dtypes.uint32)
      return vcc_bit if keep is None else keep.where(_c(0), vcc_bit)  # a lane dpp turns off writes a 0 bit
    final_vcc = ctx.unroll_lanes(get_vcc_bit, exec_mask)
    # VGPR stores: RANGE gets axis ID second (higher ID = runs after VCC loop)
    lane3 = ctx.range()
    d0_val, vcc_per_lane, lsrcs = None, None, load_srcs(lane3)
    keep, ctx.dpp_keep = ctx.dpp_keep, None
    for dest, val in parse_pcode(pcode, lsrcs)[1]:
      if dest.startswith('D0') and '[laneId]' not in dest: d0_val = val
      if dest.startswith('VCC') or (dest.startswith('D0.u64') and '[laneId]' in dest): vcc_per_lane = val
    vgpr_stores = []
    if d0_val is not None:
      if _hw_float() and 'DIV_SCALE' in inst.op.name and d0_val.dtype in (dtypes.uint32, dtypes.uint64):  # float omod then clamp on D
        fv = d0_val.bitcast(dtypes.float32 if d0_val.dtype == dtypes.uint32 else dtypes.float64)
        if (om := _iattr(inst, 'omod')): fv = _omod(fv, om)
        if clmp: fv = _clamp01(fv)
        d0_val, clmp = fv.bitcast(d0_val.dtype), 0
      # Apply clamp using carry/borrow bit: ADD overflow->0xFFFFFFFF, SUB underflow->0
      if clmp and vcc_per_lane is not None:
        is_sub = 'SUB' in inst.op.name
        sat_val = _c(0) if is_sub else _c(0xFFFFFFFF)
        d0_val = vcc_per_lane.cast(dtypes.bool).where(sat_val, d0_val.cast(dtypes.uint32))
      if d0_val.dtype in (dtypes.uint64, dtypes.int64, dtypes.float64):
        lo, hi = _split64(d0_val)
        if keep is not None: lo, hi = keep.where(ctx.rvgpr_dyn(vdst_reg, lane3), lo), keep.where(ctx.rvgpr_dyn(vdst_reg + _c(1), lane3), hi)
        vgpr_stores.extend([ctx.wvgpr_dyn(vdst_reg, lane3, lo, exec_mask), ctx.wvgpr_dyn(vdst_reg + _c(1), lane3, hi, exec_mask)])
      else:
        d0_u32 = d0_val.bitcast(dtypes.uint32) if d0_val.dtype in (dtypes.float32, dtypes.half) else d0_val.cast(dtypes.uint32)
        if keep is not None: d0_u32 = keep.where(ctx.rvgpr_dyn(vdst_reg, lane3), d0_u32)
        vgpr_stores.append(ctx.wvgpr_dyn(vdst_reg, lane3, d0_u32, exec_mask))
    # Write carry output (wmask handles lo/hi split for wave64)
    vcc_writes = ctx.wmask(sdst_off, final_vcc)
    return UOp.sink(*vcc_writes, UOp.group(*vgpr_stores).end(lane3))
  else:
    return ctx.compile_vop_pcode(inst.op, srcs, lane, vdst_reg, exec_mask, sdst_reg=inst.sdst.offset,
                                 clmp=_iattr(inst, 'clmp') if _hw_float() else 0, omod=_iattr(inst, 'omod') if _hw_float() else 0)

# MFMA shape -> (lanes per group, lane groups, output regs per lane)
_MFMA_SHAPES = {(16, 16): (16, 4, 4), (32, 32): (32, 2, 16), (4, 4): (4, 16, 4)}

def _compile_mfma(inst: irc.VOP3P|irc.VOP3PX2, ctx: _Ctx) -> UOp:
  """CDNA MFMA matrix multiply-accumulate. Inputs are unpacked/converted into a local temp array (uint32 bit patterns,
  avoiding aliasing when vdst overlaps src0/src1), then phase 2 computes the dot products and writes outputs.
  wave64 register layout: 16x16 = 4 groups of 16 lanes (K split across groups), 32x32 = 2 groups of 32 lanes,
  4x4 = 16 independent groups of 4 lanes (K not split)."""
  op_name, exec_mask = _op_name(inst), ctx.rexec()
  vdst_reg = ctx.inst_field(type(inst).vdst)
  src0_off, src1_off, src2_off = ctx.inst_field(type(inst).src0), ctx.inst_field(type(inst).src1), ctx.inst_field(type(inst).src2)
  use_acc = bool(_iattr(inst, 'acc_cd'))

  scaled = isinstance(inst, irc.VOP3PX2)
  if scaled:
    assert isinstance(inst, irc.VOP3PX2)
    # F8F6F4 input formats: 0=FP8(E4M3), 1=BF8(E5M2). FP6/FP4 (2-4) not emulated.
    if int(inst.cbsz) > 1 or int(inst.blgp) > 1: raise RuntimeError(f"unsupported scaled MFMA formats cbsz={inst.cbsz} blgp={inst.blgp}")
    # scale_src0/scale_src1 are source operands pointing at 32-bit registers holding 4 packed E8M0 scale exponents.
    # The 2-bit opsel/opsel_hi select which byte applies to A/B for this instruction.
    scale0 = ctx.inst_field(type(inst).scale_src0), _iattr(inst, 'opsel') & 3
    scale1 = ctx.inst_field(type(inst).scale_src1), _iattr(inst, 'opsel_hi') & 3
    def _scale_exp(off_sel: tuple[UOp, int], lane: UOp) -> UOp:
      byte = (ctx.rsrc_dyn(off_sel[0], lane, 32) >> _c(off_sel[1] * 8, dtypes.uint32)) & _c(0xFF, dtypes.uint32)
      return byte.cast(dtypes.int32) - _c(127, dtypes.int32)
    def scale_factor(lane: UOp) -> UOp:  # combined A*B scale for this lane: 2^(ea-127) * 2^(eb-127)
      return UOp.exp2((_scale_exp(scale0, lane) + _scale_exp(scale1, lane)).cast(dtypes.float32))

  if (m := re.search(r'(\d+)X(\d+)X(\d+)', op_name)) is None: raise ValueError(f"could not parse MFMA dimensions from {op_name}")
  M, N, K = int(m.group(1)), int(m.group(2)), int(m.group(3))
  if (M, N) not in _MFMA_SHAPES: raise RuntimeError(f"unsupported MFMA shape {M}x{N}x{K}")
  grp_size, n_grps, out_per_lane = _MFMA_SHAPES[(M, N)]  # lanes per group, lane groups, output regs per lane

  # Source type is the LAST type in the name: V_MFMA_F32_16X16X32_**F16** -> source is F16, not F32
  src_type = op_name.rsplit('_', 1)[-1]
  is_bf16, is_fp8 = 'BF16' in op_name, 'FP8' in op_name or 'F8' in op_name
  is_i8, is_f32_src = 'I8' in op_name, src_type == 'F32'
  is_int_out = 'I32' in op_name.split('_')[2]  # V_MFMA_I32_...
  vpg = 4 if is_i8 else 1 if is_f32_src else 4 if is_fp8 else 2  # elements per VGPR
  acc_dt = dtypes.int32 if is_int_out else dtypes.float32

  # Per-operand fp8 format ("fp8"=E4M3, "bf8"=E5M2) for A and B
  if 'F8F6F4' in op_name:
    assert isinstance(inst, (irc.VOP3P_MFMA, irc.VOP3PX2))
    a_fmt, b_fmt = {0: "fp8", 1: "bf8"}.get(int(inst.cbsz), "fp8"), {0: "fp8", 1: "bf8"}.get(int(inst.blgp), "fp8")
  elif is_fp8:  # A/B formats from name suffix, e.g. V_MFMA_F32_16X16X32_BF8_FP8
    a_fmt, b_fmt = ("bf8" if sfx == "BF8" else "fp8" for sfx in op_name.rsplit('_', 2)[-2:])
  else: a_fmt = b_fmt = "fp8"

  # Phase 1: read all A and B values into tmp. Layout: tmp[0:n_a] = A[m][k], tmp[n_a:] = B[n][k].
  # For 4x4 each group is an independent block (K not split), for 16x16/32x32 groups share MxK/NxK and split K.
  k_per_grp = K if M == 4 else K // n_grps
  n_a_elems = n_grps * M * K if M == 4 else M * K
  n_b_elems = n_grps * N * K if M == 4 else N * K
  # Use a uint32 temp array: the optimizer folds bitcast(uint32->f32) chains on float arrays, losing conversions.
  tmp = UOp.placeholder((n_a_elems + n_b_elems,), dtypes.uint32, slot=0, addrspace=AddrSpace.LOCAL)

  def cvt_elem(raw: UOp, sub_idx: int, fp8_fmt: str) -> UOp:
    if is_i8:  # extract i8, sign-extend to i32
      byte = (raw >> _c(sub_idx * 8)) & _c(0xFF, dtypes.uint32)
      return (byte.cast(dtypes.int32) ^ _c(0x80, dtypes.int32)) - _c(0x80, dtypes.int32)
    if is_f32_src: return raw  # already uint32 (f32 bit pattern)
    if is_fp8: return _FUNCS[f"{fp8_fmt}_to_f32"](raw >> _c(sub_idx * 8, dtypes.uint32)).bitcast(dtypes.uint32)
    h = (raw >> _c(sub_idx * 16)) & _c(0xFFFF)
    if is_bf16: return h << _c(16)  # bf16 is the upper 16 bits of f32
    return _FUNCS['f16_to_f32'](h).bitcast(dtypes.uint32)

  def mn_idx(lane: UOp) -> UOp:  # M/N matrix index held by a lane
    if M == 32:  # (lane%32)/16 selects the 16-wide block, (lane%32)%16 the index within it
      return ((lane // _c(16, dtypes.int)) % _c(2, dtypes.int)) * _c(16, dtypes.int) + lane % _c(16, dtypes.int)
    return lane % _c(grp_size, dtypes.int)

  def grp_idx(lane: UOp) -> UOp: return lane // _c(grp_size, dtypes.int)

  read_lane = ctx.range()
  mn, grp = mn_idx(read_lane), grp_idx(read_lane)
  def mat_idx(base: int, dim: int, kl: int) -> UOp:  # tmp index of element (mn, kl) of this lane's group
    if M == 4: return _c(base + kl, dtypes.int) + grp * _c(dim * K, dtypes.int) + mn * _c(K, dtypes.int)
    return _c(base + kl, dtypes.int) + mn * _c(K, dtypes.int) + grp * _c(k_per_grp, dtypes.int)

  read_stores = []
  for kl in range(k_per_grp):
    reg_idx, sub_idx = kl // vpg, kl % vpg
    # src_off >= 256 means VGPR operand, otherwise inline constant/SGPR
    for off, is_vgpr, fmt, base, dim in ((src0_off, src0_off >= _c(256), a_fmt, 0, M), (src1_off, src1_off >= _c(256), b_fmt, n_a_elems, N)):
      raw = is_vgpr.where(ctx.rvgpr_dyn(off - _c(256 - reg_idx), read_lane), ctx.rsrc_dyn(off, _c(0, dtypes.int), 32))
      read_stores.append(tmp.index(mat_idx(base, dim, kl)).store(cvt_elem(raw, sub_idx, fmt)))
  read_phase = UOp.group(*read_stores).end(read_lane)

  # Phase 2: dot products and accumulate. acc reads src2 (VGPR, or scalar inline constant/SGPR broadcast).
  src2_is_vgpr = src2_off >= _c(256)
  acc_scalar = ctx.rsgpr_dyn(src2_off, src2_is_vgpr.ne(True))
  acc_scalar = acc_scalar.cast(dtypes.int32) if is_int_out else acc_scalar.bitcast(dtypes.float32)
  acc_reader, acc_writer = (ctx.raccvgpr_dyn, ctx.waccvgpr_dyn) if use_acc else (ctx.rvgpr_dyn, ctx.wvgpr_dyn)
  tmp2 = tmp.after(read_phase)

  def _dot_accum(acc: UOp, a_row: UOp, b_row: UOp, lane: UOp) -> UOp:
    """acc += sum_k A[a_row+k] * B[b_row+k] in order (FP-associativity matters). For scaled MFMA only the dot is scaled: D = dot*scale + C."""
    def prod(k: int) -> UOp:
      return tmp2.index(a_row + _c(k, dtypes.int)).bitcast(acc_dt) * tmp2.index(b_row + _c(k, dtypes.int)).bitcast(acc_dt)
    if not scaled:
      for k in range(K): acc = acc + prod(k)
      return acc
    dot = prod(0)
    for k in range(1, K): dot = dot + prod(k)
    return acc + dot * scale_factor(lane)

  compute_lane = ctx.range()
  c_mn, c_grp = mn_idx(compute_lane), grp_idx(compute_lane)
  b_off = _c(n_a_elems, dtypes.int)
  def out_ab(out_reg: int) -> tuple[UOp, UOp]:  # A/B tmp base indices for one output element of this lane
    if M == 32:  # 16 outputs per lane: rows (lane//32)*16 + blocks of 4 within the wave
      m_base = c_grp * _c(16, dtypes.int) + _c(out_reg, dtypes.int)
      return m_base * _c(K, dtypes.int), b_off + c_mn * _c(K, dtypes.int)
    if M == 4:  # each group of 4 lanes computes an independent 4x4 block
      a_base = c_grp * _c(M * K, dtypes.int) + _c(out_reg * K, dtypes.int)
      return a_base, b_off + (c_grp * _c(N, dtypes.int) + c_mn) * _c(K, dtypes.int)
    m_base = c_grp * _c(out_per_lane, dtypes.int) + _c(out_reg, dtypes.int)  # 16x16: 4 outputs, one row each
    return m_base * _c(K, dtypes.int), b_off + c_mn * _c(K, dtypes.int)

  compute_stores = []
  for out_reg in range(out_per_lane):
    acc_v = acc_reader(src2_off - _c(256 - out_reg), compute_lane, src2_is_vgpr)
    acc_v = acc_v.cast(dtypes.int32) if is_int_out else acc_v.bitcast(dtypes.float32)
    a_base, b_base = out_ab(out_reg)
    acc = _dot_accum(src2_is_vgpr.where(acc_v, acc_scalar), a_base, b_base, compute_lane)
    out_bits = acc.cast(dtypes.uint32) if is_int_out else acc.bitcast(dtypes.uint32)
    compute_stores.append(acc_writer(vdst_reg + _c(out_reg), compute_lane, out_bits, exec_mask))
  compute_phase = UOp.group(*compute_stores).end(compute_lane)
  return UOp.sink(read_phase, compute_phase)

def _compile_wmma(inst: ir3.VOP3P | ir4.VOP3P | irc.VOP3P, ctx: _Ctx) -> UOp:
  """RDNA3/4 WMMA: snapshot A/B/C before writing D = A@B + C, allowing source and destination registers to overlap."""
  op_name, exec_mask = _op_name(inst), ctx.rexec()
  vdst_reg = ctx.inst_field(type(inst).vdst)
  src0_r, src1_r = ctx.inst_field(type(inst).src0) - _c(256), ctx.inst_field(type(inst).src1) - _c(256)
  src2_r = ctx.inst_field(type(inst).src2)
  is_c_vgpr = src2_r >= _c(256)
  src2_r = is_c_vgpr.where(src2_r - _c(256), src2_r)  # also keeps the unused VGPR-side index in bounds when src2 is a constant
  sparse = 'SWMMAC' in op_name  # A is 2:4 compressed (16 kept of 32), src2 is the index VGPR and the accumulator is vdst
  output_type, _, *input_types = op_name.split("WMMAC_" if sparse else "WMMA_", 1)[1].split("_")
  a_fmt, b_fmt = input_types if len(input_types) == 2 else input_types * 2
  is_rdna4 = isinstance(inst, ir4.VOP3P)
  sz = 8 if a_fmt in ('IU8', 'FP8', 'BF8') else 16  # input element size
  K = 32 if '16X16X32' in op_name else 16
  if sparse: idx_r, src2_r, is_c_vgpr = src2_r, vdst_reg, _c(True, dtypes.bool)

  # read a source element from VGPRs: (src, lane, vgpr, element-in-vgpr) -> f32/i32
  def gval(src, lane, vgpr, ridx, *, fmt, signed=True):
    v = ctx.rvgpr_dyn(src + _c(vgpr), _c(lane, dtypes.int))
    esz = 4 if fmt == 'IU4' else sz
    pkd = (v >> _c(ridx * esz)) & _c((1 << esz) - 1)
    if not fmt.startswith('IU'): return _FUNCS[f'{fmt.lower()}_to_f32'](pkd)
    if not signed: return pkd.bitcast(dtypes.int32)
    return (pkd << _c(32 - esz, dtypes.uint)).bitcast(dtypes.int32) >> _c(32 - esz, dtypes.int32)  # sign extend

  # RDNA3 f16/bf16: 16 lanes x 8 VGPRs x 2 halves,    k maps linearly
  # RDNA3 iu8:      16 lanes x 4 VGPRs x 4 quarters,  k maps linearly
  # RDNA4:          32 lanes x 4 VGPRs x 2 halves, k bits are scrambled (k[2] goes to lane bit 4)
  def read_mat(src, fmt, row, k, signed=True, kk=None):
    n = 32 // (4 if fmt == 'IU4' else sz)  # values per vgpr
    def ab_map(i, k):  # (row, k) -> (lane, vgpr, element-in-vgpr)
      if is_rdna4 and kk == 64:  # the 64-deep iu4 B of the sparse 16x16x64
        return i + ((k >> 4) & 1) * 16, ((k & 15) | ((k >> 1) & 16)) // n, ((k & 15) | ((k >> 1) & 16)) % n
      if is_rdna4 and (K if kk is None else kk) == 32:
        return i + ((k >> 3) & 1) * 16, ((k & 7) | ((k >> 1) & 8)) // n, ((k & 7) | ((k >> 1) & 8)) % n
      elem, lane = ((k & 3) | ((k >> 1) & 4), i + ((k >> 2) & 1) * 16) if is_rdna4 else (k, i)
      return lane, elem // n, elem % n
    return gval(src, *ab_map(row, k), fmt=fmt, signed=signed)

  def d_map(m, n):  # output (row, col) -> (lane, vgpr)
    lane_bit, vgpr = (m >> 3, m & 7) if is_rdna4 else (m & 1, m >> 1)
    return n + lane_bit * 16, vgpr

  # Accumulator C. RDNA4 f16/bf16 packs two f32 accumulator VGPRs into one f16 VGPR; RDNA3 uses the lo half of each.
  # src2 may be a VGPR or an inline/scalar constant (128 = int 0, the usual ", 0" C form); the runner must handle both dynamically
  out_dt = dtypes.int32 if output_type == "I32" else dtypes.float32
  cbits = ctx.rsrc_dyn(src2_r, None, 32)
  cval_const = _FUNCS[f'{output_type.lower()}_to_f32'](cbits & _c(0xFFFF)) if output_type in ("F16", "BF16") else cbits.bitcast(out_dt)
  native = (is_rdna4 and HW_FLOAT.value and a_fmt == b_fmt and a_fmt in ('F16', 'BF16') and output_type == 'F32' and not sparse and K == 16
            and ctx.wave_size == 32 and _wmma_native())
  if native:
    ok = UOp.custom_function("emu_wmma_rdna4", dtype=dtypes.int32).call(
      ctx.vgpr.index(_c(0, dtypes.int)), src0_r, src1_r, src2_r, vdst_reg, exec_mask, cbits, is_c_vgpr.cast(dtypes.int32),
      _c(int(a_fmt == 'BF16'), dtypes.int32))
    ctx._axis_id += 1
    g_slow = UOp.range(ok.eq(_c(0, dtypes.int32)).cast(dtypes.int), ctx._axis_id, AxisType.LOOP, dtype=dtypes.int)
    ctx.vgpr = ctx.vgpr.after(g_slow)
  elem = ctx.range(256)
  row, col = elem // 16, elem % 16
  lane, vgpr = d_map(row, col)
  cval = gval(src2_r, *((lane, vgpr // 2, vgpr % 2) if is_rdna4 else (lane, vgpr, 0)), fmt=output_type) \
    if output_type in ("F16", "BF16") else ctx.rvgpr_dyn(src2_r + _c(vgpr), lane).bitcast(out_dt)
  if sparse and '16X16X64' in op_name:  # iu4: 32 kept of 64 per row; A (row, kc) in the 32-deep layout, index bits 2e per element
    sa, sb = bool(_iattr(inst, 'neg') & 1), bool(_iattr(inst, 'neg') & 2)
    t64 = UOp.alloc((2304,), dtypes.uint32, 0, AddrSpace.REG)
    def kd(kc):
      lane_, e = row + ((kc >> _c(3)) & _c(1)) * _c(16), (kc & _c(7)) | ((kc >> _c(1)) & _c(8))
      return _c(4) * (kc >> _c(1)) + ((ctx.rvgpr_dyn(idx_r, lane_) >> (e * _c(2)).cast(dtypes.uint32)) & _c(3)).cast(dtypes.int)
    st = [t64.index(row*32+col).store(read_mat(src0_r, a_fmt, row, col, sa, kk=32).bitcast(dtypes.uint32)),
          t64.index(row*32+col+16).store(read_mat(src0_r, a_fmt, row, col + 16, sa, kk=32).bitcast(dtypes.uint32)),
          *[t64.index(512+row*64+col+16*j).store(read_mat(src1_r, b_fmt, row, col + 16*j, sb, kk=64).bitcast(dtypes.uint32)) for j in range(4)],
          t64.index(1536+row*16+col).store(cval.bitcast(dtypes.uint32)),
          t64.index(1792+row*32+col).store(kd(col).cast(dtypes.uint32)), t64.index(1792+row*32+col+16).store(kd(col + _c(16)).cast(dtypes.uint32))]
    d64 = t64.after(UOp.group(*st).end(elem))
    n = ctx.range(16)
    def w64(m:int) -> UOp:
      acc = d64.index(1536+m*16+n).bitcast(dtypes.int32)
      for kc in range(32):
        bk = d64.index(_c(512) + n*64 + d64.index(1792+m*32+kc).cast(dtypes.int))
        acc = acc + d64.index(m*32+kc).bitcast(dtypes.int32) * bk.bitcast(dtypes.int32)
      return acc.bitcast(dtypes.uint32)
    return UOp.sink(UOp.group(*[ctx.wvgpr_dyn(vdst_reg + _c(d_map(m, 0)[1]), _c(d_map(m, 0)[0], dtypes.int) + n, w64(m), exec_mask)
                                for m in range(16)]).end(n))
  tmp = UOp.alloc((1280,), dtypes.uint32, 0, AddrSpace.REG)
  sa, sb = (bool(_iattr(inst, 'neg') & 1), bool(_iattr(inst, 'neg') & 2)) if is_rdna4 and HW_FLOAT.value else (True, True)
  if sparse:  # compressed A (row, kc) in the 16-deep layout; slot 3 holds each kept element's dense k: 4*(kc//2) + its 2 index bits
    e_lane, e_idx = row + ((col >> _c(2)) & _c(1)) * _c(16), (col & _c(3)) | ((col >> _c(1)) & _c(4))
    kidx = _c(4) * (col >> _c(1)) + ((ctx.rvgpr_dyn(idx_r, e_lane) >> (e_idx * _c(2)).cast(dtypes.uint32)) & _c(3)).cast(dtypes.int)
    values = [read_mat(src0_r, a_fmt, row, col, sa, kk=16), read_mat(src1_r, b_fmt, row, col, sb), cval,
              kidx.cast(dtypes.uint32), read_mat(src1_r, b_fmt, row, col + 16, sb)]
  else:
    values = [read_mat(src0_r, a_fmt, row, col, sa), read_mat(src1_r, b_fmt, row, col, sb), is_c_vgpr.where(cval, cval_const)]
    if K == 32: values += [read_mat(src0_r, a_fmt, row, col + 16, sa), read_mat(src1_r, b_fmt, row, col + 16, sb)]
  read_phase = UOp.group(*(tmp.index(elem + i*256).store(v.bitcast(dtypes.uint32)) for i,v in enumerate(values))).end(elem)
  data = tmp.after(read_phase)
  n = ctx.range(16)
  def bget(r:int, k:int) -> UOp:  # B[k][n] for A's k-th element of row r (sparse: the dense k that element sits at)
    if not sparse: return data.index(256+n*16+k)
    kd = data.index(768+r*16+k).cast(dtypes.int)
    return data.index((kd < _c(16)).where(_c(256) + n*16 + kd, _c(1024) + n*16 + kd - _c(16)))
  def hw_acc(a:list[UOp], b:list[UOp], c0:UOp) -> UOp:  # the grid-floored sum of the four k groups
    emin = {'F16': -14, 'BF16': -126}[a_fmt]
    cmin = -14 if output_type == 'F16' else -126
    acc = c0
    for g in range(0, 16, 4):
      s_ = _grid_dot(a[g:g+4], b[g:g+4], acc, emin, cmin)
      if output_type == 'F32': acc = s_.cast(dtypes.float32)
      elif output_type == 'F16': acc = _rto32(s_).cast(dtypes.half).cast(dtypes.float32)
      else: acc = (s_.cast(dtypes.float32).bitcast(dtypes.uint32) & _c(0xFFFF0000)).bitcast(dtypes.float32)
    return acc
  def hd_acc(r:int, n:UOp) -> UOp:
    return hw_acc([data.index(r*16+k).bitcast(out_dt) for k in range(16)], [data.index(256+n*16+k).bitcast(out_dt) for k in range(16)],
                  data.index(512+r*16+n).bitcast(out_dt))
  def hw_dot(r:int) -> UOp:
    a = [data.index(r*16+k).bitcast(out_dt) for k in range(16)]
    b = [bget(r, k).bitcast(out_dt) for k in range(16)]
    c0 = data.index(512+r*16+n).bitcast(out_dt)
    acc = hw_acc(a, b, c0)
    u = dtypes.uint32
    if output_type == 'F32': fixed, dn, cq = _c(0xFFC00A3D, u), _c(0xFFC00000, u), _quiet(c0).bitcast(u)
    elif output_type == 'F16': fixed, dn, cq = _c(0xFE3D, u), _c(0xFE00, u), _quiet(c0.cast(dtypes.half)).bitcast(dtypes.uint16).cast(u)
    else: fixed, dn, cq = _c(0xFFFD, u), _c(0xFFC0, u), (c0.bitcast(u) >> _c(16)) | _c(0x40, u)
    ieee, special, is_special = c0.cast(_F64), cq, c0.ne(c0)
    for g in range(0, 16, 4):
      pr = [x.cast(_F64) * y.cast(_F64) for x, y in zip(a[g:g+4], b[g:g+4])]
      psum = functools.reduce(lambda x, y: x + y, pr)
      t = psum + ieee
      gab = functools.reduce(lambda x, y: x | y, [x.ne(x) for x in a[g:g+4] + b[g:g+4]])
      ginv = functools.reduce(lambda x, y: x | y, [x.ne(x) for x in pr]) | psum.ne(psum) | (t.ne(t) & ieee.eq(ieee))
      special, is_special = gab.where(fixed, ginv.where(dn, special)), is_special | gab | ginv
      ieee = (t.cast(dtypes.half) if output_type == 'F16' else t.cast(dtypes.float32)).cast(_F64)
    big = ieee.abs().eq(_c(float('inf'), _F64))
    res = big.where(ieee.cast(dtypes.float32), acc)
    ovnan = acc.ne(acc) & ~big & ~is_special
    special, is_special = ovnan.where(dn, special), is_special | ovnan
    return res, special, is_special
  def hw_dot8(r:int) -> UOp:
    a = [data.index(r*16+k).bitcast(out_dt) for k in range(16)]
    b = [bget(r, k).bitcast(out_dt) for k in range(16)]
    acc = data.index(512+r*16+n).bitcast(out_dt)
    for g in ((0, 1, 2, 3, 8, 9, 10, 11), (4, 5, 6, 7, 12, 13, 14, 15)):
      ga, gb = [a[k] for k in g], [b[k] for k in g]
      grid = _grid_dot8(ga, gb, acc, -6 if a_fmt == 'FP8' else -14, -6 if b_fmt == 'FP8' else -14).cast(dtypes.float32)
      pr = [x.cast(_F64) * y.cast(_F64) for x, y in zip(ga, gb)]
      prods = functools.reduce(lambda x, y: x + y, pr)
      ieee = prods + acc.cast(_F64)
      res = ieee.abs().eq(_c(float('inf'), _F64)).where(ieee.cast(dtypes.float32), grid).bitcast(dtypes.uint32)
      bad = functools.reduce(lambda x, y: x | y, [x.ne(x) for x in ga + gb + pr]) | prods.ne(prods)
      acc = bad.where(_c(0xFFC00A3D), acc.ne(acc).where(_quiet(acc).bitcast(dtypes.uint32),
                                                        ieee.ne(ieee).where(_c(0xFFC00A3D), res))).bitcast(dtypes.float32)
    return acc
  if is_rdna4 and HW_FLOAT.value and a_fmt == b_fmt and a_fmt in ('F16', 'BF16') and out_dt == dtypes.float32:
    hd = [hw_dot(r) for r in range(16)]
    mat_d = [h[0] for h in hd]
  elif is_rdna4 and HW_FLOAT.value and a_fmt in ('FP8', 'BF8') and (K == 16 or sparse):
    hd, mat_d = None, [hw_dot8(r) for r in range(16)]
  else:
    hd = None
    mat_d = [sum(data.index(r*16+k).bitcast(out_dt) * bget(r, k).bitcast(out_dt) for k in range(16))
             + (sum(data.index(768+r*16+k).bitcast(out_dt) * data.index(1024+n*16+k).bitcast(out_dt) for k in range(16))
                if K == 32 and not sparse else 0)
             + data.index(512+r*16+n).bitcast(out_dt) for r in range(16)]

  def w_store(m: int, n: UOp, val: UOp, vgpr_off: int) -> UOp:  # store one output element to its (lane, vgpr) slot
    lane_i, _ = d_map(m, n)
    return ctx.wvgpr_dyn(vdst_reg + _c(vgpr_off), _c(lane_i, dtypes.int), val, exec_mask)
  if output_type in ("F16", "BF16"):
    def to_bits(v: UOp, m:int=-1) -> UOp:  # f32 result -> 16 output bits
      bits = ((v.bitcast(dtypes.uint32) >> _c(16, dtypes.uint32)) & _c(0xFFFF)) if output_type == "BF16" \
        else v.cast(dtypes.half).bitcast(dtypes.uint16).cast(dtypes.uint32)
      return hd[m][2].where(hd[m][1], bits) if hd is not None and m >= 0 else bits
    if is_rdna4:  # pack 2 outputs per VGPR (adjacent m values share a VGPR)
      stores = [w_store(m, n, to_bits(mat_d[m], m) | (to_bits(mat_d[m+1], m+1) << _c(16, dtypes.uint32)), d_map(m, n)[1] // 2)
                for m in range(0, 16, 2)]
    else:  # one output per VGPR (lo half)
      stores = [w_store(m, n, to_bits(mat_d[m]), d_map(m, n)[1]) for m in range(16)]
  else:  # f32/i32
    stores = [w_store(m, n, (hd[m][2].where(hd[m][1], mat_d[m].bitcast(dtypes.uint32)) if hd is not None else mat_d[m].bitcast(dtypes.uint32)),
                      d_map(m, n)[1]) for m in range(16)]
  if native: return UOp.sink(UOp.group(*stores).end(n).end(g_slow))
  if hd is not None and output_type == 'F32' and not sparse and K == 16:
    # finite A and B with |C| < 2^127 can't produce a NaN, an invalid product or an overflow (16 products of finite f16/bf16 stay far
    # below f32 max), so the special-value tracking returns the grid sum unchanged: one check per instruction skips it
    def plain(x:UOp) -> UOp: return x.abs() < _c(2.0**127, dtypes.float32)
    e2 = ctx.range(256)
    chk = [v.substitute({elem: e2}) for v in values[:3]]
    ok = (plain(chk[0]) & plain(chk[1]) & plain(chk[2])).ne(True).cast(dtypes.uint32).reduce(e2, arg=Ops.MAX).eq(0)
    def gate(cnt:UOp) -> UOp:
      ctx._axis_id += 1
      return UOp.range(cnt.cast(dtypes.int), ctx._axis_id, AxisType.LOOP, dtype=dtypes.int)
    g_fast, g_full, nf = gate(ok), gate(ok.ne(True)), ctx.range(16)
    def fast_val(m:int, n:UOp) -> UOp: return hd_acc(m, n).bitcast(dtypes.uint32)
    fast = [ctx.wvgpr_dyn(vdst_reg + _c(d_map(m, nf)[1]), _c(d_map(m, 0)[0], dtypes.int) + nf, fast_val(m, nf), exec_mask, after=g_fast)
            for m in range(16)]
    full = [st.replace(src=(st.src[0].replace(src=(st.src[0].src[0].after(g_full), *st.src[0].src[1:])), *st.src[1:])) for st in stores]
    return UOp.sink(UOp.group(*fast).end(nf).end(g_fast), UOp.group(*full).end(n).end(g_full))
  return UOp.sink(UOp.group(*stores).end(n))

_INT_DOTS = {'V_DOT4_U32_U8': (8, False), 'V_DOT8_U32_U4': (4, False), 'V_DOT4_I32_IU8': (8, True), 'V_DOT8_I32_IU4': (4, True)}
def _hw_int_dot(inst, ctx, lane:UOp, op_name:str) -> UOp:
  nb, iu = _INT_DOTS[op_name]
  literal = ctx.optional_field(inst, 'literal')
  s = [ctx.rsrc_dyn(ctx.inst_field(getattr(type(inst), f)), lane, 32, literal=literal) for f in ('src0', 'src1', 'src2')]
  s[0] = _dpp_src0(ctx, inst, lane, s[0])
  opsel, opsel_hi, neg = _iattr(inst, 'opsel'), _iattr(inst, 'opsel_hi', 3), _iattr(inst, 'neg')
  def pick(x:UOp, i:int) -> UOp:
    lo, hi = x & _c(0xFFFF), x >> _c(16)
    return ((hi if opsel & (1 << i) else lo)) | ((hi if opsel_hi & (1 << i) else lo) << _c(16))
  a, b = pick(s[0].cast(dtypes.uint32), 0), pick(s[1].cast(dtypes.uint32), 1)
  i64 = dtypes.int64
  def elem(x:UOp, k:int, signed:bool) -> UOp:
    e = (x >> _c(nb * k)) & _c((1 << nb) - 1)
    return ((e << _c(32 - nb)).bitcast(dtypes.int32) >> _c(32 - nb, dtypes.int32)).cast(i64) if signed else e.cast(i64)
  acc = s[2].cast(dtypes.uint32).bitcast(dtypes.int32).cast(i64) if iu else s[2].cast(dtypes.uint32).cast(i64)
  for k in range(32 // nb): acc = acc + elem(a, k, iu and bool(neg & 1)) * elem(b, k, iu and bool(neg & 2))
  if _iattr(inst, 'clmp'):
    lo, hi = (-(1 << 31), (1 << 31) - 1) if iu else (0, (1 << 32) - 1)
    acc = (acc < _c(lo, i64)).where(_c(lo, i64), (acc > _c(hi, i64)).where(_c(hi, i64), acc))
  return acc.cast(dtypes.uint64).cast(dtypes.uint32)

def _hw_f32_dot2(inst, ctx, lane:UOp, op_name:str) -> UOp:
  literal = ctx.optional_field(inst, 'literal')
  offs = [ctx.inst_field(getattr(type(inst), f)) for f in ('src0', 'src1', 'src2')]
  s = [ctx.rsrc_dyn(o, lane, 32, literal=literal).cast(dtypes.uint32) for o in offs]
  s[0], s[1] = (_pk_const(offs[i], s[i], 'BF16' in op_name, lo_only='BF16' not in op_name) for i in (0, 1))  # f16: low half only
  s[0] = _dpp_src0(ctx, inst, lane, s[0]).cast(dtypes.uint32)
  opsel, opsel_hi, neg, neg_hi = _iattr(inst, 'opsel'), _iattr(inst, 'opsel_hi', 3), _iattr(inst, 'neg'), _iattr(inst, 'neg_hi')
  bf = 'BF16' in op_name
  conv = _b2f if bf else _h2f
  def halves(x:UOp, i:int) -> list[UOp]:
    lo, hi = x & _c(0xFFFF), x >> _c(16)
    l, h = (hi if opsel & (1 << i) else lo), (hi if opsel_hi & (1 << i) else lo)
    if neg & (1 << i): l = l ^ _c(0x8000)
    if neg_hi & (1 << i): h = h ^ _c(0x8000)
    return [conv(l), conv(h)]
  c = s[2]
  if neg_hi & 4: c = c & _c(0x7FFFFFFF)
  if neg & 4: c = c ^ _c(0x80000000)
  a, b, cf = halves(s[0], 0), halves(s[1], 1), c.bitcast(dtypes.float32)
  r = _hw_dot(a, b, cf, -126 if bf else -14, 'f32', -126)
  if _iattr(inst, 'clmp'):  # only rounding up past the largest finite saturates: an exact sum of 2^128 or more, or an infinite input, stays infinite
    fin = functools.reduce(lambda x, y: x & y, [x.abs().ne(_c(float('inf'), dtypes.float32)) for x in a + b + [cf]])
    ex = functools.reduce(lambda x, y: x + y, [x.cast(_F64) * y.cast(_F64) for x, y in zip(a, b)] + [cf.cast(_F64)])
    fin = fin & (ex.abs() < _c(2.0 ** 128, _F64))
    r = (fin & (r & _c(0x7FFFFFFF)).eq(_c(0x7F800000))).where((r & _c(0x80000000)) | _c(0x7F7FFFFF), r)
  return r

def _compile_vop3p(inst: ir3.VOP3P | ir4.VOP3P | irc.VOP3P | irc.VOP3PX2, ctx: _Ctx) -> UOp:
  op_name = _op_name(inst)
  if 'WMMA' in op_name:
    assert not isinstance(inst, irc.VOP3PX2)
    return _compile_wmma(inst, ctx)
  if 'MFMA' in op_name and any(f'{s}X{s}X' in op_name for s in ('4', '16', '32')) and isinstance(inst, (irc.VOP3P, irc.VOP3PX2)):
    return _compile_mfma(inst, ctx)

  # ACCVGPR_WRITE/READ/MOV: copies between VGPR and ACCVGPR register files
  # Detect by checking operand types for ACCVGPR involvement
  ops = inst.operands
  src0_is_acc = ops.get('src0', (None, None, None))[2] in (OpType.OPR_SRC_ACCVGPR, OpType.OPR_ACCVGPR)
  vdst_is_acc = ops.get('vdst', (None, None, None))[2] in (OpType.OPR_ACCVGPR,)
  if src0_is_acc or vdst_is_acc:
    lane = ctx.range()
    exec_mask = ctx.rexec()
    vdst_reg = ctx.inst_field(type(inst).vdst)
    src0_off = ctx.inst_field(type(inst).src0)
    if not vdst_is_acc:
      # v_accvgpr_read: VGPR[vdst] = ACCVGPR[src0]
      val = ctx.raccvgpr_dyn(src0_off - _c(256), lane)
      return UOp.sink(ctx.wvgpr_dyn(vdst_reg, lane, val, exec_mask).end(lane))
    elif not src0_is_acc:
      # v_accvgpr_write: ACCVGPR[vdst] = src0 (src0 can be VGPR or SGPR/const)
      src0 = ctx.rsrc_dyn(src0_off, lane, 32)
      return UOp.sink(ctx.waccvgpr_dyn(vdst_reg, lane, src0, exec_mask).end(lane))
    else:
      # v_accvgpr_mov: ACCVGPR[vdst] = ACCVGPR[src0]
      val = ctx.raccvgpr_dyn(src0_off - _c(256), lane)
      return UOp.sink(ctx.waccvgpr_dyn(vdst_reg, lane, val, exec_mask).end(lane))

  lane = ctx.range()
  exec_mask = ctx.rexec()
  vdst_reg = ctx.inst_field(type(inst).vdst)
  if isinstance(inst, ir4.VOP3P) and HW_FLOAT.value and op_name in _INT_DOTS:
    return UOp.sink(_dpp_store(ctx, vdst_reg, lane, _hw_int_dot(inst, ctx, lane, op_name), exec_mask).end(lane))
  if isinstance(inst, ir4.VOP3P) and HW_FLOAT.value and op_name in _DOT8:
    return UOp.sink(_dpp_store(ctx, vdst_reg, lane, _hw_dot8(inst, ctx, lane, op_name), exec_mask).end(lane))
  if isinstance(inst, ir4.VOP3P) and HW_FLOAT.value and op_name in ('V_DOT2_F32_F16', 'V_DOT2_F32_BF16'):
    return UOp.sink(_dpp_store(ctx, vdst_reg, lane, _hw_f32_dot2(inst, ctx, lane, op_name), exec_mask).end(lane))
  is_pk_f32 = 'PK' in op_name and 'F32' in op_name and 'MOV' not in op_name  # CDNA packed F32 ops
  is_pk_mov_b32 = 'PK_MOV_B32' in op_name  # CDNA packed MOV needs special handling
  do_cast = any(x in op_name for x in ('F16', 'F32', 'BF16')) and 'IU' not in op_name and not is_pk_f32
  literal = ctx.optional_field(inst, 'literal')
  src0 = _dpp_src0(ctx, inst, lane, ctx.rsrc_dyn(ctx.inst_field(type(inst).src0), lane, 16, literal=literal, do_cast=do_cast))
  src1 = ctx.rsrc_dyn(ctx.inst_field(type(inst).src1), lane, 16, literal=literal, do_cast=do_cast)
  src2 = ctx.rsrc_dyn(ctx.inst_field(type(inst).src2), lane, 16, literal=literal, do_cast=do_cast)
  opsel, opsel_hi = _iattr(inst, 'opsel'), _iattr(inst, 'opsel_hi', 3)
  opsel_hi2 = _iattr(inst, 'opsel_hi2', 1)
  neg, neg_hi = _iattr(inst, 'neg'), _iattr(inst, 'neg_hi')

  def _pk_sel(src_lo: UOp, src_off: UOp, sel: int) -> UOp:
    """Lo (sel=0) / hi (sel!=0) half of a packed source: VGPR/SGPR pairs select from the two registers of the pair
    (off>=256 is a VGPR pair, off<128 an SGPR pair), inline constants (128<=off<256) broadcast to both halves."""
    if not sel: return (src_off >= _c(256)).where(ctx.rvgpr_dyn(src_off - _c(256), lane), src_lo)
    is_sgpr_pair = src_off < _c(128)
    return (src_off >= _c(256)).where(ctx.rvgpr_dyn(src_off - _c(256) + _c(1), lane),
                                      is_sgpr_pair.where(ctx.rsgpr_dyn(src_off + _c(1), is_sgpr_pair), src_lo))

  if is_pk_mov_b32:
    # v_pk_mov_b32: D[lo] = src0[opsel_bit0 ? hi : lo], D[hi] = src1[opsel_bit1 ? hi : lo]
    lo_val = _pk_sel(src0, ctx.inst_field(type(inst).src0), opsel & 1)
    hi_val = _pk_sel(src1, ctx.inst_field(type(inst).src1), opsel & 2)
    stores = [ctx.wvgpr_dyn(vdst_reg, lane, lo_val, exec_mask), ctx.wvgpr_dyn(vdst_reg + _c(1), lane, hi_val, exec_mask)]
    return UOp.sink(UOp.group(*stores).end(lane))

  srcs: dict[str, UOp | int] = {}
  if is_pk_f32:
    # CDNA packed F32: read 32-bit sources, build 64-bit packed values per opsel, with per-half negation
    src_offs = [ctx.inst_field(type(inst).src0), ctx.inst_field(type(inst).src1), ctx.inst_field(type(inst).src2)]
    hi_bits = (opsel_hi & 1, opsel_hi & 2, 1 if opsel_hi2 else 0)
    for i, (bit, s0) in enumerate(zip((1, 2, 4), (src0, src1, src2))):
      lo, hi = _pk_sel(s0, src_offs[i], opsel & bit), _pk_sel(s0, src_offs[i], hi_bits[i])
      if neg & bit: lo = lo ^ _c(0x80000000, dtypes.uint32)
      if neg_hi & bit: hi = hi ^ _c(0x80000000, dtypes.uint32)
      srcs[f'S{i}'] = _u64(lo, hi)
  elif 'FMA_MIX' in op_name or 'MAD_MIX' in op_name:
    combined_opsel_hi = (opsel_hi & 0x3) | ((opsel_hi2 & 0x1) << 2)
    # For FMA_MIX: neg_hi is ABS (not neg!), neg is actual negation
    def apply_abs(v, bit, opsel_hi_bit, opsel_bit):
      if not (neg_hi & bit): return v
      # Apply abs based on whether source is f32 or f16
      if not (combined_opsel_hi & opsel_hi_bit): return v & _c(0x7FFFFFFF, dtypes.uint32)  # f32 abs
      if opsel & opsel_bit: return v & _c(0x7FFF0000, dtypes.uint32)  # f16 hi abs (preserve lo)
      return v & _c(0xFFFF7FFF, dtypes.uint32)  # f16 lo abs (preserve hi)
    def apply_neg_mix(v, bit, opsel_hi_bit, opsel_bit):
      if not (neg & bit): return v
      if not (combined_opsel_hi & opsel_hi_bit): return v ^ _c(0x80000000, dtypes.uint32)  # f32 neg
      if opsel & opsel_bit: return v ^ _c(0x80000000, dtypes.uint32)  # f16 hi neg
      return v ^ _c(0x00008000, dtypes.uint32)  # f16 lo neg
    s0_mod = apply_neg_mix(apply_abs(src0, 1, 1, 1), 1, 1, 1)
    s1_mod = apply_neg_mix(apply_abs(src1, 2, 2, 2), 2, 2, 2)
    s2_mod = apply_neg_mix(apply_abs(src2, 4, 4, 4), 4, 4, 4)
    srcs = {'S@0': s0_mod, 'S@1': s1_mod, 'S@2': s2_mod,
            'OPSEL_HI': _c(combined_opsel_hi, dtypes.uint32), 'OPSEL': _c(opsel, dtypes.uint32)}
  else:
    def get_half_bits(val: UOp, use_hi: bool, apply_neg: bool = False) -> UOp:
      bits = ((val >> _c(16, dtypes.uint32)) if use_hi else val) & _c(0xFFFF)
      if apply_neg: bits = bits.cast(dtypes.uint16).bitcast(dtypes.half).neg().bitcast(dtypes.uint16).cast(dtypes.uint32)
      return bits
    def build_remapped_src(src: UOp, opsel_lo_bit: int, opsel_hi_bit: int, neg_lo_bit: int, neg_hi_bit: int) -> UOp:
      lo = get_half_bits(src, bool(opsel_lo_bit), bool(neg_lo_bit))
      hi = get_half_bits(src, bool(opsel_hi_bit), bool(neg_hi_bit))
      return lo | (hi << _c(16, dtypes.uint32))
    # DOT IU instructions use NEG bits for signed/unsigned selection, not fp16 negation
    is_dot_iu = 'DOT' in op_name and 'IU' in op_name
    n0, n1, n2, nh0, nh1, nh2 = (0, 0, 0, 0, 0, 0) if is_dot_iu else (neg & 1, neg & 2, neg & 4, neg_hi & 1, neg_hi & 2, neg_hi & 4)
    srcs = {'S0': build_remapped_src(src0, opsel & 1, opsel_hi & 1, n0, nh0),
            'S1': build_remapped_src(src1, opsel & 2, opsel_hi & 2, n1, nh1),
            'S2': build_remapped_src(src2, opsel & 4, 1 if opsel_hi2 else 0, n2, nh2)}
    if is_dot_iu: srcs['NEG'] = _c(neg, dtypes.uint32)
    if _hw_float() and isinstance(inst, ir4.VOP3P) and _iattr(inst, 'clmp') and op_name in _PK_SAT:
      return UOp.sink(_dpp_store(ctx, vdst_reg, lane, _pk_sat(op_name, srcs), exec_mask).end(lane))
  return ctx.compile_vop_pcode(inst.op, srcs, lane, vdst_reg, exec_mask,
                               clmp=_iattr(inst, 'clmp') if isinstance(inst, ir4.VOP3P) and _hw_float() else 0)

_PK_SAT = {'V_PK_ADD_I16', 'V_PK_ADD_U16', 'V_PK_SUB_I16', 'V_PK_SUB_U16', 'V_PK_MAD_I16', 'V_PK_MAD_U16'}
def _pk_sat(op_name:str, srcs:dict) -> UOp:  # clamp on packed 16-bit integer ops: exact per-half result, saturated
  signed = 'I16' in op_name
  lo, hi = (-0x8000, 0x7FFF) if signed else (0, 0xFFFF)
  def half(x:UOp, k:int) -> UOp:
    h = (x.cast(dtypes.uint32) >> _c(16 * k)) & _c(0xFFFF)
    return h.cast(dtypes.uint16).bitcast(dtypes.int16).cast(dtypes.int64) if signed else h.cast(dtypes.int64)
  out = []
  for k in (0, 1):
    a, b = half(srcs['S0'], k), half(srcs['S1'], k)
    r = a + b if 'ADD' in op_name else a - b if 'SUB' in op_name else a * b + half(srcs['S2'], k)
    out.append(r.maximum(_c(lo, dtypes.int64)).minimum(_c(hi, dtypes.int64)).cast(dtypes.uint32) & _c(0xFFFF))
  return out[0] | (out[1] << _c(16))

def _compile_vopd(inst: ir3.VOPD | ir4.VOPD, ctx: _Ctx) -> UOp:
  exec_mask = ctx.rexec()
  # Read operands dynamically - use type(inst) to get correct field descriptors
  inst_type = type(inst)
  vdstx_reg = ctx.inst_field(inst_type.vdstx)
  # vdsty has complex encoding: actual = (raw << 1) | ((vdstx & 1) ^ 1)
  vdsty_raw = ctx.inst_field(inst_type.vdsty)
  vdsty_reg = (vdsty_raw << _c(1)) | ((vdstx_reg & _c(1)) ^ _c(1))
  srcx0_off = ctx.inst_field(inst_type.srcx0)
  srcy0_off = ctx.inst_field(inst_type.srcy0)
  vsrcx1_reg = ctx.inst_field(inst_type.vsrcx1)
  vsrcy1_reg = ctx.inst_field(inst_type.vsrcy1)
  literal = ctx.inst_field(inst_type.literal) if hasattr(inst_type, 'literal') else None

  lane = ctx.range()
  srcy0, srcy1 = ctx.rsrc_dyn(srcy0_off, lane, literal=literal), ctx.rvgpr_dyn(vsrcy1_reg, lane)
  all_stores = []
  srcs:dict[str, UOp | int] = {}
  for op, src0_off, vsrc1_reg, vdst_reg, label in [(inst.opx, srcx0_off, vsrcx1_reg, vdstx_reg, 'X'),
                                                    (inst.opy, srcy0_off, vsrcy1_reg, vdsty_reg, 'Y')]:
    vop = VOPD_TO_VOP2.get(op)
    assert vop is not None or op in _VOPD_HW_PCODE, f"no VOP mapping for VOPD {label}: {op}"
    if label == 'Y': srcs = {'S0': srcy0, 'S1': srcy1, 'D0': ctx.rvgpr_dyn(vdst_reg, lane)}
    else: srcs = {'S0': ctx.rsrc_dyn(src0_off, lane, literal=literal), 'S1': ctx.rvgpr_dyn(vsrc1_reg, lane), 'D0': ctx.rvgpr_dyn(vdst_reg, lane)}
    # VOP2_FMAAK/FMAMK_(DTYPE)_E32
    if vop in (ir3.VOP2Op.V_FMAAK_F32_E32, ir3.VOP2Op.V_FMAMK_F32_E32, ir4.VOP2Op.V_FMAAK_F32_E32, ir4.VOP2Op.V_FMAMK_F32_E32):
      assert literal is not None
      srcs['SIMM32'] = literal
    pcode = _VOPD_HW_PCODE[op] if op in _VOPD_HW_PCODE else get_pcode(vop)
    srcs.update(ctx.base_srcs(exec_mask, lane), VCC=ctx.rmask(_c(VCC_LO.offset)))
    for dest, val in parse_pcode(pcode, srcs)[1]:
      if dest.startswith('D0'): all_stores.append(ctx.wvgpr_dyn(vdst_reg, lane, _val_to_u32(val), exec_mask, after=srcy1))
  return UOp.sink(UOp.group(*all_stores).end(lane))

def _compile_mem_op(inst: ir3.DS|ir3.FLAT|ir3.GLOBAL|ir3.SCRATCH|ir4.DS|ir4.VFLAT|ir4.VGLOBAL|ir4.VSCRATCH
                    |irc.DS|irc.FLAT|irc.GLOBAL|irc.SCRATCH, ctx: _Ctx) -> UOp:
  """Unified memory operation compiler for DS, FLAT, GLOBAL, SCRATCH."""
  exec_mask, op_name = ctx.rexec(), _op_name(inst)
  pcode = get_pcode(inst.op)
  # CDNA and RDNA4 FLAT/SCRATCH pcode compute addresses from raw components, but make_addr already handles this.
  # Strip the addr computation line and use pre-computed ADDR directly (rename 'addr' -> 'ADDR' in remaining pcode).
  if isinstance(inst, (irc.GLOBAL, irc.FLAT, irc.SCRATCH, irc.DS, ir4.VFLAT, ir4.VSCRATCH)) and 'Calc' in pcode and 'Addr' in pcode:
    pcode = re.sub(r'addr\s*=\s*Calc\w+Addr\([^)]*\)\s*;?\n?', '', pcode).replace('MEM[addr', 'MEM[ADDR')

  is_lds = isinstance(inst, (ir3.DS, ir4.DS, irc.DS))
  is_scratch = isinstance(inst, (ir3.SCRATCH, ir4.VSCRATCH, irc.SCRATCH))
  # CDNA acc bit: when set, VGPR operands (vdst/vdata) target ACCVGPR file instead of VGPR
  use_acc = bool(_iattr(inst, 'acc'))
  mem = ctx.lds if is_lds else ctx.scratch if is_scratch else ctx.vmem
  addr_shift = _c(2, dtypes.uint32 if is_lds else dtypes.uint64)

  # Field names differ per format: DS (addr/data0/offset0+offset1), RDNA4 V* (vaddr/vsrc/ioffset), RDNA3+CDNA (addr/data/offset)
  if is_lds: addr_field, data_field = 'addr', 'data0'
  elif isinstance(inst, (ir4.VGLOBAL, ir4.VSCRATCH, ir4.VFLAT)): addr_field, data_field = 'vaddr', 'vsrc'
  else: addr_field, data_field = 'addr', 'data'
  addr_reg = ctx.inst_field(getattr(type(inst), addr_field))
  vdata_reg, vdst_reg = ctx.inst_field(getattr(type(inst), data_field)), ctx.inst_field(type(inst).vdst)
  if is_lds:
    offset0, offset1 = ctx.inst_field(type(inst).offset0), ctx.inst_field(type(inst).offset1)  # type: ignore[union-attr]
    offset, saddr_reg = (offset1 << _c(8)) | offset0, None  # DS offset is 16-bit: (offset1 << 8) | offset0
  else:
    # FLAT always uses a VGPR pair; its unused saddr bits can be zero rather than NULL.
    offset0, offset1 = _c(0), _c(0)
    saddr_reg = None if isinstance(inst, (ir3.FLAT, ir4.VFLAT, irc.FLAT)) else ctx.optional_field(inst, 'saddr')
    offset = ctx.inst_field_signed(getattr(type(inst), 'ioffset' if hasattr(type(inst), 'ioffset') else 'offset'))

  # Data width from canonical_op_bits (32/64/96/128), default to 32 for untyped ops
  data_bits_mem = inst.canonical_op_bits.get('data', 32)
  is_atomic, glc = 'ATOMIC' in op_name, _iattr(inst, 'glc')
  data1_reg = ctx.inst_field(type(inst).data1) if is_lds else _c(0)  # type: ignore[union-attr]

  if is_lds and op_name == 'DS_SWIZZLE_B32':
    # The manual's reverse_bits operates on five-bit lane indices; thread indices wrap within the wave.
    funcs = {'reverse_bits': lambda x: _bitreverse(x, 32) >> _c(27), 'count_ones': _countbits,
             'thread_in': lambda x: ctx.rvgpr_dyn(addr_reg, x & _c(ctx.wave_size - 1)),
             'thread_valid': lambda x: _lane_active(exec_mask, x & _c(ctx.wave_size - 1))}
    result, _ = parse_pcode(pcode, {'offset0': offset0.cast(dtypes.uint8), 'offset1': offset1.cast(dtypes.uint8)}, funcs)
    values = [result[f'thread_out@{i}'] for i in range(ctx.wave_size)]
    # Snapshot every source before writing: destination and source registers may be identical.
    reads = UOp(Ops.STACK, src=tuple(values))
    return UOp.sink(*(ctx.wvgpr_dyn(vdst_reg, _c(i), val, exec_mask, after=reads) for i, val in enumerate(values)))

  # DS_PERMUTE/DS_BPERMUTE: cross-lane VGPR access via pcode
  if is_lds and 'PERMUTE' in op_name:
    srcs = {'ADDR': addr_reg, 'DATA0': vdata_reg, 'VDST': vdst_reg, 'OFFSET': offset,
            'EXEC': exec_mask.cast(dtypes.uint64), '_vgpr': ctx.vgpr, '_wave_size': ctx.wave_size}
    _, assigns = parse_pcode(pcode, srcs)
    stores = [ctx.vgpr.index(val[0]).store(val[1].cast(dtypes.uint32)) for dest, val in assigns if dest.startswith('VGPR[')]
    return UOp.sink(*stores)

  def make_addr(lane: UOp) -> UOp:
    if is_lds:
      addr = ctx.rvgpr_dyn(addr_reg, lane)
      # Some DS pcode (e.g. DS_STORE_B16) uses MEM[ADDR] without adding OFFSET explicitly.
      # In those cases, add the instruction offset to ADDR here.
      if 'OFFSET' not in pcode: addr = addr + offset
      return addr
    offset64 = offset.cast(dtypes.uint64)
    # Dynamic saddr check: saddr < 124 means valid SGPR, otherwise use VGPR pair for address
    use_saddr = (saddr_reg < _c(124)) if saddr_reg is not None else UOp.const(False)
    if is_scratch:
      base = lane.cast(dtypes.uint64) * ctx.scratch_stride.cast(dtypes.uint64)
      # SVE (Scratch VGPR Enable): when SVE=1, VADDR is used as offset; when SVE=0, VADDR is ignored
      sve = _iattr(inst, 'sve')
      vaddr = ctx.rvgpr_dyn(addr_reg, lane).cast(dtypes.uint64)
      addr_offset = vaddr if sve == 1 else _c(0, dtypes.uint64)
      # Add saddr value only if use_saddr is true (saddr < 124)
      saddr_contrib = use_saddr.where(ctx.rsgpr_dyn(saddr_reg).cast(dtypes.uint64), _c(0, dtypes.uint64)) \
        if saddr_reg is not None else _c(0, dtypes.uint64)
      return base + addr_offset + saddr_contrib + offset64
    # GLOBAL can use an SGPR base plus a VGPR offset; FLAT always uses the full VGPR pair.
    saddr_base = _u64(ctx.rsgpr_dyn(saddr_reg), ctx.rsgpr_dyn(saddr_reg + _c(1))) if saddr_reg is not None else _c(0, dtypes.uint64)
    vaddr_base = _u64(ctx.rvgpr_dyn(addr_reg, lane), ctx.rvgpr_dyn(addr_reg + _c(1), lane))
    # When saddr is valid: base = saddr pair, vaddr is 32-bit offset; otherwise: base = 0, vaddr is 64-bit address
    base_addr = use_saddr.where(saddr_base + ctx.rvgpr_dyn(addr_reg, lane).cast(dtypes.uint64), vaddr_base)
    return base_addr + offset64

  def wmem(addr: UOp, val: UOp, active: UOp, data_bits: int = 32) -> UOp:
    if data_bits < 32:
      # Sub-dword LDS write: read-modify-write within the uint32 slot
      word_addr = addr >> addr_shift
      idx = mem.index(word_addr.valid(active))
      byte_pos = addr.cast(dtypes.uint32) & _c(3)
      byte_shift = byte_pos * _c(8)
      size_mask = _c(0xFF if data_bits == 8 else 0xFFFF)
      mask = size_mask << byte_shift
      new_word = (idx & (mask ^ _c(0xFFFFFFFF))) | ((val.cast(dtypes.uint32) & size_mask) << byte_shift)
      return idx.store(active.where(new_word, idx))
    idx = mem.index(addr >> addr_shift)
    return idx.store(active.where(val, idx.load()))

  def make_srcs(lane: UOp) -> dict:
    addr = make_addr(lane)
    # acc selects the data register file, not the address registers, for both LDS and global memory.
    _rvdata = ctx.raccvgpr_dyn if use_acc else ctx.rvgpr_dyn
    if is_lds:
      if data_bits_mem <= 32:
        data = {'DATA': _rvdata(vdata_reg, lane), 'DATA2': _rvdata(data1_reg, lane)}
      elif data_bits_mem == 64:  # DATA/DATA2 are the 64-bit input registers, formed from register pairs
        data = {'DATA': _u64(_rvdata(vdata_reg, lane), _rvdata(vdata_reg + _c(1), lane)),
                'DATA2': _u64(_rvdata(data1_reg, lane), _rvdata(data1_reg + _c(1), lane))}
      else:  # 96/128-bit: one register per dword
        data = {'DATA': _rvdata(vdata_reg, lane), **{f'DATA{i}': _rvdata(vdata_reg + _c(i), lane) for i in range(1, data_bits_mem // 32)}}
      if 'D16' in op_name: data['RETURN_DATA'] = _rvdata(vdst_reg, lane)
      # RDNA3 uses ADDR/OFFSET, RDNA4 uses vgpr_a/offset (lowercase) + CalcDsAddr function
      return {'ADDR': addr, 'ADDR_BASE': addr, 'OFFSET': offset, 'OFFSET0': offset0, 'OFFSET1': offset1, '_lds': mem, 'laneId': lane,
              'vgpr_a': ctx.rvgpr_dyn(addr_reg, lane), 'offset': offset, 'offset0': offset0, 'offset1': offset1,
              '_active': _lane_active(exec_mask, lane), **data}
    active = _lane_active(exec_mask, lane)
    # saddr < 124 means valid SGPR pair, otherwise use 0 (NULL means no saddr contribution)
    use_saddr = (saddr_reg < _c(124)) if saddr_reg is not None else UOp.const(False)
    saddr_raw = _u64(ctx.rsgpr_dyn(saddr_reg), ctx.rsgpr_dyn(saddr_reg + _c(1))) if saddr_reg is not None else _c(0, dtypes.uint64)
    saddr_base = use_saddr.where(saddr_raw, _c(0, dtypes.uint64))
    # Sign-extend offset to 64-bit for the final address calculation
    ioffset64 = offset.cast(dtypes.int64).cast(dtypes.uint64)
    # v_addr for CalcGlobalAddr: when saddr valid, use low 32 bits as offset; otherwise full 64-bit address. Include ioffset.
    vaddr_full = _u64(ctx.rvgpr_dyn(addr_reg, lane), ctx.rvgpr_dyn(addr_reg + _c(1), lane))
    vaddr_lo = ctx.rvgpr_dyn(addr_reg, lane).cast(dtypes.uint64)
    vaddr_base = use_saddr.where(vaddr_lo + ioffset64, vaddr_full + ioffset64)
    if is_atomic:
      atomic_data = _u64(ctx.rvgpr_dyn(vdata_reg, lane), ctx.rvgpr_dyn(vdata_reg + _c(1), lane)) \
        if data_bits_mem == 64 else ctx.rvgpr_dyn(vdata_reg, lane)
      return {'ADDR': addr, 'DATA': atomic_data, '_vmem': mem, '_active': active, 'laneId': lane, 'v_addr': vaddr_base, 's_saddr': saddr_base}
    vdata = _rvdata(vdata_reg, lane).cast(dtypes.uint64) if 'STORE' in op_name \
      else _rvdata(vdst_reg, lane) if 'D16' in op_name else _c(0, dtypes.uint32)
    if 'STORE' in op_name and data_bits_mem >= 64:
      vdata = vdata | (_rvdata(vdata_reg + _c(1), lane).cast(dtypes.uint64) << _c(32, dtypes.uint64))
    srcs = {'ADDR': addr, 'VDATA': vdata, '_vmem': mem, '_active': active,
            'laneId': lane, 'v_addr': vaddr_base, 's_saddr': saddr_base, 'SADDR': saddr_base, 'OFFSET': offset}
    for i in range(data_bits_mem // 32):
      srcs[f'VDATA{i}'] = _rvdata(vdata_reg + _c(i), lane) if 'STORE' in op_name else _c(0, dtypes.uint32)
    return srcs

  def make_stores(dest: str, val: UOp, lane: UOp, active: UOp, writes_return_data: bool) -> list[UOp]:
    # Parse bit width from dest format: MEM[...].b32 or RETURN_DATA[63:32].b64
    parts = dest.rsplit('.', 1)
    data_bits = int(parts[1][1:]) if len(parts) == 2 else 32
    if dest.startswith('MEM['):
      if is_lds or is_atomic:
        if data_bits < 32 and is_lds: return [wmem(val[0], val[1], active, data_bits)]
        return _write_val(data_bits, val[1], wmem, val[0], active, is_mem=True)
      return _mem_store_bytes(mem if is_scratch else mem.bitcast(dtypes.uint8), val[0], val[1], active, data_bits)
    if dest.startswith('RETURN_DATA') and writes_return_data:
      write_gpr = ctx.waccvgpr_dyn if use_acc else ctx.wvgpr_dyn
      _wdata = lambda r, v, l, e: write_gpr(r, l, v, e)  # noqa: E731  (arg order: reg, val, lane, exec)
      if (m := re.match(r'RETURN_DATA\[(\d+)\s*:\s*(\d+)\]', dest)):
        bit_width, dword_idx = int(m.group(1)) - int(m.group(2)) + 1, int(m.group(2)) // 32
        return _write_val(bit_width, val, _wdata, vdst_reg + _c(dword_idx), lane, exec_mask)
      return _write_val(data_bits, val, _wdata, vdst_reg, lane, exec_mask)
    return []

  # DS-specific: check for 2ADDR pattern needing separate ranges
  if is_lds:
    dummy_lane = ctx.range()
    _, assigns = parse_pcode(pcode, make_srcs(dummy_lane))
    mem_assigns = [d for d, _ in assigns if d.startswith('MEM[')]
    mem_addrs = set(m.group(1) if (m := re.match(r'MEM\[([^\]]+)\]', d)) else d for d in mem_assigns)
    use_separate_ranges = (len(mem_addrs) > 1 or '2ADDR' in op_name) and 'STOREXCHG' not in op_name
    if use_separate_ranges:
      # Split assigns into MEM writes (stores) and RETURN_DATA writes (loads).
      # Stores to different addresses need separate lane ranges. Loads must share a single lane range so the
      # addr vgpr is read before any vdst write (hardware reads addr once, then writes all results).
      store_assigns = [(i, d) for i, (d, _) in enumerate(assigns) if d.startswith('MEM[')]
      load_assigns = [(i, d) for i, (d, _) in enumerate(assigns) if d.startswith('RETURN_DATA')]
      ended: list[UOp] = []
      for i, dest in store_assigns:
        lane = ctx.range()
        active = _lane_active(exec_mask, lane)
        _, lane_assigns = parse_pcode(pcode, make_srcs(lane))
        ended.extend(s.end(lane) for s in make_stores(dest, lane_assigns[i][1], lane, active, True))
      if load_assigns:
        lane = ctx.range()
        active = _lane_active(exec_mask, lane)
        _, lane_assigns = parse_pcode(pcode, make_srcs(lane))
        load_stores: list[UOp] = []
        for i, dest in load_assigns:
          load_stores.extend(make_stores(dest, lane_assigns[i][1], lane, active, True))
        if load_stores: ended.append(UOp.group(*load_stores).end(lane))
      return UOp.sink(*ended)

  # Standard path: single lane range
  writes_return_data = '_RTN' in op_name or (is_lds and (op_name.startswith('DS_LOAD') or op_name.startswith('DS_READ'))) or bool(is_atomic and glc)
  lane = ctx.range()
  active = _lane_active(exec_mask, lane)
  pcode_vars, assigns = parse_pcode(pcode, make_srcs(lane))
  if is_lds and 'D16' in op_name and writes_return_data: assigns = [('RETURN_DATA.b32', pcode_vars['RETURN_DATA'])]
  stores = [s for dest, val in assigns for s in make_stores(dest, val, lane, active, writes_return_data)]

  # FLAT/GLOBAL/SCRATCH: collect VDATA slices for loads
  if not is_lds and not is_atomic:
    _wdst = ctx.waccvgpr_dyn if use_acc else ctx.wvgpr_dyn
    for dword_idx, val in sorted(_collect_data_slices(assigns, 'VDATA', pcode_vars, op_name).items()):
      stores.append(_wdst(vdst_reg + _c(dword_idx), lane, val, exec_mask))

  return UOp.sink(UOp.group(*stores).end(lane))

def _compile_mubuf(inst: irc.MUBUF, ctx: _Ctx) -> UOp:
  """CDNA MUBUF: linear buffer address = base + soffset + (stride * index) + vgpr_offset + inst_offset"""
  exec_mask, op_name = ctx.rexec(), _op_name(inst)
  use_acc, is_store, is_lds = bool(_iattr(inst, 'acc')), 'STORE' in op_name, bool(_iattr(inst, 'lds'))
  n_dwords = 4 if 'X4' in op_name else 2 if 'X2' in op_name else 1

  # instruction fields
  vdata, vaddr = ctx.inst_field(type(inst).vdata), ctx.inst_field(type(inst).vaddr)
  srsrc, soffset = ctx.inst_field(type(inst).srsrc) * _c(4), ctx.inst_field(type(inst).soffset)
  offset, offen, idxen = ctx.inst_field(type(inst).offset), ctx.inst_field(type(inst).offen), ctx.inst_field(type(inst).idxen)

  # V# descriptor: base[0:1], num_records[2], stride=word3[13:0]
  base = _u64(ctx.rsgpr_dyn(srsrc), ctx.rsgpr_dyn(srsrc + _c(1))) & _c(0xFFFFFFFFFFFF, dtypes.uint64)
  num_records = ctx.rsgpr_dyn(srsrc + _c(2))
  stride = (ctx.rsgpr_dyn(srsrc + _c(3)) & _c(0x3FFF)).cast(dtypes.uint64)

  lane = ctx.range()
  active = _lane_active(exec_mask, lane)

  # soffset: sgpr if < 128, else inline constant
  soff = (soffset < _c(128)).where(ctx.rsgpr_dyn(soffset), soffset - _c(128)).cast(dtypes.uint64)
  # vaddr: index (if idxen) in vaddr, offset (if offen) in vaddr or vaddr+1
  index = idxen.ne(_c(0)).where(ctx.rvgpr_dyn(vaddr, lane), _c(0)).cast(dtypes.uint64)
  voff = offen.ne(_c(0)).where(ctx.rvgpr_dyn(idxen.ne(_c(0)).where(vaddr + _c(1), vaddr), lane), _c(0)).cast(dtypes.uint64)

  # buffer_offset for bounds check, final address
  buffer_offset = (stride * index + voff + offset.cast(dtypes.uint64)).cast(dtypes.uint32)
  in_bounds = active & buffer_offset.__lt__(num_records)
  addr = base + soff + buffer_offset.cast(dtypes.uint64)
  addr = in_bounds.where(addr, _c(0, dtypes.uint64))  # safe address when OOB
  mem = ctx.vmem

  stores: list[UOp] = []
  if is_lds and not is_store:
    # LDS load: buffer -> LDS (bypass VGPRs), LDS addr = M0[17:0] + lane * elem_size
    lds_base = ctx.rsgpr_dyn(_c(124)) & _c(0x3FFFF)
    lds_addr = lds_base + lane.cast(dtypes.uint32) * _c(n_dwords * 4)
    for i in range(n_dwords):
      word_addr = (addr + _c(i * 4, dtypes.uint64)) >> _c(2, dtypes.uint64)
      val = in_bounds.where(mem.index(word_addr.cast(dtypes.int64)).load(), _c(0))
      lds_idx = (lds_addr + _c(i * 4)) >> _c(2)
      lds_slot = ctx.lds.index(lds_idx.valid(active))
      stores.append(lds_slot.store(active.where(val, lds_slot)))
  elif is_store:
    for i in range(n_dwords):
      word_addr = (addr + _c(i * 4, dtypes.uint64)) >> _c(2, dtypes.uint64)
      idx = mem.index(word_addr.cast(dtypes.int64).valid(in_bounds))
      val = (ctx.raccvgpr_dyn if use_acc else ctx.rvgpr_dyn)(vdata + _c(i), lane)
      stores.append(idx.store(in_bounds.where(_to_u32(val), idx)))
  else:
    for i in range(n_dwords):
      word_addr = (addr + _c(i * 4, dtypes.uint64)) >> _c(2, dtypes.uint64)
      val = in_bounds.where(mem.index(word_addr.cast(dtypes.int64).valid(in_bounds)).load(), _c(0))
      stores.append((ctx.waccvgpr_dyn if use_acc else ctx.wvgpr_dyn)(vdata + _c(i), lane, val, exec_mask))
  return UOp.sink(UOp.group(*stores).end(lane))

# Dispatch table: instruction type -> handler function. Classes are looked up by name across all three archs.
def _inst_kinds(*names: str) -> tuple[type, ...]:
  return tuple(getattr(m, n) for m in (ir3, ir4, irc) for n in names if hasattr(m, n))

_COMMON_HANDLERS: list[tuple[Callable[..., UOp], tuple[str, ...]]] = [
  (_compile_sopp, ('SOPP',)),
  (_compile_smem, ('SMEM',)),
  (_compile_sop, ('SOP1', 'SOP2', 'SOPC', 'SOPK')),
  (_compile_vop12, ('VOP1', 'VOP1_SDST', 'VOP1_DPP16', 'VOP2', 'VOP2_DPP16')),
  (_compile_vopc, ('VOPC', 'VOPC_DPP16')),
  (_compile_vop3, ('VOP3', 'VOP3_SDST')),
  (_compile_vinterp, ('VINTERP',)),
  (_compile_vop3sd, ('VOP3SD',)),
  (_compile_vop3p, ('VOP3P', 'VOP3PX2')),
  (_compile_vopd, ('VOPD',)),
  (_compile_sdwa, ('VOP1_SDWA', 'VOP2_SDWA', 'VOP2_SDWA_SDST', 'VOPC_SDWA_SDST')),
  (_compile_mem_op, ('DS', 'FLAT', 'GLOBAL', 'SCRATCH', 'VFLAT', 'VGLOBAL', 'VSCRATCH')),
]
_INST_HANDLERS: dict[type, Callable[..., UOp]] = {t: h for h, names in _COMMON_HANDLERS for t in _inst_kinds(*names)}
_IR4_TYPES = (ir4.VOP1, ir4.VOP2, ir4.VOPC, ir4.VOP3, ir4.VOP3SD, ir4.VOP3P)
_INST_HANDLERS[irc.MUBUF] = _compile_mubuf  # CDNA only (rdna3 also has a MUBUF class, intentionally unhandled)

def _get_handler(inst: Inst) -> Callable[..., UOp]:
  if isinstance(inst, _IR4_TYPES) and (hasattr(type(inst), 'vsrc0') or getattr(getattr(inst, 'src0', None), 'offset', 0) in (233, 234, 250)) and \
     any(bits == 64 and fmt.name != 'FMT_NUM_M64' for fmt, bits, _ in inst.canonical_operands.values()):
    # llvm rejects dpp on any 64-bit operand for gfx12 ("dpp variant of this instruction is not supported") and the chip hangs on it
    raise RuntimeError(f"{_op_name(inst)} with dpp: 64-bit operands have no dpp form on rdna4 (illegal encoding; the gpu hangs)")
  # Look up handler by type, falling back to base classes for _LIT variants
  handler = _INST_HANDLERS.get(type(inst))
  if handler is not None: return handler
  for cls in type(inst).__mro__:
    if cls in _INST_HANDLERS: return _INST_HANDLERS[cls]
  raise RuntimeError(f"[emu] unimplemented instruction type: {type(inst).__name__} {_op_name(inst)}")

# ═══════════════════════════════════════════════════════════════════════════════
# PROGRAM DECODE AND COMPILATION
# ═══════════════════════════════════════════════════════════════════════════════

_BARRIER_OPS = {ir3.SOPPOp.S_BARRIER, irc.SOPPOp.S_BARRIER, ir4.SOPPOp.S_BARRIER_WAIT}
_BARRIER_SOP1_OPS = {ir4.SOP1Op.S_BARRIER_SIGNAL}

# Inline float constants (as bit patterns) for GPU instructions
F32_INLINE = {240: 0x3f000000, 241: 0xbf000000, 242: 0x3f800000, 243: 0xbf800000,  # 0.5, -0.5, 1.0, -1.0
              244: 0x40000000, 245: 0xc0000000, 246: 0x40800000, 247: 0xc0800000, 248: 0x3e22f983}  # 2.0, -2.0, 4.0, -4.0, 1/(2*pi)

@uopfunc
def store_consts(sgpr:UOp, wave_size:int):
  ci = UOp.range(81, 2, AxisType.LOOP, dtype=dtypes.int)
  init_ints = sgpr.index(ci+128).store((ci<65).where(ci, 64-ci).cast(dtypes.uint32)).end(ci)
  init_floats = UOp.group(*[sgpr.index(i).store(_c(v)) for i,v in F32_INLINE.items()])
  return UOp.sink(init_ints, init_floats, *([sgpr.index(124).store(_c(0))] if wave_size == 32 else []))

@uopfunc
def loop_active(routes:UOp, active:UOp, header:UOp, waves:UOp):
  w = UOp.range(waves, 0, AxisType.LOOP, dtype=dtypes.int)
  return active[0].store(routes[w].load().eq(header).cast(dtypes.uint32).reduce(w, arg=Ops.MAX).ne(0)).sink()

def lower_body(sink:UOp, name:str) -> UOp:
  bufs = sorted((u for u in sink.toposort() if u.op is Ops.PARAM), key=lambda u: u.arg.slot)
  body = sink.substitute({b:b.param_like(i, name=b.arg.name) for i,b in enumerate(bufs)}, walk=True)
  return body.call(*bufs, name=name)

instruction_cache:dict[tuple, list[tuple[int, int, tuple[UOp|None, UOp|None, dict[UOp, UOp]]]]] = {}

def instruction_call(inst:Inst, arch:str, renderer:Renderer) -> tuple[UOp|None, UOp|None]:
  entries = instruction_cache.setdefault((arch, type(inst), inst.size(), type(renderer), renderer.target, *(x.value for x in to_program_config)), [])
  inst_bytes = inst.to_bytes()
  bits = int.from_bytes(inst_bytes, "little")
  for base, mask, ret in entries:
    if bits & mask == base: break
  else:
    ctx = _Ctx(_wave_size(arch))
    sink = _get_handler(inst)(inst, ctx)
    base, mask = ctx.canonical_mask(inst_bytes)
    name = f"{_op_name(inst).lower()}_{base.to_bytes(len(inst_bytes), 'little').hex()}"
    call = lower_body(sink, name) if sink.src else None
    used = UOp.sink(call, ctx.branch_cond).toposort()
    ret = call, ctx.branch_cond, {p:index for index,p in ctx.sgpr_reads.items() if p in used}
    entries.append((base, mask, ret))
  call, cond, reads = ret
  words = {f"inst_w{i}":(bits >> (32*i)) & 0xffffffff for i in range(inst.size()//4)}
  bindings = {_Ctx.inst_word(i):_c(words[f"inst_w{i}"]) for i in range(inst.size()//4)}
  bindings.update({p:_Ctx.sgpr.index(_c(index.get_idx().sym_infer(words))).load() if index.get_valid().sym_infer(words) else _c(0)
                   for p,index in reads.items()})
  if call is not None: call = call.replace(src=(call.body, *(bindings.get(b, b) for b in call.src[1:])))
  return call, cond.substitute(bindings) if cond is not None else None

def instruction_block(instructions:list[UOp]) -> tuple[UOp, list[UOp]]:
  bufs = sorted({buf for call in instructions for b in call.src[1:] if (buf:=b.buf_uop).op is Ops.PARAM}, key=lambda b: b.arg.slot)
  params = {b:b.param_like(i, name=b.arg.name) for i,b in enumerate(bufs)}
  linear = list(UOp.sink(*params.values()).toposort())[:-1]
  seen: set[UOp] = set()
  for call in instructions:
    args = [params.get(b, b) for b in call.src[1:]]
    inputs = UOp.sink(*args)
    nodes = inputs.toposort(lambda u:u.op is not Ops.PARAM and u not in seen)
    nodes.pop(inputs)
    seen.update(nodes)
    linear.extend(nodes)
    linear.append(call.replace(src=(call.body, *args)))
    if _Ctx.sgpr in call.src[1:]: seen.clear()
  return UOp(Ops.PROGRAM, src=(sink:=UOp.sink(*linear, arg=KernelInfo("asm_block", optimized=True)), UOp(Ops.LINEAR, src=(*linear, sink)))), bufs

def thread_branches(insts, blocks:dict[int, list[int]], paths:dict[int, dict[int, int]]):
  # thread jump-only blocks.
  targets:dict[int, int] = {}
  def target(pc:int) -> int:
    seen:set[int] = set()
    while pc not in targets and pc not in seen and len(blocks[pc]) == 1 and getattr(insts[blocks[pc][0]], "op_name", "") == "S_BRANCH":
      seen.add(pc)
      pc = next(iter(paths[pc]))
    pc = targets.get(pc, pc)
    targets.update((src, pc) for src in seen)
    return pc
  for pc, dsts in list(paths.items()): paths[pc] = {target(dst):kind for dst,kind in dsts.items()}

def merge_branches(insts, blocks:dict[int, list[int]], paths:dict[int, dict[int, int]]):
  groups:dict[tuple, list[int]] = {}
  opposite = {"S_CBRANCH_SCC1":"S_CBRANCH_SCC0", "S_CBRANCH_VCCNZ":"S_CBRANCH_VCCZ", "S_CBRANCH_EXECNZ":"S_CBRANCH_EXECZ"}
  for pc, pcs in blocks.items():
    if len(paths[pc]) != 2: continue
    inst = insts[pcs[-1]]
    # complementary tests with reversed destinations are the same branch.
    branch_dests = tuple(sorted((dst, kind ^ (inst.op_name in opposite)) for dst,kind in paths[pc].items()))
    key = (type(inst), opposite.get(inst.op_name, inst.op_name),
           tuple((n, getattr(inst, n)) for n,_ in inst._fields if n not in {"op", "simm16"}), branch_dests)
    groups.setdefault(key, []).append(pc)
  for group in groups.values():
    if len(group) < 2: continue
    header = blocks[group[0]][-1]
    dests = paths[group[0]]
    for pc in group:
      blocks[pc] = blocks[pc][:-1]
      paths[pc] = {header:UNCOND}
    blocks[header], paths[header] = [header], dests

# a block has an empty body; a loop contains its header block and the rest of its iteration.
CFGRegion = tuple[int, list["CFGRegion"]]
class IrreducibleCFG(RuntimeError): pass

def cfg_regions(paths:dict[int, dict[int, int]], entry:int) -> list[CFGRegion]:
  # number the reachable blocks in DFS postorder, without recursion on long instruction streams.
  order:dict[int, int] = {}
  seen, pending = set(), [(entry, False)]
  while pending:
    pc, visited = pending.pop()
    if visited: order[pc] = len(order)
    elif pc not in seen:
      seen.add(pc)
      pending.append((pc, True))
      pending.extend((dst, False) for dst in sorted(paths[pc], reverse=True))
  preds:dict[int, set[int]] = {pc:set() for pc in order}
  for pc in order:
    for dst in paths[pc]: preds[dst].add(pc)
  def build(remaining:set[int]) -> list[CFGRegion]:
    regions: list[CFGRegion] = []
    # reverse postorder and predecessor walks partition this region into SCCs in execution order.
    for pc in sorted(remaining, key=order.__getitem__, reverse=True):
      if pc not in remaining: continue
      component, todo = set(), [pc]
      while todo:
        if (dst:=todo.pop()) not in remaining: continue
        remaining.remove(dst)
        component.add(dst)
        todo.extend(preds[dst])
      body:list[CFGRegion] = []
      if len(component) > 1 or pc in paths[pc]:
        if any(preds[dst] - component for dst in component if dst != pc):
          raise IrreducibleCFG("irreducible control flow is not supported by the AMD lifter")
        # removing the single entry exposes nested loops; the original DFS order still applies.
        body = [(pc, [])] + build(component - {pc})
      regions.append((pc, body))
    return regions
  return build(set(order))

@rewrite_group(replay="emu_process_replay")
def lift(code:bytes, arch:str, renderer:Renderer, dispatch:tuple, name:str="") -> UOp:
  _lift_arch[0] = arch
  insts = amd_decode(code, arch)
  for inst in insts.values():
    inst_st = getattr(inst, "op_name", "").lower()
    if inst_st.startswith(("s_getpc", "s_setpc")): raise NotImplementedError(f"AMD lifter does not support {inst_st}")
  cfg = get_cfg(insts)
  thread_branches(insts, cfg["blocks"], cfg["paths"])
  try: regions = cfg_regions(cfg["paths"], 0)
  except IrreducibleCFG:
    # sharing branch tails can make rotated loops reducible, but adds dispatch blocks otherwise.
    merge_branches(insts, cfg["blocks"], cfg["paths"])
    regions = cfg_regions(cfg["paths"], 0)
  # propagate possible wave PCs across acyclic regions; loops retain runtime routing.
  unconditional:set[int] = set()
  possible:set[int]|None = {0}
  for pc, body in regions:
    if body: possible = None
    elif possible is not None:
      if possible == {pc}: unconditional.add(pc)
      possible = (possible-{pc}) | (set(cfg["paths"][pc]) or {-1})
  routed = len(unconditional) != len(regions)
  axes = itertools.count(sum(inst.size() for inst in insts.values()))
  gx, gy, gz, lx, ly, lz, rsrc2, scratch_size = dispatch
  # init ranges
  wave_size, total_threads = _wave_size(arch), lx*ly*lz
  n_waves = (total_threads+wave_size-1)//wave_size
  wg_base = UOp.variable("wg_base", 0, max(gx*gy*gz-1, 0), dtypes.uint64)
  wgr = UOp.range(UOp.variable("wg_n", 1, gx*gy*gz, dtypes.uint64), 0, AxisType.LOOP, dtype=dtypes.uint64)
  wg = wgr + wg_base
  wave = UOp.range(n_waves, 1, AxisType.LOOP, dtype=dtypes.int)
  # alloc register and LDS buffers
  sgpr = UOp.alloc((n_waves*SGPR_COUNT,), dtypes.uint32, 0, AddrSpace.REG)
  vgpr = UOp.alloc((n_waves*256*wave_size,), dtypes.uint32, 1, AddrSpace.REG)
  lds_size = ((rsrc2 & hsa.AMD_COMPUTE_PGM_RSRC_TWO_GRANULATED_LDS_SIZE) >> hsa.AMD_COMPUTE_PGM_RSRC_TWO_GRANULATED_LDS_SIZE_SHIFT)*512
  lds = UOp.alloc((max(lds_size//4, 1),), dtypes.uint32, 3, AddrSpace.REG)
  scratch = UOp.alloc((max(scratch_size*wave_size*n_waves, 1),), dtypes.uint8, 4, AddrSpace.REG)
  accvgpr = UOp.alloc((256*wave_size*n_waves,), dtypes.uint32, 5, AddrSpace.REG) if wave_size == 64 else vgpr
  args_ptr = UOp.variable("args_ptr", 0, dtypes.uint64.max, dtypes.uint64)
  ctx = _Ctx(wave_size)
  buffers = {ctx.sgpr:(sgpr, SGPR_COUNT), ctx.vgpr:(vgpr, 256*wave_size), ctx.vmem:(ctx.vmem, 0),
             ctx.lds:(lds, 0), ctx.scratch:(scratch, scratch_size*wave_size)}
  if wave_size == 64: buffers[ctx.accvgpr] = (accvgpr, 256*wave_size)
  routes = UOp.alloc((n_waves,), dtypes.int, 6, AddrSpace.REG)
  active = UOp.alloc((1,), dtypes.bool, 7, AddrSpace.REG)
  route = UOp.param(6, dtypes.int, (1,), name="route")
  taken, fallthrough = [UOp.param(i, dtypes.int, name=name, addrspace=AddrSpace.ALU) for i,name in enumerate(("taken", "fallthrough"), 7)]
  buffers[route] = (routes, 1)
  # set per wave registers
  wave_sgpr = sgpr.shrink(((wave*SGPR_COUNT, (wave+1)*SGPR_COUNT),)).after(wgr)
  wave_vgpr = vgpr.shrink(((wave*256*wave_size, (wave+1)*256*wave_size),)).after(wgr)
  consts = store_consts(wave_sgpr, wave_size)
  gidx, gidy, gidz = wg%gx, (wg//gx)%gy, wg//(gx*gy)
  n_lanes = (total_threads-wave*wave_size).minimum(wave_size)
  runtime_sgprs = [(0, args_ptr.cast(dtypes.uint32)), (1, (args_ptr>>32).cast(dtypes.uint32))]
  if arch == "rdna4": runtime_sgprs += [(ttmp[7].offset, (gidy&0xFFFF)|((gidz&0xFFFF)<<16)), (ttmp[9].offset, gidx)]
  else:
    sgpr_id = (rsrc2 & hsa.AMD_COMPUTE_PGM_RSRC_TWO_USER_SGPR_COUNT) >> hsa.AMD_COMPUTE_PGM_RSRC_TWO_USER_SGPR_COUNT_SHIFT
    for enabled, gid in [(hsa.AMD_COMPUTE_PGM_RSRC_TWO_ENABLE_SGPR_WORKGROUP_ID_X, gidx),
                         (hsa.AMD_COMPUTE_PGM_RSRC_TWO_ENABLE_SGPR_WORKGROUP_ID_Y, gidy),
                         (hsa.AMD_COMPUTE_PGM_RSRC_TWO_ENABLE_SGPR_WORKGROUP_ID_Z, gidz)]:
      if rsrc2 & enabled:
        runtime_sgprs.append((sgpr_id, gid))
        sgpr_id += 1
  runtime_sgprs += [(EXEC_LO.offset, ((_c(1, dtypes.uint64)<<n_lanes.minimum(32).cast(dtypes.uint64))-1).cast(dtypes.uint32))]
  if wave_size == 64:
    runtime_sgprs.append((EXEC_LO.offset+1, ((_c(1, dtypes.uint64)<<(n_lanes-32).maximum(0).cast(dtypes.uint64))-1).cast(dtypes.uint32)))
  lane = UOp.range(wave_size, 5, AxisType.LOOP, dtype=dtypes.int)
  tid = wave*wave_size+lane
  init_vgpr = wave_vgpr.index(lane.valid(tid<total_threads)).store((((tid//(lx*ly))<<20)|(((tid//lx)%ly)<<10)|(tid%lx)).cast(dtypes.uint32)).end(lane)
  init = UOp.group(init_vgpr, *(wave_sgpr.after(consts).index(i).store(_c(v)) for i,v in dict(runtime_sgprs).items()))
  # construct CALL graph
  initialized = (routes.after(init).index(wave).store(0) if routed else UOp.group(init, wave)).end(wave)
  def emit_block(block_pc:int, end:UOp, scopes:tuple[UOp, ...]) -> UOp:
    cond = UOp.const(True)
    instructions = []
    for off in cfg["blocks"][block_pc]:
      inst = insts[off]
      inst_st = getattr(inst, "op_name", "").lower()
      if inst_st.startswith("s_code_end"): continue
      call, branch_cond = instruction_call(inst, arch, renderer)
      if branch_cond is not None: cond = branch_cond
      if call is not None: instructions.append(call)
    values = {ctx.scratch_stride:_c(scratch_size)}
    if routed:
      dsts = {kind:dst for dst,kind in cfg["paths"][block_pc].items()}
      target = cond.where(taken, fallthrough) if len(dsts) == 2 else taken
      values.update({taken:_c(dsts[COND_TAKEN], dtypes.int), fallthrough:_c(dsts[COND_NOT_TAKEN], dtypes.int)} if len(dsts) == 2
                    else {taken:_c(next(iter(dsts.values()), -1), dtypes.int)})
      instructions.append(lower_body(route[0].store(target).sink(), "asm_branch"))
    if not instructions: return end
    body, bufs = instruction_block(instructions)
    args = [values[b] if b.addrspace is AddrSpace.ALU else buffers[b][0] for b in bufs]
    args += [_c(block_pc, dtypes.int).after(end, *scopes)]
    params = [UOp.param(i, a.dtype, a.shape, addrspace=AddrSpace.ALU if i >= len(bufs) or bufs[i].addrspace is AddrSpace.ALU
                        else AddrSpace.GLOBAL, name=bufs[i].arg.name if i < len(bufs) else None) for i,a in enumerate(args)]
    # lower the wave loop with the block, so repeated blocks share its indexing and route check too.
    w = UOp.range(n_waves, 0, AxisType.LOOP, dtype=dtypes.int)
    gates = () if block_pc in unconditional else (UOp.range(params[bufs.index(route)][w].load().eq(params[-1]).cast(dtypes.int),
                                                            1, AxisType.LOOP, dtype=dtypes.int),)
    call_args = [p if b.addrspace is AddrSpace.ALU else p.after(*gates, w).shrink(((w*s, (w+1)*s),))
                 if (s:=buffers[b][1]) else p.after(*gates, w) for b,p in zip(bufs, params)]
    block = UOp.group(body.call(*call_args, name="asm_block"), *gates, w).end(*gates).end(w).sink()
    return block.call(*args, name="asm_waves")
  def emit_dispatch(regions:list[CFGRegion], scopes:tuple[UOp, ...], end:UOp) -> UOp:
    for pc, body in regions:
      if body:
        loop = UOp.loop(next(axes)).replace(src=(UOp(Ops.NOOP).after(end),))
        end = emit_dispatch(body, scopes+(loop,), loop)
        # waves that exited keep their route while the remaining waves repeat the loop.
        check = loop_active(routes.after(end, *scopes, loop), active, _c(pc, dtypes.int), _c(n_waves, dtypes.int))
        end = end.backedge(loop, active.after(check, *scopes, loop)[0].load())
      else:
        # complete the block for every participating wave before entering its successors, including barrier successors.
        end = emit_block(pc, end, scopes)
    return end

  return emit_dispatch(regions, (wgr,), initialized).end(wgr).sink(ctx.vmem, arg=KernelInfo(name=name, optimized=True))

dispatch_cache:dict[tuple, UOp] = {}

RELIFT = ContextVar("RELIFT", 0) # lift and recompile to assembly N times
REPLAY_EMU = ContextVar("REPLAY_EMU", 0)

def run_asm(lib: int, lib_sz: int, gx: int, gy: int, gz: int, lx: int, ly: int, lz: int, args_ptr: int, rsrc2: int = 0x19c,
            scratch_size: int = 0, arch: str = "rdna3", name: str = "asm") -> int:
  """Execute AMD assembly program. scratch_size is private_segment_fixed_size from kernel descriptor (per-lane)."""
  with Context(DEV=DEV.target('CPU', renderer='LLVM'), LLVM_STRICT_FP=1, NOOPT=1, CHECK_OOB=0, TUPLE_ORDER=0, EMULATED_DTYPES="",
               CAPTURE_PROCESS_REPLAY=REPLAY_EMU.value, DEFAULT_FLOAT="float32", DEFAULT_INT="int32", TRANSCENDENTAL=1):
    code = bytes(to_mv(lib, lib_sz))
    dispatch = (gx, gy, gz, lx, ly, lz, rsrc2, scratch_size)
    if arch == "rdna4" and HW_FLOAT.value: _hw_tables()
    renderer = Device['CPU'].renderer
    if (key:=(code, arch, dispatch, name, type(renderer), renderer.target, *(x.value for x in to_program_config))) not in dispatch_cache:
      def build(): return to_program(lift(code, arch, renderer, dispatch, f"emu {name}"), renderer)
      host = (platform.machine(), getattr(getattr(renderer, "compiler", None), "cachekey", None) or _host_cpu(), _wmma_native())
      dispatch_cache[key] = build() if RELIFT.value else _cached("emu_program", _cache_key(*key[:4], repr(key[4:]), HW_FLOAT.value, host), build)
      relift_lib = code
      for relift_count in range(1, RELIFT.value+1):
        try:
          ret = to_program(lift(relift_lib, arch, Device["AMD"].renderer, dispatch, f"relift_{relift_count} {name}"), Device["AMD"].renderer)
        except Exception:
          print("relift err", traceback.format_exc())
          break
        relift_lib = get_elf_section(ret.src[3].arg, ".text").content
    prg = dispatch_cache[key]
  vmem_buf = UOp.from_buffer(Buffer('CPU', 1 << 48, options=BufferSpec(external_ptr=0), opaque=0), dtypes.uint32)
  total = gx*gy*gz
  ftz = not (arch == "rdna4" and HW_FLOAT.value)
  if EMU_THREADS.value <= 1 or total < 2: return _run_wgs(prg, vmem_buf, args_ptr, 0, total, ftz)
  chunk = -(-total // min(EMU_THREADS.value, total))
  list(_emu_pool().map(lambda base: _run_wgs(prg, vmem_buf, args_ptr, base, min(chunk, total-base), ftz), range(0, total, chunk)))
  return 0

EMU_THREADS = ContextVar("EMU_THREADS", os.cpu_count() or 1)
@functools.cache
def _emu_pool():
  import concurrent.futures
  return concurrent.futures.ThreadPoolExecutor(EMU_THREADS.value)

def _run_wgs(prg:UOp, vmem_buf:UOp, args_ptr:int, base:int, n:int, ftz:bool=True) -> int:
  vals = {"args_ptr": args_ptr, "wg_base": base, "wg_n": n}
  args = [vals[p.expr] if p.addrspace is AddrSpace.ALU else vmem_buf.buffer.ensure_allocated().get_buf("CPU") for p in prg.kernel_params]
  with _MXCSRContext(ftz): get_runtime("CPU", prg)(*args)
  return 0
