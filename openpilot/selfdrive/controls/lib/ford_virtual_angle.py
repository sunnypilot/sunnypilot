"""Experimental curvature-equivalent angle servo for the Lightning RL38 EPS.

One planner reference, bounded PI/rate feedback, and delayed command history.
The C0/C1 conversion is nominal firmware algebra, NOT an identified wheel plant.
"""
from collections import deque
from dataclasses import dataclass
import math
import struct

from opendbc.car.ford.values import FordFlags
from openpilot.selfdrive.controls.lib.ford_path import DBC_ANGLE, DBC_OFFSET, FordPath


# Normalized field conversion from ML3V-BD. RL38 road validation is still needed.
# C0 carries the reference; C1 carries a bounded corrective acceleration.
C0_PER_ACCEL = 0.6015625
C1_PER_ACCEL = 0.030078125
_C0_LIMIT = min(abs(v) for v in DBC_OFFSET)
_C1_LIMIT = min(abs(v) for v in DBC_ANGLE)
_MAX_AGE = 0.15
_MAX_DT = 0.1


def _clip(value, lower, upper):
  return min(max(value, lower), upper)


def _packed(value, resolution, offset):
  """Mirror Float32 carControlSP and the sign-reversed CANPacker rounding."""
  value = struct.unpack('f', struct.pack('f', value))[0]
  return -(math.floor((-value - offset) / resolution + 0.5) * resolution + offset)


@dataclass(frozen=True)
class ServoTuning:
  kp: float = 0.35
  ki: float = 0.15
  kd: float = 0.04
  rate_filter: float = 0.15
  feedback_limit: float = 1.5  # nominal m/s^2, not measured EPS authority
  integral_limit: float = 0.75
  offset_rate: float = 1.5  # m/s, limits host requests, not a claim about RL38 internal slew
  heading_rate: float = 0.1  # rad/s


