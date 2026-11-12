"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import bisect
import itertools
import math
from functools import partial

from openpilot.common.basedir import BASEDIR
from openpilot.sunnypilot.modeld_v2.helpers import _dtype, read_parts


def pack_layout(shapes: dict[str, tuple], frame_size: int) -> tuple[dict[str, int], int]:
  offsets, offset = {}, 0
  for name, shape in ({"tfm": (2, 3, 3)} | shapes).items():
    offsets[name], offset = offset, offset + -(-math.prod(shape) * 4 // 128) * 128
  return offsets | {"frames": offset}, offset + 2 * frame_size

EXTRA_WARPS = {"light_img": "light_tfm", "turn_img": "turn_tfm"}

def host_shapes(input_shapes: dict[str, tuple], states) -> dict[str, tuple]:
  shapes = {name: shape for name, shape in input_shapes.items() if name not in states and name != "new_img" and name not in EXTRA_WARPS}
  return shapes | {tfm: (1, 3, 3) for img, tfm in EXTRA_WARPS.items() if img in input_shapes}


class _Blobs:  # the model's and the warp's blobs as one address space, for a part whose ranges span both files
  def __init__(self, *blobs):
    self.blobs, self.starts = blobs, list(itertools.accumulate([0] + [len(blob) for blob in blobs[:-1]]))

  def __getitem__(self, span: slice):
    index = bisect.bisect_right(self.starts, span.start) - 1
    return self.blobs[index][span.start - self.starts[index]:span.stop - self.starts[index]]


def fused_with_warp(cam_w: int, cam_h: int, chestnut: bool):  # load_model's extend: a native model runs upload, warp and model as one submit
  models, big = f"{BASEDIR}/openpilot/sunnypilot/modeld_v2/models", 'big_' if chestnut else ''
  return partial(frame_part, f"{models}/{big}driving_warp_{cam_w}x{cam_h}_tinygrad.pkl",
                 light_warp_path=f"{models}/{big}driving_lightwarp_{cam_w}x{cam_h}_tinygrad.pkl",
                 turn_warp_path=f"{models}/{big}driving_turnwarp_{cam_w}x{cam_h}_tinygrad.pkl")


def frame_part(warp_path: str, parts: dict, extras: dict, light_warp_path: str | None = None, turn_warp_path: str | None = None) -> dict:
  if "input_specs" not in extras:  # a legacy model warps in its own parts
    return {}
  (model, model_blob), (warp, warp_blob) = parts["run"], read_parts(warp_path)[0]["run"]
  states = sorted(name for name in extras["input_specs"] if f"next_{name}" in extras["metadata"]["output_shapes"])
  host = host_shapes({name: shape for name, (shape, _, _) in extras["input_specs"].items()}, states)
  paths = {"light_img": light_warp_path, "turn_img": turn_warp_path}
  extra = [(img, tfm, *read_parts(paths[img])[0]["run"]) for img, tfm in EXTRA_WARPS.items() if img in extras["input_specs"]]
  frame_size = next(s["numel"] for s in warp["inputs"] if s["name"] == "input_frame") // 2
  offsets, packed = pack_layout(host, frame_size)
  shift = len(model_blob)
  buf_base, blob_base = [len(model["buffers"]) + len(warp["buffers"])], [len(model_blob) + len(warp_blob)]
  for _, _, part, blob in extra:
    buf_base.append(buf_base[-1] + len(part["buffers"])); blob_base.append(blob_base[-1] + len(blob))
  upload, u8 = buf_base[-1], repr(_dtype("dtypes.uint8"))
  extra_at = {img: (part, buf_base[i], blob_base[i], tfm) for i, (img, tfm, part, _) in enumerate(extra)}

  def view(name: str, nbytes: int, dtype: str) -> dict:
    return {"buffer": upload, "offset": offsets[name], "nbytes": nbytes, "dtype": dtype}
  outputs = sorted(s["slot"] for s in model["inputs"] if s["name"] is None)
  names = sorted(["host", *states])
  slots = {s["slot"]: names.index(s["name"]) for s in model["inputs"] if s["name"] in states} | \
          {slot: len(names) + i for i, slot in enumerate(outputs)}
  def warped(part: dict, base: int) -> dict:
    returned = part["returns"]["tensors"][0]
    return {k: v for k, v in returned.items() if k != "shape"} | {"buffer": returned["buffer"] + base}
  model_inputs = {s["slot"]: {"input": slots[s["slot"]]} if s["slot"] in slots else
                  warped(warp, len(model["buffers"])) if s["name"] == "new_img" else
                  warped(extra_at[s["name"]][0], extra_at[s["name"]][1]) if s["name"] in extra_at else
                  view(s["name"], s["numel"] * _dtype(s["dtype"]).itemsize, s["dtype"]) for s in model["inputs"]}
  def warp_inputs(part: dict, tfm: str) -> dict:
    return {s["slot"]: view("frames" if s["name"] == "input_frame" else tfm, s["numel"] * _dtype(s["dtype"]).itemsize, s["dtype"]) for s in part["inputs"]}

  def remap(calls: list, inputs: dict, buffers: int, lib: int) -> list:
    return [call | ({"lib": [call["lib"][0] + lib, call["lib"][1] + lib]} if "lib" in call else {}) |
            {"args": [dict(inputs[a["input"]]) if "input" in a else a | {"buffer": a["buffer"] + buffers} for a in call["args"]]} for call in calls]
  header = {"input_names": names, "returns": {"kind": "NoneType", "tensors": []}, "check": None,
            "inputs": [{"slot": names.index("host"), "name": "host", "dtype": u8, "numel": packed, "device": "NPY"}] +
                      [s | {"slot": slots[s["slot"]]} for s in model["inputs"] if s["slot"] in slots],
            "buffers": model["buffers"] + [b | ({"init": [b["init"][0] + d, b["init"][1] + d]} if "init" in b else {})
                                           for part, d in ((warp, shift), *((p, bb) for p, _, bb, _ in extra_at.values())) for b in part["buffers"]] +
                       [{"nbytes": packed, "device": model["inputs"][0]["device"], "dtype": u8}],
            "calls": [{"kind": "copy", "args": [{"buffer": upload, "offset": 0, "nbytes": packed, "dtype": u8}, {"input": names.index("host")}]}] +
                     remap(warp["calls"], warp_inputs(warp, "tfm"), len(model["buffers"]), shift) +
                     [c for p, b0, bb, tfm in extra_at.values() for c in remap(p["calls"], warp_inputs(p, tfm), b0, bb)] +
                     remap(model["calls"], model_inputs, 0, 0)}
  return {"run": (header, _Blobs(model_blob, warp_blob, *(blob for *_, blob in extra)))}
