
from tinygrad.sunnypilot.modeld_v2.tensor import Tensor
from tinygrad.sunnypilot.modeld_v2.helpers import to_mv
from tinygrad.sunnypilot.modeld_v2.dtype import PtrDType, DType, to_dtype


def qcom_tensor_from_opencl_address(opencl_address, shape, dtype):
  from tinygrad.sunnypilot.modeld_v2.dtype import PtrDType
  cl_buf_desc_ptr = to_mv(opencl_address, 8).cast('Q')[0]
  rawbuf_ptr = to_mv(cl_buf_desc_ptr, 0x100).cast('Q')[20]
  if isinstance(dtype, PtrDType):
    dtype = dtype.base
  return Tensor.from_blob(rawbuf_ptr, shape, dtype=dtype, device='QCOM')