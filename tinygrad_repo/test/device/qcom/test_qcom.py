import ctypes, platform, unittest
import numpy as np
from tinygrad import Device, Tensor, dtypes
from tinygrad.helpers import Context
from tinygrad.renderer.cstyle import ClangRenderer

class TestQCOM(unittest.TestCase):
  # image2d_t + read_imagef renders the same for half and float images, so both kernels compile to the same binary. the texture
  # descriptors (format = half/float) come from the signature, so the program cache must not hand one kernel the other's signature
  @unittest.skipUnless(Device.DEFAULT == "QCOM", "needs QCOM")
  def test_same_binary_different_image_dtypes(self):
    with Context(IMAGE=1):
      x = Tensor(np.random.default_rng(0).standard_normal(512).astype(np.float32)).realize()
      for dt in (dtypes.half, dtypes.float):
        b_np = np.random.default_rng(1).standard_normal(512).astype(np.float32)
        b = Tensor(b_np).cast(dt).contiguous().realize()
        np.testing.assert_allclose((x + b.float()).numpy(), x.numpy() + b.numpy().astype(np.float32), rtol=1e-3, atol=1e-3, err_msg=str(dt))

  # although part of the QCOM runtime, this tests flushing the CPU's dcache
  @unittest.skipUnless(isinstance(Device["CPU"].renderer, ClangRenderer) and platform.machine().lower() in {"arm64", "aarch64"},
                       "dcache_flush's inline asm needs ClangRenderer, and runs on arm64")
  def test_dcache_flush(self):
    from tinygrad.runtime.ops_qcom import dcache_flush
    buf = (ctypes.c_uint8 * 64)()
    dcache_flush().fxn(buf, 0)

if __name__ == '__main__':
  unittest.main()
