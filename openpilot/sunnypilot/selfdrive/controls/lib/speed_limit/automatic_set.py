"""Map-based automatic SET for the Honda City non-PCM longitudinal configuration.

Decision helpers and a bounded read of mapd's SHM evidence. No CAN or services.
"""
import math
import json


def read_map_evidence():
  try:
    with open('/dev/shm/params/d/MapSpeedLimitEvidence', 'rb') as stream:
      raw = stream.read(4097)
    return json.loads(raw) if len(raw) <= 4096 else None
  except (OSError, ValueError, UnicodeError, RecursionError):
    return None


def auto_supported(cp):
  return (cp.brand == 'honda' and cp.carFingerprint == 'HONDA_CITY_7G'
          and cp.openpilotLongitudinalControl and not cp.pcmCruise
          and not cp.dashcamOnly and not cp.passive)


def fresh_message(sm, topic, now, maximum_age):
  stamp = sm.logMonoTime[topic]
  return bool(sm.seen[topic] and sm.valid[topic] and stamp > 0
              and 0 <= round(now * 1e9) - stamp <= maximum_age * 1e9)


def resolve_auto_map(stable, sm, gps_service, now, offset_type, offset_value, is_metric, evidence=None):
  gps, mapped = sm[gps_service], sm['liveMapDataSP']
  valid = (fresh_message(sm, gps_service, now, 3)
           and fresh_message(sm, 'liveMapDataSP', now, 3)
           and gps.hasFix and mapped.speedLimitValid)
  limit = mapped.speedLimit
  if evidence is None:
    stable.reset()
    return None
  try:
    token = evidence['position']['logMonoTime']
    proof_limit = evidence['speedLimit']
    valid = (valid and evidence['version'] == 1 and evidence['valid'] is True
             and type(token) is int and token > 0 and 0 <= round(now * 1e9) - token <= 3_000_000_000
             and math.isfinite(proof_limit) and abs(proof_limit - limit) <= 0.001)
  except (TypeError, KeyError, ValueError, OverflowError):
    stable.reset()
    return None
  if not valid:
    stable.reset()
    return None
  # The sidecar retains mapd's double precision; liveMapDataSP uses Float32.
  # Do not let transport rounding turn an exact minimum limit into a lower SET.
  limit = proof_limit
  if offset_type == 0:
    offset = 0.
  elif offset_type == 1:
    offset = offset_value * (1 / 3.6 if is_metric else 0.44704)
  elif offset_type == 2:
    offset = limit * offset_value * 0.01
  else:
    stable.reset()
    return None
  return stable.update(now, token, limit, limit + offset,
                       valid, (offset_type, offset_value, is_metric))


class StableMapLimit:
  def __init__(self):
    self.reset()

  def reset(self):
    self.candidate = None
    self.first_stamp = self.last_stamp = 0

  def update(self, now, stamp, limit, target, valid, context):
    if (not valid or not all(math.isfinite(v) for v in (now, limit, target))
        or not 0 < limit <= 145 / 3.6 or not 0 < target <= 145 / 3.6
        or stamp <= 0 or not 0 <= round(now * 1e9) - stamp <= 10_000_000_000):
      self.reset()
      return None
    candidate = (round(limit, 5), round(target, 5), context)
    if candidate != self.candidate or stamp < self.last_stamp:
      self.candidate = candidate
      self.first_stamp = stamp
    self.last_stamp = stamp
    # Time must advance in distinct source messages, not repeated cached plans.
    return target if stamp - self.first_stamp >= 2_000_000_000 else None


class AutomaticSet:
  def __init__(self):
    self.engaged = False
    self.takeover = False
    self.armed = False
    self.quiet_since = None

  def update(self, *, now, selected, supported, enabled, available, control_ok,
             pedal, manual_event, manual_press, cancel, held, target, current, minimum):
    if not enabled:
      self.engaged = self.takeover = self.armed = False
      self.quiet_since = None
      return None
    initial = not self.engaged
    self.engaged = True
    if not selected or not supported:
      self.armed = False
      self.quiet_since = None
      return None
    if cancel or pedal or (not initial and (manual_press or (self.armed and manual_event))):
      self.takeover = True
    if self.takeover:
      return None
    if initial or held or manual_event:
      self.quiet_since = None
      return None
    if self.quiet_since is None:
      self.quiet_since = now
    if now - self.quiet_since < 0.5:
      return None
    self.armed = True
    if not available or not control_ok or target is None:
      return None
    if not all(math.isfinite(v) for v in (target, current, minimum)):
      return None
    if not minimum <= target <= 145 or not minimum <= current <= 145:
      return None
    target = round(target, 1)
    # Reject, never clamp a lower map limit upwards to the minimum cruise SET.
    if not minimum <= target <= 145 or not minimum <= current <= 145:
      return None
    return target
