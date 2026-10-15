"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import bisect
import itertools
import math
from functools import partial

import numpy as np

from openpilot.common.basedir import BASEDIR
from openpilot.sunnypilot.modeld_v2.helpers import _dtype, read_parts


def pack_layout(specs: dict[str, tuple], frame_size: int) -> tuple[dict[str, int], int]:
  offsets, offset = {}, 0
  for name, (shape, dtype) in ({"tfm": ((2, 3, 3), np.float32)} | specs).items():
    offsets[name], offset = offset, offset + -(-math.prod(shape) * np.dtype(dtype).itemsize // 128) * 128
  return offsets | {"frames": offset}, offset + 2 * frame_size


class _Blobs:  # the model's and the warp's blobs as one address space, for a part whose ranges span both files
  def __init__(self, *blobs):
    self.blobs, self.starts = blobs, list(itertools.accumulate([0] + [len(blob) for blob in blobs[:-1]]))

  def __getitem__(self, span: slice):
    index = bisect.bisect_right(self.starts, span.start) - 1
    return self.blobs[index][span.start - self.starts[index]:span.stop - self.starts[index]]


def fused_with_warp(cam_w: int, cam_h: int, chestnut: bool):  # load_model's extend: a native model runs upload, warp and model as one submit
  return partial(frame_part, f"{BASEDIR}/openpilot/sunnypilot/modeld_v2/models/{'big_' if chestnut else ''}driving_warp_{cam_w}x{cam_h}_tinygrad.pkl")


def frame_part(warp_path: str, parts: dict, extras: dict) -> dict:
  if "input_specs" not in extras:  # a legacy model warps in its own parts
    return {}
  (model, model_blob), (warp, warp_blob) = parts["run"], read_parts(warp_path)[0]["run"]
  states = sorted(name for name in extras["input_specs"] if f"next_{name}" in extras["metadata"]["output_shapes"])
  host = {name: (shape, dtype) for name, (shape, dtype, _) in extras["input_specs"].items() if name not in states and name != "new_img"}
  frame_size = next(s["numel"] for s in warp["inputs"] if s["name"] == "input_frame") // 2
  offsets, packed = pack_layout(host, frame_size)
  shift, upload, u8 = len(model_blob), len(model["buffers"]) + len(warp["buffers"]), repr(_dtype("dtypes.uint8"))

  def view(name: str, nbytes: int, dtype: str) -> dict:
    return {"buffer": upload, "offset": offsets[name], "nbytes": nbytes, "dtype": dtype}
  outputs = sorted(s["slot"] for s in model["inputs"] if s["name"] is None)
  names = sorted(["host", *states])
  slots = {s["slot"]: names.index(s["name"]) for s in model["inputs"] if s["name"] in states} | \
          {slot: len(names) + i for i, slot in enumerate(outputs)}
  returned = warp["returns"]["tensors"][0]
  model_inputs = {s["slot"]: {"input": slots[s["slot"]]} if s["slot"] in slots else
                  {k: v for k, v in returned.items() if k != "shape"} | {"buffer": returned["buffer"] + len(model["buffers"])} if s["name"] == "new_img" else
                  view(s["name"], s["numel"] * _dtype(s["dtype"]).itemsize, s["dtype"]) for s in model["inputs"]}
  warp_inputs = {s["slot"]: view("frames" if s["name"] == "input_frame" else "tfm", s["numel"] * _dtype(s["dtype"]).itemsize, s["dtype"])
                 for s in warp["inputs"]}

  def remap(calls: list, inputs: dict, buffers: int, lib: int) -> list:
    return [call | ({"lib": [call["lib"][0] + lib, call["lib"][1] + lib]} if "lib" in call else {}) |
            {"args": [dict(inputs[a["input"]]) if "input" in a else a | {"buffer": a["buffer"] + buffers} for a in call["args"]]} for call in calls]
  header = {"input_names": names, "returns": {"kind": "NoneType", "tensors": []}, "check": None,
            "inputs": [{"slot": names.index("host"), "name": "host", "dtype": u8, "numel": packed, "device": "NPY"}] +
                      [s | {"slot": slots[s["slot"]]} for s in model["inputs"] if s["slot"] in slots],
            "buffers": model["buffers"] + [b | ({"init": [b["init"][0] + shift, b["init"][1] + shift]} if "init" in b else {}) for b in warp["buffers"]] +
                       [{"nbytes": packed, "device": model["inputs"][0]["device"], "dtype": u8}],
            "calls": [{"kind": "copy", "args": [{"buffer": upload, "offset": 0, "nbytes": packed, "dtype": u8}, {"input": names.index("host")}]}] +
                     remap(warp["calls"], warp_inputs, len(model["buffers"]), shift) + remap(model["calls"], model_inputs, 0, 0)}
  return {"run": (header, _Blobs(model_blob, warp_blob))}  # replaces the model's run: one set of buffers, no separate warp
