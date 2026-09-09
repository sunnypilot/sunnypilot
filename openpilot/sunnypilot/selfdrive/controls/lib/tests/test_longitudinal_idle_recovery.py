from types import SimpleNamespace as NS

import pytest

from openpilot.sunnypilot.selfdrive.controls.controlsd_ext import longitudinal_plan_sp_idle_active


class IdleMessages(dict):
  def all_checks(self, services):
    return all(self.healthy.get(service, True) for service in services)

  def all_alive(self, services):
    return all(self.healthy.get(service, True) for service in services)

  def all_valid(self, services):
    return all(self.healthy.get(service, True) for service in services)


@pytest.fixture
def idle_messages():
  sm = IdleMessages(
    longitudinalPlanSP=NS(speedLimit=NS(assist=NS(longitudinalIdle=True))),
    longitudinalPlan=NS(shouldStop=False, fcw=False),
    driverMonitoringState=NS(noResponseForceDecel=False),
    selfdriveState=NS(state="enabled"),
    carState=NS(gasPressed=False, brakePressed=False),
  )
  sm.healthy = {}
  return sm


@pytest.mark.parametrize('service', ['longitudinalPlanSP', 'longitudinalPlan', 'radarState'])
def test_stale_or_invalid_plan_cannot_hold_idle(idle_messages, service):
  assert longitudinal_plan_sp_idle_active(idle_messages)
  idle_messages.healthy[service] = False
  assert not longitudinal_plan_sp_idle_active(idle_messages)


@pytest.mark.parametrize('service,field', [
  ('longitudinalPlan', 'shouldStop'), ('longitudinalPlan', 'fcw'), ('driverMonitoringState', 'noResponseForceDecel'),
  ('carState', 'gasPressed'), ('carState', 'brakePressed'),
])
def test_idle_yields_to_control_requests(idle_messages, service, field):
  setattr(idle_messages[service], field, True)
  assert not longitudinal_plan_sp_idle_active(idle_messages)


