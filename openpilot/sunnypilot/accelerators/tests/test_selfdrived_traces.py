"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Every event a big model raises, in order, for three drives.

Asserted as the whole list at every step, native and sunnypilot together,
because the failures that reached the car were extra events: a "Big Model
Ready" chime after a failed load, and a jetlink drive raising the native
bigModelFailed beside the link-lost alert.

Three traces, all through the real SelfdriveD.update_events with the
accelerator adapter in place:

  (a) a chestnut that loads:   loading, then one chime on the first big frame
  (b) a chestnut that fails:   loading, one failure, and never a chime
  (c) a jetlink that joins:    loading while modelV2 is held back, one chime
                               when it promotes, and on a fall while engaged
                               the native bigModelFailed beside bigModelLinkLost
                               on every tick until the driver disengages

The pair in (c) is deliberate. The main state machine consumes native events
only and cancels a soft disable the tick its event goes away, so a one-tick
sunnypilot event never disabled anything and the car stayed engaged on a 5 m
plan. bigModelLinkLost is what MADS reads and carries the guidance.

update_events runs as far as its initialization gate, past the big model
block and the adapter call and short of everything needing a car.
"""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from openpilot.cereal import custom, messaging
from openpilot.selfdrive.selfdrived.events import EVENT_NAME, Events
from openpilot.selfdrive.selfdrived.selfdrived import SelfdriveD
from openpilot.sunnypilot.selfdrive.selfdrived.accelerator_events import AcceleratorEvents
from openpilot.sunnypilot.selfdrive.selfdrived.events import EVENT_NAME_SP, EventsSP

AcceleratorState = custom.ModelDataV2SP.AcceleratorState

# added at the gate on every step, so it is in every expected list rather
# than filtered out
INIT = 'selfdriveInitializing'

SERVICES = ['modelV2', 'modelDataV2SP', 'controlsState', 'deviceState', 'lateralManeuverPlan', 'alertDebug']


def make_selfdrived(chestnut_present: bool, enabled: bool) -> SelfdriveD:
  """A SelfdriveD with no processes, no live params and no car.

  The same fixture exists as setUp methods under two selfdrived test trees;
  importing a TestCase to reuse one would re-run its tests here.
  """
  sd = SelfdriveD.__new__(SelfdriveD)
  sd.sm = messaging.SubMaster(SERVICES)
  for service in ('modelV2', 'modelDataV2SP', 'deviceState'):
    sd.sm.data[service] = sd.sm[service].as_builder()
    sd.sm.valid[service] = True
  sd.sm.seen['deviceState'] = sd.sm.alive['deviceState'] = True
  sd.sm['deviceState'].chestnutPresent = chestnut_present
  sd.events = Events()
  sd.events_sp = EventsSP()
  sd.accelerator_events = AcceleratorEvents()
  sd.params = Mock()
  sd.big_model_loading = sd.big_model_active = sd.big_model_failed = sd.big_model_running = False
  sd.big_model_ready_t = 0.
  sd.enabled = enabled
  sd.initialized = False
  sd.startup_event = None
  return sd


class TraceTest(unittest.TestCase):
  def step(self, loading=False, active=None, big=False, alive=True,
           state=AcceleratorState.none, available=False) -> tuple[list[str], list[str]]:
    """One update_events, and everything it raised."""
    sd = self.sd
    sd.params.get_bool.return_value = loading
    sd.params.get.return_value = active
    # modelV2 and modelDataV2SP are published together; the native block reads
    # a board as failed only once a modelV2 it had has gone away
    for service in ('modelV2', 'modelDataV2SP'):
      sd.sm.alive[service] = alive
      sd.sm.seen[service] = sd.sm.seen[service] or alive
    sd.sm['modelV2'].big = big
    sd.sm['modelDataV2SP'].acceleratorState = state
    sd.sm['modelDataV2SP'].bigModelAvailable = available
    sd.update_events(SimpleNamespace())
    return ([EVENT_NAME[n] for n in sd.events.names], [EVENT_NAME_SP[n] for n in sd.events_sp.names])


class ChestnutTraces(TraceTest):
  """comma's board, which is loaded before modelV2 exists and never rejoins."""

  def setUp(self):
    self.sd = make_selfdrived(chestnut_present=True, enabled=True)

  def test_trace_a_a_load_that_works_chimes_once(self):
    # modeld holds modelV2 back for the load, so the driver is kept out.
    self.assertEqual(self.step(loading=True, alive=False), ([INIT, 'bigModelLoading'], []))
    # ChestnutLoading clears, but nothing big has been published yet.
    self.assertEqual(self.step(loading=False, active=True, alive=False), ([INIT], []))
    # The first big frame, and the only chime in the drive.
    self.assertEqual(self.step(loading=False, active=True, big=True), ([INIT], ['bigModelReady']))
    for _ in range(10):
      self.assertEqual(self.step(loading=False, active=True, big=True), ([INIT], []))

  def test_trace_b_a_load_that_fails_never_chimes(self):
    self.assertEqual(self.step(loading=True, alive=False), ([INIT, 'bigModelLoading'], []))
    # modeld writes ChestnutActive=False first: the load timed out or threw.
    self.assertEqual(self.step(loading=True, active=False, alive=False), ([INIT, 'bigModelLoading', 'bigModelFailed'], []))
    # and clears ChestnutLoading once the small model is up; that second edge
    # used to chime "Big Model Ready" over "Big Model Failed"
    self.assertEqual(self.step(loading=False, active=False), ([INIT], []))
    for _ in range(10):
      self.assertEqual(self.step(loading=False, active=False), ([INIT], []))

  def test_a_board_that_falls_back_mid_drive_is_the_native_failure_alone(self):
    self.assertEqual(self.step(loading=False, active=True, big=True), ([INIT], ['bigModelReady']))
    # The adapter must not double this: acceleratorState is none for a board.
    self.assertEqual(self.step(loading=False, active=False, big=False), ([INIT, 'bigModelFailed'], []))


