import pytest
from unittest.mock import MagicMock

from cereal import custom
from openpilot.common.realtime import DT_CTRL
from openpilot.sunnypilot.mads.state import StateMachine, SOFT_DISABLE_TIME
from openpilot.selfdrive.selfdrived.events import Events, ET, EVENTS, NormalPermanentAlert

State = custom.SelfdriveStateSP.ModularAssistiveDrivingSystem.ModularAssistiveDrivingSystemState

# The event types that maintain the current state
MAINTAIN_STATES = {State.enabled: (None,), State.disabled: (None,), State.softDisabling: (ET.SOFT_DISABLE,),
                   State.paused: (None,), State.overriding: (ET.OVERRIDE_LATERAL,)}
ALL_STATES = (State.schema.enumerants.values())
# The event types checked in DISABLED section of state machine
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


class TestMADSStateMachine:
  @pytest.fixture(autouse=True)
  def setup_method(self):
    self.mads = MockMADS()
    self.events = Events()
    self.state_machine = StateMachine(self.mads)
    self.mads.selfdrive.state_machine.soft_disable_timer = int(SOFT_DISABLE_TIME / DT_CTRL)

  def test_immediate_disable(self):
    for state in ALL_STATES:
      for et in MAINTAIN_STATES[state]:
        self.events.add(make_event([et, ET.IMMEDIATE_DISABLE]))
        self.state_machine.state = state
        self.state_machine.update(self.events)
        assert State.disabled == self.state_machine.state
        self.events.clear()

  def test_user_disable(self):
    for state in ALL_STATES:
      for et in MAINTAIN_STATES[state]:
        self.events.add(make_event([et, ET.USER_DISABLE]))
        self.state_machine.state = state
        self.state_machine.update(self.events)
        assert self.state_machine.state in (State.disabled, State.paused)
        self.events.clear()

  def test_soft_disable(self):
    for state in ALL_STATES:
      if state == State.paused:  # paused considers USER_DISABLE instead
        continue
      for et in MAINTAIN_STATES[state]:
        self.events.add(make_event([et, ET.SOFT_DISABLE]))
        self.state_machine.state = state
        self.state_machine.update(self.events)
        assert self.state_machine.state == State.disabled if state == State.disabled else State.softDisabling
        self.events.clear()

  def test_soft_disable_timer(self):
    self.state_machine.state = State.enabled
    self.events.add(make_event([ET.SOFT_DISABLE]))
    self.state_machine.update(self.events)
    for _ in range(int(SOFT_DISABLE_TIME / DT_CTRL)):
      assert self.state_machine.state == State.softDisabling
      self.mads.selfdrive.state_machine.soft_disable_timer -= 1
      self.state_machine.update(self.events)

    assert self.state_machine.state == State.disabled

  def test_no_entry(self):
    for et in ENABLE_EVENT_TYPES:
      self.events.add(make_event([ET.NO_ENTRY, et]))
      self.state_machine.update(self.events)
      assert self.state_machine.state == State.disabled
      self.events.clear()

  def test_no_entry_paused(self):
    self.state_machine.state = State.paused
    self.events.add(make_event([ET.NO_ENTRY]))
    self.state_machine.update(self.events)
    assert self.state_machine.state == State.paused

  def test_maintain_states(self):
    for state in ALL_STATES:
      for et in MAINTAIN_STATES[state]:
        self.state_machine.state = state
        if et is not None:
          self.events.add(make_event([et]))
        self.state_machine.update(self.events)
        assert self.state_machine.state == state
        self.events.clear()

  def test_override_lateral(self):
    self.state_machine.state = State.enabled
    self.events.add(make_event([ET.OVERRIDE_LATERAL]))
    self.state_machine.update(self.events)
    assert self.state_machine.state == State.overriding

  def test_paused_to_enabled(self):
    self.state_machine.state = State.paused
    self.events.add(make_event([ET.ENABLE]))
    self.state_machine.update(self.events)
    assert self.state_machine.state == State.enabled

  def test_mads_unavailable(self):
    self.mads.available = False
    for state in ALL_STATES:
      self.state_machine.state = state
      enabled, active = self.state_machine.update(self.events)
      assert not enabled
      assert not active
