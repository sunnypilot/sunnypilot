import math
from statistics import median

import numpy as np

from openpilot.cereal import custom
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.constants import (
  CAP_FILTER_FRAMES, DEPARTURE_MOTION_NOISE_FLOOR, DEPARTURE_MOTION_STEP_MIN, SPEED_RELIEF_DEADBAND, STOP_HOLD_CREEP_DISTANCE,
  STOP_HOLD_CREEP_SPEED, STOP_HOLD_EXIT_FRAMES,
)
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.lead import LeadPlan


AccelControllerState = custom.LongitudinalPlanSP.AccelController.State


class DepartureTracker:
  def __init__(self) -> None:
    self.samples: list[list[float]] = [[], []]
    self.motion_samples: list[float] = []
    self.references: list[float | None] = [None, None]
    self.track_ids = [-1, -1]

  def separation(self, lead_index: int) -> float:
    samples = self.samples[lead_index]
    return float(median(samples)) if samples else -math.inf

  def update(self, lead_plan: LeadPlan, dt: float) -> None:
    for lead_index, distance in enumerate(lead_plan.departure_lead_distances):
      if not math.isfinite(distance):
        continue
      samples = self.samples[lead_index]
      track_id = lead_plan.departure_lead_track_ids[lead_index]
      identity_changed = bool(samples) and track_id != self.track_ids[lead_index] and (track_id >= 0 or self.track_ids[lead_index] >= 0)
      max_distance_step = max(STOP_HOLD_CREEP_DISTANCE / 2.0, 3.0 * lead_plan.departure_lead_speeds[lead_index] * dt)
      geometry_jump = bool(samples) and abs(distance - samples[-1]) > max_distance_step
      if identity_changed or geometry_jump:
        samples.clear()
        self.references[lead_index] = distance
      samples.append(distance)
      if len(samples) > CAP_FILTER_FRAMES:
        samples.pop(0)
      self.track_ids[lead_index] = track_id
    lead_index = lead_plan.departure_lead_index
    if lead_index >= 0:
      distance = lead_plan.departure_lead_distances[lead_index]
      samples = self.motion_samples
      max_distance_step = max(STOP_HOLD_CREEP_DISTANCE / 2.0, 3.0 * lead_plan.departure_lead_speed * dt)
      if samples and abs(distance - samples[-1]) > max_distance_step:
        samples.clear()
      samples.append(distance)
      if len(samples) > CAP_FILTER_FRAMES:
        samples.pop(0)

  def seed(self, lead_plan: LeadPlan) -> None:
    self.samples = [[], []]
    self.motion_samples = []
    self.references = [None, None]
    self.track_ids = list(lead_plan.departure_lead_track_ids)
    for lead_index, distance in enumerate(lead_plan.departure_lead_distances):
      if math.isfinite(distance):
        self.samples[lead_index].append(distance)
        self.references[lead_index] = distance
    if lead_plan.departure_lead_index >= 0:
      self.motion_samples.append(lead_plan.departure_lead_distances[lead_plan.departure_lead_index])

  def progress(self, lead_plan: LeadPlan, minimum_distance: float) -> bool:
    lead_index = lead_plan.departure_lead_index
    if lead_index < 0 or lead_plan.departure_lead_speed <= STOP_HOLD_CREEP_SPEED:
      return False
    reference = self.references[lead_index]
    distance = self.separation(lead_index)
    return reference is not None and distance - reference >= minimum_distance

  def recent_motion(self) -> bool:
    samples = self.motion_samples[-STOP_HOLD_EXIT_FRAMES:]
    if len(samples) < STOP_HOLD_EXIT_FRAMES:
      return False
    deltas = np.diff(samples)
    return bool(samples[-1] - samples[0] >= DEPARTURE_MOTION_NOISE_FLOOR and np.count_nonzero(deltas > DEPARTURE_MOTION_STEP_MIN) >= 2)

  def backfill_references(self) -> None:
    for lead_index in range(len(self.references)):
      separation = self.separation(lead_index)
      if math.isfinite(separation) and self.references[lead_index] is None:
        self.references[lead_index] = separation

  def keep_latest_motion_sample(self) -> None:
    if self.motion_samples:
      self.motion_samples = self.motion_samples[-1:]


