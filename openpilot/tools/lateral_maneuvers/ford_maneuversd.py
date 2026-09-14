#!/usr/bin/env python3
"""Eight short Ford channel pulses. Normal model tracking runs between trials."""
import math
import time
from dataclasses import dataclass

from openpilot.cereal import messaging
from openpilot.common.constants import CV
from openpilot.common.realtime import Ratekeeper
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.controls.lib.ford_channel_test import (
  AMPLITUDE, BASELINE_S, PULSE_S, TOTAL_S, SPEEDS, MAX_SPEED_ERROR, MAX_BASE_C0, MAX_BASE_C1,
)


@dataclass(frozen=True)
class Trial:
  speed: float
  channel: str
  direction: int

  @property
  def description(self):
    # Controller coordinates are left-positive; the CAN sender negates C0/C1.
    return f'{self.channel.upper()} {"left" if self.direction > 0 else "right"} {self.speed*CV.MS_TO_MPH:.0f} mph'


TRIALS = tuple(Trial(speed, channel, sign) for speed in SPEEDS for channel in AMPLITUDE for sign in (-1, 1))


@dataclass(frozen=True)
class Output:
  trial: Trial
  run_id: int
  phase: str
  text: str
  delta: float = 0.

  @property
  def active(self):
    return self.phase in ('baseline', 'pulse', 'release')


class Sequence:
  def __init__(self):
    self.index = self.run_id = 0
    self.start = self.ready_start = self.last_time = None
    self.complete_until = None
    self.need_disengage = True  # also prevents a daemon restart from re-arming while engaged
    self.reason = ''

  def update(self, now, *, engaged, lat_active, healthy, ready, driver_input, speed):
    trial = TRIALS[min(self.index, len(TRIALS)-1)]
    def out(phase, text, delta=0.):
      return Output(trial, self.run_id, phase, text, delta)
    healthy = healthy and math.isfinite(speed)
    clock_ok = math.isfinite(now) and (self.last_time is None or 0. < now-self.last_time <= .2)
    self.last_time = now
    if self.index == len(TRIALS):
      return out('complete', 'Ford tests finished')
    if self.start is not None:
      if not clock_ok or not healthy or not engaged or not lat_active or driver_input or abs(speed-trial.speed) > MAX_SPEED_ERROR:
        self.start = self.ready_start = None
        self.need_disengage = True
        self.reason = 'Aborted: disengage to retry'
        return out('aborted', self.reason)
      elapsed = now-self.start
      if elapsed < BASELINE_S:
        return out('baseline', 'Active: holding baseline')
      if elapsed < BASELINE_S+PULSE_S:
        return out('pulse', 'Active: pulse', trial.direction*AMPLITUDE[trial.channel])
      if elapsed < TOTAL_S:
        return out('release', 'Active: release')
      self.start = None
      self.complete_until = now+1.
      return out('complete', 'Complete')
    if self.complete_until is not None:
      if now < self.complete_until:
        return out('complete', 'Complete')
      self.index += 1
      self.complete_until = self.ready_start = None
      return out('waiting', 'Next trial')
    if self.need_disengage:
      if not engaged:
        self.need_disengage = False
        self.reason = ''
      else:
        return out('aborted', self.reason or 'Disengage before testing')
    ready = ready and healthy and lat_active and engaged and not driver_input and abs(speed-trial.speed) <= MAX_SPEED_ERROR and clock_ok
    if not ready:
      self.ready_start = None
      return out('waiting', f'Set {trial.speed*CV.MS_TO_MPH:.0f} mph; straight and steady')
    if self.ready_start is None:
      self.ready_start = now
    if now-self.ready_start < 2.:
      return out('waiting', 'Starting: hold straight')
    self.run_id += 1
    self.start, self.ready_start = now, None
    return out('baseline', 'Active: holding baseline')


def main():
  services = ['carState', 'carStateSP', 'carControl', 'carControlSP', 'controlsState', 'selfdriveState',
              'selfdriveStateSP', 'modelV2', 'vehicleParameters']
  sm = messaging.SubMaster(services, frequency=20)
  pm = messaging.PubMaster(['lateralManeuverPlan', 'alertDebug'])
  sequence = Sequence()
  rk = Ratekeeper(20)
  previous = None
  while True:
    sm.update(0)
    now = time.monotonic()
    cs, cc, path = sm['carState'], sm['carControl'], sm['carControlSP'].fordLateralPath
    mads = sm['selfdriveStateSP'].mads
    pscm = sm['carStateSP'].fordPscmStatus
    lp, controls = sm['vehicleParameters'], sm['controlsState']
    finite = all(math.isfinite(x) for x in (cs.vEgo, cs.steeringTorque, cs.steeringRateDeg, lp.roll, controls.curvature,
                                           controls.desiredCurvature, path.pathOffset, path.pathAngle))
    healthy = (finite and sm.all_checks(services) and cs.canValid and cs.cruiseState.enabled
               and not cs.steerFaultTemporary and not cs.steerFaultPermanent
               and pscm.valid and pscm.canMonoTime > 0 and -.005 <= now-pscm.canMonoTime*1e-9 <= .15
               and not pscm.denied and pscm.limit not in (2, 3))
    driver = cs.steeringPressed or abs(cs.steeringTorque) > 1. or cs.gasPressed or cs.brakePressed
    ready = (path.enabled and path.valid and abs(path.pathOffset) <= MAX_BASE_C0 and abs(path.pathAngle) <= MAX_BASE_C1
             and abs(controls.curvature) <= .001 and abs(controls.desiredCurvature) <= .001
             and abs(cs.steeringRateDeg) < 2. and abs(lp.roll) < .12 and pscm.lateralState == 2)
    result = sequence.update(now, engaged=mads.enabled if mads.available else sm['selfdriveState'].enabled,
                             lat_active=cc.latActive, healthy=healthy, ready=ready, driver_input=driver, speed=cs.vEgo)
    plan = messaging.new_message('lateralManeuverPlan')
    plan.valid = result.active
    test = plan.lateralManeuverPlan.fordChannelTest
    test.runId, test.channel, test.phase = result.run_id, result.trial.channel, result.phase
    test.delta, test.speed = result.delta, result.trial.speed
    pm.send('lateralManeuverPlan', plan)
    alert = messaging.new_message('alertDebug')
    alert.valid = True
    alert.alertDebug.alertText1 = result.text
    alert.alertDebug.alertText2 = result.trial.description
    pm.send('alertDebug', alert)
    key = (result.run_id, result.phase, result.text)
    if key != previous:
      cloudlog.event('Ford channel test progress', run_id=result.run_id, channel=result.trial.channel,
                     phase=result.phase, delta=result.delta, target_speed=result.trial.speed, message=result.text)
      previous = key
    rk.keep_time()


if __name__ == '__main__':
  main()
