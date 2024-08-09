import errno
import platform

_DARWIN = platform.system() == 'Darwin'

if _DARWIN:  # macOS
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
      if e.errno == errno.ENODATA or (_DARWIN and e.errno == errno.ENOATTR):
        response = None
      else:
        raise
    _cached_attributes[key] = response
  return _cached_attributes[key]

def setxattr(path: str, attr_name: str, attr_value: bytes) -> None:
  _cached_attributes.pop((path, attr_name), None)
  return _setxattr(path, attr_name, attr_value)
