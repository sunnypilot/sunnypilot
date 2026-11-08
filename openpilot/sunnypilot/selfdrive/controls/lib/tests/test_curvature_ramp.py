"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pytest

from openpilot.sunnypilot.selfdrive.controls.lib.curvature_ramp import CurvatureRamp, RAMP_TICKS


def run(ramp, frames, ticks_per_frame=RAMP_TICKS, active=True):
  """frames: one model curvature per model frame; each held for ticks_per_frame control ticks, as controlsd sees it."""
  out = []
  for f in frames:
    for k in range(ticks_per_frame):
      out.append(ramp.update(f, k == 0, active))
  return out


def test_a_step_is_spread_evenly_over_one_model_frame():
  ramp = CurvatureRamp()
  ramp.update(0., True, True)
  out = [ramp.update(0.05, k == 0, True) for k in range(RAMP_TICKS)]
  assert out == pytest.approx([0.05 * (k + 1) / RAMP_TICKS for k in range(RAMP_TICKS)])


def test_the_command_reaches_each_model_value_by_the_end_of_its_frame():
  frames = [0., 0.01, 0.03, 0.02, 0.06]
  out = run(CurvatureRamp(), frames)
  ends = out[RAMP_TICKS - 1::RAMP_TICKS]
  assert ends == pytest.approx(frames)


def test_no_tick_jumps_more_than_a_fifth_of_the_frame_change():
  frames = [0., 0.04, 0.04, -0.02, 0.08]
  out = run(CurvatureRamp(), frames)
  steps = [abs(b - a) for a, b in zip(out, out[1:], strict=False)]
  assert max(steps) <= 0.1 / RAMP_TICKS + 1e-9


def test_a_dropped_model_frame_holds_the_last_value():
  ramp = CurvatureRamp()
  run(ramp, [0.])
  out = [ramp.update(0.05, k == 0, True) for k in range(2 * RAMP_TICKS)]
  assert out[RAMP_TICKS - 1:] == pytest.approx([0.05] * (RAMP_TICKS + 1))


def test_a_new_frame_mid_ramp_continues_from_where_the_command_is():
  ramp = CurvatureRamp()
  run(ramp, [0.])
  a = ramp.update(0.05, True, True)
  b = ramp.update(0.05, False, True)
  c = ramp.update(-0.05, True, True)  # early frame
  assert c == pytest.approx(b + (-0.05 - b) / RAMP_TICKS)
  assert a < b


def test_inactive_passes_the_target_through_and_restarts_from_it():
  ramp = CurvatureRamp()
  assert ramp.update(0.03, True, False) == 0.03
  assert ramp.update(0.04, False, False) == 0.04
  # engaging: ramps from where the car was, not from an old command
  assert ramp.update(0.08, True, True) == pytest.approx(0.04 + 0.04 / RAMP_TICKS)
