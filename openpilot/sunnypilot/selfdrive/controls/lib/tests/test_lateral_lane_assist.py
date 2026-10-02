from types import SimpleNamespace

import numpy as np

from openpilot.common.constants import CV
from openpilot.sunnypilot.selfdrive.controls.lib.lateral_lane_assist import (
  CURVE_OUTWARD_DEADZONE,
  LANE_CENTER_FADE_SPEED_BP,
  LANE_CENTER_MAX_CURV,
  LateralLaneAssist,
  LaneCentering,
  apply_curve_outward_bias,
)


class FakeParams:
  def __init__(self, curve=False, centering=False):
    self.values = {
      "LateralCurveCuttingCorrection": curve,
      "LateralLaneCentering": centering,
    }

  def get_bool(self, key):
    return self.values[key]


def make_model(offset_left=0.0, heading_left=0.0, width=3.6, probs=(0.9, 0.9), lane_change=0):
  x = np.arange(0.0, 30.0, 2.0)
  center_right = offset_left + np.tan(heading_left) * x
  lines = [
    SimpleNamespace(x=x, y=center_right - width / 2 - 3.0),
    SimpleNamespace(x=x, y=center_right - width / 2),
    SimpleNamespace(x=x, y=center_right + width / 2),
    SimpleNamespace(x=x, y=center_right + width / 2 + 3.0),
  ]
  return SimpleNamespace(laneLines=lines, laneLineProbs=[0.1, probs[0], probs[1], 0.1],
                         meta=SimpleNamespace(laneChangeState=lane_change))


def test_curve_cutting_correction_is_outward_only_and_speed_scheduled():
  curvature = 0.01
  assert apply_curve_outward_bias(curvature, 30 * CV.KPH_TO_MS) == curvature
  assert apply_curve_outward_bias(CURVE_OUTWARD_DEADZONE / 2, 100 * CV.KPH_TO_MS) == CURVE_OUTWARD_DEADZONE / 2
  for k in (curvature, -curvature):
    corrected = apply_curve_outward_bias(k, 100 * CV.KPH_TO_MS)
    assert 0.0 < abs(corrected) < abs(k)
    assert corrected * k > 0.0


def test_lane_centering_corrects_offset_with_bounded_smooth_request():
  speed = 100 * CV.KPH_TO_MS
  controller = LaneCentering(dt=0.01)
  outputs = [controller.update(make_model(offset_left=0.4), speed, True, False) for _ in range(400)]
  assert outputs[-1] > 0.0  # car left of centre -> positive (right) curvature
  assert max(abs(v) for v in outputs) <= LANE_CENTER_MAX_CURV
  max_step = controller.dt * 0.25 / speed ** 2
  assert max(abs(b - a) for a, b in zip(outputs, outputs[1:], strict=False)) <= max_step + 1e-12


def test_lane_centering_rejects_uncertain_lines_driver_input_and_lane_changes():
  speed = 100 * CV.KPH_TO_MS
  controller = LaneCentering(dt=0.01)
  assert controller.update(make_model(offset_left=0.5, probs=(0.1, 0.1)), speed, True, False) == 0.0
  assert controller.update(make_model(offset_left=0.5), speed, True, True) == 0.0
  assert controller.update(make_model(offset_left=0.5, lane_change=1), speed, True, False) == 0.0


def test_lane_centering_fades_in_above_highway_threshold_and_unwinds_when_inactive():
  speed_low = LANE_CENTER_FADE_SPEED_BP[0] - 1.0
  controller = LaneCentering(dt=0.01)
  assert controller.update(make_model(offset_left=0.5), speed_low, True, False) == 0.0
  speed_high = LANE_CENTER_FADE_SPEED_BP[1] + 1.0
  outputs = [controller.update(make_model(offset_left=0.5), speed_high, True, False) for _ in range(400)]
  assert outputs[-1] > 0.0
  unwound = [controller.update(make_model(offset_left=0.5), speed_high, False, False) for _ in range(100)]
  assert abs(unwound[-1]) < abs(outputs[-1])


def test_assist_settings_are_independent_and_off_by_default():
  disabled = LateralLaneAssist(dt=0.01, params=FakeParams())
  curvature = 0.01
  assert disabled.update(curvature, 100 * CV.KPH_TO_MS, True, False, make_model(offset_left=0.5)) == curvature

  curve_only = LateralLaneAssist(dt=0.01, params=FakeParams(curve=True))
  assert curve_only.update(curvature, 100 * CV.KPH_TO_MS, True, False, make_model()) != curvature
  assert curve_only.update(curvature, 100 * CV.KPH_TO_MS, True, False, make_model(lane_change=1)) == curvature
