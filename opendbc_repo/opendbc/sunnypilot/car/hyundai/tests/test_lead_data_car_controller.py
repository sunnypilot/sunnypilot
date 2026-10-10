import unittest
from enum import IntFlag

from opendbc.sunnypilot.car.hyundai.lead_data_ext import LeadDataCarController, CanLeadData, CanFdLeadData
from opendbc.car import structs
from opendbc.car.hyundai.values import HyundaiFlags


def make_carparams(flags: IntFlag = HyundaiFlags.LEGACY):
  cp = structs.CarParams()
  cp.carFingerprint = "HYUNDAI_SONATA"
  cp.flags = flags.value
  return cp


def make_carcontrolsp(leadDistance=10.0, leadRelSpeed=0.0, leadVisible=True):
  c = structs.CarControlSP()
  c.leadOne.dRel = leadDistance
  c.leadOne.vRel = leadRelSpeed
  c.leadOne.status = leadVisible
  return c


class TestLeadDataCarController(unittest.TestCase):
  def test_update_object_gap(self):
    ctrl = LeadDataCarController(make_carparams())
    # Initial value should be 0
    self.assertEqual(ctrl.object_gap, 0)

    # Set to 15 (should become 2 after hysteresis)
    for _ in range(ctrl.LEAD_HYSTERESIS_FRAMES):
      ctrl._update_object_gap(15)
    self.assertEqual(ctrl.object_gap, 2)

    # Set to 22 (should become 3 after hysteresis)
    for _ in range(ctrl.LEAD_HYSTERESIS_FRAMES):
      ctrl._update_object_gap(22)
    self.assertEqual(ctrl.object_gap, 3)

    # Set to 0 (should become 0 after hysteresis)
    for _ in range(ctrl.LEAD_HYSTERESIS_FRAMES):
      ctrl._update_object_gap(0)
    self.assertEqual(ctrl.object_gap, 0)

  def test_update_lead_visible_hysteresis(self):
    ctrl = LeadDataCarController(make_carparams())
    ctrl._update_lead_visible_hysteresis(True)
    self.assertIsInstance(ctrl.lead_visible, bool)
    ctrl._update_lead_visible_hysteresis(False)
    self.assertIsInstance(ctrl.lead_visible, bool)

  def test_update(self):
    ctrl = LeadDataCarController(make_carparams())
    sp = make_carcontrolsp(leadDistance=25, leadRelSpeed=-0.5, leadVisible=True)
    ctrl.update(sp)
    self.assertEqual(ctrl.lead_distance, 25)
    self.assertEqual(ctrl.lead_rel_speed, -0.5)
    self.assertIsInstance(ctrl.lead_visible, bool)

  def test_lead_data_can(self):
    ctrl = LeadDataCarController(make_carparams())
    ctrl.object_gap = 1
    ctrl.lead_distance = 10
    ctrl.lead_rel_speed = -0.3
    ctrl.lead_visible = True
    ld = ctrl.lead_data
    self.assertIsInstance(ld, CanLeadData)
    self.assertEqual(ld.object_rel_gap, 2)

  def test_lead_data_canfd(self):
    ctrl = LeadDataCarController(make_carparams(HyundaiFlags.CANFD))
    ctrl.object_gap = 1
    ctrl.lead_distance = 10
    ctrl.lead_rel_speed = 1.0
    ctrl.lead_visible = True
    ld = ctrl.lead_data
    self.assertIsInstance(ld, CanFdLeadData)
    self.assertEqual(ld.object_rel_gap, 1)
