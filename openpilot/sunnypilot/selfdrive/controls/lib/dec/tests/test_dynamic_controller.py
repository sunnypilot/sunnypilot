import numpy as np

from openpilot.cereal import messaging
from opendbc.car import structs
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.sunnypilot.selfdrive.controls.lib.dec.dec import (
  DecSignals,
  DynamicExperimentalController,
  ModeHysteresis,
  should_blend,
  ENTER_FRAMES,
  MIN_BLENDED_FRAMES,
)

T_IDXS = np.array(ModelConstants.T_IDXS)


class MockParams:
  def __init__(self, enabled=True):
    self._enabled = enabled

  def get_bool(self, name):
    return self._enabled


class MockMpc:
  def __init__(self, crash_cnt=0):
    self.crash_cnt = crash_cnt


def flat_velocity(v):
  return [float(v)] * len(T_IDXS)


def decel_velocity(v0, a):
  return [float(max(0.0, v0 + a * t)) for t in T_IDXS]


def make_car_state(v_ego=10.0, v_cruise=20.0):
  msg = messaging.new_message('carState')
  msg.carState.vEgo = v_ego
  msg.carState.vCruise = v_cruise
  return msg.carState.as_reader()


def make_selfdrive_state(experimental_mode=True):
  msg = messaging.new_message('selfdriveState')
  msg.selfdriveState.experimentalMode = experimental_mode
  return msg.selfdriveState.as_reader()


def make_radar_state(lead_present=False, lead_radar=False, lead_two_present=False):
  msg = messaging.new_message('radarState')
  msg.radarState.leadOne.present = lead_present
  msg.radarState.leadOne.radar = lead_radar
  msg.radarState.leadTwo.present = lead_two_present
  return msg.radarState.as_reader()


def make_model_v2(velocity=None, position_y=None, hard_brake=False, lead_probs=None, frame_drop_perc=0.0):
  msg = messaging.new_message('modelV2')
  msg.modelV2.velocity.x = velocity if velocity is not None else flat_velocity(0.0)
  msg.modelV2.position.y = position_y if position_y is not None else [0.0] * len(T_IDXS)
  msg.modelV2.frameDropPerc = frame_drop_perc
  msg.modelV2.meta.hardBrakePredicted = hard_brake
  if lead_probs is not None:
    msg.modelV2.init('leadsV3', 3)
    for i, (prob, prob_time) in enumerate(zip(lead_probs, (0.0, 2.0, 4.0), strict=True)):
      msg.modelV2.leadsV3[i].prob = prob
      msg.modelV2.leadsV3[i].probTime = prob_time
  return msg.modelV2.as_reader()


def make_sm(v_ego=10.0, v_cruise=20.0, velocity=None, position_y=None, hard_brake=False,
            lead_present=False, lead_radar=False, lead_two_present=False, lead_probs=None,
            frame_drop_perc=0.0, experimental_mode=True):
  return {
    'carState': make_car_state(v_ego, v_cruise),
    'radarState': make_radar_state(lead_present, lead_radar, lead_two_present),
    'modelV2': make_model_v2(velocity, position_y, hard_brake, lead_probs, frame_drop_perc),
    'selfdriveState': make_selfdrive_state(experimental_mode),
  }


def make_controller(cp=None, mpc=None, enabled=True):
  return DynamicExperimentalController(cp or structs.CarParams(), mpc or MockMpc(), params=MockParams(enabled))


