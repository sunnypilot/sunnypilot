"""
Copyright (c) 2021-, rav4kumar, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Coverage for AccelPersonalityController:
- live param flip via auto-refresh (no Python set_enabled() call needed)
- V_CRUISE_UNSET guard
- enable-transition snap to fresh target
- per-personality accel limit deltas vs stock get_max_accel
"""
import numpy as np

from cereal import custom

from openpilot.common.params import Params
from opendbc.car.interfaces import ACCEL_MIN
from openpilot.selfdrive.car.cruise import V_CRUISE_UNSET
from openpilot.selfdrive.controls.lib.longitudinal_planner import get_max_accel as stock_get_max_accel

from openpilot.sunnypilot.selfdrive.controls.lib.accel_personality.accel_controller import (
  AccelPersonalityController,
  PARAM_REFRESH_FRAMES,
)


AccelPersonality = custom.LongitudinalPlanSP.AccelerationPersonality


class FakeCarState:
  def __init__(self, v_cruise=30.0):
    self.vCruise = v_cruise


class FakeSM:
  def __init__(self, v_cruise=30.0):
    self._data = {'carState': FakeCarState(v_cruise)}

  def __getitem__(self, k):
    return self._data[k]


def _print_table(title, header, rows):
  print(f"\n--- {title} ---")
  print(" | ".join(f"{h:>12}" for h in header))
  print("-" * (15 * len(header)))
  for row in rows:
    print(" | ".join(f"{v:>12.3f}" if isinstance(v, float) else f"{v:>12}" for v in row))


class TestAccelLiveFlip:
  def test_enable_via_param(self):
    Params().put_bool('AccelPersonalityEnabled', False)
    c = AccelPersonalityController()
    assert not c.is_enabled()
    Params().put_bool('AccelPersonalityEnabled', True)
    for _ in range(PARAM_REFRESH_FRAMES + 1):
      c.update(FakeSM())
    assert c.is_enabled()

  def test_disable_via_param(self):
    Params().put_bool('AccelPersonalityEnabled', True)
    c = AccelPersonalityController()
    assert c.is_enabled()
    Params().put_bool('AccelPersonalityEnabled', False)
    for _ in range(PARAM_REFRESH_FRAMES + 1):
      c.update(FakeSM())
    assert not c.is_enabled()

  def test_personality_change_via_param(self):
    Params().put('AccelPersonality', AccelPersonality.normal)
    c = AccelPersonalityController()
    assert c.get_accel_personality() == AccelPersonality.normal
    Params().put('AccelPersonality', AccelPersonality.sport)
    for _ in range(PARAM_REFRESH_FRAMES + 1):
      c.update(FakeSM())
    assert c.get_accel_personality() == AccelPersonality.sport

  def test_refresh_boundary_below_threshold(self):
    Params().put_bool('AccelPersonalityEnabled', False)
    c = AccelPersonalityController()
    Params().put_bool('AccelPersonalityEnabled', True)
    for _ in range(PARAM_REFRESH_FRAMES - 1):
      c.update(FakeSM())
    assert not c.is_enabled()

  def test_enable_transition_snaps_to_target(self):
    Params().put_bool('AccelPersonalityEnabled', True)
    Params().put('AccelPersonality', AccelPersonality.sport)
    c = AccelPersonalityController()
    for _ in range(PARAM_REFRESH_FRAMES + 1):
      c.update(FakeSM(v_cruise=35.0))
    c.get_accel_limits(25.0)

    Params().put_bool('AccelPersonalityEnabled', False)
    for _ in range(PARAM_REFRESH_FRAMES + 1):
      c.update(FakeSM(v_cruise=35.0))
    assert not c.is_enabled()

    Params().put('AccelPersonality', AccelPersonality.eco)
    Params().put_bool('AccelPersonalityEnabled', True)
    for _ in range(PARAM_REFRESH_FRAMES + 1):
      c.update(FakeSM(v_cruise=35.0))
    assert c._first

  def test_vcruise_unset_treated_as_zero(self):
    Params().put_bool('AccelPersonalityEnabled', True)
    c = AccelPersonalityController()
    c.update(FakeSM(v_cruise=V_CRUISE_UNSET))
    assert c._v_cruise == 0.0


class TestAccelUsageDiff:
  def test_accel_clip_per_personality(self, capsys):
    rows = []
    speeds = [3.0, 10.0, 20.0, 30.0]
    personalities = [
      ('eco', AccelPersonality.eco),
      ('normal', AccelPersonality.normal),
      ('sport', AccelPersonality.sport),
    ]

    Params().put_bool('AccelPersonalityEnabled', True)
    sm = FakeSM(v_cruise=35.0)

    any_delta = False
    for label, p in personalities:
      Params().put('AccelPersonality', p)
      c = AccelPersonalityController()
      c.update(sm)
      for v_ego in speeds:
        stock_hi = float(stock_get_max_accel(v_ego))
        c_lo, c_hi = c.get_accel_limits(v_ego)
        delta_hi = c_hi - stock_hi
        delta_lo = c_lo - ACCEL_MIN
        if abs(delta_hi) > 0.01 or abs(delta_lo) > 0.01:
          any_delta = True
        rows.append((label, v_ego, stock_hi, c_hi, delta_hi, c_lo, delta_lo))

    with capsys.disabled():
      _print_table(
        "AccelPersonalityController: a_max stock vs controller",
        ["personality", "v_ego", "stock_hi", "ctrl_hi", "delta_hi", "ctrl_lo", "delta_lo"],
        rows,
      )
    assert any_delta
