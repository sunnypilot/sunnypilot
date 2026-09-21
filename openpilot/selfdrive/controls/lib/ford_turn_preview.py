"""Model geometry gates a bounded action forecast; it is not a steering target."""
import math


class FordTurnPreview:
  def __init__(self):
    self.previous_time = 0
    self.previous_action = 0.0
    self.previous_valid = False
    self.sample = {'valid': False}

  def update(self, model, model_time, valid):
    # controlsd runs faster than modeld. Preserve the derivative between model
    # messages and do the array work only once per new model timestamp.
    if model_time == self.previous_time:
      return self.sample
    import numpy as np

    action = float(model.action.desiredCurvature)
    dt = (model_time - self.previous_time) * 1e-9
    action_valid = valid and math.isfinite(action)
    rate = -(action - self.previous_action) / dt if action_valid and self.previous_valid and 0.0 < dt <= 0.15 else 0.0
    self.previous_time, self.previous_action, self.previous_valid = model_time, action, action_valid
    self.sample = {'valid': False, 'modelMonoTime': model_time}
    if not action_valid or model.meta.laneChangeState != 0:
      return self.sample
    x, y, heading = (np.asarray(v, dtype=float) for v in (model.position.x, model.position.y, model.orientation.z))
    if len(x) < 2 or len(x) != len(y) or len(x) != len(heading) or not all(np.all(np.isfinite(v)) for v in (x, y, heading)):
      return self.sample
    station = np.r_[0.0, np.cumsum(np.hypot(np.diff(x), np.diff(y)))]
    if station[-1] < 14.0:
      return self.sample
    heading = np.unwrap(heading)
    h7, h14 = (-float(np.degrees(np.interp(d, station, heading) - heading[0])) for d in (7.0, 14.0))
    self.sample.update(valid=True, heading7=h7, heading14=h14, actionRate=rate)
    return self.sample


def turn_preview_lead(requested_rate, preview, now):
  """Return wheel-angle lead and geometry weight in the native pinion sign."""
  if preview is None or not preview.valid or not 0.0 <= now - preview.modelMonoTime * 1e-9 <= 0.15:
    return 0.0, 0.0
  h7, h14, raw_rate = preview.heading7, preview.heading14, preview.actionRate
  if not all(math.isfinite(v) for v in (h7, h14, raw_rate, requested_rate)) or h7 * h14 <= 0.0:
    return 0.0, 0.0
  weight = min(max(0.0, min(1.0, (abs(h7) - 5.0) / 5.0)), max(0.0, min(1.0, (abs(h14) - 20.0) / 10.0)))
  direction = math.copysign(1.0, h14)
  if direction * raw_rate <= 0.0 or direction * requested_rate <= 0.0:
    return 0.0, weight
  # Trial choices, not recovered Ford constants: 0.20 s lead, at most 30 deg.
  return direction * weight * min(30.0, 0.20 * direction * requested_rate), weight
