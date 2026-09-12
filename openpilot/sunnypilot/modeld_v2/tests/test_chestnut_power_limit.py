"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.common.test import OpenpilotTestCase
import openpilot.sunnypilot.modeld_v2.chestnut_power_limit as chestnut_power_limit


class FakeParams:
  def __init__(self, value):
    self.value = value

  def get(self, key, return_default=False):
    assert key == "ChestnutPowerLimit"
    return self.value


class FakeSmuMod:
  PPSMC_MSG_SetPptLimit = 0x11
  PPSMC_MSG_GetPptLimit = 0x12


class FakeSmu:
  def __init__(self, limit=150):
    self.smu_mod = FakeSmuMod
    self.limit = limit
    self.calls = []

  def _send_msg(self, msg, arg, read_back_arg=False, timeout=None):
    self.calls.append((msg, arg))
    if msg == FakeSmuMod.PPSMC_MSG_SetPptLimit:
      self.limit = arg
    return self.limit if read_back_arg else 0


class FakeIface:
  def __init__(self, smu):
    self.dev_impl = type("DevImpl", (), {"smu": smu})


class FakeDevice:
  def __init__(self, smu):
    self.iface = FakeIface(smu)


class TestChestnutPowerLimit(OpenpilotTestCase):
  def test_default_is_stock(self):
    assert chestnut_power_limit.get_power_limit(FakeParams(0)) == 0
    assert chestnut_power_limit.get_power_limit(FakeParams(None)) == 0

  def test_clamped_to_range(self):
    for raw, expected in ((80, 80), (10, chestnut_power_limit.POWER_LIMIT_MIN_W), (500, chestnut_power_limit.POWER_LIMIT_MAX_W), (-5, 0)):
      assert chestnut_power_limit.get_power_limit(FakeParams(raw)) == expected

  def test_garbage_is_stock(self):
    assert chestnut_power_limit.get_power_limit(FakeParams("abc")) == 0

  def test_apply_sets_and_reads_back(self, monkeypatch):
    smu = FakeSmu()
    monkeypatch.setattr(chestnut_power_limit, "Device", {"AMD": FakeDevice(smu)})
    assert chestnut_power_limit.apply_power_limit(60) == 60
    assert smu.calls == [(FakeSmuMod.PPSMC_MSG_SetPptLimit, 60), (FakeSmuMod.PPSMC_MSG_GetPptLimit, 0)]

  def test_apply_zero_touches_nothing(self, monkeypatch):
    smu = FakeSmu()
    monkeypatch.setattr(chestnut_power_limit, "Device", {"AMD": FakeDevice(smu)})
    assert chestnut_power_limit.apply_power_limit(0) is None
    assert smu.calls == []
