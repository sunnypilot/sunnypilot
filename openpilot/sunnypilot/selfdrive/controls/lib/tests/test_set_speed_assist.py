"""
Copyright (c) 2026-, Zeph Leggett, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

import openpilot.cereal.messaging as messaging
from openpilot.cereal import log
from openpilot.common.parameterized import parameterized
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.controls.lib.longcontrol import LongCtrlState
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import T_IDXS as T_IDXS_MPC
from openpilot.selfdrive.controls.lib.longitudinal_planner import J_CRUISE_BP, J_CRUISE_VALS, LongitudinalPlanner, LongitudinalPlanSource
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.sunnypilot.selfdrive.controls.lib import set_speed_assist as ssa
from openpilot.sunnypilot.selfdrive.controls.lib.set_speed_assist import SetSpeedAssist

T_IDXS = np.asarray(ModelConstants.T_IDXS)
V_EGO = 20.
A_FLOOR = 0.5
RISE = float(np.interp(V_EGO, J_CRUISE_BP, J_CRUISE_VALS))
SETTLE = int(2. / (J_CRUISE_VALS[-1] * DT_MDL)) + 10


def build_sm(v_ego=V_EGO, yaw_rate=0., throttle_prob=1., lane_change=False):
  cs = messaging.new_message('carState')
  cs.carState.vEgo = v_ego
  cs.carState.vCruise = (V_EGO + 5.) * 3.6
  md = messaging.new_message('modelV2')
  md.modelV2.velocity.x = np.full(len(T_IDXS), v_ego).tolist()
  md.modelV2.orientationRate.z = np.broadcast_to(np.asarray(yaw_rate, dtype=float), T_IDXS.shape).tolist()
  md.modelV2.meta.disengagePredictions.gasPressProbs = [1., throttle_prob, 1.]
  md.modelV2.meta.laneChangeState = log.LaneChangeState.laneChangeStarting if lane_change else log.LaneChangeState.off
  ctrl = messaging.new_message('controlsState')
  ctrl.controlsState.longControlState = LongCtrlState.pid
  return {'carState': cs.carState, 'modelV2': md.modelV2, 'controlsState': ctrl.controlsState}


def run(ctl, frames, sm, a_model=0., a_floor=A_FLOOR, reset_state=False):
  out = a_model
  for _ in range(frames):
    out = ctl.update(sm, a_model, a_floor, reset_state)
  return out


def assist():
  Params().put_bool("SetSpeedAssist", True)
  return SetSpeedAssist()


class TestSetSpeedAssist(OpenpilotTestCase):
  def test_off_passes_the_model_through(self):
    assert run(SetSpeedAssist(), SETTLE, build_sm(), a_model=0.1) == 0.1

  def test_rises_at_the_cruise_jerk_to_the_floor(self, assist):
    sm = build_sm()
    lifts = [run(assist, 1, sm) for _ in range(SETTLE)]
    assert np.isclose(lifts[0], RISE * DT_MDL)
    assert max(np.diff([0.] + lifts)) <= RISE * DT_MDL + 1e-9
    assert np.isclose(lifts[-1], A_FLOOR)

  @parameterized.expand([(0.7, A_FLOOR, 0.7), (0.2, -0.3, 0.2), (-1.5, A_FLOOR, -1.5)], names=["a_model", "a_floor", "expected"])
  def test_never_lowers_the_model(self, assist, a_model, a_floor, expected):
    # above the floor, over the set speed, or braking: the model's own answer
    assert run(assist, SETTLE, build_sm(), a_model=a_model, a_floor=a_floor) == expected

  def test_gain_fades_as_the_model_slows(self, assist):
    a_model = sum(ssa.GAIN_BP) / 2
    run(assist, SETTLE, build_sm(), a_model=a_model)
    assert np.isclose(assist.lift, 0.5 * (A_FLOOR - a_model))
    run(assist, SETTLE, build_sm(), a_model=ssa.GAIN_BP[0])
    assert assist.lift == 0.

  def test_throttle_probability_scales_the_lift(self, assist):
    run(assist, SETTLE, build_sm(throttle_prob=0.5))
    assert np.isclose(assist.lift, 0.5 * A_FLOOR)

  def test_stop_and_go_stays_the_models(self, assist):
    assert run(assist, SETTLE, build_sm(v_ego=ssa.MIN_SPEED - 1.), a_model=-0.05) == -0.05

  @parameterized.expand([(0.4, 1.), (0.8, 0.5), (1.2, 0.)], names=["lat_acc", "fade"])
  def test_a_bend_ahead_fades_the_lift(self, assist, lat_acc, fade):
    bend = np.where((T_IDXS >= 5.) & (T_IDXS <= 8.), lat_acc / V_EGO, 0.)
    run(assist, SETTLE, build_sm(yaw_rate=bend))
    assert np.isclose(assist.fade, fade)
    assert np.isclose(assist.lift, fade * A_FLOOR)

  def test_lets_go_fast(self, assist):
    run(assist, SETTLE, build_sm())
    run(assist, 1, build_sm(lane_change=True))
    assert np.isclose(assist.lift, A_FLOOR - ssa.LIFT_FALL * DT_MDL)
    run(assist, 1, build_sm(), a_model=-0.5)
    assert np.isclose(assist.lift, A_FLOOR - 2 * ssa.LIFT_FALL * DT_MDL)

  def test_switched_off_eases_out(self, assist):
    sm = build_sm()
    run(assist, SETTLE, sm)
    Params().put_bool("SetSpeedAssist", False)
    assist.enabled = False  # the next params read is up to PARAMS_UPDATE_PERIOD away
    assert np.isclose(run(assist, 1, sm), A_FLOOR - ssa.LIFT_FALL * DT_MDL)
    assert run(assist, SETTLE, sm, a_model=0.3) == 0.3

  def test_reset_and_invalid_input_pass_the_model_through(self, assist):
    run(assist, SETTLE, build_sm())
    assert run(assist, 1, build_sm(), a_model=0.05, reset_state=True) == 0.05
    run(assist, SETTLE, build_sm())
    assert run(assist, 1, build_sm(throttle_prob=float('nan')), a_model=0.05) == 0.05
    assert assist.lift == 0.


class FakeSubMaster(dict):
  def all_checks(self, service_list=None):
    return True


def planner_sm():
  sm = FakeSubMaster(build_sm())
  for service in ('radarState', 'selfdriveState', 'carControl', 'carStateSP', 'liveMapDataSP', 'gpsLocation'):
    sm[service] = getattr(messaging.new_message(service), service)
  return sm


def planner(mocker, enabled):
  from opendbc.car.honda.interface import CarInterface
  from opendbc.car.honda.values import CAR
  Params().put_bool("SetSpeedAssist", enabled)
  CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
  CP.openpilotLongitudinalControl = True
  p = LongitudinalPlanner(CP, CarInterface.get_non_essential_params_sp(CP, CAR.HONDA_CIVIC), init_v=V_EGO)

  # no lead: the MPC chases its synthetic lead far ahead, well above the cruise candidate
  mpc = p.mpc
  def mpc_update(radarstate, personality=None):
    mpc.v_solution = mpc.x0[1] + 2. * T_IDXS_MPC
    mpc.a_solution = np.full(len(T_IDXS_MPC), 2.)
    mpc.j_solution = np.zeros(len(T_IDXS_MPC) - 1)
    mpc.source = LongitudinalPlanSource.lead0
  mocker.patch.object(mpc, 'update', side_effect=mpc_update)

  sm = planner_sm()
  for _ in range(200):
    p.update(sm)
  return p


class TestSetSpeedAssistPlanner(OpenpilotTestCase):
  def test_off_is_the_models_pace(self, mocker):
    p = planner(mocker, False)
    assert p.mpc.source == LongitudinalPlanSource.e2e
    assert np.isclose(p.output_a_target, 0.)

  def test_on_drives_to_the_set_speed(self, mocker):
    p = planner(mocker, True)
    assert p.a_cruise > 1.
    assert np.isclose(p.output_a_target, p.a_cruise)
    assert np.isclose(p.set_speed_assist.lift, p.a_cruise)

    pm = mocker.MagicMock()
    p.publish_longitudinal_plan_sp(planner_sm(), pm)
    report = pm.send.call_args.args[1].longitudinalPlanSP.setSpeedAssist
    assert report.active
    assert np.isclose(report.lift, p.set_speed_assist.lift, rtol=1e-6)