class TestDynamicExperimentalController(OpenpilotTestCase):
  def test_initial_mode_is_acc(self):
    controller = make_controller()
    assert controller.mode() == "acc"

  def test_flat_plan_never_blends_at_any_speed(self):
    for v_ego in (2.5, 5.6, 8.3, 13.9, 22.2, 30.6):
      controller = make_controller()
      sm = make_sm(v_ego=v_ego, velocity=flat_velocity(v_ego))
      for _ in range(100):
        controller.update(sm)
      assert controller.mode() == "acc", f"false blend on a flat plan at v_ego={v_ego}"

  def test_highway_slowdown_without_lead_blends(self):
    v0 = 110 / 3.6
    a = (70 / 3.6 - v0) / 6.0
    controller = make_controller()
    sm = make_sm(v_ego=v0, velocity=decel_velocity(v0, a))
    for _ in range(10):
      controller.update(sm)
    assert controller.mode() == "blended"

  def test_curve_exclusion_prevents_false_blend(self):
    controller = make_controller()
    sm = make_sm(v_ego=20.0, velocity=decel_velocity(20.0, -1.0), position_y=[6.0] * len(T_IDXS))
    for _ in range(30):
      controller.update(sm)
    assert controller.mode() == "acc"

  def test_curve_does_not_override_saturated_decel_intent(self):
    controller = make_controller()
    sm = make_sm(v_ego=20.0, velocity=decel_velocity(20.0, -2.0), position_y=[6.0] * len(T_IDXS))
    for _ in range(10):
      controller.update(sm)
    assert controller.mode() == "blended"

  def test_any_lead_forces_acc_even_with_strong_model_signal(self):
    for lead_radar in (True, False):
      controller = make_controller()
      sm = make_sm(v_ego=20.0, velocity=decel_velocity(20.0, -2.0),
                   lead_present=True, lead_radar=lead_radar, lead_probs=[1.0, 1.0, 1.0])
      for _ in range(60):
        controller.update(sm)
        assert controller.mode() == "acc"

  def test_veto_releases_without_rebuild_lag(self):
    controller = make_controller()
    lead_sm = make_sm(v_ego=20.0, velocity=decel_velocity(20.0, -2.0),
                       lead_present=True, lead_probs=[1.0, 1.0, 1.0])
    for _ in range(30):
      controller.update(lead_sm)
    assert controller.mode() == "acc"
    assert controller.lead_veto

    no_lead_sm = make_sm(v_ego=20.0, velocity=decel_velocity(20.0, -2.0), lead_present=False)
    for _ in range(ENTER_FRAMES + 2):
      controller.update(no_lead_sm)
      if controller.mode() == "blended":
        break
    assert controller.mode() == "blended"

  def test_lead_gone_with_no_underlying_slowdown_stays_acc(self):
    controller = make_controller()
    lead_sm = make_sm(v_ego=20.0, velocity=flat_velocity(20.0), lead_present=True, lead_probs=[1.0, 1.0, 1.0])
    for _ in range(30):
      controller.update(lead_sm)
    assert controller.mode() == "acc"

    no_lead_sm = make_sm(v_ego=20.0, velocity=flat_velocity(20.0), lead_present=False)
    for _ in range(20):
      controller.update(no_lead_sm)
    assert controller.mode() == "acc"

  def test_creep_does_not_release_lead_veto(self):
    controller = make_controller()
    sm = make_sm(v_ego=1.0, velocity=flat_velocity(1.0), lead_present=True, lead_probs=[1.0, 1.0, 1.0])
    for _ in range(10):
      controller.update(sm)
    assert controller.mode() == "acc"
    assert controller.lead_veto

  def test_creep_hysteresis_band_without_lead(self):
    controller = make_controller()
    controller.update(make_sm(v_ego=1.5, velocity=flat_velocity(1.5)))
    assert controller.signals.creeping

    controller.update(make_sm(v_ego=2.5, velocity=flat_velocity(2.5)))
    assert controller.signals.creeping, "a small excursion above CREEP_SPEED_ENTER should not exit creeping"

    controller.update(make_sm(v_ego=5.0, velocity=flat_velocity(5.0)))
    assert not controller.signals.creeping, "should exit creeping once genuinely above CREEP_SPEED_EXIT"

  def test_crash_cnt_override_inert_while_lead_present(self):
    mpc = MockMpc(crash_cnt=0)
    controller = make_controller(mpc=mpc)
    sm = make_sm(v_ego=20.0, velocity=flat_velocity(20.0), lead_present=True, lead_probs=[1.0, 1.0, 1.0])
    for _ in range(30):
      controller.update(sm)
    assert controller.mode() == "acc"

    mpc.crash_cnt = 1
    controller.update(sm)
    assert controller.mode() == "acc"

  def test_crash_cnt_blends_within_one_frame_without_lead(self):
    mpc = MockMpc(crash_cnt=1)
    controller = make_controller(mpc=mpc)
    sm = make_sm(v_ego=20.0, velocity=flat_velocity(20.0), lead_present=False)
    controller.update(sm)
    assert controller.mode() == "blended"

  def test_hard_brake_predicted_blends_within_one_frame_without_lead(self):
    controller = make_controller()
    sm = make_sm(v_ego=20.0, velocity=flat_velocity(20.0), hard_brake=True, lead_present=False)
    controller.update(sm)
    assert controller.mode() == "blended"

  def test_hard_brake_override_inert_while_lead_present(self):
    controller = make_controller()
    sm = make_sm(v_ego=20.0, velocity=flat_velocity(20.0), hard_brake=True,
                 lead_present=True, lead_probs=[1.0, 1.0, 1.0])
    controller.update(sm)
    assert controller.mode() == "acc"

  def test_degraded_model_does_not_blend(self):
    controller = make_controller()
    sm = make_sm(v_ego=20.0, velocity=decel_velocity(20.0, -3.0), frame_drop_perc=60.0)
    for _ in range(30):
      controller.update(sm)
    assert controller.mode() == "acc"

  def test_short_plan_arrays_do_not_blend(self):
    controller = make_controller()
    sm = make_sm(v_ego=20.0, velocity=[20.0] * 5)
    for _ in range(30):
      controller.update(sm)
    assert controller.mode() == "acc"

  def test_disabled_param_holds_acc(self):
    controller = make_controller(enabled=False)
    sm = make_sm(v_ego=20.0, velocity=decel_velocity(20.0, -3.0))
    for _ in range(30):
      controller.update(sm)
    assert controller.mode() == "acc"


