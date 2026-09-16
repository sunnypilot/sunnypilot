import math
from types import SimpleNamespace

import pytest

from openpilot.selfdrive.controls.lib.ford_geometry_action import GeometryActionHybrid
from openpilot.selfdrive.controls.lib.ford_model_action import FordModelActionController
from openpilot.selfdrive.controls.tests.test_ford_model_action_adapter import Subscriptions, pipeline  # noqa: F401
from openpilot.selfdrive.controls.tests.test_ford_model_action_selection import startup


@pytest.mark.parametrize('sign', [-1., 1.])
def test_build_and_hold_keep_geometry_strength_then_release_follows_action(sign):
  h = GeometryActionHybrid()
  assert h.update(sign*.005, sign*.04) == pytest.approx(sign*(.005+.25*.035))
  for action in [.01, .02]+[.02]*100:
    assert h.update(sign*action, sign*.04) == pytest.approx(sign*.04)
  # Half the action peak leaves a quarter of the geometry excess.
  assert h.update(sign*.01, sign*.04) == pytest.approx(sign*(.01+.25*.03))
  assert h.update(0., sign*.04) == 0.
  assert h.update(-sign*.005, sign*.04) == pytest.approx(-sign*.005)


def test_small_action_dip_does_not_switch_all_assistance_off():
  h = GeometryActionHybrid()
  h.update(.02, .04)
  assert .035 < h.update(.019, .04) < .04
  assert h.update(.02, .04) == pytest.approx(.04)


@pytest.mark.parametrize('sign', [-1., 1.])
def test_tiny_action_cannot_restart_full_assistance_after_geometry_dips(sign):
  h = GeometryActionHybrid()
  h.update(sign*.03, sign*.04)
  h.update(-sign*.001, sign*.003)
  # Route 15b's exit: geometry rebounds after falling below the turn band.
  # A tiny same-direction action must not authorize the entire geometry request.
  assert abs(h.update(sign*.0008, sign*.025)) < .0012


@pytest.mark.parametrize('action,geometry', [(0., .04), (-.01, .04), (.02, .01), (.003, .006), (-.003, -.009)])
def test_conflicting_weaker_and_gentle_geometry_preserve_action(action, geometry):
  assert GeometryActionHybrid().update(action, geometry) == action


def test_exit_cannot_rearm_from_small_action_rebound_until_the_geometry_excursion_ends():
  h = GeometryActionHybrid()
  h.update(.03, .04)
  h.update(0., .04)
  assert h.update(.003, .04) < .004
  h.update(0., 0.)
  assert h.update(.003, .04) == pytest.approx(.003+.09*.037)


def test_repeated_model_frames_are_idempotent_and_inactive_invalid_inputs_reset():
  h = GeometryActionHybrid()
  h.update(.02, .04)
  expected = h.update(.01, .04)
  for _ in range(100):
    assert h.update(.01, .04) == expected
  assert h.update(.01, .04, active=False) == .01 and h.action_peak == 0.
  assert h.update(.01, math.nan) == .01 and h.action_peak == 0.
  assert h.update(math.nan, .04) == 0. and h.action_peak == 0.


def test_sign_change_starts_a_fresh_excursion():
  h = GeometryActionHybrid()
  h.update(.02, .04)
  assert h.update(-.003, -.04) == pytest.approx(-(.003+.09*.037))


def test_causal_output_stays_between_sources_for_both_directions():
  h = GeometryActionHybrid()
  for i in range(10000):
    action, geometry = .05*math.sin(i*.012), .08*math.sin(i*.008)
    result = h.update(action, geometry)
    assert min(action, geometry)-1e-12 <= result <= max(action, geometry)+1e-12
    assert 0. <= h.weight <= 1.


@pytest.mark.parametrize('values', [(0., .02, 2.), (.02, .01, 2.), (.01, .02, 0.), (.01, .02, math.nan), (math.nan, .02, 2.)])
def test_invalid_configuration_is_rejected(values):
  with pytest.raises(ValueError):
    GeometryActionHybrid(*values)


def test_future_predictions_cannot_change_earlier_outputs():
  prefix = [(.003+i*.001, .04) for i in range(20)]
  results = []
  for future in [[(.005, .04)]*20, [(-.005, -.04)]*20]:
    h = GeometryActionHybrid()
    results.append([h.update(a, g) for a, g in prefix+future][:len(prefix)])
  assert results[0] == results[1]


@pytest.mark.parametrize('controller_enabled', [False, True])
@pytest.mark.parametrize('geometry_enabled', [False, True])
def test_actual_startup_selects_upstream_action_or_hybrid(controller_enabled, geometry_enabled):
  settings = {'FordModelActionController': controller_enabled, 'FordGeometryReference': geometry_enabled}
  controls = startup(params=SimpleNamespace(get_bool=lambda key: settings.get(key, False)))
  if not controller_enabled:
    assert controls.ford_path_controller is None
    return
  assert not controls.ford_path_controller.direct_path
  assert (controls.ford_path_controller.geometry_assist is not None) == geometry_enabled
  expected = 'geometry-assisted-action-feedback-v18' if geometry_enabled else 'model-action-curvature-c0-feedback-v15'
  assert controls.ford_path_controller.hypothesis == expected


