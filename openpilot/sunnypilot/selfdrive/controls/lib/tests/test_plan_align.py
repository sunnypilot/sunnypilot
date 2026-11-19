"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import types

import numpy as np

from openpilot.cereal import custom
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.sunnypilot.selfdrive.controls.lib import plan_align
from openpilot.sunnypilot.selfdrive.controls.lib.plan_align import PlanAlignBraking

Runner = custom.ModelManagerSP.Runner
T = np.array(ModelConstants.T_IDXS)


class FakeParams:
  def __init__(self, runner, toggle):
    self.runner, self.toggle = runner, toggle

  def get(self, key):
    return int(self.runner) if key == "ModelRunnerTypeCache" else None

  def get_bool(self, key):
    return self.toggle if key == plan_align.PARAM else False


def make(runner=Runner.tinygrad, toggle=True) -> PlanAlignBraking:
  pa = PlanAlignBraking()
  pa.params = FakeParams(runner, toggle)
  pa._read_params()
  return pa


def stop_plan(v0, d_stop):
  """constant-decel plan that stops exactly at d_stop"""
  a = v0 ** 2 / (2 * d_stop)
  ts = v0 / a
  v = np.clip(v0 - a * T, 0, None)
  x = np.where(T < ts, v0 * T - 0.5 * a * T ** 2, d_stop)
  return types.SimpleNamespace(velocity=types.SimpleNamespace(x=list(v)), position=types.SimpleNamespace(x=list(x)))


def cruise_plan(v0=20.0):
  return types.SimpleNamespace(velocity=types.SimpleNamespace(x=[v0] * len(T)), position=types.SimpleNamespace(x=list(v0 * T)))


def run(pa, msg, a_action, has_lead=False, n=30):
  out = a_action
  for _ in range(n):
    out = pa.update(msg, a_action, has_lead)
  return out


class TestPlanAlignBraking(OpenpilotTestCase):
  def test_default_model_is_excluded(self):
    assert not make(runner=Runner.stock, toggle=True).enabled

  def test_custom_model_needs_toggle(self):
    assert make(runner=Runner.tinygrad, toggle=True).enabled
    assert not make(runner=Runner.tinygrad, toggle=False).enabled

  def test_disabled_is_passthrough(self):
    assert run(make(Runner.stock, True), stop_plan(80 / 3.6, 120), -1.3) == -1.3

  def test_high_speed_stop_brakes_harder(self):
    out = run(make(), stop_plan(80 / 3.6, 120), -1.3)
    assert -2.1 < out < -1.5  # needed ~ -2.06, beta 0.7 closes most of the gap

  def test_never_weaker_and_respects_floor(self):
    out = run(make(), stop_plan(80 / 3.6, 60), -1.3)  # would need ~ -4.1
    assert plan_align.FLOOR - 1e-6 <= out <= -1.3
    assert run(make(), stop_plan(15.0, 60), -2.5) == -2.5  # action already harder than plan

  def test_lead_is_untouched(self):
    assert run(make(), stop_plan(80 / 3.6, 120), -1.3, has_lead=True) == -1.3

  def test_cruise_and_acceleration_untouched(self):
    assert run(make(), cruise_plan(), 0.1) == 0.1
    assert run(make(), stop_plan(15.0, 60), 0.8) == 0.8

  def test_bad_plan_length_is_passthrough(self):
    bad = types.SimpleNamespace(velocity=types.SimpleNamespace(x=[1.0, 2.0]), position=types.SimpleNamespace(x=[1.0, 2.0]))
    assert run(make(), bad, -1.0) == -1.0
