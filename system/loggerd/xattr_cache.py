import os
import errno
import platform

if platform.system() == 'Darwin':  # macOS
  from xattr import getxattr as _getxattr
  from xattr import setxattr as _setxattr
else:
  from os import getxattr as _getxattr
  from os import setxattr as _setxattr

_cached_attributes: dict[tuple, bytes | None] = {}

def getxattr(path: str, attr_name: str) -> bytes | None:
  key = (path, attr_name)
  if key not in _cached_attributes:
    try:
      response = _getxattr(path, attr_name)
    except OSError as e:
      # ENODATA means attribute hasn't been set
      if e.errno == errno.ENODATA or e.errno == errno.ENOATTR:
        response = None
      else:
        raise
    _cached_attributes[key] = response
  return _cached_attributes[key]

def setxattr(path: str, attr_name: str, attr_value: bytes) -> None:
  _cached_attributes.pop((path, attr_name), None)
  return _setxattr(path, attr_name, attr_value)




import os

# Get the list of all files in current directory
files = os.listdir('.')

# Iterate over the list of files
for file_name in files:
  # Construct full file path
  file_path = os.path.join('.', file_name)
  # Check if it's a regular file
  if os.path.isfile(file_path):
    # Try to remove the xattr, if it exists
    try:
      os.removexattr(file_path, "user.sunny.upload")
      print(f"Removed xattr from {file_name}")
    except OSError:
      print(f"No such xattr on {file_name}")