@pytest.mark.parametrize('invalid', ['missing', 'disabled', 'invalid', 'older', 'future', 'nonfinite', 'inactive', 'service'])
def test_adapter_rejects_missing_mismatched_or_invalid_geometry_and_clears_peak(invalid):
  controller = FordModelActionController(geometry_assist=True)
  ref = SimpleNamespace(enabled=True, valid=True, modelMonoTime=1_000_000_000, selectedCurvature=.04)
  model = SimpleNamespace(action=SimpleNamespace(desiredCurvature=.02), fordGeometryReference=ref)
  kwargs = {'model_mono_time': 1_000_000_000, 'active': True, 'valid': True}
  assert controller.select_reference(model, **kwargs) == .04
  model.action.desiredCurvature = .003
  if invalid == 'missing':
    del model.fordGeometryReference
  elif invalid == 'disabled':
    ref.enabled = False
  elif invalid == 'invalid':
    ref.valid = False
  elif invalid in ('older', 'future'):
    ref.modelMonoTime += -1 if invalid == 'older' else 1
  elif invalid == 'nonfinite':
    ref.selectedCurvature = math.nan
  else:
    kwargs['active' if invalid == 'inactive' else 'valid'] = False
  assert controller.select_reference(model, **kwargs) == .003
  assert controller.geometry_assist.action_peak == controller.geometry_assist.weight == 0.


def test_incompatible_direct_and_hybrid_modes_are_rejected():
  with pytest.raises(ValueError):
    FordModelActionController(direct_path=True, geometry_assist=True)


@pytest.mark.parametrize('maneuver', [False, True])
def test_atomic_model_publication_through_controlsd_limiter_feedback_and_can(pipeline, maneuver):  # noqa: F811
  from opendbc.car import structs
  from openpilot.cereal import log
  from openpilot.selfdrive.controls.lib.drive_helpers import clip_curvature
  from openpilot.sunnypilot.modeld_v2.tests.test_ford_geometry import messages, apply
  from openpilot.sunnypilot.modeld_v2.ford_geometry import FordGeometryReference
  from tools.ford_pscm_lab.model_action_replay import WireCheck

  controls = startup(params=SimpleNamespace(get_bool=lambda key: key in ('FordModelActionController', 'FordGeometryReference')))
  controls.sm, controls.desired_curvature, controls.curvature = Subscriptions(maneuver), 0., 0.
  expected_selector = GeometryActionHybrid()
  baseline = FordModelActionController()
  publisher = FordGeometryReference()
  previous = 0.
  wire = WireCheck()
  # Build, hold, release, tiny rebound and direction change. Each model frame is
  # consumed five times at control cadence, with a real Cap'n Proto round trip.
  for i, action in enumerate([.015]*20+[.008, .004, .001, 0., .0008, -.005, -.015]):
    m, d, sp, _ = messages()
    now_model = .98+i*.05
    m.logMonoTime = round(now_model*1e9)
    m.modelV2.action.desiredCurvature = d.drivingModelData.action.desiredCurvature = action
    apply(publisher, m, d, sp)
    with log.Event.from_bytes(m.to_bytes()) as decoded:
      model = decoded.modelV2
      for j in range(5):
        now = 1.+i*.05+j*.01
        controls.sm.logMonoTime.update(modelV2=m.logMonoTime, carState=round(now*1e9), lateralManeuverPlan=round(now*1e9))
        cc = structs.CarControl(latActive=True)
        cs = SimpleNamespace(vEgo=5., yawRate=0., canValid=True, steeringPressed=False, steeringTorque=0.)
        target = -.1 if maneuver else expected_selector.update(model.action.desiredCurvature, model.fordGeometryReference.selectedCurvature)
        previous, _ = clip_curvature(5., previous, target, 0.)
        expected = baseline.update(model, previous, current_curvature=0., speed=5., yaw_rate=0., now=now,
                                   measurement_time=now, model_time=now_model, reference_time=now if maneuver else now_model,
                                   active=True, curvature_scale=controls.VM.get_steer_from_curvature(1., 5., 0.) /
                                   (controls.CP.steerRatio*controls.CP.wheelbase),
                                   reference_source='lateralManeuverPlan' if maneuver else 'modelV2')
        exec(pipeline[0], {'self': controls, 'CS': cs, 'CC': cc, 'actuators': cc.actuators, 'model_v2': model,
                          'lp': SimpleNamespace(roll=0.), 'clip_curvature': clip_curvature, 'time': SimpleNamespace(monotonic=lambda now=now: now)})
        assert controls.desired_curvature == pytest.approx(previous)
        assert controls.ford_path == expected
        assert controls.ford_path_controller.core.feedback_curvature == pytest.approx(previous)
        assert controls.ford_path_controller.diagnostics['hypothesis'] == 'geometry-assisted-action-feedback-v18'
        if maneuver:
          assert controls.ford_path_controller.geometry_assist.action_peak == 0.
        wire.check(controls.ford_path)
