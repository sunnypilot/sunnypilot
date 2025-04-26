
from tinygrad.sunnypilot.modeld_v2.tensor import Tensor
from tinygrad.sunnypilot.modeld_v2.helpers import to_mv
from tinygrad.sunnypilot.modeld_v2.dtype import PtrDType, DType

def qcom_tensor_from_opencl_address(opencl_address, shape, dtype):
  # Ensure the input dtype from the runner is actually a DType object
  if not isinstance(dtype, DType):
      # If it's not (e.g., a string from older pickles?), try converting it.
      # This path shouldn't be hit based on current runner code, but acts as a safeguard.
      from tinygrad.sunnypilot.modeld_v2.dtype import to_dtype
      try:
        dtype = to_dtype(dtype)
      except Exception as e:
        raise TypeError(f"Invalid dtype provided to qcom_tensor_from_opencl_address: {dtype} ({type(dtype)}). Conversion failed: {e}") from e

  cl_buf_desc_ptr = to_mv(opencl_address, 8).cast('Q')[0]
  rawbuf_ptr = to_mv(cl_buf_desc_ptr, 0x100).cast('Q')[20] # offset 0xA0 is a raw gpu pointer.

  # Resolve PtrDType to its base type if necessary, as Buffer needs the base type.
  final_dtype = dtype.base if isinstance(dtype, PtrDType) else dtype

  # Ensure the final resolved dtype is valid before passing to Tensor.from_blob
  if not isinstance(final_dtype, DType):
      raise TypeError(f"Failed to resolve a valid DType in qcom_tensor_from_opencl_address. Original: {dtype}, Final: {final_dtype}")

  # Pass the resolved base dtype to Tensor.from_blob
  return Tensor.from_blob(rawbuf_ptr, shape, dtype=final_dtype, device='QCOM')