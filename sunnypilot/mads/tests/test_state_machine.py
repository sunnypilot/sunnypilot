import pytest
from unittest.mock import MagicMock
from cereal import car, custom
from openpilot.selfdrive.selfdrived.events import Events, ET, EVENTS, NormalPermanentAlert
from openpilot.sunnypilot.mads.state import Disabled, Paused, Enabled, SoftDisabling, Overriding
from openpilot.selfdrive.selfdrived.state import SOFT_DISABLE_TIME
from openpilot.common.realtime import DT_CTRL

State = custom.SelfdriveStateSP.ModifiedAssistDrivingSystem.ModifiedAssistDrivingSystemState
EventName = car.OnroadEvent.EventName

# The event types that maintain the current state
MAINTAIN_STATES = {
  State.disabled: (None,),
  State.paused: (None,),
  State.enabled: (None,),
  State.softDisabling: (ET.SOFT_DISABLE,),
  State.overriding: (ET.OVERRIDE_LATERAL,)
}
ALL_STATES = tuple(State.schema.enumerants.values())
ENABLE_EVENT_TYPES = (ET.ENABLE, ET.OVERRIDE_LATERAL)


def make_event(event_types):
  event = {}
  for ev in event_types:
    event[ev] = NormalPermanentAlert("alert")
  EVENTS[0] = event
  return 0


class MockMADS:
  def __init__(self):
    self.selfdrive = MagicMock()
    self.selfdrive.state_machine = MagicMock()
    self.selfdrive.active = False
    self.available = True
    self.current_state = State.disabled


class TestMADSStateMachine:
  @pytest.fixture(autouse=True)
  def setup_method(self):
    self.mads = MockMADS()
    self.events = Events()
    self.state_machines = {
      State.disabled: Disabled(self.mads),
      State.paused: Paused(self.mads),
      State.enabled: Enabled(self.mads),
      State.softDisabling: SoftDisabling(self.mads),
      State.overriding: Overriding(self.mads),
    }

  def test_immediate_disable(self):
    for state in ALL_STATES:
      for et in MAINTAIN_STATES[state]:
        self.events.add(make_event([et, ET.IMMEDIATE_DISABLE]))
        new_state, _, _ = self.state_machines[state](self.events)
        assert State.disabled == new_state
        self.events.clear()

  def test_user_disable(self):
    for state in ALL_STATES:
      for et in MAINTAIN_STATES[state]:
        self.events.add(make_event([et, ET.USER_DISABLE]))
        new_state, _, _ = self.state_machines[state](self.events)
        assert new_state in (State.disabled, State.paused)
        self.events.clear()

  def test_soft_disable(self):
    for state in ALL_STATES:
      if state == State.paused:  # paused considers USER_DISABLE instead
        continue
      for et in MAINTAIN_STATES[state]:
        self.events.add(make_event([et, ET.SOFT_DISABLE]))
        new_state, _, _ = self.state_machines[state](self.events)
        assert new_state == State.disabled if state == State.disabled else State.softDisabling
        self.events.clear()

  #def test_soft_disable_timer(self):
  #  state_machine = self.state_machines[State.enabled]
  #  self.events.add(make_event([ET.SOFT_DISABLE]))
  #  new_state, _, _ = state_machine(self.events)
  #  assert new_state == State.softDisabling

  #  # Simulate the passage of time
  #  state_machine.ss_state_machine.soft_disable_timer = 0
  #  new_state, _, _ = state_machine(self.events)
  #  assert new_state == State.disabled

  def test_no_entry(self):
    for et in ENABLE_EVENT_TYPES:
      self.events.add(make_event([ET.NO_ENTRY, et]))
      new_state, _, _ = self.state_machines[State.disabled](self.events)
      assert new_state == State.disabled
      self.events.clear()

  def test_maintain_states(self):
    for state in ALL_STATES:
      for et in MAINTAIN_STATES[state]:
        self.mads.current_state = state
        self.events.add(make_event([et]))
        new_state, _, _ = self.state_machines[state](self.events)
        assert new_state == state
        self.events.clear()

  def test_override_lateral(self):
    self.events.add(make_event([ET.OVERRIDE_LATERAL]))
    new_state, _, _ = self.state_machines[State.enabled](self.events)
    assert new_state == State.overriding

  def test_mads_unavailable(self):
    self.mads.available = False
    for state in ALL_STATES:
      _, enabled, active = self.state_machines[state](self.events)
      assert not enabled
      assert not active
