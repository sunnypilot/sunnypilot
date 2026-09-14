"""C0 distance mapping and live setting changes, without vehicle hardware."""
import ast
import math
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from opendbc.can import CANPacker, CANParser
from opendbc.car.ford.fordcan import CanBus, create_lat_ctl2_msg
from openpilot.common.params import Params, ParamKeyFlag, ParamKeyType
from openpilot.selfdrive.controls.lib.ford_model_action import FordModelActionController, ModelActionController, encode_model_action
from openpilot.selfdrive.controls.lib.ford_path import FordPath
from openpilot.selfdrive.controls.tests.test_ford_model_action import straight
from openpilot.selfdrive.controls.tests.test_ford_model_action_adapter import _method, update
from openpilot.selfdrive.controls.tests.test_ford_model_action_selection import startup


@pytest.mark.parametrize('speed', [.3, 3., 7., 8.94, 13.41, 26.82, 55.])
@pytest.mark.parametrize('curvature', [-.03, -1e-9, 0., 1e-9, .03])
def test_arc_distance_changes_only_c0_above_seven_meters_per_second(speed, curvature):
  fixed = encode_model_action(straight(), curvature, speed)
  timed = encode_model_action(straight(), curvature, speed, c0_time_based=True)
  distance = max(7., speed)
  # Independent small-angle expansion avoids cancellation at nearly zero k.
  expected = (.5*curvature*distance**2 if abs(curvature) < 1e-6 else (1-math.cos(curvature*distance))/curvature)
  assert timed.path_offset == pytest.approx(expected)
  assert timed.path_angle == fixed.path_angle
  assert timed.curvature == timed.curvature_rate == 0.
  if speed <= 7.:
    assert timed == fixed


@pytest.mark.parametrize('enabled', [False, True])
def test_reversal_and_zero_request_remain_immediate_on_the_wire(enabled):
  core = ModelActionController(c0_time_based=enabled)
  packer = CANPacker('ford_lincoln_base_pt')
  parser = CANParser('ford_lincoln_base_pt', [('LateralMotionControl2', 100)], 0)
  bus = CanBus(fingerprint={0: {}})
  for i, k in enumerate([.01]*100+[-.01, 0.]):
    command = core.update(straight(), k, current_curvature=k, speed=20., dt=.01)
    packet = create_lat_ctl2_msg(packer, bus, 2, -command.path_offset, -command.path_angle, 0., 0., i % 16)
    parser.update([i*10_000_000, [packet]])
    wire = parser.vl['LateralMotionControl2']
    assert wire['LatCtlPathOffst_L_Actl'] == pytest.approx(-command.path_offset)
    assert wire['LatCtlPath_An_Actl'] == pytest.approx(-command.path_angle)
    assert wire['LatCtlCurv_No_Actl'] == wire['LatCtlCrv_NoRate2_Actl'] == 0.
    assert command.path_offset*k >= 0. and command.path_angle*k >= 0.
    if k == 0.:
      assert command == FordPath(True, 0., 0., 0., 0.)


def test_same_feedback_produces_identical_c1_and_integral_in_both_modes():
  cores = [ModelActionController(c0_time_based=mode) for mode in (False, True)]
  model = straight()
  for i in range(2000):
    k = .03*math.sin(i*.03)
    kwargs = {'current_curvature': .02*math.sin(i*.03-.5), 'speed': 20., 'dt': .01,
              'feedback_enabled': i % 77 != 0, 'pscm_limited': i % 3 == 0}
    outputs = [core.update(model, k, **kwargs) for core in cores]
    assert outputs[0].path_angle == outputs[1].path_angle
    assert cores[0].correction == cores[1].correction
    assert cores[0].proportional == cores[1].proportional
    for out in outputs:
      assert abs(out.path_offset) <= 5.110001 and abs(out.path_angle) <= .500001


@pytest.mark.parametrize('initial', [False, True])
def test_change_resets_feedback_and_timestamps_but_a_noop_does_not(initial):
  controller = FordModelActionController(c0_time_based=initial)
  for i in range(20):
    update(controller, 1.+i*.01, current_curvature=0.)
  assert controller.core.correction > 0.
  before = controller.diagnostics.copy()
  assert not controller.set_c0_time_based(not initial, lateral_engaged=True)
  assert controller.diagnostics == before and controller.core.c0_time_based == initial
  assert not controller.set_c0_time_based(initial, lateral_engaged=False)
  assert controller.diagnostics == before
  assert controller.set_c0_time_based(not initial, lateral_engaged=False)
  assert controller.core.correction == controller.core.proportional == controller.core.c0 == controller.core.c1 == 0.
  assert controller.last_time is controller.last_measurement_time is controller.last_model_time is None
  assert controller.diagnostics['status'] == 'c0_distance_changed'
  assert controller.diagnostics['c0_time_based'] == (not initial)
  assert update(controller, 10.) == update(FordModelActionController(c0_time_based=not initial), 10.)
  assert controller.diagnostics['offset_distance'] == (7. if initial else 20.)


