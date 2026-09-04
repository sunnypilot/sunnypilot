"""Experimental shared path loop. The BD contribution map is a hypothesis, not a vehicle plant.

All contributions below are divided by the firmware's common speed gain. They
are neither curvature nor steering angle. Keep this experiment separate from
the default controller until its closed-loop response has been validated.
"""
from dataclasses import dataclass
from itertools import product
import math
import struct

from opendbc.can import CANPacker
from opendbc.car.ford.values import CarControllerParams, FordFlags
from openpilot.selfdrive.controls.lib.ford_path import (
  DBC_ANGLE, DBC_CURVATURE, DBC_OFFSET, FordPath, FordPathController,
  _model_path, _path_pose, _predicted_pose, _relative_pose,
)

_GENTLE_CURVATURE = 0.006
_FULL_POSE_CURVATURE = 0.012
_PREVIEW_DISTANCE = 7.0
_PREDICTION_TIME = 0.1
_CONTRIBUTION_LIMITS = (0.5, 0.349609375, 0.5)
_FAST_AUTHORITY = sum(_CONTRIBUTION_LIMITS[:2])
_FIRMWARE_DT = 0.004
_STATE_RATES = (1.5, 0.100006103515625, 0.0030059814453125)
_INACTIVE_RATES = (300.0, 30.0, 2.0)
_RESOLUTIONS = (0.01, 0.0005, 0.00002)
_RANGES = tuple((-min(abs(lo), abs(hi)), min(abs(lo), abs(hi))) for lo, hi in (DBC_OFFSET, DBC_ANGLE, DBC_CURVATURE))
_UNKNOWN_RANGES = (*_RANGES[:2], (-0.03024, 0.03024))  # includes an earlier C2 + 10*C3 target


def _clip(value, lower, upper):
  return min(max(value, lower), upper)


def contributions(values, speed):
  weights = (0.5, 10.0, 0.30078125 * speed ** 2)
  return tuple(_clip(w * v, -limit, limit) for w, v, limit in zip(weights, values, _CONTRIBUTION_LIMITS, strict=True))


def _values(path):
  return path.path_offset, path.path_angle, path.curvature


def _advance(state, command, ticks, rates=_STATE_RATES):
  return tuple(_clip(target, value - rate * ticks * _FIRMWARE_DT, value + rate * ticks * _FIRMWARE_DT)
               for value, target, rate in zip(state, command, rates, strict=True))


@dataclass(frozen=True)
class PathRequest:
  total: float
  feedforward: float
  feedback: float
  preferred: FordPath
  offset_error: float
  heading_error: float


def request_for_model(model, desired_curvature: float, *, current_curvature: float, v_ego: float,
                      response_speed: float | None = None) -> PathRequest | None:
  path = _model_path(model) if model is not None else None
  if path is None or not all(math.isfinite(v) for v in (desired_curvature, current_curvature, v_ego)):
    return None
  speed = max(v_ego, 0.0)
  response_speed = speed if response_speed is None else max(response_speed, 0.0)
  if not math.isfinite(response_speed):
    return None
  advance = min(speed * _PREDICTION_TIME, path[0][-1])
  horizon = min(_PREVIEW_DISTANCE, path[0][-1] - advance)
  if horizon <= 1e-3:
    return None
  offset, angle = _relative_pose(advance + horizon, path, _path_pose(advance, path))
  error_y, error_heading = _relative_pose(advance, path, _predicted_pose(advance, current_curvature, 0.0))
  demand = max(abs(2.0 * offset / horizon ** 2), abs(angle / horizon), abs(desired_curvature))

  # A soft residual beyond the existing gentle-curvature envelope, not p*pose.
  # On a circular path its amplitude grows linearly with excess curvature.
  excess = max(0.0, 1.0 - _GENTLE_CURVATURE / max(demand, _GENTLE_CURVATURE))
  recovery = max(0.0, 1.0 - _GENTLE_CURVATURE / max(abs(current_curvature), _GENTLE_CURVATURE))
  correction_share = max(excess, recovery)
  offset_ff, angle_ff = excess * offset, excess * angle
  base_curvature = _clip(desired_curvature, -_GENTLE_CURVATURE, _GENTLE_CURVATURE)
  feedforward = _clip(sum(contributions((offset_ff, angle_ff, base_curvature), response_speed)), -_FAST_AUTHORITY, _FAST_AUTHORITY)
  # Correct AFTER nominal feedforward saturation. Otherwise a large raw preview
  # can swallow an unwind correction without changing predicted contribution.
  feedback = _clip(correction_share * (0.5 * error_y + 10.0 * error_heading), -_FAST_AUTHORITY, _FAST_AUTHORITY)
  total = _clip(feedforward + feedback, -_FAST_AUTHORITY, _FAST_AUTHORITY)

  allocation_demand = max(demand, abs(current_curvature))
  share = _clip((allocation_demand - _GENTLE_CURVATURE) / (_FULL_POSE_CURVATURE - _GENTLE_CURVATURE), 0.0, 1.0)
  preferred = FordPath(True, _clip(offset_ff + correction_share * error_y, *_RANGES[0]),
                       _clip(angle_ff + correction_share * error_heading, *_RANGES[1]),
                       _clip(desired_curvature * (1.0 - share), *_RANGES[2]), 0.0)
  return PathRequest(total, feedforward, feedback, preferred, error_y, error_heading)


