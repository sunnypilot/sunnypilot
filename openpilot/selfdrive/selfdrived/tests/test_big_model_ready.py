import unittest
from unittest.mock import Mock
from types import SimpleNamespace

from openpilot.cereal import custom, messaging
from openpilot.common.prefix import OpenpilotPrefix
from openpilot.selfdrive.selfdrived.events import Events, EventName
from openpilot.selfdrive.selfdrived.selfdrived import SelfdriveD
from openpilot.sunnypilot.selfdrive.selfdrived.accelerator_events import AcceleratorEvents
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP

EventNameSP = custom.OnroadEventSP.EventName


class TestBigModelReady(unittest.TestCase):
  def setUp(self):
    prefix = OpenpilotPrefix()
    prefix.__enter__()
    self.addCleanup(prefix.__exit__, None, None, None)
    # Drive the real update_events up to its initialization gate, without processes or live Params.
    sd = SelfdriveD.__new__(SelfdriveD)
    sd.sm = messaging.SubMaster(['modelV2', 'modelDataV2SP', 'controlsState', 'deviceState', 'lateralManeuverPlan', 'alertDebug'])
    sd.sm.data['modelV2'] = sd.sm['modelV2'].as_builder()
    sd.sm.seen['modelV2'] = sd.sm.alive['modelV2'] = sd.sm.valid['modelV2'] = True
    sd.events = Events()
    sd.events_sp = EventsSP()
    sd.accelerator_events = AcceleratorEvents()
    sd.params = Mock()
    sd.big_model_loading = sd.big_model_active = sd.big_model_failed = sd.big_model_running = False
    sd.big_model_ready_t = 0.
    sd.enabled = False
    sd.initialized = False
    sd.startup_event = None
    self.sd = sd

  def step(self, loading, active=None, big=False, alive=True):
    sd = self.sd
    sd.params.get_bool.return_value = loading
    sd.params.get.return_value = active
    sd.sm.alive['modelV2'] = alive
    sd.sm['modelV2'].big = big
    sd.update_events(SimpleNamespace())
    return EventNameSP.bigModelReady in sd.events_sp.names, EventName.bigModelFailed in sd.events.names

  def test_failed_load_never_chimes_ready(self):
    self.assertEqual(self.step(loading=True), (False, False))
    self.assertEqual(self.step(loading=True, active=False), (False, True))
    self.assertEqual(self.step(loading=False, active=False), (False, False))
    for _ in range(10):
      self.assertEqual(self.step(loading=False, active=False), (False, False))

  def test_good_load_chimes_once_on_first_big_frame(self):
    self.assertEqual(self.step(loading=True), (False, False))
    self.assertEqual(self.step(loading=False), (False, False))
    self.assertEqual(self.step(loading=False, active=True, big=True), (True, False))
    for _ in range(10):
      self.assertEqual(self.step(loading=False, active=True, big=True), (False, False))

  def test_big_frame_from_a_dead_socket_does_not_chime(self):
    self.assertEqual(self.step(loading=False, big=True, alive=False), (False, False))
    self.assertEqual(self.step(loading=False, big=True, alive=False), (False, False))

  def test_rearms_after_a_fall_back_to_the_small_model(self):
    self.assertEqual(self.step(loading=False, active=True, big=True), (True, False))
    self.assertEqual(self.step(loading=False, active=True, big=False), (False, False))
    self.assertEqual(self.step(loading=False, active=True, big=True), (True, False))
    self.assertEqual(self.step(loading=False, active=True, big=True), (False, False))
