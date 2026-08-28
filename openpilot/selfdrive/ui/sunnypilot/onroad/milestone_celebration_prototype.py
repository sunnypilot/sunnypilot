"""PROTOTYPE: Tesla-style milestone celebration over the on-road view.

Question: does a brief, full-screen confetti overlay feel at home on comma four?
This deliberately keeps all state in memory and retriggers once on every drive.
"""

import math
import os
import random
import time
from collections import deque
from dataclasses import dataclass

import pyray as rl

from openpilot.selfdrive.ui.mici.onroad.hud_renderer import FONT_SIZES
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.selfdrive.ui.sunnypilot.onroad.milestone_tracker_prototype import (
  AssistCategory,
  DistanceMilestone,
  PerDriveMilestoneTracker,
  TEST_MILESTONE_MILES,
  assist_category,
)
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget


CELEBRATION_DURATION = 4.5
PARTICLE_COUNT = 150

CONFETTI_COLORS = (
  rl.Color(255, 55, 95, 255),
  rl.Color(255, 183, 3, 255),
  rl.Color(48, 209, 88, 255),
  rl.Color(36, 179, 255, 255),
  rl.Color(112, 72, 232, 255),
  rl.Color(255, 45, 196, 255),
)


@dataclass(frozen=True)
class ConfettiParticle:
  x: float
  y: float
  width: float
  height: float
  speed: float
  drift: float
  angle: float
  spin: float
  phase: float
  color: rl.Color


