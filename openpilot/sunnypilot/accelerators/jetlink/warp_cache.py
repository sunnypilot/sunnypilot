"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

The comma-side warp JIT: what builds it, and what loads it.

The warp stays on the comma (see model_state), and upstream's fused run_model
JIT (#38684) has no warp to borrow, so compile_modeld.make_warp is JIT-compiled
as a scons target; see accelerators/SConscript. Not in modeld, where the ~9 s
compile would hold back the first frame on every ignition, and not in jetlinkd,
which only runs offroad and can lose the compile to ignition.

jetlinkd still builds one that is missing outright (`ensure`), for a prebuilt
image made without the target. load_warp is what stands between a bad pickle
and the car.
"""
from __future__ import annotations

import pickle
from pathlib import Path

from openpilot.common.swaglog import cloudlog

# in the source tree, next to upstream's dm_warp_*.pkl and under the *.pkl
# ignore. Not Paths.comma_home(): on AGNOS that is a tmpfs overlay, the pickle
# was gone every boot and jetlinkd lost the ~9 s compile race to ignition
CACHE_DIR = Path(__file__).resolve().with_name('models')


# what TinyJit records for the keyword call in call_warp: sorted(kwargs)
WARP_INPUT_NAMES = ['big_frame', 'big_tfm', 'frame', 'tfm']


def call_warp(warp, tfm, big_tfm, frame, big_frame):
  """Call a warp JIT. Every caller goes through here, capture included.

  TinyJit names inputs from enumerate(args) plus sorted(kwargs) and refuses a
  call whose names differ from the capture. A positional compile and a keyword
  call raised JitError on the first frame of a drive.
  """
  return warp(tfm=tfm, big_tfm=big_tfm, frame=frame, big_frame=big_frame)


def init_device() -> None:
  """Bring the GPU up now, on the caller's thread.

  tinygrad initialises the device on its first kernel run and spawns a libusb
  event thread doing it. A thread created after config_realtime_process(7, 54)
  inherits SCHED_FIFO 54 and the core-7 pin and preempts the frame loop; that
  cost 5% of frames once. Failure is not a reason to refuse the accelerator.
  """
  try:
    from tinygrad.tensor import Tensor
    Tensor([0.0]).realize()
  except Exception:
    cloudlog.exception("jetlink: could not bring the gpu up before modeld goes realtime")
  # the same trap for tinygrad's compile pool (engine/worker.py): created on
  # the first compile, after modeld goes realtime, its handler threads sat at
  # SCHED_FIFO 54 on core 7. An older tinygrad or PARALLEL=0 is not a failure
  try:
    from tinygrad.engine.worker import get_worker_pool
    get_worker_pool()
  except Exception:
    cloudlog.exception("jetlink: could not start tinygrad's compile pool before modeld goes realtime")


def device_geometry() -> tuple[int, int, int, int]:
  """(cam_w, cam_h, model_w, model_h) for this device.

  The same choice modeld/SConscript makes, so the warp built is the one modeld
  asks for. If they disagree, load_warp raises and the drive is small-model.
  """
  from openpilot.common.hardware import HARDWARE
  from openpilot.common.transformations.camera import _ar_ox_fisheye, _os_fisheye
  from openpilot.common.transformations.model import MEDMODEL_INPUT_SIZE

  camera = _os_fisheye if HARDWARE.get_device_type() == "mici" else _ar_ox_fisheye
  return camera.width, camera.height, *MEDMODEL_INPUT_SIZE


def ensure(cam_w: int, cam_h: int, model_w: int, model_h: int) -> bool:
  """Build the warp if there is none at all. Offroad only. Never raises.

  The build normally makes it, so this only runs on a prebuilt image made
  without the target. False means the small model, not a dead daemon.
  """
  if is_cached(cam_w, cam_h, model_w, model_h):
    return True
  try:
    pkl = compile_warp(cam_w, cam_h, model_w, model_h)
  except Exception:
    cloudlog.exception("jetlink: could not compile the warp")
    return False
  prune(keep={pkl})
  return True


def warp_path(cam_w: int, cam_h: int, model_w: int, model_h: int) -> Path:
  return CACHE_DIR / f'warp_{cam_w}x{cam_h}_{model_w}x{model_h}_tinygrad.pkl'


def is_cached(cam_w: int, cam_h: int, model_w: int, model_h: int) -> bool:
  """Is there a warp for this geometry?

  Presence only. Staleness is scons' job: the target depends on tinygrad and
  the capture sources. A pickle from an incompatible tinygrad raises in load_warp.
  """
  return warp_path(cam_w, cam_h, model_w, model_h).is_file()


def compile_warp(cam_w: int, cam_h: int, model_w: int, model_h: int, out: Path | None = None) -> Path:
  """Build the warp JIT and pickle it. Offroad only: this holds the GPU.

  `out` is for scons; jetlinkd's fallback defaults to warp_path. Three runs
  before pickling: TinyJit captures on the second call, and a pickle taken
  earlier is an empty jit that silently does nothing.
  """
  import numpy as np
  from tinygrad.device import Device
  from tinygrad.engine.jit import TinyJit
  from tinygrad.tensor import Tensor

  from openpilot.selfdrive.modeld.compile_modeld import NV12Frame, make_warp
  from openpilot.system.camerad.cameras.nv12_info import get_nv12_info

  nv12 = NV12Frame(cam_w, cam_h, *get_nv12_info(cam_w, cam_h))
  warp_jit = TinyJit(make_warp(nv12, model_w, model_h), prune=True)

  # one set of input tensors: TinyJit captures against the buffers it is
  # first handed. Random so nothing constant-folds
  rng = np.random.default_rng(42)
  tfm_npy, big_tfm_npy = np.eye(3, dtype=np.float32), np.eye(3, dtype=np.float32)
  tfm = Tensor(tfm_npy, device='NPY')
  big_tfm = Tensor(big_tfm_npy, device='NPY')
  frame = Tensor.randint(nv12.size, low=0, high=256, dtype='uint8', device=Device.DEFAULT).realize()
  big_frame = Tensor.randint(nv12.size, low=0, high=256, dtype='uint8', device=Device.DEFAULT).realize()
  for _ in range(3):
    tfm_npy[:] = rng.standard_normal((3, 3)).astype(np.float32)
    big_tfm_npy[:] = rng.standard_normal((3, 3)).astype(np.float32)
    call_warp(warp_jit, tfm, big_tfm, frame, big_frame).realize()
  Device.default.synchronize()

  pkl = warp_path(cam_w, cam_h, model_w, model_h) if out is None else Path(out)
  pkl.parent.mkdir(parents=True, exist_ok=True)
  # through a temporary: modeld may read this while jetlinkd writes it
  tmp = pkl.with_suffix('.pkl.tmp')
  with open(tmp, 'wb') as f:
    pickle.dump(warp_jit, f)
  tmp.replace(pkl)
  cloudlog.warning("jetlink: compiled the warp for %dx%d -> %dx%d", cam_w, cam_h, model_w, model_h)
  return pkl


def load_warp(cam_w: int, cam_h: int, model_w: int, model_h: int):
  """The cached warp JIT. Raises if it is not there or is stale.

  modeld's big-model load is wrapped in the one-way fallback to the small
  model, and a warp that cannot be trusted must not reach the car.
  """
  if not is_cached(cam_w, cam_h, model_w, model_h):
    raise RuntimeError(f"no warp built for {cam_w}x{cam_h} -> {model_w}x{model_h}; "
                       + "the build makes it, jetlinkd rebuilds one that is missing")
  with open(warp_path(cam_w, cam_h, model_w, model_h), 'rb') as f:
    warp = pickle.load(f)

  # a JIT pickled before TinyJit captured loads fine and computes nothing; one
  # captured with a different call convention raises JitError on the first
  # frame of a drive. Both have happened
  captured = getattr(warp, 'captured', None)
  if captured is None:
    raise RuntimeError("cached warp was pickled before it captured; it computes nothing")
  names = list(getattr(captured, 'expected_names', []))
  if names != WARP_INPUT_NAMES:
    raise RuntimeError(f"cached warp expects {names}, call_warp passes {WARP_INPUT_NAMES}")
  return warp


def warm(warp, cam_w: int, cam_h: int) -> None:
  """Run a loaded warp JIT until it is cheap to call.

  Measured: load_warp 0.3 s, the first call 1.9 s, the second 5 ms. Paid on
  modeld's frame loop that was ~26 dropped frames and 16 s of modeldLagging
  after every join.
  """
  import numpy as np
  from tinygrad.device import Device
  from tinygrad.tensor import Tensor

  from openpilot.system.camerad.cameras.nv12_info import get_nv12_info

  size = get_nv12_info(cam_w, cam_h)[3]
  frames = [np.zeros(size, dtype=np.uint8) for _ in range(2)]
  blobs = [Tensor.from_blob(f.ctypes.data, (size,), dtype='uint8', device=Device.DEFAULT) for f in frames]
  eye = [np.eye(3, dtype=np.float32) for _ in range(2)]
  tfm, big_tfm = (Tensor(e, device='NPY').realize() for e in eye)
  for _ in range(2):
    call_warp(warp, tfm, big_tfm, blobs[0], blobs[1]).realize()
  Device.default.synchronize()


def prune(keep: set[Path]) -> None:
  """Drop warps for a geometry this device does not have.

  jetlinkd's fallback only; removing a file scons built just makes it build again.
  """
  for p in CACHE_DIR.glob('warp_*_tinygrad.pkl'):
    if p not in keep:
      p.unlink(missing_ok=True)
