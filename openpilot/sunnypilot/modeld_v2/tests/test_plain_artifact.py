"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import dataclasses
import functools
import inspect
import os
import sys
import tempfile
from unittest import mock
import numpy as np
import unittest

import openpilot.sunnypilot.modeld_v2.helpers as helpers
from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.modeld_v2 import compile_warp
from openpilot.sunnypilot.modeld_v2.frame_fusion import frame_part, pack_layout
from openpilot.sunnypilot.modeld_v2.helpers import PlainJit, cache_is_fresh, load_model, read_parts, write_bundle
from openpilot.sunnypilot.modeld_v2.plain_artifact_compiler import capture_frame, record_kernel_linear, serialize_jit

CAM_W, CAM_H, MODEL_W, MODEL_H = 32, 16, 16, 8
FRAME = f"{CAM_W},{CAM_H},{CAM_W},{CAM_H},{CAM_H // 2},{CAM_W * CAM_H * 3 // 2}"
FRAME_SIZE = CAM_W * CAM_H * 3 // 2
HOST = {"desire": (8,), "traffic_convention": (2,)}
STATE, OUT = (4, 16), (1, 32)


def compile_jit(fn, inputs: dict, output_container: str | None = None) -> tuple[dict, memoryview]:
  from tinygrad import TinyJit
  run = TinyJit(fn, prune=True)
  with record_kernel_linear() as recorded:
    run(**inputs)
    run(**inputs)
    check, _ = capture_frame(run, inputs, output_container)
  assert len(recorded) == 1, f"expected one captured kernel list, got {len(recorded)}"
  return serialize_jit(run, recorded[0], check)