class MilestoneCelebrationPrototype(Widget):
  """Throwaway visual spike enabled on the sunnypilot comma four UI."""

  def __init__(self):
    super().__init__()
    self._drive_started_time = -1.0
    self._celebration_started_time: float | None = None
    self._current_milestone: DistanceMilestone | None = None
    self._pending_milestones: deque[DistanceMilestone] = deque()
    self._tracker = PerDriveMilestoneTracker()
    self._screenshot_taken = False
    self._screenshot_ready = False
    self._particles = self._make_particles()

  @staticmethod
  def _make_particles() -> list[ConfettiParticle]:
    rng = random.Random(20260828)
    return [
      ConfettiParticle(
        x=rng.random(),
        y=rng.uniform(-0.25, 0.95),
        width=rng.uniform(10, 24),
        height=rng.uniform(24, 58),
        speed=rng.uniform(0.12, 0.34),
        drift=rng.uniform(-0.035, 0.035),
        angle=rng.uniform(0, 360),
        spin=rng.uniform(-150, 150),
        phase=rng.uniform(0, math.tau),
        color=CONFETTI_COLORS[rng.randrange(len(CONFETTI_COLORS))],
      )
      for _ in range(PARTICLE_COUNT)
    ]

  def _render(self, rect: rl.Rectangle, /) -> None:
    now = time.monotonic()
    if ui_state.started_time != self._drive_started_time:
      # Reset on every off-road -> on-road transition so the spike can be tested on every drive.
      self._drive_started_time = ui_state.started_time
      self._celebration_started_time = None
      self._current_milestone = None
      self._pending_milestones.clear()
      self._tracker.reset()
      self._screenshot_taken = False
      self._screenshot_ready = False

    car_control = ui_state.sm["carControl"]
    category = assist_category(car_control.latActive, car_control.longActive)

    self._pending_milestones.extend(self._tracker.update(
      ui_state.sm.logMonoTime["carState"],
      ui_state.sm["carState"].vEgo,
      category,
    ))

    if self._current_milestone is None and self._pending_milestones:
      self._current_milestone = self._pending_milestones.popleft()
      self._celebration_started_time = now

    if self._celebration_started_time is None or self._current_milestone is None:
      return

    elapsed = now - self._celebration_started_time
    if elapsed >= CELEBRATION_DURATION:
      self._celebration_started_time = None
      self._current_milestone = None
      return

    alpha = min(1.0, elapsed / 0.2, (CELEBRATION_DURATION - elapsed) / 0.8)
    self._draw_confetti(rect, elapsed, alpha)
    self._draw_milestone(rect, elapsed, alpha, self._current_milestone)
    self._screenshot_ready = elapsed >= 1.0

  def capture_screenshot(self) -> None:
    screenshot_path = os.getenv("SP_MILESTONE_SCREENSHOT")
    if screenshot_path and self._screenshot_ready and not self._screenshot_taken:
      rl.rl_draw_render_batch_active()
      rl.take_screenshot(screenshot_path)
      self._screenshot_taken = True

  def _draw_confetti(self, rect: rl.Rectangle, elapsed: float, alpha: float) -> None:
    travel_height = rect.height * 1.45
    compact = rect.height <= 300
    particle_scale = rect.height / 1080.0
    particles = self._particles[:100] if compact else self._particles
    for particle in particles:
      x = rect.x + rect.width * (particle.x + particle.drift * elapsed + 0.012 * math.sin(elapsed * 3 + particle.phase))
      y = rect.y - rect.height * 0.2 + (particle.y * travel_height + particle.speed * rect.height * elapsed) % travel_height
      flip = 0.2 + 0.8 * abs(math.sin(elapsed * 5 + particle.phase))
      particle_rect = rl.Rectangle(x, y, particle.width * particle_scale * flip, particle.height * particle_scale)
      origin = rl.Vector2(particle_rect.width / 2, particle_rect.height / 2)
      color = rl.Color(particle.color.r, particle.color.g, particle.color.b, int(245 * alpha))
      rl.draw_rectangle_pro(particle_rect, origin, particle.angle + particle.spin * elapsed, color)

  @staticmethod
  def _draw_milestone(rect: rl.Rectangle, elapsed: float, alpha: float, milestone: DistanceMilestone) -> None:
    # Match the comma four set-speed hierarchy: DISPLAY number with a MAX-sized label.
    scale = rect.height / 240.0
    pulse = 1.0 + 0.025 * math.sin(min(elapsed, 0.6) / 0.6 * math.pi)
    number_size = int(FONT_SIZES.set_speed * scale * pulse)
    milestone_size = int(FONT_SIZES.max_speed * scale * pulse)
    category_size = int(22 * scale * pulse)
    unit_size = category_size

    display_font = gui_app.font(FontWeight.DISPLAY)
    semibold_font = gui_app.font(FontWeight.SEMI_BOLD)
    tween_progress = min(elapsed / 0.85, 1.0)
    tween_progress = 1.0 - (1.0 - tween_progress) ** 3
    previous_distance = max(0.0, milestone.distance_miles - TEST_MILESTONE_MILES)
    displayed_distance = previous_distance + (milestone.distance_miles - previous_distance) * tween_progress
    number = f"{displayed_distance:.1f}"
    unit = "MI"
    category = "FULL ASSIST" if milestone.category == AssistCategory.FULL_ASSIST else "MADS"
    milestone_label = "MILESTONE"

    number_bounds = measure_text_cached(display_font, number, number_size)
    unit_bounds = measure_text_cached(semibold_font, unit, unit_size)
    category_bounds = measure_text_cached(semibold_font, category, category_size)
    milestone_bounds = measure_text_cached(semibold_font, milestone_label, milestone_size)

    center_x = rect.x + rect.width / 2
    center_y = rect.y + rect.height / 2
    glow_radius = int(112 * scale * pulse)
    rl.draw_circle_gradient(
      rl.Vector2(center_x, center_y),
      glow_radius,
      rl.Color(0, 0, 0, int(110 * alpha)),
      rl.BLANK,
    )

    text_color = rl.Color(255, 255, 255, int(255 * 0.9 * alpha))
    secondary_color = rl.Color(255, 255, 255, int(255 * 0.72 * alpha))
    number_x = center_x - number_bounds.x / 2
    number_y = center_y - 76 * scale
    unit_y = center_y + 22 * scale
    category_y = center_y - 91 * scale
    milestone_y = center_y + 50 * scale

    rl.draw_text_ex(semibold_font, category, rl.Vector2(center_x - category_bounds.x / 2, category_y),
                    category_size, 0, secondary_color)
    rl.draw_text_ex(display_font, number, rl.Vector2(number_x, number_y), number_size, 0, text_color)
    rl.draw_text_ex(semibold_font, unit, rl.Vector2(center_x - unit_bounds.x / 2, unit_y),
                    unit_size, 0, secondary_color)
    rl.draw_text_ex(semibold_font, milestone_label, rl.Vector2(center_x - milestone_bounds.x / 2, milestone_y),
                    milestone_size, 0, text_color)
