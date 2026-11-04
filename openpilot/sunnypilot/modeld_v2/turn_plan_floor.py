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
TURN_PLAN_FLOOR_BP = [4., 8.]
TURN_PLAN_FLOOR_V = [0.85, 0.]


def turn_plan_floor_scale(v_ego: float) -> float:
  return float(np.interp(v_ego, TURN_PLAN_FLOOR_BP, TURN_PLAN_FLOOR_V))


def apply_turn_plan_floor(action_curvature: float, plan_curvature: float, turn_sign: float, scale: float) -> float:
  """Keep the steering command from falling below a scaled share of the model's own plan during a requested turn.

  Curvature is + to the right. turn_sign is +1 for a right turn, -1 for a left turn and 0 when no turn is requested.
  The floor only acts in the turn direction: it can strengthen a turn the action head under-commits to, but never
  weakens or reverses the action. A scale of 0 turns the floor off.
  """
  if turn_sign == 0. or scale <= 0.:
    return action_curvature
  return turn_sign * max(turn_sign * action_curvature, scale * turn_sign * plan_curvature)
