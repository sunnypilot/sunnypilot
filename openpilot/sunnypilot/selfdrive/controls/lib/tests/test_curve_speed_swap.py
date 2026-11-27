"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from types import SimpleNamespace

from openpilot.common.parameterized import parameterized
from openpilot.common.realtime import DT_MDL
from openpilot.common.test import OpenpilotTestCase

from openpilot.selfdrive.controls.lib.curve_speed import CurveSpeed
from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlannerSP, NoCurveSpeed


def _planner(vision_enabled: bool, openpilot_longitudinal: bool):
  return SimpleNamespace(scc=SimpleNamespace(vision=SimpleNamespace(enabled=vision_enabled)),
                         openpilot_longitudinal=openpilot_longitudinal, curve_speed=CurveSpeed(DT_MDL), dt=DT_MDL)


class TestCurveSpeedSwap(OpenpilotTestCase):
  @parameterized.expand([(True, True, NoCurveSpeed), (True, False, CurveSpeed), (False, True, CurveSpeed), (False, False, CurveSpeed)])
  def test_swap(self, vision_enabled, openpilot_longitudinal, expected):
    planner = _planner(vision_enabled, openpilot_longitudinal)
    LongitudinalPlannerSP._update_curve_speed(planner)
    self.assertIsInstance(planner.curve_speed, expected)

  def test_no_offset_when_scc_vision_on(self):
    planner = _planner(True, True)
    LongitudinalPlannerSP._update_curve_speed(planner)
    self.assertEqual(planner.curve_speed.update(None, 0.0), 0.0)

  def test_toggle_back_restores_upstream(self):
    planner = _planner(True, True)
    LongitudinalPlannerSP._update_curve_speed(planner)
    planner.scc.vision.enabled = False
    LongitudinalPlannerSP._update_curve_speed(planner)
    self.assertIsInstance(planner.curve_speed, CurveSpeed)

  def test_keeps_instance_when_unchanged(self):
    planner = _planner(False, True)
    before = planner.curve_speed
    LongitudinalPlannerSP._update_curve_speed(planner)
    self.assertIs(planner.curve_speed, before)
