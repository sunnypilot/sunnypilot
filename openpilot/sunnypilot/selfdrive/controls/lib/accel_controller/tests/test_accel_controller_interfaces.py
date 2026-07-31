import inspect
import math
from types import SimpleNamespace

import numpy as np
import pytest

from openpilot.cereal import custom, log, messaging
from opendbc.car.interfaces import ACCEL_MAX, ACCEL_MIN
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlanner
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import N, LongitudinalMpc
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import LongitudinalPlanSource as MpcLongitudinalPlanSource
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.accel_controller import AccelController, AccelControllerState
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.constants import (
  MPC_DECEL_JERK_COST_MULTIPLIER, MPC_DECEL_JERK_MAX_REQUIRED_DECEL, MPC_DECEL_JERK_MAX_TARGET_REDUCTION, AccelProfile,
)
from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import LongitudinalMpcSP
from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlannerSP, LongitudinalPlanSource


def radar_state():
  return messaging.new_message("radarState").radarState


class PlannerSM(dict):
  def __init__(self, radar_log_mono_time: int):
    super().__init__(
      radarState=radar_state(),
      carState=SimpleNamespace(vEgo=10.0, aEgo=0.0, vCruise=20.0),
      selfdriveState=SimpleNamespace(personality=0),
      controlsState=SimpleNamespace(forceDecel=False),
    )
    self.valid = {"radarState": True}
    self.alive = {"radarState": True}
    self.logMonoTime = {"radarState": radar_log_mono_time}


class ControllerStub:
  def __init__(self, *, target_speed=15.0, active=True, mpc_accel_max=None, cruise_accel_max=None,
               state=AccelControllerState.free, selected_lead=-1,
               selected_lead_track_id=-1, launching=False, departure_launching=False, required_decel=0.0):
    self.available = self.enabled = True
    self.profile = AccelProfile.normal
    self.output_v_target = target_speed
    self.is_active = active
    self.mpc_accel_max = mpc_accel_max
    self.cruise_accel_max = cruise_accel_max
    self.state = state
    self.selected_lead = selected_lead
    self.selected_lead_track_id = selected_lead_track_id
    self.launching = launching
    self.departure_launching = departure_launching
    self.required_decel = required_decel
    self.dt = DT_MDL
    self._jerk_smoothing_blocked = False
    self._required_decel_samples = []
    self._required_decel_lead = -1
    self._required_decel_lead_track_id = -1
    self._lead_trend_warmup = False
    self.update_kwargs = None
    self.reset_calls = 0

  def update(self, _radar_state, **kwargs):
    self.update_kwargs = kwargs

  @property
  def is_enabled(self):
    return self.available and self.enabled

  def update_params(self):
    pass

  def reset(self):
    self.reset_calls += 1

  def get_jerk_cost_multiplier(self, *args):
    return AccelController.get_jerk_cost_multiplier(self, *args)

  def update_should_stop(self, should_stop):
    return AccelController.update_should_stop(self, should_stop)


def planner_for_mpc_test(*, target_speed=15.0, active=True, is_e2e=False, mpc_accel_max=None,
                         cruise_accel_max=None,
                         state=AccelControllerState.free, selected_lead=-1, launching=False,
                         departure_launching=False, required_decel=0.0,
                         mpc_source=MpcLongitudinalPlanSource.lead0):
  planner = LongitudinalPlannerSP.__new__(LongitudinalPlannerSP)
  is_e2e_calls = []
  planner.is_e2e = lambda _sm: is_e2e_calls.append(True) or is_e2e
  planner.output_v_target = 20.0
  planner.output_should_stop = False
  planner.allow_throttle = True
  planner.a_desired = 0.0
  planner.v_desired_filter = SimpleNamespace(x=10.0)
  planner._radar_fresh_this_cycle = True
  planner.mpc = SimpleNamespace(source=mpc_source, last_solution_status=0)
  planner.accel_controller = ControllerStub(
    target_speed=target_speed, active=active, state=state, selected_lead=selected_lead, launching=launching,
    departure_launching=departure_launching, required_decel=required_decel, mpc_accel_max=mpc_accel_max,
    cruise_accel_max=cruise_accel_max,
  )
  return planner, is_e2e_calls


