import unittest
from unittest.mock import Mock
from types import SimpleNamespace

from openpilot.cereal import custom, messaging
from openpilot.common.prefix import OpenpilotPrefix
from openpilot.selfdrive.selfdrived.selfdrived import SelfdriveD
from openpilot.selfdrive.selfdrived.events import Events, ET
from openpilot.sunnypilot.selfdrive.selfdrived.accelerator_events import AcceleratorEvents
from openpilot.sunnypilot.selfdrive.selfdrived.events import EVENTS_SP, EventsSP

EventName = custom.OnroadEventSP.EventName


class TestBigModelAvailability(unittest.TestCase):
  def setUp(self):
    prefix = OpenpilotPrefix()
    prefix.__enter__()
    self.addCleanup(prefix.__exit__, None, None, None)
    self.sm = messaging.SubMaster(['modelV2', 'modelDataV2SP'])
    self.events = Events()
    self.events_sp = EventsSP()
    self.accel = AcceleratorEvents()
    for service in self.sm.services:
      self.sm.data[service] = self.sm[service].as_builder()
      self.sm.seen[service] = True
      self.sm.alive[service] = True
      self.sm.valid[service] = True

  def update(self, available=False, big=False):
    self.sm['modelDataV2SP'].bigModelAvailable = available
    self.sm['modelV2'].big = big
    self.events.clear()
    self.events_sp.clear()
    self.accel.update(self.sm, False, self.events, self.events_sp)
    return EventName.bigModelAvailable in self.events_sp.names

  def test_late_boot_chimes_once_then_can_rejoin(self):
    self.assertFalse(self.update())
    self.assertTrue(self.update(available=True))
    for _ in range(100):
      self.assertFalse(self.update(available=True))
    self.assertFalse(self.update(big=True))
    self.assertFalse(self.update())  # fallback, waiting to reconnect
    self.assertTrue(self.update(available=True))

  def test_chestnut_and_old_messages_do_not_announce_availability(self):
    self.assertFalse(custom.ModelDataV2SP.new_message().bigModelAvailable)
    self.assertFalse(self.update())
    self.assertFalse(self.update(big=True))
    self.assertFalse(self.update())

  def test_running_big_suppresses_a_pending_status_from_previous_frame(self):
    self.assertFalse(self.update(available=True, big=True))

  def test_missing_invalid_or_stale_messages_never_announce(self):
    for service in ('modelV2', 'modelDataV2SP'):
      for check in ('seen', 'alive', 'valid'):
        with self.subTest(service=service, check=check):
          checks = getattr(self.sm, check)
          checks[service] = False
          self.assertFalse(self.update(available=True))
          checks[service] = True
    self.assertTrue(self.update(available=True))

  def test_stale_gap_does_not_repeat_chime(self):
    self.assertTrue(self.update(available=True))
    self.sm.alive['modelDataV2SP'] = False
    self.assertFalse(self.update())
    self.sm.alive['modelDataV2SP'] = True
    self.assertFalse(self.update(available=True))
    self.assertFalse(self.update())  # an explicit loss rearms it
    self.assertTrue(self.update(available=True))

  def test_notification_has_no_control_effect(self):
    alerts = EVENTS_SP[EventName.bigModelAvailable]
    self.assertEqual(set(alerts), {ET.PERMANENT})
    self.assertEqual(alerts[ET.PERMANENT].alert_text_2, 'Disengage to switch')

  def test_main_event_loop_checks_availability_and_preserves_ready(self):
    # Stop update_events at its normal initialization gate, after model events.
    sd = SelfdriveD.__new__(SelfdriveD)
    sd.sm = messaging.SubMaster(['modelV2', 'modelDataV2SP', 'controlsState', 'deviceState',
                                'lateralManeuverPlan', 'alertDebug'])
    for service in ('modelV2', 'modelDataV2SP'):
      sd.sm.data[service] = sd.sm[service].as_builder()
      sd.sm.seen[service] = sd.sm.alive[service] = sd.sm.valid[service] = True
    sd.events = Events()
    sd.events_sp = EventsSP()
    sd.accelerator_events = AcceleratorEvents()
    sd.params = Mock()
    sd.params.get_bool.return_value = False
    sd.params.get.return_value = None
    sd.big_model_loading = sd.big_model_running = sd.big_model_active = sd.big_model_failed = False
    sd.big_model_ready_t = 0.
    sd.enabled = True
    sd.initialized = False
    sd.startup_event = None
    sd.sm['modelDataV2SP'].acceleratorState = 'joining'
    sd.sm['modelDataV2SP'].bigModelAvailable = True
    sd.update_events(SimpleNamespace())
    self.assertIn(EventName.bigModelAvailable, sd.events_sp.names)
    self.assertNotIn(EventName.bigModelReady, sd.events_sp.names)
    sd.sm['modelDataV2SP'].acceleratorState = 'running'
    sd.sm['modelDataV2SP'].bigModelAvailable = False
    sd.sm['modelV2'].big = True
    sd.update_events(SimpleNamespace())
    self.assertIn(EventName.bigModelReady, sd.events_sp.names)
    self.assertNotIn(EventName.bigModelAvailable, sd.events_sp.names)
    sd.update_events(SimpleNamespace())
    self.assertNotIn(EventName.bigModelReady, sd.events_sp.names)
