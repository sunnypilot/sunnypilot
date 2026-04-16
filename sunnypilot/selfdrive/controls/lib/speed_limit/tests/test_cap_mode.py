"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from cereal import car, custom
from openpilot.common.realtime import DT_MDL
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.speed_limit_assist import SpeedLimitAssist, \
  SpeedLimitAssistState
from openpilot.sunnypilot.selfdrive.selfdrived.events import EventsSP


def make_mock_car_params(mocker, pcm_op_long: bool = True) -> car.CarParams:
  """Create a minimal CarParams mock with pcm_op_long setting."""
  cp = mocker.MagicMock(spec=car.CarParams)
  cp.openpilotLongitudinalControl = pcm_op_long
  cp.pcmCruise = pcm_op_long
  cp.brand = "generic"
  return cp


def make_mock_car_params_sp(mocker) -> custom.CarParamsSP:
  """Create a minimal CarParamsSP mock."""
  cp_sp = mocker.MagicMock(spec=custom.CarParamsSP)
  return cp_sp


def get_event_name_sp():
  """Get EventNameSP enum."""
  return custom.OnroadEventSP.EventName


def make_sla_factory(mocker, pcm_op_long: bool = True) -> SpeedLimitAssist:
  """Factory: create a SpeedLimitAssist instance with mocked params."""
  cp = make_mock_car_params(mocker, pcm_op_long)
  cp_sp = make_mock_car_params_sp(mocker)

  mock_params = mocker.MagicMock()
  mock_params.get_bool.return_value = True
  mock_params.get.return_value = True

  mocker.patch("openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.speed_limit_assist.Params",
               return_value=mock_params)
  mocker.patch("openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.helpers.set_speed_limit_assist_availability")
  mocker.patch("openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.helpers.get_min_cap_floor", return_value=5.0)
  sla = SpeedLimitAssist(cp, cp_sp)
  return sla


class TestBug1OverrideNoOscillation:
  """Override falling edge arms suspend timer, preventing oscillation."""

  def test_sustained_override_stays_disabled(self, mocker):
    """5s sustained override: state never enters capping."""
    sla = make_sla_factory(mocker, pcm_op_long=True)

    sla.long_enabled = True
    sla.enabled = True
    sla._has_speed_limit = True
    sla._speed_limit_final_last = 25.0
    sla._min_cap_floor = 5.0
    sla.state = SpeedLimitAssistState.capping
    sla._state_prev = SpeedLimitAssistState.capping
    sla._target_cap = 25.0
    events_sp = EventsSP()

    num_ticks = int(5.0 / DT_MDL)
    for _ in range(num_ticks):
      sla.long_override = True
      sla.update_state_machine_cap(events_sp)

      assert (sla.state != SpeedLimitAssistState.capping), "State entered capping during sustained override"

    assert sla.state == SpeedLimitAssistState.disabled

  def test_override_release_enters_capping_after_guard(self, mocker):
    """Release override: state enters capping after guard period."""
    sla = make_sla_factory(mocker, pcm_op_long=True)

    sla.long_enabled = True
    sla.enabled = True
    sla._has_speed_limit = True
    sla._speed_limit_final_last = 25.0
    sla._min_cap_floor = 5.0
    sla.state = SpeedLimitAssistState.disabled
    sla._state_prev = SpeedLimitAssistState.disabled
    sla._target_cap = 25.0
    sla._was_cap_suspended = True
    sla._override_active_last = True
    sla.long_override = True
    events_sp = EventsSP()

    sla.update_state_machine_cap(events_sp)
    sla.long_override = False

    guard_ticks = int(1.0 / DT_MDL)
    for i in range(guard_ticks + 1):
      sla.update_state_machine_cap(events_sp)
      if i < guard_ticks:
        assert sla.state == SpeedLimitAssistState.disabled

    assert sla.state == SpeedLimitAssistState.capping


