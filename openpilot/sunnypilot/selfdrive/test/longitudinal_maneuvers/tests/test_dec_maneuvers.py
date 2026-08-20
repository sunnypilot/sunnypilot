import numpy as np

from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.sunnypilot.selfdrive.controls.lib.dec.dec import ENTER_FRAMES, MIN_BLENDED_FRAMES
from openpilot.sunnypilot.selfdrive.test.longitudinal_maneuvers.plant import PlantSP

T_IDXS = np.array(ModelConstants.T_IDXS)


def decel_plan(a):
  def fn(_current_time, speed, _acceleration):
    return [float(max(0.0, speed + a * t)) for t in T_IDXS]
  return fn


def flat_plan():
  def fn(_current_time, speed, _acceleration):
    return [float(speed)] * len(T_IDXS)
  return fn


def alternating_plan(a):
  def fn(current_time, speed, _acceleration):
    frame_a = a if round(current_time / DT_MDL) % 2 == 0 else 0.0
    return [float(max(0.0, speed + frame_a * t)) for t in T_IDXS]
  return fn


def persistent_lead_probs(_current_time):
  return (1.0, 0.95, 0.9)


def _run(plant, steps, v_lead=0.0, v_cruise=50.0):
  solver_failures = 0
  original_reset = plant.planner.mpc.reset

  def counting_reset(*args, **kw):
    nonlocal solver_failures
    if plant.planner.mpc.solution_status != 0:
      solver_failures += 1
    return original_reset(*args, **kw)

  plant.planner.mpc.reset = counting_reset
  return [plant.step(v_lead=v_lead, v_cruise=v_cruise) for _ in range(steps)], solver_failures


def mode_changes(results):
  modes = [r["dec_mode"] for r in results]
  return sum(a != b for a, b in zip(modes, modes[1:], strict=False))


