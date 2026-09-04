"""Default-off Ford C2-free path experiment."""
from dataclasses import dataclass
import math

import numpy as np

from opendbc.car.ford.values import FordFlags
from openpilot.selfdrive.controls.lib.ford_path import DBC_ANGLE, DBC_OFFSET, FordPath


# For a constant-curvature path, y(H) ~= 0.5 * curvature * (speed * H)^2.
# This horizon makes the recovered C0 contribution equal the recovered C2
# contribution: 0.5 * y(H) == 0.30078125 * speed^2 * curvature.
_C2_FREE_HORIZON_S = math.sqrt(0.30078125 / 0.25)
_C0_RANGE = (-min(abs(DBC_OFFSET[0]), abs(DBC_OFFSET[1])), min(abs(DBC_OFFSET[0]), abs(DBC_OFFSET[1])))
_C1_RANGE = (-min(abs(DBC_ANGLE[0]), abs(DBC_ANGLE[1])), min(abs(DBC_ANGLE[0]), abs(DBC_ANGLE[1])))


@dataclass(frozen=True)
class _C2FreeRequest:
  command: FordPath
  model_offset: float
  model_heading: float
  predicted_heading: float
  arc: float


def _clip(value: float, limits: tuple[float, float]) -> float:
  return min(max(value, limits[0]), limits[1])


def _wrap(angle: float) -> float:
  return math.atan2(math.sin(angle), math.cos(angle))


def _sample(time: list[float], values: list[float]) -> float:
  return float(np.interp(_C2_FREE_HORIZON_S, time, values))


def _c2_free_request(model, current_curvature: float) -> _C2FreeRequest | None:
  """Encode one temporal model pose through C0/C1 without charging C2."""
  try:
    time = [float(value) for value in model.position.t]
    x = [float(value) for value in model.position.x]
    y = [float(value) for value in model.position.y]
    heading = [float(value) for value in model.orientation.z]
    current_curvature = float(current_curvature)
  except (AttributeError, TypeError, ValueError):
    return None
  if (len(time) < 2 or len(time) != len(x) or len(time) != len(y) or len(time) != len(heading) or
      not math.isfinite(current_curvature) or
      not all(math.isfinite(value) for values in (time, x, y, heading) for value in values) or
      any(after <= before for before, after in zip(time[:-1], time[1:], strict=True)) or
      not time[0] <= _C2_FREE_HORIZON_S <= time[-1]):
    return None

  unwrapped_heading = np.unwrap(heading).tolist()
  target_x = _sample(time, x)
  target_y = _sample(time, y)
  target_heading = _sample(time, unwrapped_heading)
  distance = [0.0]
  for i in range(1, len(x)):
    distance.append(distance[-1] + math.hypot(x[i] - x[i - 1], y[i] - y[i - 1]))
  arc = _sample(time, distance)

  dx = target_x - x[0]
  dy = target_y - y[0]
  cosine = math.cos(unwrapped_heading[0])
  sine = math.sin(unwrapped_heading[0])
  model_offset = -sine * dx + cosine * dy
  model_heading = _wrap(target_heading - unwrapped_heading[0])
  predicted_heading = current_curvature * arc
  heading_residual = _wrap(model_heading - predicted_heading)
  command = FordPath(
    valid=True,
    path_offset=_clip(model_offset, _C0_RANGE),
    path_angle=_clip(heading_residual, _C1_RANGE),
    curvature=0.0,
    curvature_rate=0.0,
  )
  return _C2FreeRequest(command, model_offset, model_heading, predicted_heading, arc)


class FordSharedPathController:
  """Use model C0 and residual C1 directly, with C2/C3 always zero."""

  def __init__(self):
    self.diagnostics: dict[str, object] = {"status": "initializing", "hypothesis": "ML3V-BD-C2-free-v1"}

  def update(self, model, desired_curvature: float, *, current_curvature: float = 0.0, v_ego: float = 0.0,
             v_ego_raw: float = 0.0, active: bool = True, now: float | None = None) -> FordPath:
    request = _c2_free_request(model, current_curvature) if active and model is not None else None
    status = "inactive" if not active else "invalid_input" if request is None else "active"
    result = request.command if request is not None else FordPath(valid=active)
    self.diagnostics = {
      "status": status, "hypothesis": "ML3V-BD-C2-free-v1", "horizon_s": _C2_FREE_HORIZON_S,
      "model_offset": request.model_offset if request else None,
      "model_heading": request.model_heading if request else None,
      "predicted_heading": request.predicted_heading if request else None,
      "heading_residual": _wrap(request.model_heading - request.predicted_heading) if request else None,
      "arc": request.arc if request else None,
      "command": (result.path_offset, result.path_angle, result.curvature, result.curvature_rate),
    }
    return result


def select_shared_path_controller(brand, flags, enabled, previous_controller):
  if enabled and brand == "ford" and flags & FordFlags.CANFD:
    return FordSharedPathController()
  return previous_controller