class TestBug2TargetCapPreserved:
  """Target cap preserved across override-release cycles."""

  def test_target_cap_preserved_on_override_suspension(self, mocker):
    """Override pulse: _target_cap preserved, not reset to new limit."""
    sla = make_sla_factory(mocker, pcm_op_long=True)

    sla.long_enabled = True
    sla.enabled = True
    sla._has_speed_limit = True
    sla._speed_limit_final_last = 25.0
    sla._min_cap_floor = 5.0
    sla.state = SpeedLimitAssistState.capping
    sla._state_prev = SpeedLimitAssistState.capping
    sla._target_cap = 25.0
    sla._cap_change_timer = 0
    events_sp = EventsSP()

    sla._speed_limit_final_last = 30.0

    sla.long_override = True
    sla.update_state_machine_cap(events_sp)
    assert sla.state == SpeedLimitAssistState.disabled
    assert sla._was_cap_suspended is True

    sla.long_override = False
    guard_ticks = int(1.0 / DT_MDL)
    for _ in range(guard_ticks + 1):
      sla.update_state_machine_cap(events_sp)

    assert sla.state == SpeedLimitAssistState.capping
    assert sla._target_cap == 25.0, f"Expected 25.0, got {sla._target_cap}"


class TestBug3AccelPressedWired:
  """Accel_pressed parameter wired to sla.update()."""

  def test_accel_pressed_parameter_received(self, mocker):
    """sla.update() receives accel_pressed=True."""
    sla = make_sla_factory(mocker, pcm_op_long=True)

    sla.long_enabled = True
    sla.enabled = True
    sla.v_ego = 20.0
    sla.a_ego = 0.0
    sla.v_cruise_cluster = 30.0
    events_sp = EventsSP()

    sla.update(
      long_enabled=True,
      long_override=False,
      v_ego=20.0,
      a_ego=0.0,
      v_cruise_cluster=30.0,
      speed_limit=30.0,
      speed_limit_final_last=30.0,
      has_speed_limit=True,
      distance=100.0,
      events_sp=events_sp,
      accel_pressed=True,
    )

    assert sla._accel_pressed is True

  def test_accel_pressed_false_by_default(self, mocker):
    """sla.update() with accel_pressed=False (default)."""
    sla = make_sla_factory(mocker, pcm_op_long=True)

    events_sp = EventsSP()

    sla.update(
      long_enabled=True,
      long_override=False,
      v_ego=20.0,
      a_ego=0.0,
      v_cruise_cluster=30.0,
      speed_limit=30.0,
      speed_limit_final_last=30.0,
      has_speed_limit=True,
      distance=100.0,
      events_sp=events_sp,
    )

    assert sla._accel_pressed is False


class TestBug4NoAudioCueOnOverrideReentry:
  """Audio cue suppressed on override-release re-entry."""

  def test_cue_fires_on_cold_entry(self, mocker):
    """Fresh engagement: audio cue fires exactly once."""
    sla = make_sla_factory(mocker, pcm_op_long=True)

    sla.long_enabled = True
    sla.enabled = True
    sla._has_speed_limit = True
    sla._speed_limit_final_last = 25.0
    sla._min_cap_floor = 5.0
    sla.state = SpeedLimitAssistState.disabled
    sla._state_prev = SpeedLimitAssistState.disabled
    sla._was_cap_suspended = False
    sla._cap_audio_cue_enabled = True
    events_sp = EventsSP()

    sla.update_state_machine_cap(events_sp)

    assert sla.state == SpeedLimitAssistState.capping
    assert sla._cap_audio_cue_fired is True
    event_name_sp = get_event_name_sp()
    assert event_name_sp.speedLimitCapActive in events_sp.events, "Audio cue event not fired"

  def test_no_cue_on_override_reentry(self, mocker):
    """Override-release re-entry: audio cue NOT fired."""
    sla = make_sla_factory(mocker, pcm_op_long=True)

    sla.long_enabled = True
    sla.enabled = True
    sla._has_speed_limit = True
    sla._speed_limit_final_last = 25.0
    sla._min_cap_floor = 5.0
    sla.state = SpeedLimitAssistState.disabled
    sla._state_prev = SpeedLimitAssistState.capping
    sla._target_cap = 25.0
    sla._was_cap_suspended = True
    sla._override_active_last = False
    sla._cap_audio_cue_enabled = True
    sla._cap_audio_cue_fired = True
    events_sp = EventsSP()

    sla._cap_suspended_timer = int(1.0 / DT_MDL)
    guard_ticks = int(1.0 / DT_MDL) + 1
    for _ in range(guard_ticks):
      sla.update_state_machine_cap(events_sp)
      sla._state_prev = sla.state

    assert sla.state == SpeedLimitAssistState.capping
    event_name_sp = get_event_name_sp()
    assert (event_name_sp.speedLimitCapActive not in events_sp.events), "Audio cue should not fire on override re-entry"


