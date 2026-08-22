import os
from openpilot.common.file_chunker import open_file_chunked, get_existing_chunks
from openpilot.common.params import Params


class ProgressReader:
  # wraps a chunked stream, writes byte-read % to a param (throttled to whole percent)
  def __init__(self, inner, total, param):
    self._inner, self._total, self._param = inner, total, param
    self._params = Params()
    self._read = 0
    self._pct = -1
    # sub-read size ~ 1% of total, so big weight buffers advance the % smoothly (not in jumps)
    self._step = max(64 * 1024, total // 100)

  def _bump(self, n):
    self._read += n
    if self._total:
      pct = min(100, self._read * 100 // self._total)
      if pct != self._pct:
        self._pct = pct
        self._params.put(self._param, pct)

  def read(self, size=-1):
    data = self._inner.read(size)
    self._bump(len(data))
    return data

  def readinto(self, b):
    # sub-chunk big buffers so the % advances smoothly instead of jumping per weight
    view = memoryview(b)
    done = 0
    while done < len(view):
      n = self._inner.readinto(view[done:done + self._step])
      if not n:
        break
      done += n
      self._bump(n)
    return done


def open_with_progress(pkl_path, param="UsbGpuLoadProgress"):
  # chunked reader that reports load progress to `param`
  total = sum(os.path.getsize(p) for p in get_existing_chunks(pkl_path))
  return ProgressReader(open_file_chunked(pkl_path), total, param)