class JetlinkTrace(TraceTest):
  """A Jetson on its own power: it joins onto a modelV2 the small model owns.

  Nothing in this trace writes ChestnutLoading or ChestnutActive - the joining
  state stopped doing that - so the native block sees a device with no board
  and stays silent for the whole drive. Everything said is said by the
  adapter, from modelV2.big and the additive modelDataV2SP fields.
  """

  def setUp(self):
    self.sd = make_selfdrived(chestnut_present=False, enabled=True)

  def test_trace_c_join_promote_and_lose_the_link(self):
    # Joining before camerad and modeld have a frame out: the same block on
    # the driver as a chestnut load, and for the same reason.
    self.assertEqual(self.step(state=AcceleratorState.joining, alive=False), ([INIT, 'bigModelLoading'], []))
    # modelV2 starts publishing on the small model. The join carries on in the
    # background and stops blocking the moment there is something to drive on.
    self.assertEqual(self.step(state=AcceleratorState.joining), ([INIT], []))
    # The promotion gate: a big model is there, waiting for a disengagement.
    self.assertEqual(self.step(state=AcceleratorState.joining, available=True), ([INIT], ['bigModelAvailable']))
    self.assertEqual(self.step(state=AcceleratorState.joining, available=True), ([INIT], []))
    # It swaps. One chime, from modelV2.big and nothing else.
    self.assertEqual(self.step(state=AcceleratorState.running, big=True), ([INIT], ['bigModelReady']))
    for _ in range(10):
      self.assertEqual(self.step(state=AcceleratorState.running, big=True), ([INIT], []))
    # the link drops while engaged: both events on every tick, both from the
    # adapter. The native one walks the main state machine through its 3 s
    # soft disable; a single tick of either would be cancelled the next
    for _ in range(10):
      self.assertEqual(self.step(state=AcceleratorState.retrying), ([INIT, 'bigModelFailed'], ['bigModelLinkLost']))
    # The soft disable lands and the driver is out. Nothing more is said.
    self.sd.enabled = False
    for _ in range(10):
      self.assertEqual(self.step(state=AcceleratorState.retrying), ([INIT], []))
    # And it comes back, which a chestnut never does.
    self.assertEqual(self.step(state=AcceleratorState.running, big=True), ([INIT], ['bigModelReady']))
    self.sd.enabled = True
    self.assertEqual(self.step(state=AcceleratorState.running, big=True), ([INIT], []))

  def test_a_link_that_drops_while_disengaged_says_nothing(self):
    self.sd.enabled = False
    self.assertEqual(self.step(state=AcceleratorState.running, big=True), ([INIT], ['bigModelReady']))
    # the small model carries on; engaging afterwards does not replay a fall
    # the driver never felt
    self.assertEqual(self.step(state=AcceleratorState.retrying), ([INIT], []))
    self.sd.enabled = True
    self.assertEqual(self.step(state=AcceleratorState.retrying), ([INIT], []))

  def test_nothing_is_said_on_a_device_with_no_accelerator_at_all(self):
    for _ in range(10):
      self.assertEqual(self.step(), ([INIT], []))


if __name__ == '__main__':
  unittest.main()
