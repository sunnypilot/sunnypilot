"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from types import SimpleNamespace
from unittest import mock

from openpilot.cereal import log
from openpilot.common.realtime import DT_MDL
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.controls.lib.accel_boost import AccelBoost, ACCEL_BOOST_MAX, ACCEL_BOOST_PER_OVERRIDE, ACCEL_BOOST_RATE
from openpilot.sunnypilot import PARAMS_UPDATE_PERIOD
from openpilot.sunnypilot.selfdrive.controls.lib.accel_boost_ext import AccelBoostExt, get_accel_boost_max
from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlannerSP

E2E_ACCEL = 0.5
PLANNER_ACCEL = 2.0
STEPS_PER_OVERRIDE = round(ACCEL_BOOST_PER_OVERRIDE / (ACCEL_BOOST_RATE * DT_MDL))
EXPECTED_SCALE = {
  log.LongitudinalPersonality.relaxed: 0.3,
  log.LongitudinalPersonality.standard: 0.5,
  log.LongitudinalPersonality.aggressive: 0.7,
}


class FakeParams:
  def __init__(self, enabled=True):
    self.enabled = enabled

  def get_bool(self, key):
    return self.enabled


class FakeSubMaster:
  def __init__(self, enabled=True, gas_pressed=False, v_ego=15.0,
               personality=log.LongitudinalPersonality.standard):
    self._messages = {
      'selfdriveState': SimpleNamespace(enabled=enabled, personality=personality),
      'carState': SimpleNamespace(gasPressed=gas_pressed, vEgo=v_ego),
    }

  def __getitem__(self, key):
    return self._messages[key]


def update(boost, sm, e2e=E2E_ACCEL):
  return boost.update(sm, e2e, PLANNER_ACCEL, PLANNER_ACCEL)


class PlannerStub(LongitudinalPlannerSP):
  def __init__(self):
    self._accel_boost = None


