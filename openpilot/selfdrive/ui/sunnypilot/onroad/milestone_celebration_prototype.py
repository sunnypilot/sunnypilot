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

from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.selfdrive.ui.sunnypilot.onroad.milestone_tracker_prototype import (
  AssistCategory,
  DistanceMilestone,
  PerDriveMilestoneTracker,
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
    self._draw_milestone_card(rect, elapsed, alpha, self._current_milestone)
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
  def _draw_milestone_card(rect: rl.Rectangle, elapsed: float, alpha: float, milestone: DistanceMilestone) -> None:
    compact = rect.height <= 300
    scale = rect.height / (240.0 if compact else 1080.0)
    card_width = (210 if compact else 590) * scale
    card_height = (82 if compact else 230) * scale
    pulse = 1.0 + 0.025 * math.sin(min(elapsed, 0.6) / 0.6 * math.pi)
    card_width *= pulse
    card_height *= pulse
    card = rl.Rectangle(
      rect.x + (rect.width - card_width) / 2,
      rect.y + (rect.height - card_height) / 2,
      card_width,
      card_height,
    )

    rl.draw_rectangle_rounded(card, 0.20, 16, rl.Color(25, 31, 42, int(225 * alpha)))
    rl.draw_rectangle_rounded_lines_ex(card, 0.20, 16, max(1, int(2 * scale)), rl.Color(255, 255, 255, int(90 * alpha)))

    number_font = gui_app.font(FontWeight.BOLD)
    label_font = gui_app.font(FontWeight.MEDIUM)
    number_size = int((35 if compact else 98) * scale)
    label_size = int((14 if compact else 42) * scale)
    number = f"{milestone.distance_miles:.1f} mi"
    label = "FULL ASSIST MILESTONE" if milestone.category == AssistCategory.FULL_ASSIST else "MADS MILESTONE"

    number_bounds = measure_text_cached(number_font, number, number_size)
    label_bounds = measure_text_cached(label_font, label, label_size)
    number_y = 9 if compact else 35
    label_y = 55 if compact else 145
    number_pos = rl.Vector2(card.x + (card.width - number_bounds.x) / 2, card.y + number_y * scale)
    label_pos = rl.Vector2(card.x + (card.width - label_bounds.x) / 2, card.y + label_y * scale)
    rl.draw_text_ex(number_font, number, number_pos, number_size, 0, rl.Color(255, 255, 255, int(255 * alpha)))
    rl.draw_text_ex(label_font, label, label_pos, label_size, 2 * scale, rl.Color(220, 226, 235, int(230 * alpha)))