def prepare_controller_mpc(planner, *, mpc_v_cruise=20.0, force_decel=False):
  configs = []
  sm = {
    "radarState": radar_state(),
    "controlsState": SimpleNamespace(forceDecel=force_decel),
    "carState": SimpleNamespace(vCruise=20.0, vEgo=10.0, aEgo=0.0),
    "selfdriveState": SimpleNamespace(personality=0),
  }
  planner.mpc.set_accel_controller_params = lambda *args: configs.append(args)
  is_e2e, target = planner.update_accel_controller(sm, mpc_v_cruise, True, ACCEL_MAX, False)
  assert len(configs) == 1
  return is_e2e, target, configs[0]


def test_accel_controller_schema_contract():
  expected = {"eco": 0, "normal": 1, "sport": 2}
  state = {"inactive": 0, "free": 1, "restrict": 2, "hold": 3, "release": 4, "stopHold": 5}
  accel_controller = custom.LongitudinalPlanSP.schema.fields["accelController"]
  fields = custom.LongitudinalPlanSP.AccelController.schema.fields

  assert accel_controller.proto.ordinal.explicit == 8
  assert {name: field.proto.ordinal.explicit for name, field in fields.items()} == {
    "enabled": 0, "active": 1, "shadowOnlyDEPRECATED": 2, "profile": 3, "state": 4,
  }
  assert fields["shadowOnlyDEPRECATED"].proto.slot.type.which() == "bool"
  assert custom.LongitudinalPlanSP.AccelerationPersonality.schema.enumerants == expected
  assert custom.LongitudinalPlanSP.AccelController.Profile.schema.enumerants == expected
  assert custom.LongitudinalPlanSP.AccelController.State.schema.enumerants == state


def test_accel_controller_schema_round_trip_and_toyota_compatibility():
  message = custom.LongitudinalPlanSP.new_message()
  message.accelController.enabled = True
  message.accelController.active = True
  message.accelController.profile = custom.LongitudinalPlanSP.AccelController.Profile.sport
  message.accelController.state = custom.LongitudinalPlanSP.AccelController.State.release

  with custom.LongitudinalPlanSP.from_bytes(message.to_bytes()) as reader:
    assert reader.accelController.enabled and reader.accelController.active
    assert reader.accelController.profile == custom.LongitudinalPlanSP.AccelController.Profile.sport
    assert reader.accelController.state == custom.LongitudinalPlanSP.AccelController.State.release

  from opendbc.car.toyota.carstate import AccelPersonality, CarState

  assert AccelPersonality.schema.enumerants == {"eco": 0, "normal": 1, "sport": 2}
  assert CarState.__module__ == "opendbc.car.toyota.carstate"


def test_longitudinal_planner_sp_owns_accel_controller_integration():
  assert "update_accel_controller" in LongitudinalPlannerSP.__dict__
  assert "update_should_stop" in LongitudinalPlannerSP.__dict__


def test_mpc_inherits_accel_controller_extension_without_changing_stock_signature_or_bounds():
  assert LongitudinalMpc.__bases__ == (LongitudinalMpcSP,)
  assert tuple(inspect.signature(LongitudinalMpc.update).parameters) == ("self", "radarstate", "v_cruise", "personality")
  mpc = LongitudinalMpc()
  radar = radar_state()
  mpc.run = lambda: None

  mpc.set_cur_state(10.0, 0.8)
  mpc.update(radar, 30.0)
  np.testing.assert_array_equal(mpc.params[:, 0], ACCEL_MIN)
  np.testing.assert_array_equal(mpc.params[:, 1], ACCEL_MAX)
  assert mpc.cruise_accel_max(1.6) == 1.6

  mpc.set_accel_controller_params(None, 1.0, 0.4)
  assert mpc.cruise_accel_max(1.6) == 0.4

  requested_ceiling = tuple(np.full(N + 1, 0.4))
  mpc.set_accel_controller_params(requested_ceiling, 1.0)
  mpc.update(radar, 30.0)
  np.testing.assert_array_equal(mpc.params[:, 0], ACCEL_MIN)
  assert mpc.params[0, 1] == pytest.approx(0.8)
  np.testing.assert_array_equal(mpc.params[1:, 1], requested_ceiling[1:])

  for malformed_ceiling in ("bad", [0.4] * N, np.full(N + 1, math.nan), [10**10000] * (N + 1)):
    mpc.set_accel_controller_params(malformed_ceiling, 1.0)
    mpc.update(radar, 30.0)
    np.testing.assert_array_equal(mpc.params[:, 0], ACCEL_MIN)
    np.testing.assert_array_equal(mpc.params[:, 1], ACCEL_MAX)

  mpc.set_accel_controller_params(None, 1.0)
  mpc.update(radar, 30.0)
  np.testing.assert_array_equal(mpc.params[:, 1], ACCEL_MAX)