class TestEdgeACases:
  """Edge A: No spurious timer on non-capping override."""

  def test_edge_a_no_spurious_timer_on_disabled_override(self, mocker):
    """Override during disabled state should not arm timer."""
    sla = make_sla_factory(mocker, pcm_op_long=True)

    sla.long_enabled = True
    sla.enabled = True
    sla._has_speed_limit = False
    sla._was_cap_suspended = False
    sla.state = SpeedLimitAssistState.disabled
    sla._state_prev = SpeedLimitAssistState.disabled
    events_sp = EventsSP()

    sla.long_override = True
    sla.update_state_machine_cap(events_sp)

    sla.long_override = False
    sla.update_state_machine_cap(events_sp)

    assert sla._cap_suspended_timer == 0

    sla._has_speed_limit = True
    sla._speed_limit_final_last = 25.0
    sla._min_cap_floor = 5.0
    sla.update_state_machine_cap(events_sp)

    assert sla.state == SpeedLimitAssistState.capping


class TestEdgeBCases:
  """Edge B: _target_cap preserved via pending."""

  def test_edge_b_target_cap_preserved_via_pending(self, mocker):
    """Target cap preserved when transiting pending->capping after suspension."""
    sla = make_sla_factory(mocker, pcm_op_long=True)

    sla.long_enabled = True
    sla.enabled = True
    sla._has_speed_limit = True
    sla._speed_limit_final_last = 25.0
    sla._min_cap_floor = 5.0
    sla.state = SpeedLimitAssistState.capping
    sla._state_prev = SpeedLimitAssistState.capping
    sla._target_cap = 25.0
    sla._was_cap_suspended = True
    events_sp = EventsSP()

    sla._has_speed_limit = False
    sla.update_state_machine_cap(events_sp)
    assert sla.state == SpeedLimitAssistState.pending

    sla._has_speed_limit = True
    sla._speed_limit_final_last = 30.0
    sla.update_state_machine_cap(events_sp)

    assert sla.state == SpeedLimitAssistState.capping
    assert sla._target_cap == 25.0


class TestEdgeCCases:
  """Edge C: Timer cleared on disengage."""

  def test_edge_c_timer_cleared_on_disengage(self, mocker):
    """Timer cleared when long_enabled=False."""
    sla = make_sla_factory(mocker, pcm_op_long=True)

    sla.long_enabled = True
    sla.enabled = True
    sla._has_speed_limit = True
    sla._speed_limit_final_last = 25.0
    sla._min_cap_floor = 5.0
    sla._cap_suspended_timer = 50
    sla.state = SpeedLimitAssistState.capping
    sla._state_prev = SpeedLimitAssistState.capping
    events_sp = EventsSP()

    sla.long_enabled = False
    sla.update_state_machine_cap(events_sp)

    assert sla._cap_suspended_timer == 0
    assert sla.state == SpeedLimitAssistState.disabled
