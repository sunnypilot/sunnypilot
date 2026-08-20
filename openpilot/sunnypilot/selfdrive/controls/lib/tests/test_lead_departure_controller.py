"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from types import SimpleNamespace
from unittest import mock

from openpilot.cereal import log
from openpilot.common.realtime import DT_MDL
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.controls.lib.longcontrol import LongCtrlState
from openpilot.sunnypilot.selfdrive.controls.lib.lead_departure_controller import LeadDepartureController
from openpilot.sunnypilot.selfdrive.test.longitudinal_maneuvers.plant import PRIUS_TSS2_ROUTE_MODEL, PlantSP


MpcPlanSource = log.LongitudinalPlan.LongitudinalPlanSource


def make_lead(*, d_rel: float = 4.0, v_lead: float = 0.5, v_rel: float = 0.5, present: bool = True, radar: bool = True, track_id: int = 7):
  return SimpleNamespace(dRel=d_rel, vLeadK=v_lead, vRel=v_rel, present=present, radar=radar, radarTrackId=track_id)


def make_sm(
  *,
  lead_one=None,
  lead_two=None,
  v_ego: float = 0.0,
  long_active: bool = True,
  long_state=LongCtrlState.stopping,
  gas: bool = False,
  brake: bool = False,
  override: bool = False,
  force_decel: bool = False,
  radar_error: str | None = None,
):
  errors = SimpleNamespace(canError=False, radarFault=False, wrongConfig=False, radarUnavailableTemporary=False)
  if radar_error is not None:
    setattr(errors, radar_error, True)
  return {
    'carState': SimpleNamespace(vEgo=v_ego, gasPressed=gas, brakePressed=brake),
    'carControl': SimpleNamespace(longActive=long_active, cruiseControl=SimpleNamespace(override=override)),
    'controlsState': SimpleNamespace(longControlState=long_state, forceDecel=force_decel),
    'radarState': SimpleNamespace(leadOne=lead_one or make_lead(), leadTwo=lead_two or make_lead(track_id=8), radarErrors=errors),
  }


def update(controller, sm, *, source=MpcPlanSource.lead0, a_target: float = 0.05, should_stop: bool = True, reset: bool = False, radar_valid: bool = True):
  return controller.update(sm, source, a_target, should_stop, reset, radar_valid)


def activate(controller: LeadDepartureController):
  assert update(controller, make_sm(lead_one=make_lead(d_rel=4.00)))
  assert update(controller, make_sm(lead_one=make_lead(d_rel=4.01)))
  assert not update(controller, make_sm(lead_one=make_lead(d_rel=4.04)))
  assert controller.active


def run_closed_loop(controller_enabled: bool, gap: float, lead_speed, duration: float, model_should_stop: bool | None = None):
  def observe_lead(_t, _name, truth):
    truth.update(radar=True, radarTrackId=7)
    return truth

  def model_action(_t, _v_ego, _a_ego):
    return 0.0, bool(model_should_stop)

  plant = PlantSP(
    lead_relevancy=True,
    speed=0.0,
    distance_lead=gap,
    lead_observation_fn=observe_lead,
    actuator_model=PRIUS_TSS2_ROUTE_MODEL,
    run_long_control=True,
    e2e=model_should_stop is not None,
    model_action_fn=model_action if model_should_stop is not None else None,
  )
  plant.planner.lead_departure_controller.enabled = controller_enabled

  original_update = plant.planner.update

  def long_active_update(sm):
    sm['carControl'].longActive = True
    original_update(sm)

  solver_resets = 0
  original_reset = plant.planner.mpc.reset

  def counted_reset(*args, **kwargs):
    nonlocal solver_resets
    if plant.planner.mpc.solution_status != 0:
      solver_resets += 1
    return original_reset(*args, **kwargs)

  rows = []
  active = []
  with (
    mock.patch.object(plant.planner, 'get_max_accel_override', return_value=None),
    mock.patch.object(plant.planner, 'get_min_accel_override', return_value=None),
    mock.patch.object(plant.planner, 'update', side_effect=long_active_update),
    mock.patch.object(plant.planner.mpc, 'reset', side_effect=counted_reset),
  ):
    for _ in range(round(duration / DT_MDL)):
      t = plant.current_time
      result = plant.step(v_lead=lead_speed(t), v_cruise=8.0)
      rows.append(
        (t, result['speed'], result['distance'], result['distance_lead'] - result['distance'], result['actuator_command'], result['should_stop'], result['fcw'])
      )
      active.append(plant.planner.lead_departure_controller.active)

  return rows, active, solver_resets


