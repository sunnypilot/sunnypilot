"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

# Share of the plan-derived curvature the command may not fall below during a requested turn. The plan-derived
# curvature reads ~15-20% tighter than turns actually driven, so it is only trusted as a scaled-down floor.
TURN_PLAN_FLOOR = 0.75


def apply_turn_plan_floor(action_curvature: float, plan_curvature: float, turn_sign: float,
                          scale: float = TURN_PLAN_FLOOR) -> float:
  """Keep the steering command from falling below a scaled share of the model's own plan during a requested turn.

  Curvature is + to the right. turn_sign is +1 for a right turn, -1 for a left turn and 0 when no turn is requested.
  The floor only acts in the turn direction: it can strengthen a turn the action head under-commits to, but never
  weakens or reverses the action.
  """
  if turn_sign == 0.:
    return action_curvature
  return turn_sign * max(turn_sign * action_curvature, scale * turn_sign * plan_curvature)
