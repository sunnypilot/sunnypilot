"""Opt-in output isolation for the normal lateral maneuver controller path."""
import math

from opendbc.car.ford.values import FordFlags
from openpilot.common.constants import CV
from openpilot.selfdrive.controls.lib.ford_path import FordPath

PARAM = 'FordChannelTestMode'
CONFLICTS = ('LateralManeuverMode', 'LongitudinalManeuverMode', 'JoystickDebugMode')
SPEEDS = (15.*CV.MPH_TO_MS, 20.*CV.MPH_TO_MS)
MAX_SPEED_ERROR = .7
MAX_RUN_S = 4.  # 2.6 s nominal, with room for the accepted 16–24 Hz model cadence


def selected(CP, params):
  return bool(CP.brand == 'ford' and CP.flags & FordFlags.CANFD and params.get_bool('FordModelActionController')
              and params.get_bool(PARAM) and not any(params.get_bool(key) for key in CONFLICTS))


def is_channel_plan(plan):
  test = getattr(plan, 'fordChannelTest', None)
  return test is not None and test.channel != 'none'


def is_channel_maneuver(plan):
  return is_channel_plan(plan) and plan.fordChannelTest.phase == 'maneuver'


def use_maneuver_reference(plan, valid, channel_test_enabled):
  return valid and (not is_channel_plan(plan) or (channel_test_enabled and is_channel_maneuver(plan)))


class FordChannelTest:
  """Check the maneuver lease, then select one already-computed controller field.

  The normal curvature limiter, model mapping and PI feedback run unchanged.
  This class supplies no waveform, captured command, gain or feedback reset.
  """
  def __init__(self):
    self.clear()

  def clear(self):
    self.run_id = self.channel = self.start = self.last_time = None
    self.aborted = False
    self.diagnostics = {}

  def fail(self, reason):
    self.aborted = True
    self.diagnostics.update(status='aborted', reason=reason, command=(0., 0., 0., 0.))
    return FordPath()

  def update(self, plan, *, plan_valid, plan_time, now, normal, active, healthy, driver_input, speed):
    test = plan.fordChannelTest
    fresh = math.isfinite(now) and math.isfinite(plan_time) and -.005 <= now-plan_time <= .15
    if not plan_valid and (fresh or self.run_id is None):
      self.clear()
      return None
    if self.aborted:
      return FordPath()
    if not fresh or not plan_valid:
      return self.fail('stale maneuver plan')
    if not is_channel_maneuver(plan) or test.runId == 0 or test.delta != 0.:
      return self.fail('invalid maneuver identity')
    if not active or not healthy or not normal.valid or driver_input:
      return self.fail('driver input, disengagement or invalid service')
    if not all(math.isfinite(x) for x in (speed, test.speed, plan.desiredCurvature, normal.path_offset, normal.path_angle)):
      return self.fail('nonfinite input')
    if not any(abs(test.speed-v) < 1e-5 for v in SPEEDS) or abs(speed-test.speed) > MAX_SPEED_ERROR:
      return self.fail('speed out of range')
    if self.run_id is None:
      self.run_id, self.channel, self.start, self.target_speed = test.runId, str(test.channel), now, test.speed
    if (test.runId != self.run_id or test.channel != self.channel or test.speed != self.target_speed
        or (self.last_time is not None and not .002 <= now-self.last_time <= .1) or now-self.start > MAX_RUN_S):
      return self.fail('maneuver identity or timing changed')
    self.last_time = now
    command = FordPath(True, normal.path_offset if self.channel == 'c0' else 0., normal.path_angle if self.channel == 'c1' else 0., 0., 0.)
    self.diagnostics = {'status': 'active', 'run_id': self.run_id, 'channel': self.channel,
                        'desired_curvature': plan.desiredCurvature, 'target_speed': test.speed,
                        'command': (command.path_offset, command.path_angle, 0., 0.)}
    return command