def test_mpc_jerk_cost_multiplier_is_backward_compatible_and_does_not_change_other_costs():
  mpc = LongitudinalMpc.__new__(LongitudinalMpc)
  LongitudinalMpcSP.__init__(mpc)
  captured = []
  mpc.set_cost_weights = lambda costs, constraints: captured.append((np.asarray(costs), np.asarray(constraints)))

  mpc.set_weights(True, personality=log.LongitudinalPersonality.standard)
  default_costs, default_constraints = captured[-1]
  mpc.set_accel_controller_params(None, 1.0)
  mpc.set_weights(True, personality=log.LongitudinalPersonality.standard)
  explicit_costs, explicit_constraints = captured[-1]
  mpc.set_accel_controller_params(None, 1.2)
  mpc.set_weights(True, personality=log.LongitudinalPersonality.standard)
  smoothed_costs, smoothed_constraints = captured[-1]

  np.testing.assert_array_equal(explicit_costs, default_costs)
  np.testing.assert_array_equal(explicit_constraints, default_constraints)
  np.testing.assert_array_equal(smoothed_costs[:-1], default_costs[:-1])
  assert smoothed_costs[-1] == pytest.approx(default_costs[-1] * 1.2)
  np.testing.assert_array_equal(smoothed_constraints, default_constraints)

  mpc.set_weights(False, personality=log.LongitudinalPersonality.standard)
  assert captured[-1][0][-2] == 0.0
  assert captured[-1][0][-1] == pytest.approx(default_costs[-1] * 1.2)


def test_stock_planner_owns_mpc_solve():
  source = inspect.getsource(LongitudinalPlanner.update)
  assert source.count("self.mpc.set_weights(") == 1
  assert source.count("self.mpc.set_cur_state(") == 1
  assert source.count("self.mpc.update(") == 1


def test_accel_controller_hook_only_configures_mpc():
  radar = radar_state()
  planner, _ = planner_for_mpc_test(active=False)
  calls = []
  planner.mpc = SimpleNamespace(
    source=MpcLongitudinalPlanSource.cruise,
    last_solution_status=0,
    set_accel_controller_params=lambda accel_max, multiplier, cruise_accel_max: calls.append(
      ("configure", accel_max, multiplier, cruise_accel_max)),
    set_weights=lambda constraint, personality: calls.append(("weights", constraint, personality)),
    set_cur_state=lambda speed, accel: calls.append(("state", speed, accel)),
    update=lambda radar_arg, target, *, personality: calls.append(("update", radar_arg, target, personality)),
  )
  sm = {
    "radarState": radar,
    "controlsState": SimpleNamespace(forceDecel=False),
    "carState": SimpleNamespace(vCruise=20.0, vEgo=10.0, aEgo=0.0),
    "selfdriveState": SimpleNamespace(personality=2),
  }
  is_e2e, target = planner.update_accel_controller(sm, 17.5, True, ACCEL_MAX, False)

  assert not is_e2e and target == 17.5
  assert calls == [("configure", None, 1.0, None)]


def test_active_acc_uses_target_and_ceiling_in_exactly_one_solve():
  ceiling = tuple(np.linspace(0.8, 0.4, N + 1))
  planner, mode_calls = planner_for_mpc_test(mpc_accel_max=ceiling)
  is_e2e, target, config = prepare_controller_mpc(planner)

  assert not is_e2e
  assert len(mode_calls) == 1
  assert target == 15.0
  assert config == (ceiling, 1.0, None)


def test_cruise_accel_ceiling_is_forwarded_to_mpc():
  planner, _ = planner_for_mpc_test(cruise_accel_max=0.3)
  _, _, config = prepare_controller_mpc(planner)
  assert config == (None, 1.0, 0.3)


def test_valid_lead_stop_hold_preplans_from_raw_target_without_an_accel_ceiling():
  planner, _ = planner_for_mpc_test(
    target_speed=0.0, mpc_accel_max=None, state=AccelControllerState.stopHold, selected_lead=0,
  )
  _, target, config = prepare_controller_mpc(planner)

  assert target == 20.0
  assert config == (None, 1.0, None)


def test_missing_lead_stop_hold_keeps_zero_mpc_target_without_an_accel_ceiling():
  planner, _ = planner_for_mpc_test(
    target_speed=0.0, mpc_accel_max=None, state=AccelControllerState.stopHold, selected_lead=-1,
  )
  _, target, config = prepare_controller_mpc(planner)

  assert target == 0.0
  assert config == (None, 1.0, None)


