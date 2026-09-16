import ast
import itertools
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from opendbc.car.ford.values import FordFlags
from openpilot.cereal import log
from openpilot.common.params import Params, ParamKeyFlag
from openpilot.selfdrive.controls.lib.drive_helpers import clip_curvature, get_curvature_from_plan, smooth_value
from openpilot.selfdrive.controls.lib.latcontrol_angle import LatControlAngle
from openpilot.selfdrive.controls.tests.test_ford_model_action_adapter import Subscriptions, pipeline  # noqa: F401
from openpilot.selfdrive.controls.tests.test_ford_model_action_selection import car_params, startup
from openpilot.sunnypilot.modeld_v2.constants import ModelConstants
from openpilot.sunnypilot.modeld_v2.ford_geometry import FordGeometryReference, select_ford_geometry_reference


TIMES = np.array(ModelConstants.T_IDXS)


def update(ref, curvature=.02, speed=5., **overrides):
  kwargs = {'yaws': TIMES*speed*curvature, 'yaw_rates': np.full(len(TIMES), speed*curvature), 'times': TIMES,
            'speed': speed, 'preview': .743946, 'smooth_seconds': .1, 'smoothing_enabled': True}
  return ref.update(**(kwargs | overrides))


@pytest.mark.parametrize('speed', [1., 5., 15., 30.])
@pytest.mark.parametrize('preview', [.1, .3, .743946, 1.2])
@pytest.mark.parametrize('curvature', [-.04, 0., .04])
def test_constant_radius_sign_and_units(speed, preview, curvature):
  raw, selected = update(FordGeometryReference(), curvature, speed, preview=preview, smoothing_enabled=False)
  assert raw == pytest.approx(curvature)
  assert selected == raw


def test_entry_reversal_and_release_use_existing_model_smoothing_once_per_frame():
  ref = FordGeometryReference()
  previous = 0.
  for requested in [.02]*20+[-.02]*20+[0.]*40:
    raw, selected = update(ref, requested)
    previous = smooth_value(requested, previous, .1)
    assert raw == pytest.approx(requested)
    assert selected == pytest.approx(previous)
  assert abs(selected) < 1e-9


def test_standstill_hold_and_model_specific_smoothing():
  ref = FordGeometryReference()
  _, moving = update(ref)
  for speed in [0., .1, .3]:
    assert update(ref, -.02, speed)[1] == moving
  assert update(ref, -.02, 5., smooth_seconds=0.)[1] == pytest.approx(-.02)


@pytest.mark.parametrize('changes', [
  {'yaws': []}, {'yaw_rates': []}, {'times': TIMES[:-1]}, {'times': TIMES[::-1]},
  {'times': np.ones(33)}, {'times': TIMES+1}, {'yaws': np.ones((33, 1))},
  {'yaws': np.full(33, np.nan)}, {'yaw_rates': np.full(33, np.inf)},
  {'yaws': np.full(33, 1e40)},
  {'speed': np.nan}, {'speed': -1.}, {'preview': 0.}, {'preview': np.inf}, {'preview': 11.}, {'smooth_seconds': -1.},
])
def test_invalid_geometry_resets_history(changes):
  ref = FordGeometryReference()
  update(ref)
  assert update(ref, **changes) is None
  assert ref.previous == 0.
  assert update(ref) == update(FordGeometryReference())


@pytest.mark.parametrize('controller,geometry', list(itertools.product([False, True], repeat=2)))
@pytest.mark.parametrize('brand,flags', [('ford', FordFlags.CANFD), ('ford', FordFlags.CANFD | 8), ('ford', 0), ('tesla', 1)])
def test_opt_in_cannot_change_other_vehicles_or_upstream(controller, geometry, brand, flags):
  ref = select_ford_geometry_reference(SimpleNamespace(brand=brand, flags=flags), controller, geometry)
  assert (ref is not None) == bool(controller and geometry and brand == 'ford' and flags & FordFlags.CANFD)


def messages():
  m, d, sp = [log.Event.new_message(**{key: {}}) for key in ('modelV2', 'drivingModelData', 'modelDataV2SP')]
  m.logMonoTime = 980_000_000
  action = log.ModelDataV2.Action(desiredCurvature=-.003, desiredAcceleration=.4, shouldStop=True)
  m.modelV2.action = d.drivingModelData.action = action
  m.modelV2.orientation.z = (TIMES*5.*.02).tolist()
  m.modelV2.orientation.t = TIMES.tolist()
  m.modelV2.orientationRate.z = np.full(33, .1).tolist()
  m.modelV2.position.x = (TIMES*5.).tolist()
  m.modelV2.position.y = np.zeros(33).tolist()
  return m, d, sp, action


def apply(ref, m, d, sp):
  ref.apply(m, d, sp, speed=5., preview=.743946, smooth_seconds=.1, smoothing_enabled=True)