class ContributionAllocator:
  """Allocate a separately supplied total under the nominal BD coefficient model.

  Unknown history starts as an interval, not zero. An interval becoming narrow
  means the NOMINAL recurrence has initialized, not that firmware equivalence
  or successful PSCM execution has been established.
  """

  def __init__(self, dt=0.01, *, initial_state=None):
    self.dt = dt
    self.lower = tuple(bounds[0] for bounds in _UNKNOWN_RANGES) if initial_state is None else tuple(initial_state)
    self.upper = tuple(bounds[1] for bounds in _UNKNOWN_RANGES) if initial_state is None else tuple(initial_state)
    self.command = FordPath()
    self.last_path = FordPath()
    self.sent_curvature = 0.0
    signals = CANPacker('ford_lincoln_base_pt').dbc.name_to_msg['LateralMotionControl2'].sigs
    self._wire_signals = tuple(signals[name] for name in ('LatCtlPathOffst_L_Actl', 'LatCtlPath_An_Actl', 'LatCtlCurv_No_Actl'))
    self._has_command = False
    self.phase = 0.0
    self.predicted_total = 0.0
    self.shortfall = 0.0
    self.predicted_peak_error = 0.0

  @property
  def state(self):
    return tuple((low + high) * 0.5 for low, high in zip(self.lower, self.upper, strict=True))

  @property
  def initialized(self):
    return all(high - low <= resolution * 0.5 for low, high, resolution in zip(self.lower, self.upper, _RESOLUTIONS, strict=True))

  def advance(self, elapsed):
    if not math.isfinite(elapsed) or elapsed < 0.0 or elapsed > 0.1:
      self.lower = tuple(bounds[0] for bounds in _UNKNOWN_RANGES)
      self.upper = tuple(bounds[1] for bounds in _UNKNOWN_RANGES)
      self.phase = 0.0
      return
    if not self._has_command:
      return
    self.phase += elapsed
    ticks = int((self.phase + 1e-12) / _FIRMWARE_DT)
    self.phase -= ticks * _FIRMWARE_DT
    rates = _STATE_RATES if self.command.valid else _INACTIVE_RATES
    self.lower = _advance(self.lower, _values(self.command), ticks, rates)
    self.upper = _advance(self.upper, _values(self.command), ticks, rates)

  def _packet_field(self, index, value, speed):
    # carControlSP uses Float32; CANPacker rounds in the sign-reversed DBC
    # coordinate system with floor(x + .5), NOT Python's ties-to-even round.
    value = struct.unpack('f', struct.pack('f', value))[0]
    if index == 2 and speed is not None:
      value = CarControllerParams.CURVATURE_LIMITS.apply_limits(
        value, self.sent_curvature, speed, 0.0, True, CarControllerParams.LMC2_STEP,
      )
    signal = self._wire_signals[index]
    return -(math.floor((-value - signal.offset) / signal.factor + 0.5) * signal.factor + signal.offset), value

  def _packet(self, values, speed=None):
    fields = tuple(self._packet_field(i, value, speed) for i, value in enumerate(values))
    return tuple(field[0] for field in fields), fields[2][1]

  def set_command(self, command, speed=None):
    if command.curvature_rate != 0.0:
      raise ValueError("C3 is not part of this experiment")
    self.last_path = command
    self._has_command = True
    if command.valid:
      packed, self.sent_curvature = self._packet(_values(command), speed)
      self.command = FordPath(True, *packed, 0.0)
    else:
      self.command = FordPath()
      self.sent_curvature = 0.0

  @staticmethod
  def tolerance(speed):
    # Half a wire LSB in each normalized contribution, not a tuning deadband.
    return 0.5 * (0.5 * _RESOLUTIONS[0] + 10.0 * _RESOLUTIONS[1] + 0.30078125 * speed ** 2 * _RESOLUTIONS[2])

  def _bounds(self, preferred, speed):
    previous = _values(self.last_path)
    low = [_clip(previous[0] - 4.0 * self.dt, *_RANGES[0]), _clip(previous[1] - self.dt, *_RANGES[1])]
    high = [_clip(previous[0] + 4.0 * self.dt, *_RANGES[0]), _clip(previous[1] + self.dt, *_RANGES[1])]
    # C2 may move only toward the preferred range. In large maneuvers that
    # range is exactly zero: unreachable fast demand must NOT refill C2.
    limits = CarControllerParams.CURVATURE_LIMITS
    for bounds, target in ((low, min(0.0, preferred.curvature)), (high, max(0.0, preferred.curvature))):
      bounds.append(limits.apply_limits(target, self.sent_curvature, speed, 0.0, True, CarControllerParams.LMC2_STEP))
    return tuple(low), tuple(high)

  def _continuous_candidate(self, requested, preferred, speed, low, high, ticks):
    state = self.state
    qlow = contributions(_advance(state, low, ticks), speed)
    qhigh = contributions(_advance(state, high, ticks), speed)
    total = _clip(requested, sum(qlow), sum(qhigh))
    qpref = contributions(_advance(state, _values(preferred), ticks), speed)
    slow = _clip(qpref[2], max(qlow[2], total - qhigh[0] - qhigh[1]), min(qhigh[2], total - qlow[0] - qlow[1]))
    fast = total - slow
    q0 = _clip(0.5 * (fast + qpref[0] - qpref[1]), max(qlow[0], fast - qhigh[1]), min(qhigh[0], fast - qlow[1]))
    weights = (0.5, 10.0, 0.30078125 * speed ** 2)
    # Minimum latent coefficient for this contribution; no benefit is assumed
    # from continuing to wind a state beyond its nominal contribution plateau.
    return tuple(_clip(q / weight if weight else pref, lo, hi)
                 for q, weight, pref, lo, hi in zip((q0, fast - q0, slow), weights, _values(preferred), low, high, strict=True))

  def allocate(self, requested, preferred, speed):
    if not self.initialized:
      raise ValueError("coefficient history is not initialized")
    if not all(math.isfinite(v) for v in (requested, speed, *_values(preferred))) or speed < 0.0 or preferred.curvature_rate != 0.0:
      raise ValueError("invalid allocation request")
    low, high = self._bounds(preferred, speed)
    ticks = max(1, int((self.phase + self.dt + 1e-12) / _FIRMWARE_DT))
    candidates = {tuple(_clip(v, lo, hi) for v, lo, hi in zip(_values(path), low, high, strict=True))
                  for path in (preferred, self.last_path)}
    for horizon in {1, ticks}:
      candidate = self._continuous_candidate(requested, preferred, speed, low, high, horizon)
      neighbors = [tuple({_clip(round(value / resolution) * resolution + shift * resolution, lo, hi) for shift in (-1, 0, 1)})
                   for value, resolution, lo, hi in zip(candidate, _RESOLUTIONS, low, high, strict=True)]
      candidates.update(product(*neighbors))

    qpref = contributions(_values(preferred), speed)
    weights = (0.5, 10.0, 0.30078125 * speed ** 2)
    tolerance = self.tolerance(speed)
    state = self.state
    effects = []
    # Candidate packets share most coefficient values. Packing, limiting and
    # projecting each field once avoids repeating them for every combination.
    # Keep the original candidates, score order and all intermediate ticks.
    for i, (weight, limit, rate) in enumerate(zip(weights, _CONTRIBUTION_LIMITS, _STATE_RATES, strict=True)):
      cache = {}
      for value in {candidate[i] for candidate in candidates}:
        packed, _ = self._packet_field(i, value, speed)
        totals = tuple(_clip(weight * _clip(packed, bound[i] - rate * tick * _FIRMWARE_DT,
                                            bound[i] + rate * tick * _FIRMWARE_DT), -limit, limit)
                       for bound in (self.lower, self.upper) for tick in range(1, ticks + 1))
        endpoint = _clip(weight * _clip(packed, state[i] - rate * ticks * _FIRMWARE_DT,
                                       state[i] + rate * ticks * _FIRMWARE_DT), -limit, limit)
        cache[value] = totals, endpoint, max(0.0, abs(weight * packed) - limit)
      effects.append(cache)
    best = None
    for candidate in sorted(candidates):
      fields = tuple(cache[value] for cache, value in zip(effects, candidate, strict=True))
      totals = [sum(parts) for parts in zip(*(field[0] for field in fields), strict=True)]
      endpoint = tuple(field[1] for field in fields)
      worst_error = max(abs(total - requested) for total in totals)
      latent = sum(field[2] for field in fields)
      score = (round(max(0.0, worst_error - tolerance), 12), abs(endpoint[2] - qpref[2]),
               (endpoint[0] - qpref[0]) ** 2 + (endpoint[1] - qpref[1]) ** 2, latent,
               sum((new - old) ** 2 for new, old in zip(candidate, _values(self.last_path), strict=True)))
      if best is None or score < best[0]:
        best = score, candidate, sum(endpoint), worst_error

    assert best is not None
    _, command, self.predicted_total, self.predicted_peak_error = best
    self.shortfall = requested - self.predicted_total
    result = FordPath(True, *command, 0.0)
    self.set_command(result, speed)
    return result