class TestModeHysteresis(OpenpilotTestCase):
  def test_entry_requires_enter_frames(self):
    h = ModeHysteresis()
    for _ in range(ENTER_FRAMES - 1):
      assert h.update(want_blended=True, override=False, veto=False) == "acc"
    assert h.update(want_blended=True, override=False, veto=False) == "blended"

  def test_override_beats_veto(self):
    h = ModeHysteresis()
    assert h.update(want_blended=False, override=True, veto=True) == "blended"

  def test_veto_forces_acc_even_when_reason_active(self):
    h = ModeHysteresis()
    for _ in range(ENTER_FRAMES + 5):
      assert h.update(want_blended=True, override=False, veto=True) == "acc"

  def test_counter_accumulates_under_veto_then_releases_instantly(self):
    h = ModeHysteresis()
    for _ in range(ENTER_FRAMES + 5):
      h.update(want_blended=True, override=False, veto=True)
    assert h.mode == "acc"
    assert h.update(want_blended=True, override=False, veto=False) == "blended"

  def test_exit_requires_min_dwell_and_sustained_absence(self):
    h = ModeHysteresis()
    for _ in range(ENTER_FRAMES):
      h.update(want_blended=True, override=False, veto=False)
    assert h.mode == "blended"
    for _ in range(MIN_BLENDED_FRAMES - 1):
      assert h.update(want_blended=False, override=False, veto=False) == "blended"
    assert h.update(want_blended=False, override=False, veto=False) == "acc"

  def test_no_flapping_on_alternating_reason(self):
    h = ModeHysteresis()
    changes = 0
    prev = h.mode
    for i in range(200):
      mode = h.update(want_blended=i % 2 == 0, override=False, veto=False)
      changes += mode != prev
      prev = mode
    assert changes == 0


class TestShouldBlend(OpenpilotTestCase):
  def test_slowdown_detected_triggers(self):
    assert should_blend(DecSignals(decel_intent=1.0))
    assert not should_blend(DecSignals(decel_intent=0.0))

  def test_curve_exclusion_suppresses_slowdown(self):
    assert not should_blend(DecSignals(decel_intent=0.7, curve_detected=True))

  def test_curve_exclusion_does_not_override_saturated_decel_intent(self):
    assert should_blend(DecSignals(decel_intent=1.0, curve_detected=True))

  def test_degraded_model_suppresses_model_based_reasons(self):
    s = DecSignals(decel_intent=1.0, model_trust=0.0)
    assert not should_blend(s)

  def test_creep_bypasses_everything(self):
    assert should_blend(DecSignals(model_trust=0.0, creeping=True))