@pytest.mark.parametrize('invalid', [False, True])
def test_publication_preserves_original_history_and_longitudinal_and_serializes_provenance(invalid):
  m, d, sp, original = messages()
  before = original.to_dict()
  if invalid:
    m.modelV2.orientationRate.z = []
  apply(FordGeometryReference(), m, d, sp)
  assert original.to_dict() == before  # prev_action held by modeld must remain the learned action.
  assert m.modelV2.action.to_dict() == d.drivingModelData.action.to_dict()
  assert m.modelV2.action.to_dict() == before
  assert m.modelV2.action.desiredAcceleration == original.desiredAcceleration
  assert m.modelV2.action.shouldStop == original.shouldStop
  with log.Event.from_bytes(sp.to_bytes()) as decoded:
    ref = decoded.modelDataV2SP.fordGeometryReference
    assert ref.enabled and ref.valid == (not invalid)
    assert ref.modelMonoTime == m.logMonoTime
    assert ref.actionDesiredCurvature == original.desiredCurvature
    assert ref.to_dict() == m.modelV2.fordGeometryReference.to_dict()
    if invalid:
      assert ref.selectedCurvature == original.desiredCurvature
    else:
      assert ref.selectedCurvature > 0. and ref.actionDesiredCurvature < 0.


@pytest.mark.parametrize('maneuver', [False, True])
def test_published_geometry_flows_through_actual_controlsd_selection_feedback_and_angle_target(pipeline, maneuver):  # noqa: F811
  from opendbc.car import structs

  m, d, sp, _ = messages()
  m.modelV2.action.desiredCurvature = d.drivingModelData.action.desiredCurvature = .015
  apply(FordGeometryReference(), m, d, sp)
  controls = startup(params=SimpleNamespace(get_bool=lambda k: k in ('FordModelActionController', 'FordGeometryReference')))
  controls.sm, controls.desired_curvature, controls.curvature = Subscriptions(maneuver), 0., 0.
  cc = structs.CarControl(latActive=True)
  cs = SimpleNamespace(vEgo=5., yawRate=0., canValid=True, steeringPressed=False, steeringTorque=0., steeringAngleDeg=0.)
  exec(pipeline[0], {'self': controls, 'CS': cs, 'CC': cc, 'actuators': cc.actuators, 'model_v2': m.modelV2,
                    'lp': SimpleNamespace(roll=0.), 'clip_curvature': clip_curvature, 'time': SimpleNamespace(monotonic=lambda: 1.)})
  # Both sources ask right; maneuver asks left and retains priority. The unchanged
  # upstream jerk limit permits 0.002 curvature in this first 10 ms step.
  expected = -.002 if maneuver else .002
  assert controls.desired_curvature == pytest.approx(expected)
  assert controls.ford_path.path_offset*expected > 0.
  assert controls.ford_path.path_angle*expected > 0.
  lac = SimpleNamespace(use_steer_limited_by_safety=False, _check_saturation=lambda *args: False)
  _, angle, angle_log = LatControlAngle.update(lac, True, cs, controls.VM, SimpleNamespace(roll=0., angleOffsetDeg=0.),
                                              False, controls.desired_curvature, None, False, .743946)
  assert angle*expected < 0. and angle_log.steeringAngleDesiredDeg == pytest.approx(angle)


def test_new_setting_default_off_persists_without_enabling_controller(tmp_path):
  params = Params(str(tmp_path))
  assert params.get_default_value('FordGeometryReference') is False
  params.put_bool('FordGeometryReference', True, block=True)
  assert b'FordGeometryReference' in params.all_keys(ParamKeyFlag.BACKUP)
  assert startup(params=params).ford_path_controller is None
  assert select_ford_geometry_reference(car_params(), params.get_bool('FordModelActionController'), True) is None
  params.clear_all(ParamKeyFlag.CLEAR_ON_MANAGER_START)
  assert params.get_bool('FordGeometryReference')


@pytest.mark.parametrize('enabled', [False, True])
def test_actual_modeld_hook_uses_exact_timing_after_original_action_history_is_saved(enabled):
  path = Path(__file__).resolve().parents[1]/'modeld.py'
  tree = ast.parse(path.read_text())
  hook = next(n for n in ast.walk(tree) if isinstance(n, ast.If) and ast.unparse(n.test) == 'ford_geometry is not None')
  m, d, sp, _ = messages()
  ref = FordGeometryReference() if enabled else None
  before = m.modelV2.to_dict(), d.drivingModelData.to_dict(), sp.modelDataV2SP.to_dict()
  env = {'ford_geometry': ref, 'modelv2_send': m, 'drivingdata_send': d, 'mdv2sp_send': sp, 'v_ego': 5., 'lat_action_t': .743946,
         'model': SimpleNamespace(LAT_SMOOTH_SECONDS=.1, generation=12)}
  exec(compile(ast.Module(body=[hook], type_ignores=[]), str(path), 'exec'), env)
  if not enabled:
    assert before == (m.modelV2.to_dict(), d.drivingModelData.to_dict(), sp.modelDataV2SP.to_dict())
    return
  expected = smooth_value(get_curvature_from_plan(list(m.modelV2.orientation.z), list(m.modelV2.orientationRate.z),
                                                 TIMES, 5., .743946), 0., .1)
  assert m.modelV2.action.desiredCurvature == pytest.approx(-.003)
  assert sp.modelDataV2SP.fordGeometryReference.selectedCurvature == pytest.approx(expected)
  assert m.modelV2.fordGeometryReference.to_dict() == sp.modelDataV2SP.fordGeometryReference.to_dict()
  assert sp.modelDataV2SP.fordGeometryReference.previewSeconds == pytest.approx(.743946)
