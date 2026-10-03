from collections.abc import Callable
import math
from typing import cast

from openpilot.common.parameterized import parameterized
from openpilot.common.realtime import DT_MDL
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.test.longitudinal_maneuvers.plant import Plant
from openpilot.sunnypilot.selfdrive.test.longitudinal_maneuvers.plant import PlantSP

STOCK_STEP_KEYS = ("distance", "speed", "acceleration", "should_stop", "distance_lead", "fcw")


def departing_lead(current_time: float) -> float:
  return 0.0 if current_time < 1.0 else min(2.0, 2.0 * (current_time - 1.0))


def stopped_lead(_current_time: float) -> float:
  return 0.0


PARITY_SCENARIOS = {
  "approach_stopped_lead": {"lead_relevancy": True, "speed": 15.0, "distance_lead": 60.0, "v_cruise": 20.0, "v_lead": stopped_lead, "steps": 80},
  "stop_then_depart": {"lead_relevancy": True, "speed": 0.0, "distance_lead": 6.0, "v_cruise": 8.0, "v_lead": departing_lead, "steps": 120},
}


def _drive(cls, *, v_cruise: float, v_lead: Callable[[float], float], steps: int, **kwargs):
  plant = cls(**kwargs)
  plant.v_lead_prev = v_lead(0.0)
  solver_failures = 0
  original_reset = plant.planner.mpc.reset

  def counting_reset(*args, **kw):
    nonlocal solver_failures
    if plant.planner.mpc.solution_status != 0:
      solver_failures += 1
    return original_reset(*args, **kw)

  plant.planner.mpc.reset = counting_reset
  results = []
  for _ in range(steps):
    lead_speed = v_lead(plant.current_time)
    result = plant.step(v_lead=lead_speed, v_cruise=v_cruise)
    results.append((result, plant.planner.mpc.source, plant.planner.output_a_target))
  return results, solver_failures