class TargetState:
  def __init__(self) -> None:
    self.cap_samples = [math.inf] * CAP_FILTER_FRAMES
    self.lead_speed_samples = [math.inf] * CAP_FILTER_FRAMES
    self.lead_accel_samples = [0.0] * CAP_FILTER_FRAMES
    self.departure = DepartureTracker()
    self.target_speed: float | None = None
    self.state = AccelControllerState.inactive
    self.departure_frames = self.active_frames = self.lead_loss_frames = self.release_settle_frames = 0
    self.lead_switch_guard_frames = self.lead_switch_elapsed_frames = self.lead_switch_stable_frames = self.stale_frames = 0
    self.selected_lead = self.selected_lead_track_id = -1
    self.launching = self.departure_launch = self.matched_lead = self.lead_dropout = self.release_slew_armed = False
    self.lead_braking = self.e2e_braking_handoff = self.speed_reserve_armed = False
    self.speed_reserve_suppressed = False
    self.matched_accel_limit: float | None = None
    self.release_settle_speed: float | None = None

  def reset_lead_switch_guard(self) -> None:
    self.lead_switch_guard_frames = self.lead_switch_elapsed_frames = self.lead_switch_stable_frames = 0

  def arm_release_slew(self, force: bool = False) -> None:
    if self.release_slew_armed:
      self.release_settle_frames = 0
      return
    if not force and self.release_settle_speed is not None and self.target_speed is not None:
      if self.release_settle_speed - self.target_speed < SPEED_RELIEF_DEADBAND:
        return
    self.release_slew_armed = True
    self.release_settle_frames = 0
    self.release_settle_speed = None

  def reset_release_slew(self, settled_speed: float | None = None) -> None:
    self.release_slew_armed = False
    self.release_settle_frames = 0
    self.release_settle_speed = settled_speed

  def update_release_slew(self, ceiling: float, settled: bool) -> None:
    if not self.release_slew_armed:
      return
    if not settled:
      self.release_settle_frames = 0
    elif self.release_settle_speed is None or ceiling > self.release_settle_speed:
      self.release_settle_frames = 1
      self.release_settle_speed = ceiling
    else:
      self.release_settle_frames += 1
    if self.release_settle_frames >= CAP_FILTER_FRAMES:
      self.release_slew_armed = False
      self.release_settle_frames = 0

  def update_lead_switch_guard(self, arm: bool, confirmed: bool, unstable: bool, hold_frames: int, max_frames: int) -> None:
    if self.lead_switch_elapsed_frames > 0:
      self.lead_switch_stable_frames = 0 if unstable else self.lead_switch_stable_frames + 1
      if self.lead_switch_guard_frames == 0 and self.lead_switch_stable_frames >= hold_frames:
        self.reset_lead_switch_guard()
    if arm and self.lead_switch_elapsed_frames == 0:
      self.lead_switch_guard_frames, self.lead_switch_elapsed_frames = hold_frames, 1
    elif self.lead_switch_guard_frames > 0:
      self.lead_switch_elapsed_frames += 1
      if self.lead_switch_elapsed_frames >= max_frames:
        self.lead_switch_guard_frames = 0
      else:
        self.lead_switch_guard_frames = self.lead_switch_guard_frames - 1 if confirmed else hold_frames

  @property
  def filtered_cap(self) -> float:
    return sorted(self.cap_samples)[CAP_FILTER_FRAMES // 2]

  @property
  def filtered_lead_speed(self) -> float:
    return sorted(self.lead_speed_samples)[CAP_FILTER_FRAMES // 2]

  @property
  def filtered_lead_accel(self) -> float:
    return sorted(self.lead_accel_samples)[CAP_FILTER_FRAMES // 2]

  def update_samples(self, lead_plan: LeadPlan, dt: float) -> bool:
    had_filtered_lead = math.isfinite(self.filtered_cap)
    has_lead = lead_plan.selected_lead >= 0
    self.cap_samples.append(lead_plan.cap if has_lead else math.inf)
    self.lead_speed_samples.append(lead_plan.selected_lead_speed if has_lead else math.inf)
    self.lead_accel_samples.append(lead_plan.selected_lead_accel if has_lead else 0.0)
    self.cap_samples.pop(0)
    self.lead_speed_samples.pop(0)
    self.lead_accel_samples.pop(0)
    self.lead_loss_frames = 0 if has_lead else self.lead_loss_frames + 1
    self.departure.update(lead_plan, dt)
    return not had_filtered_lead and math.isfinite(self.filtered_cap)

  def enter_stop_hold(self, lead_plan: LeadPlan) -> None:
    self.departure.seed(lead_plan)
    self.target_speed = 0.0
    self.state = AccelControllerState.stopHold
    self.departure_frames = 0
    self.launching = self.departure_launch = False
    self.reset_release_slew()
    self.matched_lead = self.speed_reserve_armed = self.speed_reserve_suppressed = False
    self.matched_accel_limit = None
    self.reset_lead_switch_guard()
