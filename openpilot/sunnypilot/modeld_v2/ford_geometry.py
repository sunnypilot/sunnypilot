"""Optional Ford reference from the published plan, using modeld's own timing."""
import numpy as np

from opendbc.car.ford.values import FordFlags
from openpilot.selfdrive.controls.lib.drive_helpers import MIN_STABLE_DELAY, get_curvature_from_plan, smooth_value


def select_ford_geometry_reference(CP, controller_enabled, geometry_enabled):
  if controller_enabled and geometry_enabled and CP.brand == 'ford' and CP.flags & FordFlags.CANFD:
    return FordGeometryReference()
  return None


class FordGeometryReference:
  def __init__(self):
    self.previous = 0.

  def update(self, yaws, yaw_rates, times, *, speed, preview, smooth_seconds, smoothing_enabled):
    # Reject an incomplete/nonfinite plan instead of extrapolating beyond it.
    yaws, yaw_rates, times = (np.asarray(x) for x in (yaws, yaw_rates, times))
    if (yaws.ndim != 1 or yaw_rates.shape != yaws.shape or times.shape != yaws.shape or len(times) < 2
        or not np.isfinite([speed, preview, smooth_seconds]).all() or speed < 0 or preview <= 0 or smooth_seconds < 0
        or not all(np.isfinite(x).all() for x in (yaws, yaw_rates, times))
        or times[0] != 0 or not np.all(np.diff(times) > 0) or times[-1] < max(preview, MIN_STABLE_DELAY)):
      self.previous = 0.
      return None
    raw = float(get_curvature_from_plan(yaws, yaw_rates, times, speed, preview))
    selected = raw
    if smoothing_enabled:
      selected = float(smooth_value(raw, self.previous, smooth_seconds)) if speed > .3 else self.previous
    if not np.isfinite([raw, selected]).all() or max(abs(raw), abs(selected)) > float(np.finfo(np.float32).max):
      self.previous = 0.
      return None
    self.previous = selected
    return raw, selected

  def apply(self, model_msg, driving_msg, sp_msg, *, speed, preview, smooth_seconds, smoothing_enabled):
    """Publish geometry alongside the untouched action for controlsd's selector.

    Embed the pair in modelV2 as well as diagnostic telemetry so controlsd never
    has to join independently delivered publications from different frames.
    """
    model = model_msg.modelV2
    ref = sp_msg.modelDataV2SP.fordGeometryReference
    ref.enabled = True
    ref.modelMonoTime = model_msg.logMonoTime
    ref.actionDesiredCurvature = model.action.desiredCurvature
    ref.previewSeconds = preview
    ref.smoothSeconds = smooth_seconds if smoothing_enabled else 0.
    result = self.update(model.orientation.z, model.orientationRate.z, model.orientation.t,
                         speed=speed, preview=preview, smooth_seconds=smooth_seconds, smoothing_enabled=smoothing_enabled)
    ref.valid = result is not None
    if result is not None:
      ref.rawCurvature, ref.selectedCurvature = result
    else:
      ref.selectedCurvature = model.action.desiredCurvature
    model.fordGeometryReference = ref
