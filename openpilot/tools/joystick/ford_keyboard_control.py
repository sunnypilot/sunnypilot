#!/usr/bin/env python3
"""Keyboard frontend for Ford isolated-channel tests. Keeps controlsd and ACC/MADS running."""
import argparse
import math
import time

from opendbc.car.ford.values import FordFlags
from opendbc.car.structs import car
from openpilot.cereal import log, messaging
from openpilot.common.constants import CV
from openpilot.common.params import Params
from openpilot.common.realtime import Ratekeeper
from openpilot.selfdrive.controls.lib.ford_channel_test import CONFLICTS, KEYBOARD_PARAM, PARAM, SPEEDS
from openpilot.tools.lateral_maneuvers.ford_keyboard import MIN_ACCEL, MAX_ACCEL, ACCEL_INCREMENT
from openpilot.tools.lib.kbhit import KBHit

HELP = '1 C0 | 2 C1 | V 15/20 mph | +/- strength | A left step | D right step | R cancel | Q quit'


class KeyboardControl:
  def __init__(self, speed=15, accel=.5):
    if speed not in (15, 20) or not math.isfinite(accel) or not MIN_ACCEL <= accel <= MAX_ACCEL:
      raise ValueError(f'Use 15/20 mph and {MIN_ACCEL}–{MAX_ACCEL} m/s²')
    self.request = log.Joystick.FordKeyboard.new_message(channel='c0', speed=speed*CV.MPH_TO_MS, accel=accel, action='idle')
    self.last_key, self.last_key_time = '', -math.inf

  def action(self, action, now):
    self.request.requestId = max(self.request.requestId+1, int(now*1e9))
    self.request.action = action

  def key(self, key, now):
    key = key.lower()
    repeated = key == self.last_key and now-self.last_key_time < .5
    self.last_key, self.last_key_time = key, now
    if key in ('a', 'd'):
      if not repeated:
        self.action('left' if key == 'a' else 'right', now)
    elif key in ('r', 'q'):
      self.action('cancel', now)
    else:
      self.request.action = 'idle'
      if key in ('1', '2'):
        self.request.channel = 'c0' if key == '1' else 'c1'
      elif key == 'v':
        self.request.speed = SPEEDS[1] if abs(self.request.speed-SPEEDS[0]) < 1e-5 else SPEEDS[0]
      elif key in ('+', '=', '-', '_'):
        increment = ACCEL_INCREMENT if key in ('+', '=') else -ACCEL_INCREMENT
        self.request.accel = min(MAX_ACCEL, max(MIN_ACCEL, self.request.accel+increment))
    return key != 'q'

  def message(self):
    msg = messaging.new_message('testJoystick')
    msg.valid = True
    # Normal joystick consumers receive no gas/brake or steering-axis request.
    msg.testJoystick.axes = [0., 0.]
    msg.testJoystick.fordKeyboard = self.request
    return msg


def enable(params):
  offroad = params.get_bool('IsOffroad')
  if not offroad and (not params.get_bool(KEYBOARD_PARAM) or any(params.get_bool(k) for k in (*CONFLICTS, PARAM))):
    raise ValueError('Start this tool while the car is off and openpilot is offroad.')
  if not params.get_bool('FordModelActionController'):
    raise ValueError('Enable the Ford model-action controller first.')
  raw = params.get('CarParamsPersistent')
  if not raw:
    raise ValueError('Drive once to identify the car before enabling this test.')
  cp = messaging.log_from_bytes(raw, car.CarParams)
  if cp.brand != 'ford' or not cp.flags & FordFlags.CANFD:
    raise ValueError('This test requires a CAN FD Ford.')
  if not offroad:
    return  # Reconnect to an already-selected keyboard mode without changing any driving mode.
  for key in (*CONFLICTS, PARAM):
    params.put_bool(key, False, block=True)
  params.put_bool(KEYBOARD_PARAM, True, block=True)


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--speed', type=int, choices=(15, 20), default=15, help='target mph (default: 15)')
  parser.add_argument('--accel', type=float, default=.5, help=f'step strength in m/s², {MIN_ACCEL}–{MAX_ACCEL} (default: 0.5)')
  args = parser.parse_args()
  params = Params()
  try:
    control = KeyboardControl(args.speed, args.accel)
    kb = KBHit()
    enable(params)
  except (ValueError, OSError) as exc:
    parser.exit(1, f'{exc}\n')
  pm = messaging.PubMaster(['testJoystick'])
  sm = messaging.SubMaster(['alertDebug', 'carState', 'carStateSP', 'carControlSP'])
  rk = Ratekeeper(20, print_delay_threshold=None)
  print(f'\nFord keyboard test connected. Use ACC or MADS with manual throttle.\n{HELP}\n', flush=True)
  print('Strength is a maneuver target, not a percentage of C0/C1. R cancels the test; normal lateral control remains active.', flush=True)
  running = True
  try:
    while running:
      # Bound input work so pasted text cannot stall the heartbeat/watchdog.
      for _ in range(32):
        if not kb.kbhit():
          break
        key = kb.getch()
        if not key:
          running = False
          break
        running = control.key(key, time.monotonic())
        if not running:
          break
      if not params.get_bool(KEYBOARD_PARAM):
        print('\nKeyboard test mode cleared; exiting.', flush=True)
        break
      pm.send('testJoystick', control.message())
      sm.update(0)
      if rk.frame % 10 == 0:
        req, cs = control.request, sm['carState']
        path, pscm = sm['carControlSP'].fordLateralPath, sm['carStateSP'].fordPscmStatus
        telemetry = (f'C0 {path.pathOffset:+.2f}m C1 {path.pathAngle:+.4f}rad | wheel {cs.steeringAngleDeg:+.1f}° | limit {pscm.limit}'
                     if sm.all_alive() and sm.all_valid() else 'Waiting for live vehicle data')
        print(f'{str(req.channel).upper()} | {req.speed*CV.MS_TO_MPH:.0f}mph | {req.accel:.2f}m/s² | '
              + f'{sm["alertDebug"].alertText1} | {telemetry}', flush=True)
      rk.keep_time()
  except KeyboardInterrupt:
    pass
  finally:
    control.action('cancel', time.monotonic())
    pm.send('testJoystick', control.message())
    kb.set_normal_term()
    # Keep the daemon alive onroad so it can explicitly publish an inactive plan;
    # otherwise controlsd would only see the last, now-stale active plan.
    if params.get_bool('IsOffroad'):
      params.put_bool(KEYBOARD_PARAM, False, block=True)
    print('\nKeyboard disconnected; no further steps will start.', flush=True)


if __name__ == '__main__':
  main()
