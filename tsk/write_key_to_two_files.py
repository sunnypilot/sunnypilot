import os
import re
from typing import Tuple, Optional

def write_key_to_files(key: str) -> Tuple[Optional[ValueError], Optional[OSError], Optional[IOError]]:
  """
  Writes a 32-character hexadecimal string to two files.

  Args:
    key: The 32-character hexadecimal string to write.

  Returns:
    A tuple of (ValueError, OSError, IOError) where:
      - If there's a ValueError (invalid input), the tuple will be (ValueError, None, None).
      - Otherwise, OSError and IOError will either be None (if no error) or the exception object.
  """

  # Input validation: Check if the string is 32 characters long and contains only valid hexadecimal characters
  if not re.fullmatch(r"^[0-9a-f]{32}$", key):
    return ValueError(f"Invalid key, must be 32 characters hexadecimal: {key}"), None, None

  params_error: Optional[OSError] = None
  persist_error: Optional[OSError] = None

  # Write to /data/params/d/SecOCKey
  try:
    os.makedirs("/data/params/d", exist_ok=True)
    with open("/data/params/d/SecOCKey", "w") as f:
      f.write(key)
  except OSError as e:
    params_error = e

  # Write to /persist/tsk/key
  try:
    os.makedirs("/persist/tsk", exist_ok=True)
    with open("/persist/tsk/key", "w") as f:
      f.write(key)
  except OSError as e:
    persist_error = e

  return None, params_error, persist_error