@pytest.mark.parametrize(
  ("active", "departure_launching", "expected"),
  [
    (True, True, False),
    (True, False, True),
    (False, True, True),
  ],
)
def test_only_confirmed_live_acc_departure_clears_should_stop(active, departure_launching, expected):
  planner = LongitudinalPlannerSP.__new__(LongitudinalPlannerSP)
  planner.accel_controller = ControllerStub(active=active, departure_launching=departure_launching, state=AccelControllerState.stopHold)
  assert planner.update_should_stop(True) is expected
  assert planner.update_should_stop(False) is (active and not departure_launching)


@pytest.mark.parametrize(("active", "is_e2e"), [(False, False), (True, True)])
def test_disabled_or_e2e_is_an_exact_mpc_bypass(active, is_e2e):
  ceiling = tuple(np.linspace(0.8, 0.4, N + 1))
  planner, mode_calls = planner_for_mpc_test(active=active, is_e2e=is_e2e, mpc_accel_max=ceiling)
  returned_e2e, target, config = prepare_controller_mpc(planner)

  assert returned_e2e is is_e2e
  assert len(mode_calls) == 1
  assert target == 20.0
  assert config == (None, 1.0, None)


def test_force_decel_target_remains_authoritative_and_disables_ceiling():
  ceiling = tuple(np.linspace(0.8, 0.4, N + 1))
  planner, mode_calls = planner_for_mpc_test(mpc_accel_max=ceiling)
  _, target, config = prepare_controller_mpc(planner, mpc_v_cruise=0.0, force_decel=True)

  assert len(mode_calls) == 1
  assert target == 0.0
  assert config == (None, 1.0, None)


def test_previous_mpc_failure_gets_one_stock_recovery_cycle():
  ceiling = tuple(np.linspace(0.8, 0.4, N + 1))
  planner, mode_calls = planner_for_mpc_test(mpc_accel_max=ceiling)
  controller = planner.accel_controller
  planner.mpc.last_solution_status = 4

  _, failed_target, failed_config = prepare_controller_mpc(planner)
  assert controller.reset_calls == 1
  assert len(mode_calls) == 1
  assert failed_target == 20.0
  assert failed_config == (None, 1.0, None)

  planner.mpc.last_solution_status = 0
  _, recovered_target, recovered_config = prepare_controller_mpc(planner)
  assert controller.reset_calls == 1
  assert len(mode_calls) == 2
  assert recovered_target == 15.0
  assert recovered_config == (ceiling, 1.0, None)


@pytest.mark.parametrize(
  "mpc_source",
  (MpcLongitudinalPlanSource.cruise, MpcLongitudinalPlanSource.lead0, MpcLongitudinalPlanSource.lead1),
)
def test_routine_governor_restriction_forwards_the_jerk_cost_multiplier(mpc_source):
  planner, _ = planner_for_mpc_test(
    state=AccelControllerState.restrict, selected_lead=0, required_decel=0.30,
    mpc_source=mpc_source,
  )
  _, target, config = prepare_controller_mpc(planner)

  assert target == 15.0
  assert config == (None, MPC_DECEL_JERK_COST_MULTIPLIER, None)


def test_ineligible_required_decel_blocks_smoothing_only_until_the_restriction_episode_ends():
  planner, _ = planner_for_mpc_test(
    state=AccelControllerState.restrict, selected_lead=0, required_decel=0.30,
  )
  _, _, initial_config = prepare_controller_mpc(planner)
  controller = planner.accel_controller
  assert initial_config[1] == MPC_DECEL_JERK_COST_MULTIPLIER

  controller.required_decel = MPC_DECEL_JERK_MAX_REQUIRED_DECEL
  _, _, ineligible_config = prepare_controller_mpc(planner)
  assert ineligible_config[1] == 1.0

  controller.required_decel = 0.30
  _, _, flicker_config = prepare_controller_mpc(planner)
  assert flicker_config[1] == 1.0

  controller.state = AccelControllerState.free
  controller.output_v_target = 20.0
  prepare_controller_mpc(planner)
  controller.state = AccelControllerState.restrict
  controller.output_v_target = 15.0
  _, _, rearmed_config = prepare_controller_mpc(planner)
  assert rearmed_config[1] == MPC_DECEL_JERK_COST_MULTIPLIER


