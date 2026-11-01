"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import os
import re
import sys
import tempfile
import unittest
from unittest import mock
import numpy as np

os.environ.setdefault("CHECK_OOB", "0")
os.environ.setdefault("GMMU", "0")
if sys.platform == "darwin" and os.environ.get("DEV", "").startswith("MOCKUSB"):  # the mock's VRAM is a memfd, which macOS lacks: an unlinked file is the same
  from tinygrad.runtime.autogen import libc

  def _memfd_create(name, flags):
    fd, path = tempfile.mkstemp()
    os.unlink(path)
    return fd
  libc.memfd_create = _memfd_create

from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.modeld_v2 import convert_upstream_pkl
from openpilot.sunnypilot.modeld_v2.convert_upstream_pkl import convert
from openpilot.sunnypilot.modeld_v2.helpers import PlainJit, load_model
from openpilot.sunnypilot.modeld_v2.plain_artifact_compiler import capture_frame

IMG, DESIRE, STATE, OUT = (6, 8, 8), (8,), (4, 16), (1, 32)


class TestConvertUpstreamPkl(OpenpilotTestCase):
  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    if not os.environ.get("TINYGRAD_TESTS"):
      raise unittest.SkipTest("TINYGRAD_TESTS not set. skipping converter test")
    from tinygrad import Device, Tensor
    assert Device.DEFAULT == "AMD" and getattr(Device["AMD"], "is_usb", False), f"{Device.DEFAULT} is not an AMD device behind the USB bridge"
    assert (Tensor([1, 2, 3]) * 2).tolist() == [2, 4, 6]
    cls.tmp = tempfile.TemporaryDirectory()
    cls.rng = np.random.default_rng(0)
    cls.weights = Tensor(cls.rng.standard_normal((16, 32)).astype(np.float32)).realize()
    cls.bias = Tensor(cls.rng.standard_normal((1, 32)).astype(np.float32)).realize()
    cls.input_specs = {"input_imgs": (IMG, "uint8", Device.DEFAULT), "desire": (DESIRE, "float32", Device.DEFAULT),
                       "features": (STATE, "float32", Device.DEFAULT)}
    cls.output_specs = {"outputs": (OUT, "float32", Device.DEFAULT), "next_features": (STATE, "float32", Device.DEFAULT)}

  @classmethod
  def tearDownClass(cls):
    cls.tmp.cleanup()
    super().tearDownClass()

  def model(self, input_imgs, desire, features, output_buffers):
    from tinygrad import Tensor
    feat = features.mean(axis=0).reshape(1, 16) + input_imgs.float().mean() + desire.sum()
    Tensor.realize(output_buffers["outputs"].assign((feat @ self.weights + self.bias).relu()),
                   output_buffers["next_features"].assign(features[1:].cat(feat * 2)))

  def inputs(self, seed: int) -> dict:
    from examples.openpilot.helpers import allocate_inputs
    rng = np.random.default_rng(seed)

    def initialize(arrays: dict):
      for value in arrays.values():
        value[...] = rng.standard_normal(value.shape) if value.dtype.kind == "f" else rng.integers(0, 256, value.shape)
    return allocate_inputs(self.input_specs, initialize) | {"output_buffers": allocate_inputs(self.output_specs)}

  def jit(self):
    from tinygrad import TinyJit
    run = TinyJit(self.model, prune=True)
    kwargs = self.inputs(1)
    run(**kwargs)
    run(**kwargs)
    return run

  def assert_matches_eager(self, plain, seed: int):
    fresh, expected = self.inputs(seed), self.inputs(seed)
    plain(**fresh)
    self.model(**expected)
    for name in self.output_specs:
      assert np.array_equal(fresh["output_buffers"][name].numpy(), expected["output_buffers"][name].numpy()), name

  def convert(self, jit) -> tuple[dict, memoryview]:
    from tinygrad import Device
    kwargs = self.inputs(2)
    frame, _ = capture_frame(jit, kwargs, "output_buffers")
    header, blob = convert(jit, kwargs, frame, Device[Device.DEFAULT].renderer.target)
    kernels = jit.captured._linear.src[0].without_after.arg.aux.kernels
    assert [call["name"] for call in header["calls"]] == [re.sub(r"\x1b\[[0-9;]*m", "", kernel[1]) for kernel in kernels]
    assert all(re.fullmatch(r"\w+", call["name"]) for call in header["calls"]), "kernel names: failure point 1"
    assert [(tuple(call["outs"]), tuple(call["ins"])) for call in header["calls"]] == [tuple(kernel[6]) for kernel in kernels], "outs/ins: failure point 1"
    bound = {argument["input"] for call in header["calls"] for argument in call["args"] if "input" in argument}
    assert bound == {spec["slot"] for spec in header["inputs"]}, f"input slots bound by pokes {sorted(bound)}: failure point 4"
    assert [spec["name"] for spec in header["inputs"]][:len(self.input_specs)] == sorted(self.input_specs)
    return header, blob

  def test_converted_jit_matches_eager(self):  # the submit decoded into plain calls, replayed against its own frame
    jit = self.jit()
    plain = PlainJit(*self.convert(jit))
    self.assert_matches_eager(plain, 3)
    self.assert_matches_eager(plain, 4)

  def test_pickle_round_trip_through_main(self):
    from examples.openpilot.helpers import dump_pickle, load_pickle
    from tinygrad.engine.realize import lower_and_compile
    pkl, out = os.path.join(self.tmp.name, "tiny_tinygrad.pkl"), os.path.join(self.tmp.name, "tiny_plain.pkl")
    dump_pickle({"run": self.jit(), "input_specs": self.input_specs, "output_specs": self.output_specs, "metadata": {"name": "tiny"}}, pkl)

    artifact = load_pickle(pkl, out_of_band=True)
    artifact["run"].captured._linear = lower_and_compile(artifact["run"].captured._linear)
    self.assert_matches_eager(PlainJit(*self.convert(artifact["run"])), 5)

    with mock.patch.object(sys, "argv", ["convert_upstream_pkl", pkl, out]):
      convert_upstream_pkl.main()
    bundle = load_model(out, cache=False, verify=True)
    assert bundle["metadata"] == {"name": "tiny"} and bundle["input_specs"] == self.input_specs and bundle["output_specs"] == self.output_specs
    self.assert_matches_eager(bundle["run"], 6)
