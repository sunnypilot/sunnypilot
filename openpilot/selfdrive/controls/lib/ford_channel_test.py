"""Bounded, opt-in channel isolation. This is a diagnostic, not a driving controller."""
import math

from opendbc.car.ford.values import FordFlags
from openpilot.common.constants import CV
from openpilot.selfdrive.controls.lib.ford_path import FordPath

PARAM = 'FordChannelTestMode'
CONFLICTS = ('LateralManeuverMode', 'LongitudinalManeuverMode', 'JoystickDebugMode')
SPEEDS = (10.*CV.MPH_TO_MS, 20.*CV.MPH_TO_MS)
AMPLITUDE = {'c0': .03, 'c1': .01}
BASELINE_S, PULSE_S, RELEASE_S = .5, .5, 2.
TOTAL_S = BASELINE_S + PULSE_S + RELEASE_S
MAX_SPEED_ERROR = .7
MAX_BASE_C0, MAX_BASE_C1 = .03, .015
MAX_STEERING_CHANGE = 15.
MAX_LAT_ACCEL = 1.


def selected(CP, params):
  return bool(CP.brand == 'ford' and CP.flags & FordFlags.CANFD and params.get_bool('FordModelActionController')
              and params.get_bool(PARAM) and not any(params.get_bool(key) for key in CONFLICTS))


def is_channel_plan(plan):
  test = getattr(plan, 'fordChannelTest', None)
  return test is not None and test.channel != 'none'


class FordChannelTest:
  """Validate the 20 Hz test lease at the 100 Hz command boundary.

  Capture the normal command once during baseline. Hold the untested field
  throughout, and return the tested field to that baseline for release. No PI
  or live model change may alter the output of an accepted run.
  """
  def __init__(self):
    self.clear()

  def clear(self):
    self.run_id = None
    self.channel = None
    self.baseline = FordPath()
    self.start = self.pulse_start = self.last_time = None
    self.phase = 'waiting'
    self.aborted = False
    self.diagnostics = {}

  def fail(self, reason):
    self.aborted = True
    self.diagnostics.update(status='aborted', reason=reason, command=(0., 0., 0., 0.))
    return FordPath()

  def update(self, plan, *, plan_valid, plan_time, now, normal, active, healthy, driver_input,
             speed, angle, curvature, pscm):
    test = plan.fordChannelTest
    channel, phase = str(test.channel), str(test.phase)
    fresh = math.isfinite(now) and math.isfinite(plan_time) and -.005 <= now-plan_time <= .15
    # An explicit fresh end releases the override. A vanished/stale publisher
    # cannot silently remove an active test lease and re-arm an old pulse.
    if (not plan_valid or phase in ('waiting', 'complete', 'aborted') or channel == 'none') and (fresh or self.run_id is None):
      self.clear()
      return None
    if self.aborted:
      return FordPath()
    if not fresh or not plan_valid:
      return self.fail('stale test plan')
    if not active or not healthy or not normal.valid or driver_input:
      return self.fail('driver input, disengagement or invalid service')
    if not all(math.isfinite(x) for x in (speed, angle, curvature, test.delta, test.speed, normal.path_offset, normal.path_angle)):
      return self.fail('nonfinite input')
    if (pscm is None or not pscm.valid or pscm.canMonoTime <= 0 or not -.005 <= now-pscm.canMonoTime*1e-9 <= .15
        or pscm.denied or pscm.limit in (2, 3) or pscm.lateralState != 2):
      return self.fail('PSCM unavailable, denied or limited')
    if not any(abs(test.speed-v) < 1e-5 for v in SPEEDS) or abs(speed-test.speed) > MAX_SPEED_ERROR:
      return self.fail('speed out of range')
    if channel not in AMPLITUDE or phase not in ('baseline', 'pulse', 'release') or test.runId == 0:
      return self.fail('invalid test identity')
    if ((phase == 'pulse' and abs(abs(test.delta)-AMPLITUDE[channel]) > 1e-6)
        or (phase != 'pulse' and test.delta != 0.)):
      return self.fail('invalid pulse amplitude')
    if self.run_id is None:
      if phase != 'baseline' or abs(normal.path_offset) > MAX_BASE_C0 or abs(normal.path_angle) > MAX_BASE_C1 or abs(curvature) > .001:
        return self.fail('baseline not ready')
      self.run_id, self.channel = test.runId, channel
      self.baseline, self.start, self.base_angle = normal, now, angle
      self.target_speed = test.speed
    if (test.runId != self.run_id or channel != self.channel or test.speed != self.target_speed
        or (self.last_time is not None and not .002 <= now-self.last_time <= .1)
        or now-self.start > TOTAL_S+.2):
      return self.fail('test identity or timing changed')
    stages = ('waiting', 'baseline', 'pulse', 'release')
    if stages.index(phase) < stages.index(self.phase) or stages.index(phase) > stages.index(self.phase)+1:
      return self.fail('invalid phase transition')
    if phase == 'baseline' and now-self.start > BASELINE_S+.15:
      return self.fail('baseline timeout')
    if phase == 'pulse':
      if self.pulse_start is None:
        if now-self.start < BASELINE_S-.15:
          return self.fail('pulse started early')
        self.pulse_start, self.pulse_delta = now, test.delta
      if now-self.pulse_start > PULSE_S+.1 or test.delta != self.pulse_delta:
        return self.fail('pulse timeout or direction changed')
    if phase == 'release' and (self.pulse_start is None or now-self.pulse_start < PULSE_S-.15):
      return self.fail('release started early')
    if abs(angle-self.base_angle) > MAX_STEERING_CHANGE or abs(curvature)*speed**2 > MAX_LAT_ACCEL:
      return self.fail('steering response exceeded test envelope')
    self.phase, self.last_time = phase, now
    c0 = self.baseline.path_offset + (test.delta if channel == 'c0' else 0.)
    c1 = self.baseline.path_angle + (test.delta if channel == 'c1' else 0.)
    command = FordPath(True, c0, c1, 0., 0.)
    self.diagnostics = {'status': 'active', 'run_id': self.run_id, 'channel': channel, 'phase': phase,
                        'delta': test.delta, 'target_speed': test.speed,
                        'baseline_c0': self.baseline.path_offset, 'baseline_c1': self.baseline.path_angle,
                        'command': (c0, c1, 0., 0.)}
    return command