class FordSharedPathController:
  """Default-off live experiment: independent demand, feedback, and allocation."""

  def __init__(self, dt=0.01):
    self.dt = dt
    self.allocator = ContributionAllocator(dt)
    self.fallback = FordPathController(dt)
    self.last_time = None
    self.diagnostics = {"status": "initializing", "hypothesis": "ML3V-BD-normalized-v1"}

  def update(self, model, desired_curvature: float, *, current_curvature=0.0, v_ego=0.0,
             v_ego_raw=0.0, active=True, now=None):
    elapsed = self.dt if now is None or self.last_time is None else now - self.last_time
    self.last_time = now
    self.allocator.advance(elapsed)
    # Keep fallback history current, seeded from the command actually requested
    # by this controller. A missing model/history must not cause an output jump.
    self.fallback._last_path = self.allocator.last_path
    valid_inputs = all(math.isfinite(v) for v in (desired_curvature, current_curvature, v_ego, v_ego_raw))
    baseline = self.fallback.update(model if valid_inputs else None, desired_curvature, current_curvature=current_curvature,
                                    v_ego=v_ego, active=active)
    speed = max(v_ego_raw, 0.0) if math.isfinite(v_ego_raw) else 0.0
    request = request_for_model(model, desired_curvature, current_curvature=current_curvature, v_ego=v_ego,
                                response_speed=speed) if active and valid_inputs else None
    status = "inactive" if not active else "invalid_input" if request is None else "warming_history" if not self.allocator.initialized else "active"
    # The reference uses filtered travel speed, while contribution scheduling
    # and the unchanged downstream curvature limiter use raw wheel speed.
    if status == "active":
      result = self.allocator.allocate(request.total, request.preferred, speed)
    else:
      curvature = CarControllerParams.CURVATURE_LIMITS.apply_limits(
        baseline.curvature, self.allocator.sent_curvature, speed, 0.0, True, CarControllerParams.LMC2_STEP,
      ) if baseline.valid else 0.0
      result = FordPath(baseline.valid, _clip(baseline.path_offset, *_RANGES[0]), _clip(baseline.path_angle, *_RANGES[1]), curvature, 0.0)
      self.allocator.set_command(result, speed)
    self.diagnostics = {
      "status": status, "hypothesis": "ML3V-BD-normalized-v1",
      "requested": request.total if request else 0.0,
      "feedforward": request.feedforward if request else 0.0,
      "feedback": request.feedback if request else 0.0,
      "offset_error": request.offset_error if request else 0.0,
      "heading_error": request.heading_error if request else 0.0,
      "state": self.allocator.state,
      "state_width": tuple(hi - lo for lo, hi in zip(self.allocator.lower, self.allocator.upper, strict=True)),
      "predicted_total": self.allocator.predicted_total if status == "active" else 0.0,
      "predicted_peak_error": self.allocator.predicted_peak_error if status == "active" else 0.0,
      "shortfall": self.allocator.shortfall if status == "active" else 0.0,
    }
    return result


def select_shared_path_controller(brand, flags, enabled, previous_controller):
  if enabled and brand == "ford" and flags & FordFlags.CANFD:
    return FordSharedPathController()
  return previous_controller