@pytest.fixture
def planner_flow(monkeypatch):
  """Run the real planner update with deterministic MPC output, without a native solver."""
  import importlib.util
  import sys
  from pathlib import Path
  import numpy as np
  from openpilot.cereal import log
  from openpilot.common.constants import CV
  from openpilot.common.filter_simple import FirstOrderFilter
  from openpilot.selfdrive.modeld.constants import ModelConstants
  from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlannerSP, SpeedLimitApproach

  mpc_name = 'openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc'
  with monkeypatch.context() as imports:
    imports.setitem(sys.modules, mpc_name, NS(LongitudinalMpc=object,
                    LongitudinalPlanSource=log.LongitudinalPlan.LongitudinalPlanSource, T_IDXS=ModelConstants.T_IDXS))
    spec = importlib.util.spec_from_file_location('planner_idle_test', Path(__file__).resolve().parents[5] /
                                                 'selfdrive/controls/lib/longitudinal_planner.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

  monkeypatch.setattr(LongitudinalPlannerSP, 'update', lambda self, sm: None)
  monkeypatch.setattr(LongitudinalPlannerSP, 'update_targets', lambda self, *args: (51. * CV.KPH_TO_MS, self.output_a_target))
  monkeypatch.setattr(module, 'get_slc_no_brake', lambda: True)
  monkeypatch.setattr(module, 'get_slc_no_brake_mode', lambda: 'idle')
  monkeypatch.setattr(module, 'get_longitudinal_no_lead_decel_mode', lambda: 'idle')
  monkeypatch.setattr(module, 'get_slc_no_brake_release_gap_kph', lambda: 5.)
  monkeypatch.setattr(module, 'get_accel_from_plan', lambda *args, **kwargs: planner.mpc.accel)

  planner = module.LongitudinalPlanner.__new__(module.LongitudinalPlanner)
  planner.CP = NS(openpilotLongitudinalControl=True, longitudinalActuatorDelay=0.2, steerRatio=15., wheelbase=2.8)
  planner.dt = 0.05
  planner.fcw = False
  planner.longitudinal_idle = False
  planner.longitudinal_idle_block_frames = 0
  planner.no_lead_idle_target = 0.
  planner.v_cruise_kph_prev = 80.
  planner.speed_limit_approach = SpeedLimitApproach()
  planner.coast_lead_stable_time = module.LEAD_COAST_REENTRY_STABLE_S
  planner.coast_lead_present = (False, False)
  planner.coast_lead_distances = (None, None)
  planner.v_desired_filter = FirstOrderFilter(70. * CV.KPH_TO_MS, 2., 0.05)
  planner.a_cruise = planner.output_a_target = 0.
  planner.source = module.SpeedLimitPlanSource.speedLimitAssist
  planner.resolver = NS(lower_lookahead_active=True, speed_limit_final_last=51. * CV.KPH_TO_MS,
                        distance=200., lookahead_speed_factor_down=4.)
  planner.is_e2e = lambda sm: False
  planner.mpc = NS(set_weights=lambda *a, **k: None, set_cur_state=lambda *a: None, update=lambda *a, **k: None,
                   v_solution=np.zeros(len(ModelConstants.T_IDXS)), a_solution=np.zeros(len(ModelConstants.T_IDXS)),
                   j_solution=np.zeros(len(ModelConstants.T_IDXS)-1), crash_cnt=0,
                   source=module.LongitudinalPlanSource.lead0, accel=0.5)
  sm = IdleMessages(
    carControl=NS(orientationNED=[]),
    carState=NS(vEgo=70. * CV.KPH_TO_MS, vCruise=80., buttonEvents=[], standstill=False, brakePressed=False,
                gasPressed=False, aEgo=0., steeringAngleDeg=0.),
    controlsState=NS(forceDecel=False, longControlState=module.LongCtrlState.pid),
    selfdriveState=NS(enabled=True, personality=log.LongitudinalPersonality.standard),
    modelV2=NS(meta=NS(disengagePredictions=NS(gasPressProbs=[1., 1.])), action=NS(desiredAcceleration=0., shouldStop=False)),
    vehicleParameters=NS(angleOffsetDeg=0.),
    radarState=NS(leadOne=NS(present=False, dRel=60., vRel=0., aLeadK=0.),
                  leadTwo=NS(present=False, dRel=70., vRel=0., aLeadK=0.)),
  )
  sm.healthy = {}
  return planner, sm


def test_planner_releases_to_final_target_without_reentering_idle(planner_flow):
  from openpilot.common.constants import CV
  planner, sm = planner_flow
  planner.update(sm)
  assert planner.longitudinal_idle
  sm['carState'].vEgo = 56. * CV.KPH_TO_MS
  planner.update(sm)
  assert not planner.longitudinal_idle
  assert planner.output_a_target < 0.
  sm['carState'].vEgo = 57. * CV.KPH_TO_MS
  planner.update(sm)
  assert not planner.longitudinal_idle
  sm['carState'].vEgo = 49. * CV.KPH_TO_MS
  for _ in range(80):
    planner.update(sm)
  assert planner.output_a_target > 0.


def test_new_lead_requires_stability_and_braking_wins(planner_flow):
  planner, sm = planner_flow
  for _ in range(45):
    planner.update(sm)
  sm['radarState'].leadOne.present = True
  planner.update(sm)
  assert not planner.longitudinal_idle
  for _ in range(45):
    planner.update(sm)
  assert planner.longitudinal_idle
  planner.mpc.accel = -0.4
  planner.update(sm)
  assert not planner.longitudinal_idle
  assert planner.output_a_target <= -0.4


@pytest.mark.parametrize('field,value', [('vRel', -0.5), ('aLeadK', -0.5), ('dRel', 10.)])
def test_unsafe_second_lead_blocks_idle(planner_flow, field, value):
  planner, sm = planner_flow
  sm['radarState'].leadTwo.present = True
  setattr(sm['radarState'].leadTwo, field, value)
  for _ in range(45):
    planner.update(sm)
  assert not planner.longitudinal_idle


def test_released_approach_survives_temporary_other_cruise_source(planner_flow):
  from openpilot.common.constants import CV
  from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlanSource
  planner, sm = planner_flow
  sm['carState'].vEgo = 56. * CV.KPH_TO_MS
  planner.update(sm)
  planner.source = LongitudinalPlanSource.sccMap
  sm['carState'].vEgo = 57. * CV.KPH_TO_MS
  planner.update(sm)
  planner.source = LongitudinalPlanSource.speedLimitAssist
  planner.update(sm)
  assert not planner.longitudinal_idle
  assert planner.output_a_target < 0.


def test_flickering_lead_cannot_reenter_idle_on_missing_frames(planner_flow):
  planner, sm = planner_flow
  planner.update(sm)
  assert planner.longitudinal_idle
  for i in range(100):
    sm['radarState'].leadOne.present = i % 2 == 0
    planner.update(sm)
    assert not planner.longitudinal_idle
  # Once the lead is consistently absent, coasting can resume.
  for _ in range(45):
    planner.update(sm)
  assert planner.longitudinal_idle


def test_braking_requires_stable_recovery_before_idle(planner_flow):
  planner, sm = planner_flow
  sm['radarState'].leadOne.present = True
  for _ in range(45):
    planner.update(sm)
  assert planner.longitudinal_idle
  for _ in range(20):
    planner.mpc.accel = -0.4
    planner.update(sm)
    assert not planner.longitudinal_idle
    assert planner.output_a_target <= -0.4
    planner.mpc.accel = 0.5
    planner.update(sm)
    assert not planner.longitudinal_idle
  for _ in range(45):
    planner.update(sm)
  assert planner.longitudinal_idle


def test_lead_disappearing_after_braking_does_not_bypass_delay(planner_flow):
  planner, sm = planner_flow
  sm['radarState'].leadOne.present = True
  planner.mpc.accel = -0.4
  planner.update(sm)
  sm['radarState'].leadOne.present = False
  planner.mpc.accel = 0.5
  for _ in range(30):
    planner.update(sm)
    assert not planner.longitudinal_idle
  for _ in range(15):
    planner.update(sm)
  assert planner.longitudinal_idle


def test_idle_check_does_not_require_its_own_controls_state_output(idle_messages):
  # controlsd publishes controlsState; it is absent from its SubMaster inputs.
  assert 'controlsState' not in idle_messages
  assert longitudinal_plan_sp_idle_active(idle_messages)


def test_idle_rejected_while_soft_disabling(idle_messages):
  from openpilot.cereal import log
  idle_messages['selfdriveState'].state = log.SelfdriveState.OpenpilotState.softDisabling
  assert not longitudinal_plan_sp_idle_active(idle_messages)


@pytest.fixture
def rocket_fuel(monkeypatch):
  import importlib.util
  import sys
  from pathlib import Path

  # Import the real indicator without starting the global UI application.
  with monkeypatch.context() as imports:
    imports.setitem(sys.modules, 'openpilot.selfdrive.ui.ui_state', NS(ui_state=NS()))
    imports.setitem(sys.modules, 'openpilot.system.ui.lib.application',
                    NS(gui_app=NS(font=lambda weight: None), FontWeight=NS(BOLD='bold')))
    imports.setitem(sys.modules, 'openpilot.system.ui.lib.text_measure',
                    NS(measure_text_cached=lambda *args: NS(x=30., y=48.)))
    path = Path(__file__).resolve().parents[5] / 'selfdrive/ui/sunnypilot/onroad/rocket_fuel.py'
    spec = importlib.util.spec_from_file_location('rocket_fuel_idle_test', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
  return module.RocketFuel


def test_n_indicator_requires_accepted_controls_request(rocket_fuel, idle_messages):
  idle_messages['carControlSP'] = NS(longitudinalIdle=False)
  idle_messages['carControl'] = NS(longActive=True)
  # A planner request alone must not light N when controls rejected it.
  assert not rocket_fuel.longitudinal_idle_active(idle_messages)
  idle_messages['carControlSP'].longitudinalIdle = True
  assert rocket_fuel.longitudinal_idle_active(idle_messages)
  idle_messages['carControl'].longActive = False
  assert not rocket_fuel.longitudinal_idle_active(idle_messages)


@pytest.mark.parametrize('service', ['carControlSP', 'carControl'])
def test_n_indicator_rejects_stale_controls_request(rocket_fuel, idle_messages, service):
  idle_messages['carControlSP'] = NS(longitudinalIdle=True)
  idle_messages['carControl'] = NS(longActive=True)
  idle_messages.healthy[service] = False
  assert not rocket_fuel.longitudinal_idle_active(idle_messages)


def test_n_indicator_accepts_fresh_requests_at_20_fps(rocket_fuel, idle_messages):
  from openpilot.cereal.messaging import FrequencyTracker
  tracker = FrequencyTracker(service_freq=100., update_freq=100., is_poll=False)
  for i in range(1, 41):
    tracker.record_recv_time(i / 20.)
  assert not tracker.valid
  idle_messages['carControlSP'] = NS(longitudinalIdle=True)
  idle_messages['carControl'] = NS(longActive=True)
  idle_messages.all_checks = lambda services: tracker.valid
  assert rocket_fuel.longitudinal_idle_active(idle_messages)


def test_n_indicator_draws_with_application_font(rocket_fuel, idle_messages, monkeypatch):
  from unittest.mock import Mock
  render_globals = rocket_fuel.render.__globals__
  rl = render_globals['rl']
  font = object()
  monkeypatch.setattr(render_globals['gui_app'], 'font', Mock(return_value=font))
  monkeypatch.setattr(render_globals['ui_state'], 'rocket_fuel', True, raising=False)
  draw = Mock()
  monkeypatch.setattr(rl, 'draw_text_ex', draw)
  monkeypatch.setattr(rl, 'draw_rectangle', Mock())
  idle_messages['carControlSP'] = NS(longitudinalIdle=True)
  idle_messages['carControl'] = NS(longActive=True)
  idle_messages['carState'].aEgo = 0.
  rocket_fuel().render(rl.Rectangle(0., 0., 100., 200.), idle_messages)
  draw.assert_called_once()
  assert draw.call_args.args[:2] == (font, 'N')
  assert draw.call_args.args[2].x == 13.
  assert draw.call_args.args[2].y == 76.


@pytest.fixture
def manual_cruise_flow(planner_flow, monkeypatch):
  from openpilot.common.constants import CV
  from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlannerSP, LongitudinalPlanSource
  planner, sm = planner_flow
  monkeypatch.setattr(LongitudinalPlannerSP, 'update_targets', lambda self, sm, v_ego, a_ego, v_cruise: (v_cruise, a_ego))
  planner.source = LongitudinalPlanSource.cruise
  planner.resolver.lower_lookahead_active = False
  planner.resolver.speed_limit_final_last = 50. * CV.KPH_TO_MS
  planner.v_cruise_kph_prev = sm['carState'].vCruise = 40.
  sm['carState'].vEgo = 40. * CV.KPH_TO_MS
  return planner, sm


def test_manual_40_to_20_coasts_without_lead_and_releases(manual_cruise_flow):
  from openpilot.common.constants import CV
  planner, sm = manual_cruise_flow
  sm['carState'].vCruise = 20.
  for _ in range(10):
    planner.update(sm)
  assert planner.longitudinal_idle
  sm['carState'].vEgo = 25. * CV.KPH_TO_MS
  planner.update(sm)
  assert not planner.longitudinal_idle
  assert planner.output_a_target < 0.


def test_manual_40_to_20_coasts_with_qualified_steady_lead(manual_cruise_flow):
  planner, sm = manual_cruise_flow
  sm['radarState'].leadOne.present = True
  for _ in range(45):
    planner.update(sm)
  sm['carState'].vCruise = 20.
  for _ in range(10):
    planner.update(sm)
  assert planner.longitudinal_idle
  planner.mpc.accel = -0.4
  planner.update(sm)
  assert not planner.longitudinal_idle
  assert planner.output_a_target <= -0.4


def test_manual_target_drop_during_pedal_override_survives_release(manual_cruise_flow):
  from openpilot.selfdrive.controls.lib.longcontrol import LongCtrlState
  planner, sm = manual_cruise_flow
  sm['controlsState'].longControlState = LongCtrlState.off
  sm['carState'].gasPressed = True
  sm['carState'].vCruise = 20.
  for _ in range(5):
    planner.update(sm)
    assert not planner.longitudinal_idle
  sm['controlsState'].longControlState = LongCtrlState.pid
  sm['carState'].gasPressed = False
  for _ in range(45):
    planner.update(sm)
  assert planner.longitudinal_idle


@pytest.mark.parametrize('field,value', [('vRel', -0.5), ('aLeadK', -0.5), ('dRel', 10.)])
def test_manual_cruise_idle_rejects_unsafe_lead(manual_cruise_flow, field, value):
  planner, sm = manual_cruise_flow
  sm['carState'].vCruise = 20.
  sm['radarState'].leadOne.present = True
  setattr(sm['radarState'].leadOne, field, value)
  for _ in range(45):
    planner.update(sm)
  assert not planner.longitudinal_idle


@pytest.mark.parametrize('cancel', ['disengage', 'increase'])
def test_manual_pending_target_is_cleared_by_cancellation(manual_cruise_flow, cancel):
  from openpilot.selfdrive.controls.lib.longcontrol import LongCtrlState
  planner, sm = manual_cruise_flow
  sm['controlsState'].longControlState = LongCtrlState.off
  sm['carState'].vCruise = 20.
  planner.update(sm)
  if cancel == 'disengage':
    sm['selfdriveState'].enabled = False
  else:
    sm['carState'].vCruise = 30.
  planner.update(sm)
  assert planner.no_lead_idle_target == 0.
  sm['selfdriveState'].enabled = True
  sm['controlsState'].longControlState = LongCtrlState.pid
  for _ in range(45):
    planner.update(sm)
  assert not planner.longitudinal_idle


def test_manual_idle_does_not_override_curve_speed_control(manual_cruise_flow):
  from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlanSource
  planner, sm = manual_cruise_flow
  planner.source = LongitudinalPlanSource.sccMap
  sm['carState'].vCruise = 20.
  for _ in range(45):
    planner.update(sm)
  assert not planner.longitudinal_idle


def _qualified_steady_lead(planner, sm):
  sm['radarState'].leadOne.present = True
  for _ in range(45):
    planner.update(sm)
  sm['carState'].vCruise = 20.
  for _ in range(10):
    planner.update(sm)
  assert planner.longitudinal_idle


def test_steady_lead_small_brake_request_still_coasts(manual_cruise_flow):
  planner, sm = manual_cruise_flow
  _qualified_steady_lead(planner, sm)
  # A stable lead's tiny gap correction must not permanently suppress idle.
  planner.mpc.accel = -0.06
  for _ in range(10):
    planner.update(sm)
  assert planner.longitudinal_idle


def test_sustained_moderate_brake_blocks_steady_lead_idle(manual_cruise_flow):
  planner, sm = manual_cruise_flow
  _qualified_steady_lead(planner, sm)
  planner.mpc.accel = -0.25
  for _ in range(6):
    planner.update(sm)
  assert not planner.longitudinal_idle
  assert planner.output_a_target <= -0.25


def test_departing_qualified_lead_keeps_coasting(manual_cruise_flow):
  planner, sm = manual_cruise_flow
  _qualified_steady_lead(planner, sm)
  sm['radarState'].leadOne.present = False
  for _ in range(10):
    planner.update(sm)
  assert planner.longitudinal_idle


def test_brief_unsafe_lead_blip_blocks_idle_but_keeps_qualification(manual_cruise_flow):
  planner, sm = manual_cruise_flow
  _qualified_steady_lead(planner, sm)
  sm['radarState'].leadOne.vRel = -0.5
  planner.update(sm)
  # An unsafe reading always blocks idle immediately, even briefly.
  assert not planner.longitudinal_idle
  sm['radarState'].leadOne.vRel = 0.
  planner.update(sm)
  # Qualification was retained, so coasting resumes without a full 2 s wait.
  assert planner.longitudinal_idle


def test_braking_closing_lead_blocks_idle_immediately(manual_cruise_flow):
  planner, sm = manual_cruise_flow
  _qualified_steady_lead(planner, sm)
  planner.mpc.accel = -1.0
  sm['radarState'].leadOne.vRel = -2.0
  sm['radarState'].leadOne.aLeadK = -1.5
  planner.update(sm)
  assert not planner.longitudinal_idle
  assert planner.output_a_target < 0.



def test_manual_cruise_idle_request_reaches_can_output(manual_cruise_flow, idle_messages):
  from opendbc.car.hyundai.hyundaicanfd import create_acc_control
  from opendbc.sunnypilot.car.hyundai.lead_data_ext import CanFdLeadData
  planner, sm = manual_cruise_flow
  sm['carState'].vCruise = 20.
  for _ in range(10):
    planner.update(sm)
  idle_messages['longitudinalPlanSP'].speedLimit.assist.longitudinalIdle = planner.longitudinal_idle
  idle_messages['longitudinalPlan'].shouldStop = planner.output_should_stop
  idle_messages['longitudinalPlan'].fcw = planner.fcw
  accepted_idle = longitudinal_plan_sp_idle_active(idle_messages)
  assert accepted_idle
  packer = NS(make_can_msg=lambda name, bus, values: values)
  tuning = NS(stopping=False, actual_accel=0.1, jerk_lower=1., jerk_upper=1.)
  values = create_acc_control(packer, NS(ECAN=0), True, 0., 0., False, False, 20., NS(leadDistanceBars=2),
                              CanFdLeadData(0, 0., 0., False), True, tuning, longitudinal_idle=accepted_idle)
  assert values['ACCMode'] == 0
  assert values['aReqRaw'] == 0.
