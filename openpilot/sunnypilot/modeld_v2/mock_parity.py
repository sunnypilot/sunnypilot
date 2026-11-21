import json
import os
import shutil
import struct
import sys
import tempfile
import time

os.environ.setdefault("DEV", "MOCKUSB+AMD")
QCOM = "QCOM" in os.environ["DEV"]
ON_MOCK = os.environ["DEV"].startswith("MOCK")
ARCH, HARDWARE = ("a630", "comma 3x/4 (a630)") if QCOM else ("gfx1200", "chestnut")
os.environ.setdefault("CHECK_OOB", "0")
os.environ.setdefault("GMMU", "0")
if sys.platform == "darwin" and os.environ["DEV"].startswith("MOCKUSB"):  # the mock's VRAM is a memfd, which macOS lacks: an unlinked file is the same
  from tinygrad.runtime.autogen import libc

  def _memfd_create(name, flags):
    fd, path = tempfile.mkstemp()
    os.unlink(path)
    return fd
  libc.memfd_create = _memfd_create

import numpy as np

from openpilot.sunnypilot.modeld_v2.helpers import ALIGNMENT, MAGIC, PlainJit, _device, read_parts


class ParityError(RuntimeError):
  pass


def _emulator():
  try:
    if QCOM:
      from test.mockgpu.qcom import emu
    else:
      from test.mockgpu.amd import emu
  except ImportError as e:
    raise ParityError(f"tinygrad's {'qcom' if QCOM else 'amd'} mock is not importable: put tinygrad_repo on PYTHONPATH") from e
  if not hasattr(emu, "hw_unverified"):
    raise ParityError(f"this tinygrad's emulator has no {ARCH} rounding model, its check frames would not match a {HARDWARE}")
  return emu


def unverified(header: dict, blob: memoryview) -> dict[str, int]:
  emu, out = _emulator(), {}
  for call in header["calls"]:
    if call["kind"] != "program":
      continue
    if (arch := call["target"].get("arch", "")).split(",")[0] != ARCH:  # IMAGE builds append ",IMAGE_PITCH_ALIGNMENT=64"
      out[f"arch={arch}"] = out.get(f"arch={arch}", 0) + 1
      continue
    for sig, n in emu.hw_unverified(bytes(blob[slice(*call["lib"])])).items():
      out[sig] = out.get(sig, 0) + n
  return out


def _array(blob: memoryview, stored: dict) -> np.ndarray:
  return np.frombuffer(blob[slice(*stored["data"])], dtype=np.dtype(stored["dtype"])).reshape(stored["shape"]).copy()


def replay(header: dict, blob: memoryview, shared: dict) -> list[np.ndarray]:
  from tinygrad import Tensor
  check = header["check"]
  jit = PlainJit(header, blob, None, verify=False, shared=shared)
  kwargs: dict = {}
  for path, stored, device in check["inputs"]:
    tensor = Tensor(_array(blob, stored), device=_device(device, None)).realize()
    kwargs[path[0]] = tensor if len(path) == 1 else {**kwargs.get(path[0], {}), path[1]: tensor}
  result = jit(**kwargs)
  outputs = kwargs[check["output_container"]].values() if check["output_container"] else result
  return [t.numpy() for t in (outputs if isinstance(outputs, (list, tuple)) or check["output_container"] else [outputs])]


def _parts_with_offsets(path: str) -> tuple[dict, dict]:
  parts, _ = read_parts(path)
  with open(path, "rb") as f:
    head = f.read(len(MAGIC) + 8)
    start = len(MAGIC) + 8 + struct.unpack_from("<Q", head, len(MAGIC))[0]
    f.seek(len(MAGIC) + 8)
    entries = json.loads(f.read(start - len(MAGIC) - 8))["parts"]
  base = start + -start % ALIGNMENT
  offsets = {tuple(e["key"]) if isinstance(e["key"], list) else e["key"]: base + e["blob"][0] for e in entries}
  return parts, offsets


def _gate(parts: dict) -> None:
  missing: dict[str, int] = {}
  for header, blob in parts.values():
    if "check" not in header:
      raise ParityError("artifact has no check frame")
    for sig, n in unverified(header, blob).items():
      missing[sig] = missing.get(sig, 0) + n
  if missing:
    raise ParityError(f"kernels use instructions the emulator is not verified against a {HARDWARE} for: " +
                      ", ".join(f"{s} ({n}x)" for s, n in sorted(missing.items(), key=lambda kv: -kv[1])))


def check(path: str) -> None:
  parts, _ = read_parts(path)
  if ON_MOCK:
    _gate(parts)
  shared: dict = {}
  for key, (header, blob) in parts.items():
    got = replay(header, blob, shared)
    for i, (g, stored) in enumerate(zip(got, header["check"]["outputs"], strict=True)):
      want = _array(blob, stored)
      if g.shape != want.shape or not np.array_equal(g.view(np.uint8), want.view(np.uint8)):
        n = int(np.count_nonzero(g != want)) if g.shape == want.shape else -1
        where = "mock" if ON_MOCK else "device"
        raise ParityError(f"part {key} output {i}: the {where}'s check frame differs from the stored one in {n} of {want.size} values")


def record(path: str, out: str) -> None:
  parts, offsets = _parts_with_offsets(path)
  _gate(parts)
  shared, writes = {}, []
  for key, (header, blob) in parts.items():
    for g, stored in zip(replay(header, blob, shared), header["check"]["outputs"], strict=True):
      want = np.dtype(stored["dtype"])
      if tuple(g.shape) != tuple(stored["shape"]) or g.dtype != want:
        raise ParityError(f"part {key}: replayed output {g.dtype}{g.shape} does not fit the stored {want}{tuple(stored['shape'])}")
      writes.append((offsets[key] + stored["data"][0], np.ascontiguousarray(g).tobytes()))
  shutil.copyfile(path, out)
  with open(out, "r+b") as f:
    for offset, data in writes:
      f.seek(offset)
      f.write(data)


def main(argv: list[str]) -> int:
  if len(argv) < 2 or argv[0] not in ("check", "record") or (argv[0] == "record" and len(argv) != 3):
    print("usage: mock_parity check ARTIFACT... | record ARTIFACT OUT", file=sys.stderr)
    return 2
  try:
    if argv[0] == "record":
      st = time.perf_counter()
      record(argv[1], argv[2])
      print(f"{argv[2]}: check frame recorded on the mock in {time.perf_counter() - st:.0f}s")
      return 0
    for path in argv[1:]:
      st = time.perf_counter()
      check(path)
      print(f"{os.path.basename(path)}: bit-identical to its {HARDWARE} check frame on the {'mock' if ON_MOCK else 'device'} ({time.perf_counter() - st:.0f}s)")
    return 0
  except ParityError as e:
    print(f"PARITY FAIL: {e}", file=sys.stderr)
    return 1


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
