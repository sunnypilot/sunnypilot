
from tinygrad.sunnypilot.modeld_v2.tensor import Tensor
from tinygrad.sunnypilot.modeld_v2.helpers import to_mv
from tinygrad.sunnypilot.modeld_v2.dtype import PtrDType, DType, to_dtype


def qcom_tensor_from_opencl_address(opencl_address, shape, dtype):
  cl_buf_desc_ptr = to_mv(opencl_address, 8).cast('Q')[0]
  rawbuf_ptr = to_mv(cl_buf_desc_ptr, 0x100).cast('Q')[20]
  canonical_dtype = to_dtype(dtype)

  if isinstance(canonical_dtype, PtrDType):
    final_dtype = canonical_dtype.base
  else:
    final_dtype = canonical_dtype

  if not isinstance(final_dtype, DType):
    raise TypeError(
      "Failed to determine a valid DType in qcom_tensor_from_opencl_address. " +
      f"Original: {dtype}, Canonical: {canonical_dtype}, Final: {final_dtype}"
    )

  return Tensor.from_blob(rawbuf_ptr, shape, dtype=final_dtype, device='QCOM')
