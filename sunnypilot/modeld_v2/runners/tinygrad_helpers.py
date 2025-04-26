from tinygrad.sunnypilot.modeld_v2.tensor import Tensor
from tinygrad.sunnypilot.modeld_v2.helpers import to_mv
from tinygrad.sunnypilot.modeld_v2.dtype import PtrDType, DType, to_dtype

def qcom_tensor_from_opencl_address(opencl_address, shape, dtype):
  original_dtype = dtype

  try:
    # Attempt to canonicalize the input dtype using the imported to_dtype
    # This should handle strings or pass through DType objects (using its own definition)
    canonical_dtype = to_dtype(dtype)
  except Exception as e:
    # If canonicalization itself fails (e.g., invalid string), raise the error
    raise TypeError(f"Invalid initial dtype provided: {repr(original_dtype)} ({type(original_dtype)}). Canonicalization failed: {e}") from e

  # check if the canonicalized dtype is a valid DType according to *this* module's definition
  if not isinstance(canonical_dtype, DType):
    # This path should ideally not be reached if to_dtype worked correctly
    raise TypeError(f"Canonicalization resulted in invalid type: {repr(canonical_dtype)} ({type(canonical_dtype)})")

  cl_buf_desc_ptr = to_mv(opencl_address, 8).cast('Q')[0]
  rawbuf_ptr = to_mv(cl_buf_desc_ptr, 0x100).cast('Q')[20] # offset 0xA0 is a raw gpu pointer.

  # 3. Resolve PtrDType using the canonicalized dtype
  final_dtype = canonical_dtype.base if isinstance(canonical_dtype, PtrDType) else canonical_dtype

  if not isinstance(final_dtype, DType):
    # This should also not be reached if logic is sound
    raise TypeError(f"Failed to resolve a valid final DType. Original: {repr(original_dtype)}, Canonical: {repr(canonical_dtype)}, Final: {repr(final_dtype)}")

  return Tensor.from_blob(rawbuf_ptr, shape, dtype=final_dtype, device='QCOM')