class TestDecManeuvers(OpenpilotTestCase):
  def setUp(self):
    super().setUp()
    self.params = Params()
    self.params.put_bool("DynamicExperimentalControl", True, block=True)

  def test_s1_lead_clears_with_underlying_slowdown_blends_quickly(self):
    clear_t = 1.0

    def lead_obs(current_time, _lead_name, truth):
      return None if current_time >= clear_t else dict(truth)

    plant = PlantSP(lead_relevancy=True, speed=20.0, distance_lead=40.0, e2e=True, only_radar=True,
                     lead_observation_fn=lead_obs, model_plan_fn=decel_plan(-2.5),
                     lead_future_probs_fn=persistent_lead_probs)
    clear_frame = round(clear_t / DT_MDL)
    results, _ = _run(plant, steps=clear_frame + ENTER_FRAMES + 5, v_lead=20.0, v_cruise=20.0)

    assert all(r["dec_mode"] == "acc" for r in results[:clear_frame])
    assert all(r["dec_lead_veto"] for r in results[:clear_frame])
    post_clear = [r["dec_mode"] for r in results[clear_frame:clear_frame + ENTER_FRAMES + 2]]
    assert "blended" in post_clear

  def test_s1b_lead_clears_with_no_underlying_slowdown_stays_acc(self):
    clear_t = 1.0

    def lead_obs(current_time, _lead_name, truth):
      return None if current_time >= clear_t else dict(truth)

    plant = PlantSP(lead_relevancy=True, speed=20.0, distance_lead=40.0, e2e=True, only_radar=True,
                     lead_observation_fn=lead_obs, model_plan_fn=flat_plan(),
                     lead_future_probs_fn=persistent_lead_probs)
    clear_frame = round(clear_t / DT_MDL)
    results, _ = _run(plant, steps=clear_frame + MIN_BLENDED_FRAMES, v_lead=20.0, v_cruise=20.0)

    assert all(r["dec_mode"] == "acc" for r in results)

  def test_s2_steady_highway_following_never_blends(self):
    v = 80.0 / 3.6
    plant = PlantSP(lead_relevancy=True, speed=v, distance_lead=40.0, e2e=True, only_radar=True,
                     model_plan_fn=flat_plan(), lead_future_probs_fn=persistent_lead_probs)
    results, failures = _run(plant, steps=100, v_lead=v, v_cruise=v)

    assert failures <= 1
    assert all(r["dec_mode"] == "acc" for r in results)

  def test_s3_low_speed_cruise_no_lead_never_blends(self):
    v = 15.0 / 3.6
    plant = PlantSP(lead_relevancy=False, speed=v, e2e=True, model_plan_fn=flat_plan())
    results, _ = _run(plant, steps=100, v_cruise=v)

    assert all(r["dec_mode"] == "acc" for r in results)

  def test_s4_highway_slowdown_without_lead_blends(self):
    v0 = 110.0 / 3.6
    a = (70.0 / 3.6 - v0) / 6.0
    plant = PlantSP(lead_relevancy=False, speed=v0, e2e=True, model_plan_fn=decel_plan(a))
    results, _ = _run(plant, steps=10, v_cruise=v0)

    assert any(r["dec_mode"] == "blended" for r in results)

  def test_s5_stop_then_depart_with_lead_present_stays_acc_throughout(self):
    def departing_lead(current_time):
      return 0.0 if current_time < 1.0 else min(15.0, 3.0 * (current_time - 1.0))

    plant = PlantSP(lead_relevancy=True, speed=0.0, distance_lead=6.0, e2e=True)
    results = []
    solver_failures = 0
    original_reset = plant.planner.mpc.reset

    def counting_reset(*args, **kw):
      nonlocal solver_failures
      if plant.planner.mpc.solution_status != 0:
        solver_failures += 1
      return original_reset(*args, **kw)

    plant.planner.mpc.reset = counting_reset
    for _ in range(200):
      results.append(plant.step(v_lead=departing_lead(plant.current_time), v_cruise=15.0))

    assert solver_failures <= 1
    assert all(r["dec_mode"] == "acc" for r in results)
    assert all(r["dec_lead_veto"] for r in results)

  def test_s6_creep_cycles_behind_lead_stay_acc(self):
    def creep_cycle_lead(current_time):
      return 1.5 + 1.5 * np.sin(current_time * 2.0)

    plant = PlantSP(lead_relevancy=True, speed=1.0, distance_lead=8.0, e2e=True, only_radar=True,
                     model_plan_fn=flat_plan(), lead_future_probs_fn=persistent_lead_probs)
    results = [plant.step(v_lead=creep_cycle_lead(plant.current_time), v_cruise=5.0) for _ in range(200)]

    assert all(r["dec_mode"] == "acc" for r in results)

  def test_s7_oscillating_near_threshold_demand_does_not_flap(self):
    plant = PlantSP(lead_relevancy=False, speed=20.0, e2e=True, model_plan_fn=alternating_plan(-2.5))
    results, _ = _run(plant, steps=200, v_cruise=20.0)

    assert mode_changes(results) <= 2

  def test_s8_degraded_model_holds_acc_through_a_slowdown(self):
    def degraded_meta(_current_time):
      return [0.0] * 5, False, 60.0

    plant = PlantSP(lead_relevancy=False, speed=20.0, e2e=True, model_plan_fn=decel_plan(-3.0), model_meta_fn=degraded_meta)
    results, _ = _run(plant, steps=30, v_cruise=20.0)

    assert all(r["dec_mode"] == "acc" for r in results)

  def test_s9_curve_exclusion_prevents_false_blend_on_a_bend(self):
    plant = PlantSP(lead_relevancy=False, speed=20.0, e2e=True, model_plan_fn=decel_plan(-2.5),
                     position_y_fn=lambda _t: [6.0] * len(T_IDXS))
    results, _ = _run(plant, steps=30, v_cruise=20.0)

    assert all(r["dec_mode"] == "acc" for r in results)

  def test_s10_hard_brake_override_inert_while_lead_present(self):
    def hard_brake_meta(_current_time):
      return [0.0] * 5, True, 0.0

    plant = PlantSP(lead_relevancy=True, speed=20.0, distance_lead=40.0, e2e=True, only_radar=True,
                     model_plan_fn=flat_plan(), model_meta_fn=hard_brake_meta, lead_future_probs_fn=persistent_lead_probs)
    results, _ = _run(plant, steps=10, v_lead=20.0, v_cruise=20.0)

    assert all(r["dec_mode"] == "acc" for r in results)
