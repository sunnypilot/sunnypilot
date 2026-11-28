import ctypes, os, sys, unittest
import numpy as np
from tinygrad.runtime.autogen import mesa
from test.mockgpu.qcom import emu

NT = 2048
END = (mesa.OPC_END << 55).to_bytes(8, "little")

def special32(rng, n:int) -> np.ndarray:
  v = rng.integers(0, 2**32, n, dtype=np.uint32)
  kind = rng.integers(0, 10, n)
  tiny = np.float32(2.0**-126)
  pool = np.array([0, 0x80000000, 0x7f800000, 0xff800000, 0x7fc00000, 0x7f800001, 0xffc12345, 0x00800000, 0x80800000, 0x3f800000, 0xbf800000,
                   0x3f000000, 0x4b000000, 0x4effffff, 0xcf000000, 1, 0xffffffff, 0x7fffffff, 0x8000, 0x7bff, 0xfc00, 0x7e00], np.uint32)
  near = (np.sqrt(tiny) * (1 + rng.standard_normal(n).astype(np.float32) * np.float32(2**-12))).astype(np.float32).view(np.uint32)
  v = np.where(kind == 0, v & 0x807fffff, v)                                # f32 denormals
  v = np.where(kind == 1, rng.choice(pool, n), v)
  v = np.where(kind == 2, near | (v & 0x80000000), v)                       # factors whose product lands near 2^-126
  v = np.where(kind == 3, (v & 0x81ffffff) | 0x3f000000, v)                 # around 1
  v = np.where(kind == 4, v & 0x3ff, v)                                     # small integers
  v = np.where(kind == 5, (v & 0xffff) | (rng.choice(pool, n) << 16), v)    # f16 pairs
  v = np.where(kind == 6, (v & 0x83ff83ff), v)                              # f16 denormal pairs
  return v.astype(np.uint32)

def random_words(rng, n:int) -> list[int]:
  out, seen = [], set()
  cats = [1, 2, 2, 2, 3, 3, 4]
  while len(out) < n:
    w = int(rng.integers(0, 2**61, dtype=np.uint64)) | (int(rng.choice(cats)) << 61)
    if w >> 61 == 4: w &= ~(0x3f << 53) | (int(rng.choice([0, 1, 2, 3, 4, 5, 6, 9, 10, 11])) << 53)  # the sfu opcodes
    w &= ~(0x3 << 40) | (int(rng.integers(0, 4) if rng.random() < 0.2 else 0) << 40)                   # mostly no repeat
    try: i = emu.decode_inst(0, w)
    except (NotImplementedError, KeyError, IndexError): continue
    if w in seen or isinstance(i, emu.Cat0): continue
    seen.add(w)
    out.append(w)
  return out

