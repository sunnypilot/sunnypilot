
from tinygrad.sunnypilot.modeld_v3.tensor import Tensor
from tinygrad.sunnypilot.modeld_v3.helpers import to_mv

def qcom_tensor_from_opencl_address(opencl_address, shape, dtype):
  cl_buf_desc_ptr = to_mv(opencl_address, 8).cast('Q')[0]
  rawbuf_ptr = to_mv(cl_buf_desc_ptr, 0x100).cast('Q')[20] # offset 0xA0 is a raw gpu pointer.
  return Tensor.from_blob(rawbuf_ptr, shape, dtype=dtype, device='QCOM')
