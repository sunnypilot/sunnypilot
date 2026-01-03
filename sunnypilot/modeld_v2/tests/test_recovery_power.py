import numpy as np

from cereal import log

from openpilot.sunnypilot.modeld_v2.constants import Plan
from openpilot.sunnypilot.modeld_v2.modeld import ModelState
import openpilot.sunnypilot.modeld_v2.modeld as modeld


class MockStruct:
  def __init__(self, **kwargs):
    for k, v in kwargs.items():
      setattr(self, k, v)


def test_recovery_power_scaling():
  state = MockStruct(
    PLANPLUS_CONTROL=1.0,
    LONG_SMOOTH_SECONDS=0.3,
    LAT_SMOOTH_SECONDS=0.1,
    MIN_LAT_CONTROL_SPEED=0.3,
    mlsim=True,
    generation=12,
    constants=MockStruct(T_IDXS=np.arange(100), DESIRE_LEN=8)
  )
  prev_action = log.ModelDataV2.Action()
  recorded_vel: list = []

  def mock_accel(plan_vel, plan_accel, t_idxs, action_t=0.0):
    recorded_vel.append(plan_vel.copy())
    return 0.0, False

  modeld.get_accel_from_plan = mock_accel
  modeld.get_curvature_from_output = lambda *args: 0.0
  plan = np.random.rand(1, 100, 15).astype(np.float32)
  planplus = np.random.rand(1, 100, 15).astype(np.float32)

  model_output: dict = {
    'plan': plan.copy(),
    'planplus': planplus.copy()
  }

  test_cases: list = [
    # (control, v_ego, expected_factor)
    (0.55, 20.0, 1.0),
    (1.0, 25.0, .75),
    (1.5, 25.1, 0.75),
    (2.0, 20.0, 1.0),
    (0.75, 19.0, 1.0),
    (0.8, 25.1, 0.75),
  ]

  for control, v_ego, factor in test_cases:
    state.PLANPLUS_CONTROL = control
    recorded_vel.clear()
    ModelState.get_action_from_model(state, model_output, prev_action, 0.0, 0.0, v_ego)

    expected_recovery_power = control * factor
    expected_plan_vel = plan[0, :, Plan.VELOCITY][:, 0] + expected_recovery_power * planplus[0, :, Plan.VELOCITY][:, 0]

    np.testing.assert_allclose(recorded_vel[0], expected_plan_vel, rtol=1e-5, atol=1e-6)
