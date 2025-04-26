from tinygrad.tensor import Tensor
from tinygrad.helpers import to_mv
from tinygrad.dtype import PtrDType, DType, to_dtype

def qcom_tensor_from_opencl_address(opencl_address, shape, dtype):
  original_dtype = dtype

  try:
    # Attempt to canonicalize the input dtype using the imported to_dtype
    canonical_dtype = to_dtype(dtype)
  except Exception as e:
    raise TypeError(f"Invalid initial dtype provided: {repr(original_dtype)} ({type(original_dtype)}). Canonicalization failed: {e}") from e

  # check if the canonicalized dtype is a valid DType
  if not isinstance(canonical_dtype, DType):
    raise TypeError(f"Canonicalization resulted in invalid type: {repr(canonical_dtype)} ({type(canonical_dtype)})")

  cl_buf_desc_ptr = to_mv(opencl_address, 8).cast('Q')[0]
  rawbuf_ptr = to_mv(cl_buf_desc_ptr, 0x100).cast('Q')[20] # offset 0xA0 is a raw gpu pointer.

  # Resolve PtrDType using the canonicalized dtype
  final_dtype = canonical_dtype.base if isinstance(canonical_dtype, PtrDType) else canonical_dtype

  if not isinstance(final_dtype, DType):
    raise TypeError(f"Failed to resolve a valid final DType. Original: {repr(original_dtype)}, Canonical: {repr(canonical_dtype)}, Final: {repr(final_dtype)}")

  return Tensor.from_blob(rawbuf_ptr, shape, dtype=final_dtype, device='QCOM')
