import time
import numpy as np
from tinygrad.helpers import to_mv, getenv
from tinygrad.runtime.autogen import mesa
from test.mockgpu.qcom import emu
METAL = getenv("QCOM_METAL")
if METAL: from test.mockgpu.qcom import metal

_fields:dict[str, tuple[int, int]] = {}
def field(val:int, name:str) -> int:
  if (f := _fields.get(name)) is None: f = _fields[name] = (getattr(mesa, f"{name}__MASK"), getattr(mesa, f"{name}__SHIFT"))
  return (val & f[0]) >> f[1]
def u64(lo:int, hi:int) -> int: return lo | (hi << 32)

class Mappings(dict):
  gen = 0
  def __setitem__(self, k, v):
    self.gen += 1
    super().__setitem__(k, v)
  def pop(self, *a):
    self.gen += 1
    return super().pop(*a)

class QCOMGPU:
  def __init__(self, mappings:Mappings):
    self.regs:dict[int, int] = {}
    self.mappings = mappings
    self._gen, self._ranges, self._known = -1, [], {}
    self.consts, self.shader = np.zeros(4096, np.uint32), b""
    self.samplers:list[bool] = []
    self.errors:list[Exception] = []
    self.pending:list[list[int]] = []
    self.draining = 0 # after an error, IBs already queued only signal
    self._rec:list|None = None
    self._rec_regs:dict[int, int] = {}
    self._plans:dict[tuple[int, int], tuple] = {}

  def report_error(self) -> Exception:
    err, self.draining = self.errors[0], len(self.pending)
    self.errors.clear()
    self.progress()
    return err

  def submit(self, addr:int, ndwords:int):
    words = np.frombuffer(to_mv(addr, ndwords * 4), np.uint32).copy()
    if METAL and not self.pending and not self.errors and not self.draining and self._replay(addr, words):
      metal.runtime().sync()
      return
    self.pending.append(words.tolist())
    if METAL and not self.pending[1:] and not self.errors and not self.draining: self._rec, self._rec_regs = [], dict(self.regs)
    self.progress()
    if self._rec is not None and not self.pending and not self.errors: self._record(addr, words)
    self._rec = None

  def _record(self, addr:int, words:np.ndarray):
    fixed = np.ones(len(words), bool)
    for kind, s, e, *_ in self._rec:
      if kind == "live": fixed[s + 1:e] = False
    self._plans[(addr, len(words))] = (words, fixed, self._rec_regs, self._rec, dict(self.regs))

  def _replay(self, addr:int, words:np.ndarray) -> bool:
    if (plan := self._plans.get((addr, len(words)))) is None: return False
    tpl, fixed, regs0, steps, regs1 = plan
    if self.regs != regs0 or not np.array_equal(words[fixed], tpl[fixed]): return False
    for step in steps:
      kind, s, e, regs, arg = step
      try:
        if kind == "live":
          if not self._exec_pkt7(arg, words[s + 1:e].tolist()):
            self.regs = dict(regs)
            self.pending.append(words[s:].tolist())
            self.progress()
            return True
        elif kind == "load": self._load_state(words[s + 1:e].tolist())
        else:
          self.regs = regs
          self._exec_cs(arg[0], arg[1])
      except Exception as ex:
        self.regs = dict(regs)
        self.errors.append(ex)
        self.pending.append(words[e:].tolist())
        return True
    self.regs = dict(regs1)
    return True

  def _refresh(self):  # the same list object until the mappings change: metal keys its host-memory wrappers on it
    if self._gen != self.mappings.gen: self._gen, self._ranges, self._known = self.mappings.gen, list(self.mappings.values()), {}

  def _ranges_now(self) -> list[tuple[int, int]]:
    self._refresh()
    return self._ranges

  def _cached(self, key, fn):
    self._refresh()
    if key not in self._known: self._known[key] = fn()
    return self._known[key]

  def progress(self):
    while self.pending and not self.errors:
      words, i = self.pending[0], 0
      while i < len(words):
        hdr = words[i]
        if hdr >> 28 == mesa.CP_TYPE4_PKT >> 28:
          reg, cnt = (hdr >> 8) & 0x3FFFF, hdr & 0x7F
          for k in range(cnt): self.regs[reg + k] = words[i + 1 + k]
        elif hdr >> 28 == mesa.CP_TYPE7_PKT >> 28:
          cnt, op = hdr & 0x3FFF, (hdr >> 16) & 0x7F
          if not self.draining or op not in (mesa.CP_EXEC_CS, mesa.CP_RUN_OPENCL, mesa.CP_LOAD_STATE6_FRAG):
            if self._rec is not None:
              snap = dict(self.regs)
              if op == mesa.CP_LOAD_STATE6_FRAG: self._rec.append(("load", i, i + 1 + cnt, snap, None))
              elif op in (mesa.CP_EXEC_CS, mesa.CP_RUN_OPENCL):
                groups = words[i+2:i+5] if op == mesa.CP_EXEC_CS else [self.regs[mesa.REG_A6XX_SP_CS_KERNEL_GROUP_X + k] for k in range(3)]
                self._rec.append(("cs", i, i + 1 + cnt, snap, (groups, {})))
              else: self._rec.append(("live", i, i + 1 + cnt, snap, op))
            try:
              if not self._exec_pkt7(op, words[i+1:i+1+cnt]):
                self.pending[0] = words[i:]
                self._rec = None
                return
            except Exception as e:
              self.errors.append(e)
              self.pending[0] = words[i+1+cnt:]
              self._rec = None
              return
        else:
          self.errors.append(RuntimeError(f"unknown packet header {hdr:#x}"))
          break
        i += 1 + cnt
      self.pending.pop(0)
      self.draining = max(0, self.draining - 1)
    if METAL: metal.runtime().sync()

  def _exec_pkt7(self, op:int, d:list[int]) -> bool: # False when the CP has to wait
    if METAL and op == mesa.CP_EVENT_WRITE and d[0] & 0xFF == mesa.CACHE_FLUSH_TS:
      metal.runtime().deferred.append((u64(d[1], d[2]), d[3]))
      return True
    if METAL and op in (mesa.CP_WAIT_REG_MEM, mesa.CP_REG_TO_MEM): metal.runtime().sync()
    if op in (mesa.CP_SET_MARKER, mesa.CP_WAIT_FOR_IDLE, mesa.CP_WAIT_MEM_WRITES): return True
    if op == mesa.CP_EVENT_WRITE:
      if d[0] & 0xFF == mesa.CACHE_FLUSH_TS: to_mv(u64(d[1], d[2]), 4).cast("I")[0] = d[3]
      elif d[0] & 0xFF != mesa.CACHE_INVALIDATE: raise RuntimeError(f"unsupported event {d[0]:#x}")
    elif op == mesa.CP_WAIT_REG_MEM:
      if (field(d[0], "CP_WAIT_REG_MEM_0_FUNCTION"), field(d[0], "CP_WAIT_REG_MEM_0_POLL")) != (mesa.WRITE_GE, mesa.POLL_MEMORY):
        raise RuntimeError(f"unsupported CP_WAIT_REG_MEM {d[0]:#x}")
      return to_mv(u64(d[1], d[2]), 4).cast("I")[0] & d[4] >= d[3]
    elif op == mesa.CP_REG_TO_MEM:
      if field(d[0], "CP_REG_TO_MEM_0_REG") != mesa.REG_A6XX_CP_ALWAYS_ON_COUNTER: raise RuntimeError(f"unsupported CP_REG_TO_MEM {d[0]:#x}")
      to_mv(u64(d[1], d[2]), 8).cast("Q")[0] = time.perf_counter_ns() * 192 // 10000 # 19.2MHz ticks
    elif op == mesa.CP_LOAD_STATE6_FRAG: self._load_state(d)
    elif op == mesa.CP_EXEC_CS: self._exec_cs(d[1:4])
    elif op == mesa.CP_RUN_OPENCL: self._exec_cs([self.regs[mesa.REG_A6XX_SP_CS_KERNEL_GROUP_X + k] for k in range(3)])
    else: raise RuntimeError(f"unsupported pkt7 opcode {op:#x}")
    return True

  def _load_state(self, d:list[int]):
    typ, src, block, num, off = [field(d[0], f"CP_LOAD_STATE6_0_{f}") for f in ("STATE_TYPE", "STATE_SRC", "STATE_BLOCK", "NUM_UNIT", "DST_OFF")]
    addr = u64(d[1], d[2])
    if src != mesa.SS6_INDIRECT: raise RuntimeError(f"unsupported load state {d[0]:#x}")
    if (typ, block) == (mesa.ST_CONSTANTS, mesa.SB6_CS_SHADER): self.consts[off*4:(off+num)*4] = np.frombuffer(to_mv(addr, num * 16), np.uint32)
    elif (typ, block) == (mesa.ST_SHADER, mesa.SB6_CS_SHADER):
      # NUM_UNIT is 10 bits (128 KB) and only preloads: the SP fetches the rest from memory, so a bigger shader (a 19k instruction kernel)
      # runs whole on hardware. take the program up to the end of its mapping
      def read():
        end = next((st + sz for st, sz in self.mappings.values() if st <= addr < st + sz), addr + num * 128)
        return bytes(to_mv(addr, max(num * 128, end - addr)))
      self.shader = self._cached(("shader", addr, num), read)
    elif (typ, block) in ((mesa.ST_CONSTANTS, mesa.SB6_CS_TEX), (mesa.ST6_UAV, mesa.SB6_CS_SHADER)): pass # read through the base registers
    elif (typ, block) == (mesa.ST_SHADER, mesa.SB6_CS_TEX):
      self.samplers = []
      for k in range(num):
        s = to_mv(addr + k * 16, 16).cast("I")
        wrap = [field(s[0], f"A6XX_TEX_SAMP_0_WRAP_{c}") for c in "STR"]
        self.samplers.append(wrap == [mesa.A6XX_TEX_CLAMP_TO_BORDER] * 3 and not s[0] & 0x1e and bool(s[1] & mesa.A6XX_TEX_SAMP_1_UNNORM_COORDS))
    else: raise RuntimeError(f"unsupported load state {d[0]:#x}")

  def _reg64(self, r:int) -> int: return u64(self.regs[r], self.regs[r + 1])

  def _images(self, addr:int, num:int, tex:bool) -> list[emu.Image]:
    return self._cached(("images", bytes(to_mv(addr, num * 64)), tex), lambda: self._decode_images(addr, num, tex))

  def _decode_images(self, addr:int, num:int, tex:bool) -> list[emu.Image]:
    ret = []
    for k in range(num):
      d = to_mv(addr + k * 64, 64).cast("I")
      fmt = field(d[0], "A6XX_TEX_CONST_0_FMT")
      if fmt not in (mesa.FMT6_32_32_32_32_FLOAT, mesa.FMT6_16_16_16_16_FLOAT): raise RuntimeError(f"unsupported image format {fmt}")
      swiz = [field(d[0], f"A6XX_TEX_CONST_0_SWIZ_{c}") for c in "XYZW"]
      if field(d[2], "A6XX_TEX_CONST_2_TYPE") != mesa.A6XX_TEX_2D or (tex and swiz != [mesa.A6XX_TEX_X, mesa.A6XX_TEX_Y,
                                                                                         mesa.A6XX_TEX_Z, mesa.A6XX_TEX_W]):
        raise RuntimeError(f"unsupported image descriptor {d[0]:#x} {d[2]:#x}")
      img = emu.Image(u64(d[4], d[5]), field(d[1], "A6XX_TEX_CONST_1_WIDTH"), field(d[1], "A6XX_TEX_CONST_1_HEIGHT"),
                      field(d[2], "A6XX_TEX_CONST_2_PITCH"), np.dtype(np.float32 if fmt == mesa.FMT6_32_32_32_32_FLOAT else np.float16))
      ext = img.pitch * img.height
      if not self._cached(("image", img.addr, ext), lambda: any(st <= img.addr and img.addr + ext <= st + sz for st, sz in self.mappings.values())):
        raise RuntimeError(f"unmapped image {img.addr:#x}")
      ret.append(img)
    return ret

  def _exec_cs(self, groups:list[int], memo:dict|None=None):
    if memo is None or "static" not in memo:
      nd, cfg, mode = self.regs[mesa.REG_A6XX_SP_CS_NDRANGE_0], self.regs[mesa.REG_A6XX_SP_CS_CONST_CONFIG_0], self.regs[mesa.REG_A6XX_SP_MODE_CNTL]
      demote = bool(mode & mesa.A6XX_SP_MODE_CNTL_CONSTANT_DEMOTION_ENABLE)
      if field(mode, "A6XX_SP_MODE_CNTL_ISAMMODE") != (mesa.ISAMMODE_GL if demote else mesa.ISAMMODE_CL):
        raise RuntimeError(f"unsupported SP_MODE_CNTL {mode:#x}")
      local = tuple(field(nd, f"A6XX_SP_CS_NDRANGE_0_LOCALSIZE{c}") + 1 for c in "XYZ")
      lmem_size = (field(self.regs[mesa.REG_A6XX_SP_CS_CNTL_0 + 1], "A6XX_SP_CS_CNTL_1_SHARED_SIZE") + 1) * 1024
      pvt_size = field(self.regs[mesa.REG_A6XX_SP_CS_PVT_MEM_PARAM], "A6XX_SP_CS_PVT_MEM_PARAM_MEMSIZEPERITEM") * 512 or (0 if demote else 512)
      ntex, nuav = (field(self.regs[mesa.REG_A6XX_SP_CS_CONFIG], f"A6XX_SP_CS_CONFIG_{f}") for f in ("NTEX", "NUAV"))
      static = (local, tuple(groups), field(cfg, "A6XX_SP_CS_CONST_CONFIG_0_LOCALIDREGID"), field(cfg, "A6XX_SP_CS_CONST_CONFIG_0_WGIDCONSTID"),
                lmem_size, pvt_size, demote, self.regs[mesa.REG_A6XX_SP_CS_PROGRAM_COUNTER_OFFSET],
                bool(self.regs[mesa.REG_A6XX_SP_CS_CNTL_0] & mesa.A6XX_SP_CS_CNTL_0_MERGEDREGS),
                ntex, self._reg64(mesa.REG_A6XX_SP_CS_TEXMEMOBJ_BASE) if ntex else 0, nuav, self._reg64(mesa.REG_A6XX_SP_CS_UAV_BASE) if nuav else 0)
      if memo is not None: memo["static"] = static
    else: static = memo["static"]
    local, grid, lid, wgid, lmem_size, pvt_size, demote, entry, merged, ntex, tex_base, nuav, uav_base = static
    textures = self._images(tex_base, ntex, tex=True) if ntex else []
    ibos = self._images(uav_base, nuav, tex=False) if nuav else []
    ranges = self._ranges_now()
    inputs = (self.shader, textures, ibos, ranges)
    if memo is not None and (last := memo.get("last")) is not None and all(x is y for x, y in zip(last[0], inputs)) and last[1] == self.samplers:
      d = last[2]
    else:
      d = emu.Dispatch(self.shader, self.consts, local, grid, lid, wgid, lmem_size, pvt_size, ranges, textures, ibos, demote, self.samplers, entry, merged)
      if memo is not None: memo["last"] = (inputs, list(self.samplers), d)
    (metal.run if METAL else emu.run)(d)