class TestPlainArtifact(OpenpilotTestCase):
  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    if not os.environ.get("TINYGRAD_TESTS"):
      raise unittest.SkipTest("TINYGRAD_TESTS env var not set, skipping artifact test.")
    from tinygrad import Tensor
    cls.tmp = tempfile.TemporaryDirectory()
    cls.rng = np.random.default_rng(0)
    cls.weights = Tensor(cls.rng.standard_normal((16, 32)).astype(np.float32)).realize()
    cls.bias = Tensor(cls.rng.standard_normal((1, 32)).astype(np.float32)).realize()

  @classmethod
  def tearDownClass(cls):
    cls.tmp.cleanup()
    super().tearDownClass()

  def model(self, x, h):  # a two input, one weight model: the shape of a policy without the size
    return ((x @ self.weights + self.bias).relu() + h.mean()).contiguous()

  def tensors(self, seed: int):
    from tinygrad import Tensor
    rng = np.random.default_rng(seed)
    return {"x": Tensor(rng.standard_normal((1, 16)).astype(np.float32)).realize(), "h": Tensor(rng.standard_normal((4, 16)).astype(np.float32)).realize()}

  def artifact(self, name: str = "model") -> str:
    path = os.path.join(self.tmp.name, f"{name}_tinygrad.pkl")
    if not os.path.exists(path):
      write_bundle(path, {"run": compile_jit(self.model, self.tensors(1))}, {"metadata": {"name": name}})
    return path

  def test_round_trip_matches_jit(self):  # compiler -> bundle -> PlainJit, replay verified, then fresh inputs bit exact with eager tinygrad
    bundle = load_model(self.artifact(), cache=False, verify=True)
    assert bundle["metadata"] == {"name": "model"} and isinstance(bundle["run"], PlainJit)
    fresh = self.tensors(2)
    assert np.array_equal(bundle["run"](**fresh).numpy(), self.model(**fresh).numpy())

  def test_replay_check_catches_a_changed_kernel(self):
    parts, extras = read_parts(self.artifact())
    header, blob = parts["run"]
    poisoned = dict(header, check=dict(header["check"], outputs=[header["check"]["inputs"][0][1]]))
    with self.assertRaises(helpers.ArtifactMismatch):
      PlainJit(poisoned, blob)

  def test_cache_round_trip_holds_no_weights_and_is_rebuilt_when_stale(self):
    path = self.artifact("cached")
    expected = load_model(path, cache=False, verify=False)["run"](**self.tensors(3)).numpy()
    load_model(path)
    assert cache_is_fresh(path)
    with open(f"{path}.cache", "rb") as file:
      cache = file.read()
    assert self.weights.numpy().tobytes() not in cache and len(cache) < os.path.getsize(path)
    with mock.patch.object(helpers, "PlainJit", side_effect=AssertionError("a fresh cache must not rebuild")):
      cached = load_model(path)
    assert np.array_equal(cached["run"](**self.tensors(3)).numpy(), expected)
    with mock.patch.object(helpers, "tinygrad_identity", return_value="another tinygrad"):
      assert not cache_is_fresh(path)
      assert isinstance(load_model(path)["run"], PlainJit)
      assert cache_is_fresh(path)
    assert not cache_is_fresh(path)  # keyed on the tinygrad that wrote it, so the next boot after a bump rebuilds once
    os.utime(path)
    with mock.patch.object(helpers, "tinygrad_identity", return_value="another tinygrad"):
      assert not cache_is_fresh(path)

  def test_fused_with_warp_matches_warp_then_model(self):
    from tinygrad import Tensor
    warp_path = os.path.join(self.tmp.name, "warp_tinygrad.pkl")
    with mock.patch.object(sys, "argv", ["compile_warp", "--frame", FRAME, "--warp-to", f"{MODEL_W}x{MODEL_H}", "--output", warp_path]):
      compile_warp.main()
    warp = load_model(warp_path, cache=False)["run"]

    def native(new_img, desire, traffic_convention, state_feat_q, output_buffers):
      feat = state_feat_q.mean(axis=0).reshape(1, 16) + new_img.float().mean() + desire.sum() + traffic_convention[0]
      Tensor.realize(output_buffers["outputs"].assign((feat @ self.weights + self.bias).relu()),
                     output_buffers["next_state_feat_q"].assign(state_feat_q[1:].cat(feat * 2)))

    def model_inputs(new_img):
      return {"new_img": new_img} | {name: Tensor(np.ones(shape, np.float32) * 0.5).realize() for name, shape in HOST.items()} | \
             {"state_feat_q": Tensor(self.rng.standard_normal(STATE).astype(np.float32)).realize(),
              "output_buffers": {"outputs": Tensor.zeros(OUT).contiguous().realize(), "next_state_feat_q": Tensor.zeros(STATE).contiguous().realize()}}
    frames = Tensor(self.rng.integers(0, 256, (2, FRAME_SIZE), dtype=np.uint8)).realize()
    tfm = Tensor(np.tile(np.eye(3, dtype=np.float32), (2, 1, 1))).realize()
    path = os.path.join(self.tmp.name, "native_tinygrad.pkl")
    part = compile_jit(native, model_inputs(warp(input_frame=frames, M_inv=tfm).realize()), "output_buffers")
    extras = {"input_specs": {"new_img": ((2, 6, MODEL_H // 2, MODEL_W // 2), "|u1", "CPU"), "state_feat_q": (STATE, "<f4", "CPU")}
              | {name: (shape, "<f4", "CPU") for name, shape in HOST.items()},
              "output_specs": {"outputs": (OUT, "<f4", "CPU"), "next_state_feat_q": (STATE, "<f4", "CPU")},
              "metadata": {"output_shapes": {"outputs": OUT, "next_state_feat_q": STATE}}}
    write_bundle(path, {"run": part}, extras)

    fused = load_model(path, cache=False, extend=functools.partial(frame_part, warp_path))
    assert fused["run"].input_names == ["host", "state_feat_q"]
    offsets, packed = pack_layout(HOST, FRAME_SIZE)
    host = np.zeros(packed, np.uint8)
    inputs = model_inputs(None)
    for name, shape in ({"tfm": (2, 3, 3)} | HOST).items():
      np.ndarray(shape, np.float32, host, offsets[name])[...] = tfm.numpy() if name == "tfm" else inputs[name].numpy()
    host[offsets["frames"]:] = frames.numpy().ravel()
    fused["run"](host=Tensor(host, device="NPY"), state_feat_q=inputs["state_feat_q"], output_buffers=inputs["output_buffers"])

    expected = model_inputs(warp(input_frame=frames, M_inv=tfm).realize()) | {k: inputs[k] for k in ("state_feat_q",)}
    native(**expected)
    for name in ("outputs", "next_state_feat_q"):
      assert np.array_equal(inputs["output_buffers"][name].numpy(), expected["output_buffers"][name].numpy()), name

  def test_tinygrad_api_the_loader_reads(self):
    import tinygrad.engine.jit as jit
    from tinygrad.device import Buffer, TinyELF
    from tinygrad.helpers import Target
    from tinygrad.uop.ops import ParamArg, ProgramInfo, UOp
    fields = {cls: {f.name for f in dataclasses.fields(cls)} for cls in (ProgramInfo, ParamArg, Target)}
    assert fields[ProgramInfo] >= {"global_size", "local_size", "globals", "outs", "ins", "target"}, "ProgramInfo changed: update helpers._program_uop"
    assert fields[ParamArg] >= {"slot", "dtype", "name", "image"}, "ParamArg changed: update helpers._program_uop"
    assert fields[Target] >= {"device", "renderer", "arch"}, "Target changed: update the 'target' key in plain_artifact_compiler.serialize_jit"
    assert "signature" in getattr(TinyELF, "__annotations__", {}) or hasattr(UOp, "kernel_params"), \
      "kernel signatures moved: update plain_artifact_compiler.serialize_jit"
    assert callable(getattr(UOp, "param", None)) and callable(getattr(UOp, "from_buffer", None)), "UOp.param/from_buffer: update helpers.PlainJit"
    assert callable(getattr(UOp, "store_call", None)) and callable(getattr(UOp, "call", None)), "UOp.call/store_call: update helpers.PlainJit"
    assert callable(getattr(Buffer, "view", None)) and callable(getattr(Buffer, "ensure_allocated", None)), "Buffer.view: update helpers._upload"
    assert callable(getattr(jit, "compile_linear", None)) and callable(getattr(jit, "_prepare_jit_inputs", None)), "engine.jit: update helpers._Jit"
    assert "expected_names" in inspect.signature(jit.CapturedJit).parameters, "CapturedJit: update helpers.PlainJit and plain_artifact_compiler.serialize_jit"