class TestAccelBoostExt(OpenpilotTestCase):
  def setUp(self):
    super().setUp()
    self.params = FakeParams()
    patcher = mock.patch("openpilot.sunnypilot.selfdrive.controls.lib.accel_boost_ext.Params", return_value=self.params)
    patcher.start()
    self.addCleanup(patcher.stop)

  def _boost_to_max(self, personality):
    boost = AccelBoostExt()
    sm = FakeSubMaster(personality=personality)
    # Eligibility is latched on a frame without gas, then applied on the next override.
    update(boost, sm)
    for _ in range(10):
      sm['carState'].gasPressed = True
      for _ in range(STEPS_PER_OVERRIDE):
        update(boost, sm)
      sm['carState'].gasPressed = False
      update(boost, sm)
    return boost, sm

  def _applied_extra(self, boost, sm):
    update(boost, sm)
    return boost.extra_boost

  def test_off_matches_stock_boost_exactly(self):
    self.params.enabled = False
    sm = FakeSubMaster()
    stock = AccelBoost()
    ext = AccelBoostExt()

    stock_out = update(stock, sm)
    ext_out = update(ext, sm)
    self.assertAlmostEqual(ext_out, stock_out)

    for _ in range(10):
      sm['carState'].gasPressed = True
      for _ in range(STEPS_PER_OVERRIDE):
        stock_out = update(stock, sm)
        ext_out = update(ext, sm)
        self.assertAlmostEqual(ext_out, stock_out)
      sm['carState'].gasPressed = False
      stock_out = update(stock, sm)
      ext_out = update(ext, sm)
      self.assertAlmostEqual(ext_out, stock_out)

    self.assertAlmostEqual(ext.total_boost, stock.total_boost)
    self.assertAlmostEqual(ext._stock.total_boost, stock_out - E2E_ACCEL)
    self.assertEqual(ext.extra_boost, 0.0)
    self.assertEqual(ext._extra.total_boost, 0.0)

  def test_no_boost_without_gas(self):
    ext = AccelBoostExt()
    sm = FakeSubMaster(gas_pressed=False)
    out = update(ext, sm)
    self.assertEqual(ext.total_boost, 0.0)
    self.assertEqual(ext._extra.total_boost, 0.0)
    self.assertAlmostEqual(out, E2E_ACCEL)

  def test_boost_requires_e2e_to_be_limiting(self):
    ext = AccelBoostExt()
    sm = FakeSubMaster(gas_pressed=False)
    ext.update(sm, E2E_ACCEL, E2E_ACCEL, E2E_ACCEL)
    sm['carState'].gasPressed = True
    for _ in range(10):
      ext.update(sm, E2E_ACCEL, E2E_ACCEL, E2E_ACCEL)
    self.assertEqual(ext.total_boost, 0.0)
    self.assertEqual(ext._stock.total_boost, 0.0)
    self.assertEqual(ext.extra_boost, 0.0)
    self.assertEqual(ext._extra.total_boost, 0.0)

  def test_extra_layer_per_override_cap(self):
    ext = AccelBoostExt()
    sm = FakeSubMaster(gas_pressed=False)
    update(ext, sm)
    sm['carState'].gasPressed = True
    for _ in range(1000):
      update(ext, sm)

    self.assertAlmostEqual(ext._extra.total_boost, ACCEL_BOOST_PER_OVERRIDE)
    applied = self._applied_extra(ext, sm)
    expected = ACCEL_BOOST_PER_OVERRIDE * EXPECTED_SCALE[log.LongitudinalPersonality.standard]
    self.assertAlmostEqual(applied, expected)

  def test_extra_scales_with_following_distance(self):
    applied = {}
    for personality in (log.LongitudinalPersonality.relaxed,
                        log.LongitudinalPersonality.standard,
                        log.LongitudinalPersonality.aggressive):
      ext, sm = self._boost_to_max(personality)
      sm['carState'].gasPressed = True
      applied[personality] = self._applied_extra(ext, sm)

    for personality, value in applied.items():
      self.assertAlmostEqual(value, ACCEL_BOOST_MAX * EXPECTED_SCALE[personality])

    self.assertLess(applied[log.LongitudinalPersonality.relaxed], applied[log.LongitudinalPersonality.standard])
    self.assertLess(applied[log.LongitudinalPersonality.standard], applied[log.LongitudinalPersonality.aggressive])

  def test_capnp_dynamic_enum_personality_scales(self):
    # Real SubMaster messages expose personality as a capnp DynamicEnum; equality still matches the enum value.
    msg = log.SelfdriveState.new_message()
    msg.personality = log.LongitudinalPersonality.aggressive
    ext, sm = self._boost_to_max(msg.personality)
    sm['carState'].gasPressed = True
    applied = self._applied_extra(ext, sm)
    self.assertAlmostEqual(applied, ACCEL_BOOST_MAX * EXPECTED_SCALE[log.LongitudinalPersonality.aggressive])

  def test_extra_feeds_into_stock_last(self):
    ext, sm = self._boost_to_max(log.LongitudinalPersonality.standard)
    sm['carState'].gasPressed = True
    inputs = []
    original_update = AccelBoost.update

    def spy(boost, sm_, e2e, mpc, cruise):
      inputs.append(e2e)
      return original_update(boost, sm_, e2e, mpc, cruise)

    with mock.patch.object(AccelBoost, "update", spy):
      out = update(ext, sm)

    # First call is our extra layer on the raw target, last call is stock on the boosted target.
    self.assertAlmostEqual(inputs[0], E2E_ACCEL)
    self.assertAlmostEqual(inputs[-1], E2E_ACCEL + ext.extra_boost)
    self.assertAlmostEqual(out, inputs[-1] + ext._stock.total_boost)

  def test_extra_is_added_on_top_of_stock_boost(self):
    ext, sm = self._boost_to_max(log.LongitudinalPersonality.aggressive)
    sm['carState'].gasPressed = True
    out = update(ext, sm)
    extra = out - E2E_ACCEL - ext._stock.total_boost
    self.assertAlmostEqual(ext._stock.total_boost, ACCEL_BOOST_MAX)
    self.assertAlmostEqual(ext.total_boost, ACCEL_BOOST_MAX + ext.extra_boost)
    self.assertAlmostEqual(ext._stock.total_boost, ACCEL_BOOST_MAX)
    self.assertAlmostEqual(ext.extra_boost, ACCEL_BOOST_MAX * EXPECTED_SCALE[log.LongitudinalPersonality.aggressive])
    self.assertAlmostEqual(extra, ext.extra_boost)

  def test_sp_planner_wraps_assigned_stock_controller(self):
    planner = PlannerStub()
    stock = AccelBoost()
    planner.accel_boost = stock

    self.assertIsInstance(planner.accel_boost, AccelBoostExt)
    self.assertIs(planner.accel_boost._stock, stock)

  def test_wraps_existing_stock_controller(self):
    stock = AccelBoost()
    sm = FakeSubMaster()
    update(stock, sm)
    sm['carState'].gasPressed = True
    update(stock, sm)

    ext = AccelBoostExt(stock)
    self.assertIs(ext._stock, stock)
    self.assertAlmostEqual(ext.total_boost, stock.total_boost)

  def test_boost_bar_max_matches_profile_cap(self):
    for personality, scale in EXPECTED_SCALE.items():
      self.assertAlmostEqual(get_accel_boost_max(personality), ACCEL_BOOST_MAX * (1.0 + scale))

  def test_total_boost_is_stock_accumulated_plus_extra_applied(self):
    ext, sm = self._boost_to_max(log.LongitudinalPersonality.aggressive)
    sm['carState'].gasPressed = True
    update(ext, sm)
    self.assertAlmostEqual(ext.total_boost, ext._stock.total_boost + ext.extra_boost)

  def test_turning_toggle_off_restores_stock_only(self):
    ext, sm = self._boost_to_max(log.LongitudinalPersonality.aggressive)
    self.assertGreater(ext._extra.total_boost, 0.0)

    self.params.enabled = False
    sm['carState'].gasPressed = True
    # Params are re-read every PARAMS_UPDATE_PERIOD; the extra layer must clear on the next poll.
    for _ in range(int(PARAMS_UPDATE_PERIOD / DT_MDL) + 1):
      out = update(ext, sm)

    self.assertEqual(ext._extra.total_boost, 0.0)
    self.assertEqual(ext.extra_boost, 0.0)
    self.assertAlmostEqual(out, E2E_ACCEL + ext._stock.total_boost)

  def test_relaxing_following_distance_applies_immediately(self):
    ext, sm = self._boost_to_max(log.LongitudinalPersonality.aggressive)
    sm['selfdriveState'].personality = log.LongitudinalPersonality.relaxed
    sm['carState'].gasPressed = True
    applied = self._applied_extra(ext, sm)
    self.assertAlmostEqual(applied, ACCEL_BOOST_MAX * EXPECTED_SCALE[log.LongitudinalPersonality.relaxed])
