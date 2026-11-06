"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

# Share of the plan-derived curvature the command may not fall below during a requested turn. The plan-derived
# curvature reads ~15-20% tighter than turns actually driven, so it is only trusted as a scaled-down floor.
# Routes 93-96 (CD210): the layers built on top of this (a speed fade, a gate on the model's own turn state, a turn-in
# hold, look-ahead and route scaling) made turns unreliable, so it's back to this alone, at every turn speed.
TURN_PLAN_FLOOR = 0.75


def apply_turn_plan_floor(action_curvature: float, plan_curvature: float, turn_sign: float,
                          scale: float = TURN_PLAN_FLOOR) -> float:
  """Keep the steering command from falling below a scaled share of the model's own plan during a requested turn.

  Curvature is + to the right. turn_sign is +1 for a right turn, -1 for a left turn and 0 when no turn is requested.
  The floor only acts in the turn direction: it can strengthen a turn the action head under-commits to, but never
  weakens or reverses the action.
  """
  if turn_sign == 0. or turn_sign * plan_curvature <= 0.:
    # with the plan steering out of the turn (a stale desire on exit, or a right straight into a left) the action steers
    return action_curvature
  return turn_sign * max(turn_sign * action_curvature, scale * turn_sign * plan_curvature)