class TestPlantSP(OpenpilotTestCase):
  @parameterized.expand(PARITY_SCENARIOS, names=("scenario",), ids=lambda scenario: scenario)
  def test_plant_sp_matches_stock_plant_on_shared_kwargs(self, scenario: str):
    kwargs = dict(PARITY_SCENARIOS[scenario])
    v_cruise = cast(float, kwargs.pop("v_cruise"))
    v_lead = cast(Callable[[float], float], kwargs.pop("v_lead"))
    steps = cast(int, kwargs.pop("steps"))

    stock_results, stock_failures = _drive(Plant, v_cruise=v_cruise, v_lead=v_lead, steps=steps, **kwargs)
    sp_results, sp_failures = _drive(PlantSP, v_cruise=v_cruise, v_lead=v_lead, steps=steps, **kwargs)

    assert stock_failures == 0, f"stock Plant solver failed {stock_failures} times in {scenario!r}"
    assert sp_failures == 0, f"PlantSP solver failed {sp_failures} times in {scenario!r}"

    for frame, ((stock_result, stock_source, stock_a_target), (sp_result, sp_source, sp_a_target)) in enumerate(
      zip(stock_results, sp_results, strict=True),
    ):
      for key in STOCK_STEP_KEYS:
        if isinstance(stock_result[key], float):
          self.assertAlmostEqual(sp_result[key], stock_result[key], msg=f"{scenario} frame {frame} key {key}")
        else:
          assert sp_result[key] == stock_result[key], f"{scenario} frame {frame} key {key}"
      assert sp_source == stock_source, f"{scenario} frame {frame} mpc.source"
      self.assertAlmostEqual(sp_a_target, stock_a_target, msg=f"{scenario} frame {frame} output_a_target")

    if scenario == "stop_then_depart":
      departure_frame = round(1.0 / DT_MDL)
      for results in (stock_results, sp_results):
        assert all(result["speed"] < 0.01 for result, _, _ in results[:departure_frame])
        assert results[departure_frame - 1][0]["should_stop"]
        assert any(not result["should_stop"] for result, _, _ in results[departure_frame:])
        assert any(result["speed"] > 0.05 for result, _, _ in results[departure_frame:])
      stock_release = next(frame for frame, (result, _, _) in enumerate(stock_results)
                           if frame >= departure_frame and not result["should_stop"])
      sp_release = next(frame for frame, (result, _, _) in enumerate(sp_results)
                        if frame >= departure_frame and not result["should_stop"])
      stock_motion = next(frame for frame, (result, _, _) in enumerate(stock_results)
                          if frame >= departure_frame and result["speed"] > 0.05)
      sp_motion = next(frame for frame, (result, _, _) in enumerate(sp_results)
                       if frame >= departure_frame and result["speed"] > 0.05)
      assert sp_release == stock_release
      assert sp_motion == stock_motion

  def test_full_lead_observation_is_independent_from_truth(self):
    callback_inputs = []

    def observe_lead(current_time, lead_name, truth):
      callback_inputs.append((current_time, lead_name, truth))
      if lead_name == "leadOne":
        return {
          "dRel": 12.5,
          "vRel": -4.0,
          "vLead": 6.0,
          "vLeadK": 5.5,
          "aLeadK": -1.25,
          "aLeadTau": 0.7,
          "present": True,
          "modelProb": 0.9,
          "radarTrackId": 42,
        }
      return None

    plant = PlantSP(lead_relevancy=True, speed=10.0, distance_lead=50.0, lead_observation_fn=observe_lead)
    result = plant.step(v_lead=8.0)

    assert [entry[1] for entry in callback_inputs] == ["leadOne", "leadTwo"]
    self.assertAlmostEqual(callback_inputs[0][2]["dRel"], 50.0)
    self.assertAlmostEqual(result["truth_lead"]["dRel"], 50.0)
    self.assertAlmostEqual(result["lead_one_observation"]["dRel"], 12.5)
    assert result["lead_one_observation"]["radarTrackId"] == 42
    assert result["lead_two_observation"] is None
    self.assertAlmostEqual(result["distance_lead"], 50.0 + 8.0 * DT_MDL)

  def test_model_action_realized_acceleration_and_source_logging(self):
    def model_action(current_time, v_ego, a_ego):
      return -1.25, True

    plant = PlantSP(speed=10.0, e2e=True, force_decel=True, model_action_fn=model_action, actuator_lag=0.5)
    first = plant.step()
    second = plant.step()

    assert first["model_action"] == {"desiredAcceleration": -1.25, "shouldStop": True}
    self.assertAlmostEqual(first["published_a_ego"], 0.0)
    self.assertAlmostEqual(second["published_a_ego"], first["realized_acceleration"])
    assert first["acceleration"] == first["realized_acceleration"]
    assert abs(first["realized_acceleration"]) < abs(first["actuator_command"])
    assert first["mpc_source"] is not None
    assert first["dec_mode"] in ("acc", "blended")
    assert "controller_active" in first
    assert first["lead_one_observation"] is not None
    assert first["truth_lead"] == first["lead_one_observation"]

  def test_default_model_action_matches_stock_plant(self):
    result = PlantSP(speed=10.0).step()

    self.assertAlmostEqual(result["model_action"]["desiredAcceleration"], 0.5)
    assert not result["model_action"]["shouldStop"]

  def test_configurable_transport_delay_and_first_order_lag(self):
    plant = PlantSP(speed=10.0, actuator_delay=2 * DT_MDL, actuator_lag=0.2)

    self.assertAlmostEqual(plant.planner.CP.longitudinalActuatorDelay, 2 * DT_MDL)
    delayed_commands = [plant._update_actuator(-1.0) for _ in range(3)]
    assert [command for command, _ in delayed_commands[:2]] == [0.0, 0.0]

    expected_acceleration = -(1.0 - math.exp(-DT_MDL / 0.2))
    assert delayed_commands[2][0] == -1.0
    self.assertAlmostEqual(delayed_commands[2][1], expected_acceleration)

  @parameterized.expand(
    [(-0.1, 0.0), (float("nan"), 0.0), (float("inf"), 0.0), (None, -0.1), (None, float("nan")), (None, float("inf"))],
    names=("delay", "lag"),
  )
  def test_invalid_actuator_dynamics(self, delay, lag):
    with self.assertRaises(ValueError):
      PlantSP(actuator_delay=delay, actuator_lag=lag)
