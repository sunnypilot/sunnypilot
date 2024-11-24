import hashlib
import os


async def calculate_hash(file_path: str) -> tuple[bytes, str]:
  """Calculate SHA256 hash of a file"""
  sha256_hash = hashlib.sha256()
  file_data = b""
  if os.path.exists(file_path):
    with open(file_path, "rb") as file:
      file_data = file.read()
      sha256_hash.update(file_data)
  return file_data, sha256_hash.hexdigest()


async def verify_file_hash(file_path: str, expected_hash: str) -> tuple[bytes, bool]:
  """Verifies the file's hash against the expected hash."""
  if not expected_hash:
    return b"", True
  file_data, current_hash = await calculate_hash(file_path)
  return file_data if current_hash.lower() == expected_hash.lower() else b"", current_hash.lower() == expected_hash.lower()
