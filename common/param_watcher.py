import os
import platform
import struct
import select
import threading
import time
import ctypes
import ctypes.util
import traceback
from ctypes import c_void_p, c_size_t, POINTER, c_uint32, c_uint64

from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.system.hardware.hw import Paths


class ParamWatcher(Params):
  _instance = None
  _instance_lock = threading.Lock()

  def __new__(cls):
    if cls._instance is None:
      with cls._instance_lock:
        if cls._instance is None:
          cls._instance = super().__new__(cls)
          cls._instance._initialized = False
    return cls._instance

  def __init__(self):
    if self._initialized:
      return
    with self._instance_lock:
      if self._initialized:
        return
      super().__init__()
      self._cache = {}
      self._last_trigger = {}
      self._lock = threading.Lock()
      self._callbacks = []
      threading.Thread(target=self._run_watcher, daemon=True).start()
      self._initialized = True

  def add_watcher(self, callback):
    if callback not in self._callbacks:
      self._callbacks.append(callback)
      cloudlog.warning(f"ParamWatcher: Added watcher {callback}")  # remove me after testing

  def _trigger_callbacks(self, path, mask):
    now = time.monotonic()
    cloudlog.warning(f"Param raw: {path}")
    with self._lock:
      if now - self._last_trigger.get(path, 0) < 0.1:
        cloudlog.warning(f"Param debounced: {path}")  # remove me after testing
        return
      self._last_trigger[path] = now
      self._cache.pop(path, None)

    for callback in self._callbacks:
      try:
        callback(path, mask)
      except Exception:
        cloudlog.exception("Param watcher callback failed")

  def _get_cached(self, key, getter, sig):
    k = str(key)
    with self._lock:
      if k in self._cache and sig in self._cache[k]:
        return self._cache[k][sig]
    val = getter()
    with self._lock:
      self._cache.setdefault(k, {})[sig] = val
    return val

  def get(self, key, block=False, return_default=False):
    if block:
      return super().get(key, block, return_default)
    fetcher = super().get
    return self._get_cached(key, lambda: fetcher(key, block, return_default), (block, return_default))

  def get_bool(self, key, block=False):
    if block:
      return super().get_bool(key, block)
    fetcher = super().get_bool
    return self._get_cached(key, lambda: fetcher(key, block), ("bool", block))

  def _run_watcher(self):
    system = platform.system()
    try:
      if system == "Linux":
        self._run_linux()
      elif system == "Darwin":
        self._run_darwin()
    except Exception:
      traceback.print_exc()

  def _run_linux(self):
    # inotify constants: https://sites.uclouvain.be/SystInfo/usr/include/linux/inotify.h.html
    # more docs: https://linux.die.net/man/7/inotify
    # inotify init docs: https://www.man7.org/linux/man-pages/man2/inotify_init.2.html
    # docs for add watch: https://www.man7.org/linux/man-pages/man2/inotify_add_watch.2.html
    IN_MODIFY = 0x00000002
    IN_CREATE = 0x00000100
    IN_DELETE = 0x00000200
    IN_MOVED_TO = 0x00000080
    IN_CLOSE_WRITE = 0x00000008

    path = Paths.params_root()
    fd = os.inotify_init()
    os.inotify_add_watch(fd, path, IN_MODIFY | IN_CREATE | IN_DELETE | IN_MOVED_TO | IN_CLOSE_WRITE)
    poll = select.epoll()
    poll.register(fd, select.EPOLLIN)

    while True:
      for fileno, _ in poll.poll():
        if fileno == fd:
          buffer = os.read(fd, 1024)
          i = 0
          while i + 16 <= len(buffer):
            _, mask, _, name_len = struct.unpack_from("iIII", buffer, i)
            i += 16
            name = buffer[i:i+name_len].rstrip(b"\0").decode()
            i += name_len
            self._trigger_callbacks(name, mask)

  def _run_darwin(self):
    # FS documentation: https://developer.apple.com/documentation/coreservices/file_system_events
    # More FS documentation: https://wiki.python.org/moin/MacPython/ctypes/CoreFoundation
    CS = ctypes.cdll.LoadLibrary(ctypes.util.find_library("CoreServices"))
    CF = ctypes.cdll.LoadLibrary(ctypes.util.find_library("CoreFoundation"))

    kCFAllocatorDefault = c_void_p(0)
    kCFStringEncodingUTF8 = 0x08000100
    kFSEventStreamCreateFlagFileEvents = 0x00000010

    CF.CFStringCreateWithCString.restype = c_void_p
    CF.CFStringCreateWithCString.argtypes = [c_void_p, ctypes.c_char_p, c_uint32]
    CF.CFArrayCreate.restype = c_void_p
    CF.CFArrayCreate.argtypes = [c_void_p, POINTER(c_void_p), c_size_t, c_void_p]
    CS.FSEventStreamCreate.restype = c_void_p
    CS.FSEventStreamCreate.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p, c_uint64, ctypes.c_double, c_uint32]
    CS.FSEventStreamScheduleWithRunLoop.argtypes = [c_void_p, c_void_p, c_void_p]
    CS.FSEventStreamStart.argtypes = [c_void_p]
    CF.CFRunLoopGetCurrent.restype = c_void_p

    def _cb(stream, ctx, num, paths, flags, ids):
      try:
        paths_arr = ctypes.cast(paths, POINTER(c_void_p))
        flags_arr = ctypes.cast(flags, POINTER(c_uint32))
        for i in range(num):
          path = ctypes.cast(paths_arr[i], ctypes.c_char_p).value
          if path:
            self._trigger_callbacks(os.path.basename(path.decode('utf-8').rstrip('/')), flags_arr[i])
      except Exception:
        traceback.print_exc()

    self._darwin_cb = ctypes.CFUNCTYPE(None, c_void_p, c_void_p, c_size_t, c_void_p, POINTER(c_uint32), POINTER(c_uint64))(_cb)

    path_str = Paths.params_root().encode('utf-8')
    cf_path = CF.CFStringCreateWithCString(kCFAllocatorDefault, path_str, kCFStringEncodingUTF8)
    cf_paths = CF.CFArrayCreate(kCFAllocatorDefault, (c_void_p * 1)(cf_path), 1, None)
    stream = CS.FSEventStreamCreate(kCFAllocatorDefault, self._darwin_cb, None, cf_paths, -1, 0.05, kFSEventStreamCreateFlagFileEvents)

    run_loop = CF.CFRunLoopGetCurrent()
    kDefaultMode = CF.CFStringCreateWithCString(kCFAllocatorDefault, b"kCFRunLoopDefaultMode", kCFStringEncodingUTF8)
    CS.FSEventStreamScheduleWithRunLoop(stream, run_loop, kDefaultMode)
    CS.FSEventStreamStart(stream)
    CF.CFRunLoopRun()
