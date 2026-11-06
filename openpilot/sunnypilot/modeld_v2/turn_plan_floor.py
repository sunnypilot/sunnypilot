"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import numpy as np

# Share of the plan-derived curvature the command may not fall below during a requested turn, by speed (m/s).
# The action head falls short of the plan by a roughly fixed lateral acceleration (~0.2 m/s^2), which costs the most
# curvature at low speed: logged turns put it at ~0.65-0.8x the plan below 4 m/s and ~0.85-0.9x above 6 m/s.
# The plan reads tight against driven turns, so the floor stays below 1 and fades out where the action head is close.
# 0.85 was too strong on Light Speed 2 (routes 85/89): below 4 m/s the floor set the command most of the time and every
# hard driver push against the turn came while it did, mostly turning in early when pulling away from a stop. The early
# turn-in is now held off until the plan's corner reaches the front bumper (turn_shaping.py), so from there the floor
# can be the full plan: past the entrance, then a harder turn, so both wheels clear.
TURN_PLAN_FLOOR_BP = [4., 8.]
TURN_PLAN_FLOOR_V = [1.0, 0.]

# The model's own state for the requested turn (meta.desireState) gates the floor. In rolling turns it sits at ~1.0
# while the floor acts. After a wait at a stop it fades to ~0 and is only ~0.6 when pulling away, yet the plan still has
# the turn, so the floor turned in early: the driver pushed back in 48% of those frames vs 9% in rolling turns
# (routes 85/89, Light Speed 2). Below 0.5 the action head steers alone.
TURN_STATE_BP = [0.5, 0.8]
TURN_STATE_V = [0., 1.]


def turn_plan_floor_scale(v_ego: float) -> float:
  return float(np.interp(v_ego, TURN_PLAN_FLOOR_BP, TURN_PLAN_FLOOR_V))


def turn_state_gate(turn_state: float) -> float:
  return float(np.interp(turn_state, TURN_STATE_BP, TURN_STATE_V))


def apply_turn_plan_floor(action_curvature: float, plan_curvature: float, turn_sign: float, scale: float) -> float:
  """Keep the steering command from falling below a scaled share of the model's own plan during a requested turn.

  Curvature is + to the right. turn_sign is +1 for a right turn, -1 for a left turn and 0 when no turn is requested.
  The floor only acts in the turn direction: it can strengthen a turn the action head under-commits to, but never
  weakens or reverses the action. A scale of 0 turns the floor off.
  """
  if turn_sign == 0. or scale <= 0. or turn_sign * plan_curvature <= 0.:
    # with the plan steering out of the turn (a stale desire on exit, or a right straight into a left) the action steers
    return action_curvature
  return turn_sign * max(turn_sign * action_curvature, scale * turn_sign * plan_curvature)