class TestQCOMMetal(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    if sys.platform != "darwin": raise unittest.SkipTest("Metal only")
    from test.mockgpu.qcom import metal
    cls.metal, cls.rt = metal, metal.MetalQCOM(1 << 24)

  def check(self, words:list[int], merged:bool, demote:bool, seed:int, init=None):
    rt, metal, m = self.rt, self.metal, self.metal._objc()[1]
    rng = np.random.default_rng(seed)
    consts = special32(rng, 4096)
    bad, ran = [], 0
    for w in words:
      image = w.to_bytes(8, "little") + END
      d = emu.Dispatch(image, consts, (NT, 1, 1), (1, 1, 1), 0xfc, 0xfc, 1024, 512, [], [], [], demote, [], 0, merged)
      t = emu.Threads(d, NT)
      t.r[:] = special32(rng, emu.NREGS * NT).reshape(emu.NREGS, NT)
      t.r[emu.A0] = rng.integers(0, 64, NT)
      if not merged: t.h[:] = (special32(rng, emu.NREGS * NT) & 0xffff).reshape(emu.NREGS, NT)
      if init is not None: init(t.r, rng)
      r0, h0 = t.r.copy(), (t.h.copy() if not merged else None)
      i = emu.decode(image)[0]
      try:
        with np.errstate(all="ignore"):
          for k in range(i.iterations): emu.EXEC[type(i)](t, i, k)
      except (RuntimeError, NotImplementedError, IndexError): continue
      try: g = metal.Gen((image, 0, merged, demote, 0xfc, 0xfc, 1024, 512, (), (), True))
      except metal.Unsupported as e:
        bad.append(f"{w:#018x} {mesa.opc_t.get(i.op)}: not translated ({e})")
        continue
      src = g.source()
      lib = rt.compiler.compile(src)
      library = rt.checked(rt.dev.newLibraryWithData_error, rt.objc.dispatch_data_create(lib, len(lib), None, None))
      pso = rt.checked(rt.dev.newComputePipelineStateWithFunction_error, library.newFunctionWithName(rt.to_ns_str("k")))
      bufs = {}
      for idx, arr in ((1, consts), (2, np.zeros(64, np.uint32)), (3, np.zeros(8, np.uint64)), (30, r0), (29, h0.astype(np.uint32) if h0 is not None
                                                                                                         else np.zeros(1, np.uint32)),
                       (28, np.array(g.imms or [0], np.uint32))):
        b = rt.dev.newBufferWithLength_options(max(arr.nbytes, 16), 0)
        ctypes.memmove(b.contents(), np.ascontiguousarray(arr).ctypes.data, arr.nbytes)
        bufs[idx] = b
      cb = rt.queue.commandBuffer()
      enc = cb.computeCommandEncoder()
      enc.setComputePipelineState(pso)
      enc.setBuffer_offset_atIndex(rt.arena, 0, 0)
      for idx, b in bufs.items(): enc.setBuffer_offset_atIndex(b, 0, idx)
      for n in g.tables: enc.setBuffer_offset_atIndex(rt.table(n), 0, 4 + metal.TABLES.index(n))
      enc.dispatchThreadgroups_threadsPerThreadgroup(m.MTLSize(NT // 256, 1, 1), m.MTLSize(256, 1, 1))
      enc.endEncoding()
      cb.commit()
      cb.waitUntilCompleted()
      gr = np.zeros_like(r0)
      ctypes.memmove(gr.ctypes.data, bufs[30].contents(), gr.nbytes)
      ran += 1
      if not np.array_equal(gr, t.r):
        reg, lane = [int(x[0]) for x in np.nonzero(gr != t.r)]
        bad.append(f"{w:#018x} {mesa.opc_t.get(i.op)}: r{reg} lane {lane} metal {gr[reg, lane]:#x} emu {t.r[reg, lane]:#x} (was {r0[reg, lane]:#x})")
      elif h0 is not None:
        gh = np.zeros(h0.shape, np.uint32)
        ctypes.memmove(gh.ctypes.data, bufs[29].contents(), gh.nbytes)
        if not np.array_equal(gh.astype(np.uint16), t.h):
          reg, lane = [int(x[0]) for x in np.nonzero(gh.astype(np.uint16) != t.h)]
          bad.append(f"{w:#018x} {mesa.opc_t.get(i.op)}: hr{reg} lane {lane} metal {gh[reg, lane]:#x} emu {t.h[reg, lane]:#x}")
    return bad, ran

  def test_random_encodings(self):
    n = int(os.getenv("QCOM_METAL_FUZZ", "400"))
    for k, (merged, demote) in enumerate([(False, False), (True, False), (False, True), (True, True)]):
      seed = k + 4 * int(os.getenv("QCOM_METAL_SEED", "0"))
      bad, ran = self.check(random_words(np.random.default_rng(seed), n), merged, demote, seed)
      print(f"merged={merged} demote={demote}: {ran} encodings run, {len(bad)} differ", *bad[:20], sep="\n  ")
      self.assertEqual(bad, [])

  def run_fn(self, fn:str, x:np.ndarray) -> np.ndarray:  # a prelude function over a u32 array
    rt, m = self.rt, self.metal._objc()[1]
    src = self.metal.PRELUDE + f"kernel void k(device const uint* A [[buffer(0)]], device uint* O [[buffer(1)]], uint i [[thread_position_in_grid]]) {{ O[i] = {fn}(A[i]); }}"
    lib = rt.compiler.compile(src)
    library = rt.checked(rt.dev.newLibraryWithData_error, rt.objc.dispatch_data_create(lib, len(lib), None, None))
    pso = rt.checked(rt.dev.newComputePipelineStateWithFunction_error, library.newFunctionWithName(rt.to_ns_str("k")))
    a, o = rt.dev.newBufferWithLength_options(x.nbytes, 0), rt.dev.newBufferWithLength_options(x.nbytes, 0)
    ctypes.memmove(a.contents(), x.ctypes.data, x.nbytes)
    cb = rt.queue.commandBuffer()
    enc = cb.computeCommandEncoder()
    enc.setComputePipelineState(pso)
    enc.setBuffer_offset_atIndex(a, 0, 0)
    enc.setBuffer_offset_atIndex(o, 0, 1)
    enc.dispatchThreadgroups_threadsPerThreadgroup(m.MTLSize(len(x) // 256, 1, 1), m.MTLSize(256, 1, 1))
    enc.endEncoding()
    cb.commit()
    cb.waitUntilCompleted()
    out = np.zeros_like(x)
    ctypes.memmove(out.ctypes.data, o.contents(), x.nbytes)
    return out

  def test_conversions(self):  # numpy's f16 conversions, which the emulator's astype uses
    h = np.arange(1 << 16, dtype=np.uint32)
    with np.errstate(all="ignore"): want = h.astype(np.uint16).view(np.float16).astype(np.float32).view(np.uint32)
    np.testing.assert_array_equal(self.run_fn("h2f", h), want)
    rng = np.random.default_rng(0)
    f = np.concatenate([special32(rng, 1 << 22), rng.integers(0, 2**32, 1 << 22, dtype=np.uint32), (rng.integers(0, 2**23, 1 << 20, dtype=np.uint32) |
                        0x7f800000 | (rng.integers(0, 2, 1 << 20, dtype=np.uint32) << 31))]).astype(np.uint32)
    with np.errstate(all="ignore"): want = f.view(np.float32).astype(np.float16).view(np.uint16).astype(np.uint32)
    np.testing.assert_array_equal(self.run_fn("f2h", f), want)

  def test_mul_boundary(self):  # r0 * r1 exactly around 2^-126 - 2^-150, the midpoint below 2^-126 that the gpu flushes past
    def init(r, rng):
      a = (1 + rng.random(NT)).astype(np.float32) * np.where(rng.random(NT) < 0.5, 1, 2**-1).astype(np.float32)
      target = 2.0**-126 * (1 - 2.0**-24 * rng.integers(-3, 4, NT))
      b = (target / a.astype(np.float64)).astype(np.float32).view(np.uint32).astype(np.int64) + rng.integers(-2, 3, NT)
      sign = rng.integers(0, 2, (2, NT)).astype(np.uint32) << 31
      r[0], r[1] = a.view(np.uint32) | sign[0], b.astype(np.uint32) | sign[1]
    mul = (2 << 61) | (mesa.OPC_MUL_F & 0x3f) << 53 | 1 << 52 | 2 << 32 | 1 << 16 | 0
    mad = (3 << 61) | (mesa.OPC_MAD_F32 & 0x7) << 55 | 1 << 47 | 2 << 32 | 3 << 16 | 0
    bad, ran = self.check([mul, mad], False, False, 99, init)
    self.assertEqual(bad, [])
    self.assertEqual(ran, 2)
    rng = np.random.default_rng(99)
    r = np.zeros((2, NT), np.uint32)
    init(r, rng)
    with np.errstate(all="ignore"): prod = emu.ftz(emu.ftz(r[0].view(np.float32)) * emu.ftz(r[1].view(np.float32))).view(np.uint32)
    self.assertGreater(int(((prod & 0x7fffffff) == 0x00800000).sum()), 50)

if __name__ == "__main__":
  unittest.main()