class FordVirtualAngleController:
  """Track the bounded planner curvature, equivalent to its vehicle-model angle.

  Histories contain published, packing-equivalent requests, not EPS execution
  acknowledgments. Feedback waits for the configured response interval, and
  discounts corrections still pending within that interval. It never projects
  the wheel with an unbounded constant-rate extrapolation.
  """

  def __init__(self, response_delay=0.2, tuning: ServoTuning | None = None):
    tuning = tuning if tuning is not None else ServoTuning()
    if not math.isfinite(response_delay) or not 0.05 <= response_delay <= 0.5:
      raise ValueError("response delay must be within 0.05..0.5 seconds")
    if not all(math.isfinite(v) and v >= 0 for v in vars(tuning).values()) or min(
      tuning.rate_filter, tuning.feedback_limit, tuning.integral_limit, tuning.offset_rate, tuning.heading_rate,
    ) <= 0:
      raise ValueError("invalid servo tuning")
    self.delay = response_delay
    self.tuning = tuning
    self.history = deque(maxlen=512)
    self.diagnostics = {}
    self.reset()

  def reset(self):
    self.history.clear()
    self.last_time = None
    self.last_measurement_time = None
    self.last_curvature = 0.0
    self.curvature_rate = 0.0
    self.integral = 0.0
    self.last_reference_accel = 0.0
    self.command = FordPath()
    self.offset_request = 0.0
    self.heading_request = 0.0
    self.stalled = False
    self.diagnostics = {"status": "inactive", "hypothesis": "virtual-angle-v1", "command": (0.0, 0.0, 0.0, 0.0)}

  def _at(self, time):
    """Causal interpolation of retained (time, reference curvature, feedback, measurement)."""
    previous = self.history[0]
    for current in self.history:
      if current[0] >= time:
        fraction = _clip((time - previous[0]) / max(current[0] - previous[0], 1e-9), 0.0, 1.0)
        return tuple(a + fraction * (b - a) for a, b in zip(previous[1:], current[1:], strict=True))
      previous = current
    return previous[1:]

  def update(self, desired_curvature, *, current_curvature, speed, now, measurement_time, reference_time,
             active, valid=True, steering_pressed=False, limited=False):
    finite = all(math.isfinite(v) for v in (desired_curvature, current_curvature, speed, now, measurement_time, reference_time))
    fresh = finite and -0.005 <= now - measurement_time <= _MAX_AGE and -0.005 <= now - reference_time <= _MAX_AGE
    if not active or not valid or not fresh or not 0.3 <= speed <= 55.0 or max(abs(desired_curvature), abs(current_curvature)) > 1.0:
      self.reset()
      self.diagnostics['status'] = 'inactive' if not active else 'invalid_input'
      return self.command

    dt = 0.01 if self.last_time is None else now - self.last_time
    if not 0.002 <= dt <= _MAX_DT or (self.last_measurement_time is not None and measurement_time < self.last_measurement_time):
      self.reset()
      self.diagnostics['status'] = 'timing_reset'
      return self.command
    self.last_time = now
    tuning = self.tuning
    speed_squared = speed * speed

    if not self.history:
      self.history.append((now - self.delay, current_curvature, 0.0, current_curvature))
      self.last_curvature = current_curvature
      self.last_measurement_time = measurement_time
    if measurement_time > self.last_measurement_time:
      measurement_dt = measurement_time - self.last_measurement_time
      rate = (current_curvature - self.last_curvature) / measurement_dt
      alpha = measurement_dt / (tuning.rate_filter + measurement_dt)
      self.curvature_rate += alpha * (rate - self.curvature_rate)
      self.last_curvature = current_curvature
      self.last_measurement_time = measurement_time

    # The input is already the planner's actuator-delay-aware, bounded reference.
    # Do not advance it again or add a second model-pose reference.
    reference_accel = desired_curvature * speed_squared
    offset_target = _clip(C0_PER_ACCEL * reference_accel, -_C0_LIMIT, _C0_LIMIT)
    # Preserve fractional LSBs between cycles; limiting the rounded value can
    # otherwise change the sustained slew rate with cycle time or turn sign.
    self.offset_request = _clip(offset_target, self.offset_request - tuning.offset_rate * dt,
                                self.offset_request + tuning.offset_rate * dt)
    offset = _packed(self.offset_request, 0.01, DBC_OFFSET[0])

    delayed_reference, delayed_feedback, _ = self._at(measurement_time - self.delay)
    error = (delayed_reference - current_curvature) * speed_squared
    previous_feedback = self.command.path_angle / C1_PER_ACCEL
    pending = previous_feedback - delayed_feedback
    proportional = tuning.kp * (error - pending)
    damping = _clip(-tuning.kd * self.curvature_rate * speed_squared, -tuning.feedback_limit, tuning.feedback_limit)

    # Old-direction bias must discharge with the reference, including release
    # to straight. Avoid spending seconds unwinding an integral after a turn.
    if reference_accel * self.last_reference_accel <= 0:
      self.integral = 0.0
    elif abs(reference_accel) < abs(self.last_reference_accel):
      self.integral *= abs(reference_accel / self.last_reference_accel)
    self.last_reference_accel = reference_accel

    # A sizable corrective-command increase without corresponding motion is
    # evidence against further integration even if EPS reports no limit flag.
    stalled_evidence = False
    if self.history[0][0] <= now - 1.0:
      _, old_feedback, old_curvature = self._at(now - 1.0)
      correction_change = previous_feedback - old_feedback
      measured_change = (current_curvature - old_curvature) * speed_squared
      stalled_evidence = correction_change * error > 0 and abs(correction_change) > 0.2 and abs(measured_change) < 0.02
      if abs(measured_change) > 0.05 or self.integral * error <= 0:
        self.stalled = False
    self.stalled |= stalled_evidence

    # About one C1 LSB in nominal corrective acceleration: do not integrate
    # sub-resolution error. Integral state is independent of road speed.
    integral_error = math.copysign(max(abs(error) - 0.02, 0.0), error)
    candidate_integral = _clip(self.integral + tuning.ki * integral_error * dt, -tuning.integral_limit, tuning.integral_limit)
    freeze = limited or self.stalled or abs(offset - offset_target) > 0.0051
    if freeze:
      candidate_integral = self.integral
    if steering_pressed:
      candidate_integral = self.integral = 0.0
      proportional = damping = 0.0
      self.stalled = False

    requested_feedback = proportional + damping + candidate_integral
    feedback = _clip(requested_feedback, -tuning.feedback_limit, tuning.feedback_limit)
    heading_target = _clip(C1_PER_ACCEL * feedback, -_C1_LIMIT, _C1_LIMIT)
    self.heading_request = _clip(heading_target, self.heading_request - tuning.heading_rate * dt,
                                 self.heading_request + tuning.heading_rate * dt)
    heading = _packed(self.heading_request, 0.0005, DBC_ANGLE[0])
    applied_feedback = heading / C1_PER_ACCEL
    # Conditional integration at output/rate limits; allow error to unwind it.
    output_limited = abs(requested_feedback - applied_feedback) > 0.00026 / C1_PER_ACCEL
    if not freeze and (not output_limited or error * (requested_feedback - applied_feedback) <= 0):
      self.integral = candidate_integral

    self.command = FordPath(True, offset, heading, 0.0, 0.0)
    self.history.append((now, offset / C0_PER_ACCEL / speed_squared, applied_feedback, current_curvature))
    while len(self.history) > 2 and self.history[1][0] < now - 1.5:
      self.history.popleft()
    self.diagnostics = {
      "status": "driver_override" if steering_pressed else "active", "hypothesis": "virtual-angle-v1",
      "reference": desired_curvature, "measured": current_curvature, "delayed_reference": delayed_reference,
      "error_accel": error, "pending_feedback": pending, "p": proportional, "d": damping, "i": self.integral,
      "integrator_frozen": bool(freeze or steering_pressed or output_limited), "stalled": bool(self.stalled),
      "response_delay": self.delay, "measurement_age": now - measurement_time, "reference_age": now - reference_time,
      "command": (offset, heading, 0.0, 0.0),
    }
    return self.command


def select_virtual_angle_controller(CP, enabled, previous_controller):
  # The source route analysis covers only this vehicle/firmware.
  compatible = CP.brand == 'ford' and CP.flags & FordFlags.CANFD and CP.carFingerprint == 'FORD_F_150_LIGHTNING_MK1'
  firmware = compatible and any(str(fw.ecu) == 'eps' and bytes(fw.fwVersion).rstrip(b'\0') == b'RL38-14D003-AA' for fw in CP.carFw)
  if enabled and firmware:
    return FordVirtualAngleController(CP.steerActuatorDelay)
  return previous_controller