@pytest.fixture
def runtime(tmp_path):
  params = Params(str(tmp_path))
  params.put_bool('FordModelActionController', True, block=True)
  controls = startup(params=params)
  controls.CP.lateralTuning = SimpleNamespace(which=lambda: 'angle')
  controls._param_update_time = 0.
  controls.blinker_pause_lateral = SimpleNamespace(get_params=lambda: None)
  clock = SimpleNamespace(now=4., monotonic=lambda: clock.now)
  events = []
  filename = Path(__file__).resolve().parents[3]/'sunnypilot/selfdrive/controls/controlsd_ext.py'
  method = _method(filename, 'ControlsExt', 'get_params_sp')
  env = {'time': clock, 'PARAMS_UPDATE_PERIOD': 3., 'messaging': SimpleNamespace(SubMaster=object),
         'cloudlog': SimpleNamespace(event=lambda *args, **kwargs: events.append((args, kwargs)))}
  exec(compile(ast.Module(body=[method], type_ignores=[]), str(filename), 'exec'), env)
  controls.refresh = lambda sm: env['get_params_sp'](controls, sm)
  return controls, params, clock, events


class EngagementMessages(dict):
  healthy = True

  def all_checks(self, services):
    return self.healthy and all(service in self for service in services)


@pytest.mark.parametrize('mads_available', [False, True])
def test_running_process_defers_changes_until_disengaged_and_honors_poll_period(runtime, mads_available):
  controls, params, clock, events = runtime
  mads = SimpleNamespace(available=mads_available, enabled=True, active=False)  # includes a paused MADS state
  standard = SimpleNamespace(enabled=True, active=False)
  sm = EngagementMessages(selfdriveStateSP=SimpleNamespace(mads=mads), selfdriveState=standard)
  params.put_bool('FordC0TimeBased', True, block=True)
  controller = controls.ford_path_controller
  update(controller, current_curvature=0.)
  controls.refresh(sm)
  assert not controller.core.c0_time_based
  mads.enabled = standard.enabled = False
  clock.now = 5.
  controls.refresh(sm)
  assert not controller.core.c0_time_based  # next scheduled refresh has not run yet
  clock.now = 7.01
  controls.refresh(sm)
  assert controller.core.c0_time_based and controller.last_time is None
  assert controls.ford_path_controller is controller  # same controlsd/controller instance
  assert len(events) == 1
  params.put_bool('FordC0TimeBased', False, block=True)
  sm.healthy = False
  clock.now += 3.01
  controls.refresh(sm)
  assert controller.core.c0_time_based  # stale engagement data cannot permit a swap
  sm.healthy = True
  clock.now += 3.01
  controls.refresh(sm)
  assert not controller.core.c0_time_based and len(events) == 2


def test_setting_is_persistent_default_off_and_cannot_enable_custom_control(tmp_path):
  params = Params(str(tmp_path))
  assert params.get_default_value('FordC0TimeBased') is False
  assert params.get_type('FordC0TimeBased') == ParamKeyType.BOOL
  for flag in (ParamKeyFlag.PERSISTENT, ParamKeyFlag.BACKUP):
    assert b'FordC0TimeBased' in params.all_keys(flag)
  params.put_bool('FordC0TimeBased', True, block=True)
  assert startup(params=params).ford_path_controller is None
  params.put_bool('FordModelActionController', True, block=True)
  assert startup(params=params).ford_path_controller.core.c0_time_based
  params.clear_all(ParamKeyFlag.CLEAR_ON_MANAGER_START)
  assert Params(str(tmp_path)).get_bool('FordC0TimeBased')


@pytest.mark.parametrize('speed', [3., 10., 20., 35., 55.])
def test_timed_mode_retains_bounds_at_extreme_and_nonfinite_requests(speed):
  core = ModelActionController(c0_time_based=True)
  for curvature in np.linspace(-1., 1., 101):
    out = core.update(straight(), curvature, current_curvature=0., speed=speed, dt=.01)
    assert out.valid and abs(out.path_offset) <= 5.110001 and abs(out.path_angle) <= .500001
  for invalid in (math.nan, math.inf, -math.inf):
    assert core.update(straight(), invalid, current_curvature=0., speed=speed, dt=.01) == FordPath()