def test_consistently_tightening_lead_releases_smoothing_until_the_restriction_ends():
  planner, _ = planner_for_mpc_test(
    state=AccelControllerState.restrict, selected_lead=0, required_decel=0.18,
  )
  _, _, config = prepare_controller_mpc(planner)
  controller = planner.accel_controller
  multipliers = [config[1]]
  for required_decel in (0.20, 0.23, 0.25):
    controller.required_decel = required_decel
    _, _, config = prepare_controller_mpc(planner)
    multipliers.append(config[1])

  assert multipliers == [MPC_DECEL_JERK_COST_MULTIPLIER] * 3 + [1.0]

  controller.required_decel = 0.20
  _, _, config = prepare_controller_mpc(planner)
  assert config[1] == 1.0

  controller.state = AccelControllerState.free
  controller.output_v_target = 20.0
  prepare_controller_mpc(planner)
  controller.state = AccelControllerState.restrict
  controller.output_v_target = 15.0
  controller.required_decel = 0.18
  _, _, config = prepare_controller_mpc(planner)
  assert config[1] == MPC_DECEL_JERK_COST_MULTIPLIER


def test_one_frame_required_decel_noise_does_not_disable_routine_smoothing():
  planner, _ = planner_for_mpc_test(
    state=AccelControllerState.restrict, selected_lead=0, required_decel=0.18,
  )
  _, _, config = prepare_controller_mpc(planner)
  controller = planner.accel_controller
  multipliers = [config[1]]
  for required_decel in (0.24, 0.19, 0.22):
    controller.required_decel = required_decel
    _, _, config = prepare_controller_mpc(planner)
    multipliers.append(config[1])

  assert multipliers == [MPC_DECEL_JERK_COST_MULTIPLIER] * 4


@pytest.mark.parametrize(
  ("state", "selected_lead", "launching", "required_decel", "target_speed", "mpc_source"),
  [
    (AccelControllerState.free, 0, False, 0.30, 15.0, MpcLongitudinalPlanSource.cruise),
    (AccelControllerState.hold, 0, False, 0.30, 15.0, MpcLongitudinalPlanSource.cruise),
    (AccelControllerState.stopHold, 0, False, 0.30, 15.0, MpcLongitudinalPlanSource.cruise),
    (AccelControllerState.restrict, -1, False, 0.30, 15.0, MpcLongitudinalPlanSource.cruise),
    (AccelControllerState.restrict, 0, True, 0.30, 15.0, MpcLongitudinalPlanSource.cruise),
    (AccelControllerState.restrict, 0, False, MPC_DECEL_JERK_MAX_REQUIRED_DECEL, 15.0, MpcLongitudinalPlanSource.cruise),
    (AccelControllerState.restrict, 0, False, math.inf, 15.0, MpcLongitudinalPlanSource.cruise),
    (AccelControllerState.restrict, 0, False, math.nan, 15.0, MpcLongitudinalPlanSource.cruise),
    (AccelControllerState.restrict, 0, False, 0.0, 15.0, MpcLongitudinalPlanSource.cruise),
    (AccelControllerState.restrict, 0, False, -0.01, 15.0, MpcLongitudinalPlanSource.cruise),
    (AccelControllerState.restrict, 0, False, 0.30, 20.0 - MPC_DECEL_JERK_MAX_TARGET_REDUCTION, MpcLongitudinalPlanSource.cruise),
    (AccelControllerState.restrict, 0, False, 0.30, 20.0, MpcLongitudinalPlanSource.cruise),
    (AccelControllerState.restrict, 0, False, 0.30, 25.0, MpcLongitudinalPlanSource.cruise),
  ],
)
def test_non_routine_or_stock_lead_states_keep_stock_jerk_cost(
  state, selected_lead, launching, required_decel, target_speed, mpc_source,
):
  planner, _ = planner_for_mpc_test(
    state=state, selected_lead=selected_lead, launching=launching,
    required_decel=required_decel, target_speed=target_speed, mpc_source=mpc_source,
  )
  _, _, config = prepare_controller_mpc(planner)

  assert config[1] == 1.0


def test_controller_receives_previous_mpc_state_and_cached_radar_freshness():
  planner, _ = planner_for_mpc_test(mpc_source=log.LongitudinalPlan.LongitudinalPlanSource.lead0)
  planner._radar_fresh_this_cycle = True
  planner.a_desired = -0.4
  planner.v_desired_filter = SimpleNamespace(x=9.5)
  prepare_controller_mpc(planner)
  received = planner.accel_controller.update_kwargs

  assert received["previous_mpc_source"] == log.LongitudinalPlan.LongitudinalPlanSource.lead0
  assert received["planner_speed"] == 9.5
  assert received["planner_accel"] == -0.4
  assert received["radar_fresh"] is True