def first_delay(rows, cue: float, column: int, predicate):
  return next(row[0] - cue for row in rows if row[0] >= cue and predicate(row[column]))


class TestLeadDepartureController(OpenpilotTestCase):
  def test_requires_three_coherent_radar_frames(self):
    controller = LeadDepartureController(True)
    assert update(controller, make_sm(lead_one=make_lead(d_rel=4.00)))
    assert update(controller, make_sm(lead_one=make_lead(d_rel=4.01)))
    assert not update(controller, make_sm(lead_one=make_lead(d_rel=4.04)))
    assert controller.active

  def test_distance_confirmation_uses_a_sliding_three_frame_window(self):
    controller = LeadDepartureController(True)
    for d_rel in (4.00, 4.01, 4.02, 4.03):
      assert update(controller, make_sm(lead_one=make_lead(d_rel=d_rel)))
    assert not controller.active

    assert not update(controller, make_sm(lead_one=make_lead(d_rel=4.06)))
    assert controller.active

  def test_persistent_false_speed_cue_with_static_range_never_arms(self):
    controller = LeadDepartureController(True)
    for _ in range(10):
      assert update(controller, make_sm(lead_one=make_lead(d_rel=4.0)))
    assert not controller.active

  def test_same_track_can_move_between_lead_slots(self):
    controller = LeadDepartureController(True)
    assert update(controller, make_sm(lead_one=make_lead(d_rel=4.00)), source=MpcPlanSource.lead0)
    assert update(controller, make_sm(lead_two=make_lead(d_rel=4.01)), source=MpcPlanSource.lead1)
    assert not update(controller, make_sm(lead_one=make_lead(d_rel=4.04)), source=MpcPlanSource.lead0)

  def test_different_track_restarts_confirmation(self):
    controller = LeadDepartureController(True)
    assert update(controller, make_sm(lead_one=make_lead(d_rel=4.00, track_id=7)))
    assert update(controller, make_sm(lead_one=make_lead(d_rel=4.02, track_id=7)))
    assert update(controller, make_sm(lead_one=make_lead(d_rel=4.20, track_id=9)))
    assert update(controller, make_sm(lead_one=make_lead(d_rel=4.22, track_id=9)))
    assert not update(controller, make_sm(lead_one=make_lead(d_rel=4.24, track_id=9)))

  def test_active_release_latches_through_native_threshold_churn(self):
    controller = LeadDepartureController(True)
    activate(controller)
    sm = make_sm(lead_one=make_lead(d_rel=4.10), long_state=LongCtrlState.pid)
    assert not update(controller, sm, a_target=0.12, should_stop=False)
    assert not update(controller, sm, a_target=0.05, should_stop=True)
    assert controller.active

  def test_active_release_latches_across_same_track_source_churn(self):
    controller = LeadDepartureController(True)
    activate(controller)
    sm = make_sm(lead_two=make_lead(d_rel=4.10), long_state=LongCtrlState.pid)
    assert not update(controller, sm, source=MpcPlanSource.lead1)
    assert controller.active

  def test_active_release_cancels_on_invalid_state(self):
    cases = (
      ('lead lost', make_sm(lead_one=make_lead(present=False))),
      ('vision lead', make_sm(lead_one=make_lead(radar=False))),
      ('track changed', make_sm(lead_one=make_lead(track_id=9))),
      ('lead too slow', make_sm(lead_one=make_lead(v_lead=0.29))),
      ('relative speed too low', make_sm(lead_one=make_lead(v_rel=0.29))),
      ('gas', make_sm(gas=True)),
      ('brake', make_sm(brake=True)),
      ('override', make_sm(override=True)),
      ('force decel', make_sm(force_decel=True)),
      ('long inactive', make_sm(long_active=False)),
      ('long control off', make_sm(long_state=LongCtrlState.off)),
      ('ego rolling', make_sm(v_ego=0.3)),
      ('radar CAN error', make_sm(radar_error='canError')),
      ('radar fault', make_sm(radar_error='radarFault')),
      ('radar config', make_sm(radar_error='wrongConfig')),
      ('radar unavailable', make_sm(radar_error='radarUnavailableTemporary')),
    )
    for name, sm in cases:
      with self.subTest(name=name):
        controller = LeadDepartureController(True)
        activate(controller)
        assert update(controller, sm)
        assert not controller.active

  def test_active_release_cancels_on_invalid_update_input(self):
    cases = (('negative target', -0.01, False, True), ('reset', 0.05, True, True), ('radar invalid', 0.05, False, False))
    for name, a_target, reset, radar_valid in cases:
      with self.subTest(name=name):
        controller = LeadDepartureController(True)
        activate(controller)
        assert update(controller, make_sm(), a_target=a_target, reset=reset, radar_valid=radar_valid)
        assert not controller.active

  def test_inactive_controller_arms_only_from_native_stop_and_stopping_state(self):
    controller = LeadDepartureController(True)
    for d_rel in (4.00, 4.02, 4.04):
      assert not update(controller, make_sm(lead_one=make_lead(d_rel=d_rel)), should_stop=False)
    for d_rel in (4.00, 4.02, 4.04):
      assert update(controller, make_sm(lead_one=make_lead(d_rel=d_rel), long_state=LongCtrlState.pid))
    assert not controller.active

  def test_capability_gate_disables_controller(self):
    controller = LeadDepartureController(False)
    for d_rel in (4.00, 4.02, 4.04):
      assert update(controller, make_sm(lead_one=make_lead(d_rel=d_rel)))
    assert not controller.active

  def test_closed_loop_departure_releases_earlier_without_a_safety_regression(self):
    lead_accel = 0.31
    cue = 1.0 + 0.4 / lead_accel

    def lead_speed(t):
      return 0.0 if t < 1.0 else min(5.0, lead_accel * (t - 1.0))

    stock, stock_active, stock_resets = run_closed_loop(False, 3.81, lead_speed, 8.0)
    controller, controller_active, controller_resets = run_closed_loop(True, 3.81, lead_speed, 8.0)

    stock_release = first_delay(stock, cue, 5, lambda should_stop: not should_stop)
    controller_release = first_delay(controller, cue, 5, lambda should_stop: not should_stop)
    stock_motion = first_delay(stock, cue, 1, lambda speed: speed > 0.01)
    controller_motion = first_delay(controller, cue, 1, lambda speed: speed > 0.01)
    stock_v01 = first_delay(stock, cue, 1, lambda speed: speed > 0.1)
    controller_v01 = first_delay(controller, cue, 1, lambda speed: speed > 0.1)

    assert any(controller_active) and not any(stock_active)
    assert stock_resets == controller_resets == 0
    assert not any(row[6] for row in stock + controller)
    assert controller_release <= stock_release - 1.0
    assert controller_motion <= stock_motion - 0.1
    assert controller_v01 <= stock_v01 - 0.1
    assert min(row[3] for row in controller) >= min(row[3] for row in stock)
    assert max(abs(right[4] - left[4]) for left, right in zip(controller, controller[1:], strict=False)) <= max(
      abs(right[4] - left[4]) for left, right in zip(stock, stock[1:], strict=False)
    )

  def test_model_stop_remains_authoritative(self):
    def lead_speed(t):
      return 0.0 if t < 1.0 else min(5.0, 0.8 * (t - 1.0))

    rows, active, solver_resets = run_closed_loop(True, 4.0, lead_speed, 6.0, model_should_stop=True)

    assert any(active)
    assert solver_resets == 0
    assert all(row[5] for row in rows)
    assert all(row[1] == 0.0 and row[2] == 0.0 for row in rows)
    assert not any(row[6] for row in rows)

  def test_stationary_lead_remains_stock_identical(self):
    stock, stock_active, stock_resets = run_closed_loop(False, 8.0, lambda _t: 0.0, 12.0)
    controller, controller_active, controller_resets = run_closed_loop(True, 8.0, lambda _t: 0.0, 12.0)

    assert stock == controller
    assert not any(stock_active) and not any(controller_active)
    assert stock_resets == controller_resets == 0
