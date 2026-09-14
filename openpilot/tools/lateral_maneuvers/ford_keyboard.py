"""Manually triggered curvature steps through the normal Ford channel test path."""
import math
import time

from openpilot.cereal import messaging
from openpilot.common.constants import CV
from openpilot.common.realtime import DT_MDL, Ratekeeper
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.controls.lib.drive_helpers import MAX_LATERAL_ACCEL_NO_ROLL, MIN_SPEED
from openpilot.selfdrive.controls.lib.ford_channel_test import SPEEDS, MAX_SPEED_ERROR
from openpilot.tools.lateral_maneuvers.lateral_maneuversd import MAX_CURV, MAX_ROLL, TIMER

INPUT_TIMEOUT = .2
ACCEL_INCREMENT = .25
MIN_ACCEL, MAX_ACCEL = ACCEL_INCREMENT, MAX_LATERAL_ACCEL_NO_ROLL
BASELINE_S, STEP_S, RELEASE_S = .5, 1., 1.5


class KeyboardManeuver:
  def __init__(self):
    self.last_request_id = 0
    self.ready_since = self.start = self.last_update = None
    self.request_id = self.run_id = 0
    self.channel, self.speed, self.accel, self.baseline = 'none', SPEEDS[0], 0., 0.
    self.phase, self.status = 'waiting', 'Waiting for keyboard'

  @property
  def active(self):
    return self.start is not None

  def stop(self, status, phase='aborted'):
    self.start = self.ready_since = None
    self.phase, self.status = phase, status

  def update(self, now, request, *, input_time, input_valid, healthy, ready, speed, curvature):
    # Consume every new request, including ones received while busy/unready/stale.
    # A rejected keypress must never become a delayed automatic start.
    new_request = request.requestId > self.last_request_id
    self.last_request_id = max(request.requestId, self.last_request_id)
    valid_input = (input_valid and math.isfinite(now) and math.isfinite(input_time)
                   and -.005 <= now-input_time <= INPUT_TIMEOUT
                   and request.channel in ('c0', 'c1') and request.action in ('idle', 'left', 'right', 'cancel')
                   and math.isfinite(request.speed) and any(abs(request.speed-v) < 1e-5 for v in SPEEDS)
                   and math.isfinite(request.accel) and MIN_ACCEL-1e-6 <= request.accel <= MAX_ACCEL+1e-6)
    continuous = self.last_update is None or 0. < now-self.last_update <= .15
    self.last_update = now
    if not valid_input or not healthy or not continuous or not all(math.isfinite(v) for v in (speed, curvature)):
      self.stop('Aborted: input/data lost' if self.active else 'Waiting for keyboard and active lateral control')
      return
    if new_request and request.action == 'cancel':
      self.stop('Aborted: keyboard cancel')
      return
    if self.active:
      if abs(speed-self.speed) > MAX_SPEED_ERROR:
        self.stop('Aborted: speed out of range')
      else:
        elapsed = now-self.start
        if elapsed >= BASELINE_S+STEP_S+RELEASE_S:
          self.stop('Complete', 'complete')
        else:
          self.phase = 'baseline' if elapsed < BASELINE_S else ('pulse' if elapsed < BASELINE_S+STEP_S else 'release')
          self.status = f'Active {self.channel.upper()} {self.phase}'
      return
    if not ready or abs(speed-request.speed) > MAX_SPEED_ERROR:
      self.ready_since = None
      self.status = f'Set {request.speed*CV.MS_TO_MPH:.0f} mph; straight and steady'
    else:
      if self.ready_since is None:
        self.ready_since = now
      self.status = 'Ready: A left / D right' if now-self.ready_since >= TIMER else 'Waiting: steady for 2 seconds'
    if new_request and request.action in ('left', 'right'):
      if self.ready_since is None or now-self.ready_since < TIMER:
        self.status = 'Not ready; press A/D again when ready'
        return
      self.start = now
      self.run_id += 1
      self.request_id = request.requestId
      self.channel, self.speed = str(request.channel), request.speed
      # Ford's desired-curvature coordinates are right-positive, like normal lat man.
      self.accel = request.accel * (-1 if request.action == 'left' else 1)
      self.baseline = curvature
      self.phase, self.status = 'baseline', f'Active {self.channel.upper()} baseline'

  def plan(self, speed):
    msg = messaging.new_message('lateralManeuverPlan')
    msg.valid = self.active
    plan = msg.lateralManeuverPlan
    if self.active:
      plan.desiredCurvature = self.baseline + (self.accel if self.phase == 'pulse' else 0.) / max(speed, MIN_SPEED)**2
    plan.fordChannelTest = {'runId': self.run_id, 'channel': self.channel, 'speed': self.speed,
                            'phase': 'maneuver' if self.active else self.phase, 'delta': 0.,
                            'keyboardRequestId': self.request_id, 'keyboardPhase': self.phase, 'targetAccel': self.accel}
    return msg

  @property
  def description(self):
    direction = 'right' if self.accel > 0 else 'left'
    return f'step {direction} {abs(self.accel):.2f}m/s² {self.speed*CV.MS_TO_MPH:.0f}mph {self.channel.upper()} keyboard'


def main():
  services = ['carState', 'carControl', 'controlsState', 'selfdriveState', 'modelV2', 'carStateSP', 'vehicleParameters']
  sm = messaging.SubMaster(services+['testJoystick'], frequency=1./DT_MDL)
  pm = messaging.PubMaster(['lateralManeuverPlan', 'alertDebug'])
  test = KeyboardManeuver()
  rk = Ratekeeper(1./DT_MDL, print_delay_threshold=None)
  previous = None
  while True:
    sm.update(0)
    cs, cc, status = sm['carState'], sm['carControl'], sm['carStateSP'].fordPscmStatus
    now = time.monotonic()
    healthy = (sm.all_checks(services) and cs.canValid and cc.latActive
               and not (cs.steerFaultTemporary or cs.steerFaultPermanent or cs.steeringPressed or cs.brakePressed)
               and math.isfinite(cs.steeringTorque) and abs(cs.steeringTorque) <= 1.)
    curvature, roll = sm['controlsState'].desiredCurvature, sm['vehicleParameters'].roll
    ready = (abs(curvature) < MAX_CURV and abs(sm['controlsState'].curvature) < MAX_CURV and abs(roll) < MAX_ROLL
             and status.valid and -.005 <= now-status.canMonoTime*1e-9 <= .15 and status.lateralState == 2
             and not status.denied and status.limit != 3)
    test.update(now, sm['testJoystick'].fordKeyboard, input_time=sm.logMonoTime['testJoystick']*1e-9,
                input_valid=sm.valid['testJoystick'], healthy=healthy, ready=ready, speed=cs.vEgo, curvature=curvature)
    alert = messaging.new_message('alertDebug')
    alert.valid = True
    alert.alertDebug.alertText1 = test.status
    alert.alertDebug.alertText2 = test.description if test.run_id else 'Ford keyboard C0 / C1 test'
    pm.send('alertDebug', alert)
    pm.send('lateralManeuverPlan', test.plan(cs.vEgo))
    identity = (test.run_id, test.phase, test.status)
    if identity != previous:
      cloudlog.event('Ford keyboard test', run_id=test.run_id, request_id=test.request_id, phase=test.phase, status=test.status,
                     channel=test.channel, target_accel=test.accel, speed=cs.vEgo, wheel_angle=cs.steeringAngleDeg,
                     pscm_limit=status.limit)
      previous = identity
    rk.keep_time()