def test_controller_is_disabled_when_openpilot_longitudinal_control_is_unavailable():
  controller = AccelController(SimpleNamespace(longitudinalActuatorDelay=0.1, openpilotLongitudinalControl=False))
  controller.enabled = True
  assert not controller.is_enabled


def test_radar_freshness_is_computed_once_and_shared_with_dec_and_controller():
  planner = LongitudinalPlannerSP.__new__(LongitudinalPlannerSP)
  planner._radar_log_mono_time = None
  planner._radar_fresh_this_cycle = True
  planner.events_sp = SimpleNamespace(clear=lambda: None)
  dec_freshness = []
  planner.dec = SimpleNamespace(update=lambda _sm, *, radar_fresh, planner_accel: dec_freshness.append(radar_fresh))
  planner.e2e_alerts_helper = SimpleNamespace(update=lambda *_args: None)
  planner.output_a_target = 0.0
  planner.output_v_target = 20.0
  planner.output_should_stop = False
  planner.allow_throttle = True
  planner.a_desired = 0.0
  planner.v_desired_filter = SimpleNamespace(x=10.0)
  planner.mpc = SimpleNamespace(
    source=log.LongitudinalPlan.LongitudinalPlanSource.cruise, last_solution_status=0,
    set_accel_controller_params=lambda *_args: None,
  )
  planner.is_e2e = lambda _sm: False
  planner.accel_controller = ControllerStub(target_speed=20.0, active=False)

  sm = PlannerSM(100)
  for expected in (True, False):
    planner.update(sm)
    planner.update_accel_controller(sm, 20.0, True, ACCEL_MAX, False)
    assert dec_freshness[-1] is expected and planner.accel_controller.update_kwargs["radar_fresh"] is expected

  sm.logMonoTime["radarState"] = 101
  planner.update(sm)
  planner.update_accel_controller(sm, 20.0, True, ACCEL_MAX, False)
  assert dec_freshness[-1] is True and planner.accel_controller.update_kwargs["radar_fresh"] is True


def test_accel_controller_status_publishes_minimal_fields():
  planner = LongitudinalPlannerSP.__new__(LongitudinalPlannerSP)
  planner.source = LongitudinalPlanSource.cruise
  planner.output_v_target = 20.0
  planner.output_a_target = 0.0
  planner.events_sp = SimpleNamespace(to_msg=list)
  planner.dec = SimpleNamespace(mode=lambda: "acc", enabled=lambda: False, active=lambda: False)
  planner.accel_controller = ControllerStub(active=False, state=AccelControllerState.restrict)
  planner.scc = SimpleNamespace(
    vision=SimpleNamespace(state=0, output_v_target=20.0, output_a_target=0.0, current_lat_acc=0.0, max_pred_lat_acc=0.0, is_enabled=False, is_active=False),
    map=SimpleNamespace(state=0, output_v_target=20.0, output_a_target=0.0, is_enabled=False, is_active=False),
  )
  planner.resolver = SimpleNamespace(
    speed_limit=0.0, speed_limit_last=0.0, speed_limit_final=0.0, speed_limit_final_last=0.0,
    speed_limit_valid=False, speed_limit_last_valid=False, speed_limit_offset=0.0, distance=0.0,
    source=custom.LongitudinalPlanSP.SpeedLimit.Source.none,
  )
  planner.sla = SimpleNamespace(
    state=custom.LongitudinalPlanSP.SpeedLimit.AssistState.disabled, is_enabled=False, is_active=False,
    output_v_target=20.0, output_a_target=0.0,
  )
  planner.e2e_alerts_helper = SimpleNamespace(green_light_alert=False, lead_depart_alert=False)
  sent = {}
  planner.publish_longitudinal_plan_sp(
    SimpleNamespace(all_checks=lambda service_list: True),
    SimpleNamespace(send=lambda service, message: sent.update({service: message})),
  )

  telemetry = sent["longitudinalPlanSP"].longitudinalPlanSP.accelController
  assert telemetry.enabled and not telemetry.active
  assert telemetry.profile == int(AccelProfile.normal)
  assert telemetry.state == int(AccelControllerState.restrict)
  assert set(custom.LongitudinalPlanSP.AccelController.schema.fields) == {"enabled", "active", "shadowOnlyDEPRECATED", "profile", "state"}
