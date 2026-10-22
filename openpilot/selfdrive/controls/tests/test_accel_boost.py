from types import SimpleNamespace

from openpilot.cereal import log
from openpilot.common.realtime import DT_MDL
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.controls.lib.accel_boost import (
  AccelBoost, ACCEL_BOOST_MAX, ACCEL_BOOST_PER_OVERRIDE, ACCEL_BOOST_RATE
)

E2E_ACCEL = 0.5
PLANNER_ACCEL = 2.0
RATE_PER_STEP = ACCEL_BOOST_RATE * DT_MDL


class FakeSubMaster:
  def __init__(self, enabled=True, gas_pressed=False, v_ego=15.0,
               personality=log.LongitudinalPersonality.standard):
    self._messages = {
      'selfdriveState': SimpleNamespace(enabled=enabled, personality=personality),
      'carState': SimpleNamespace(gasPressed=gas_pressed, vEgo=v_ego),
    }

  def __getitem__(self, key):
    return self._messages[key]


def run_boost(boost, sm, steps=1):
  out = E2E_ACCEL
  for _ in range(steps):
    out = boost.update(sm, E2E_ACCEL, PLANNER_ACCEL, PLANNER_ACCEL)
  return out


class TestAccelBoost(OpenpilotTestCase):
  def _boost_to_max(self):
    boost = AccelBoost()
    sm = FakeSubMaster()
    steps = round(ACCEL_BOOST_PER_OVERRIDE / RATE_PER_STEP)
    # Eligibility is latched on a frame without gas, then applied on the next override.
    run_boost(boost, sm)
    for _ in range(10):
      sm['carState'].gasPressed = True
      run_boost(boost, sm, steps)
      sm['carState'].gasPressed = False
      run_boost(boost, sm)
    return boost

  def test_no_boost_without_gas(self):
    boost = AccelBoost()
    sm = FakeSubMaster(gas_pressed=False)
    out = run_boost(boost, sm)
    self.assertEqual(boost.total_boost, 0.0)
    self.assertAlmostEqual(out, E2E_ACCEL)

  def test_boost_requires_e2e_to_be_limiting(self):
    boost = AccelBoost()
    sm = FakeSubMaster(gas_pressed=False)
    # Eligibility is latched before the override, so keep the e2e plan at the planner limit here.
    boost.update(sm, E2E_ACCEL, E2E_ACCEL, E2E_ACCEL)
    sm['carState'].gasPressed = True
    for _ in range(10):
      boost.update(sm, E2E_ACCEL, E2E_ACCEL, E2E_ACCEL)
    self.assertEqual(boost.total_boost, 0.0)

  def test_per_override_cap(self):
    boost = AccelBoost()
    sm = FakeSubMaster(gas_pressed=False)
    run_boost(boost, sm)
    sm['carState'].gasPressed = True
    run_boost(boost, sm, 1000)
    self.assertAlmostEqual(boost.total_boost, ACCEL_BOOST_PER_OVERRIDE)

  def test_max_boost(self):
    boost = self._boost_to_max()
    self.assertAlmostEqual(boost.total_boost, ACCEL_BOOST_MAX)

  def test_boost_is_applied_to_e2e_accel(self):
    boost = self._boost_to_max()
    sm = FakeSubMaster(gas_pressed=True)
    out = run_boost(boost, sm)
    self.assertAlmostEqual(out, E2E_ACCEL + boost.total_boost)

  def test_boost_does_not_depend_on_following_distance(self):
    totals = []
    for personality in (log.LongitudinalPersonality.relaxed,
                        log.LongitudinalPersonality.standard,
                        log.LongitudinalPersonality.aggressive):
      boost = AccelBoost()
      sm = FakeSubMaster(personality=personality)
      steps = round(ACCEL_BOOST_PER_OVERRIDE / RATE_PER_STEP)
      run_boost(boost, sm)
      for _ in range(10):
        sm['carState'].gasPressed = True
        run_boost(boost, sm, steps)
        sm['carState'].gasPressed = False
        run_boost(boost, sm)
      totals.append(boost.total_boost)

    self.assertEqual(len(totals), 3)
    for total in totals:
      self.assertAlmostEqual(total, ACCEL_BOOST_MAX)
