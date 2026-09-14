#!/usr/bin/env python3

import math
import numpy as np

from openpilot.cereal import messaging
from opendbc.car.structs import car
from opendbc.car.vehicle_model import VehicleModel
from opendbc.car.ford.values import FordFlags
from openpilot.common.realtime import DT_CTRL, Ratekeeper
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.controls.lib.drive_helpers import should_stop

LongCtrlState = car.CarControl.Actuators.LongControlState
MAX_LAT_ACCEL = 3.0
FORD_FIELD_LIMITS = {1: 5.11, 2: .5}  # C0 metres and C1 radians, symmetric existing command bounds


class FordJoystick:
  def __init__(self, CP):
    self.supported = CP.brand == 'ford' and bool(CP.flags & FordFlags.CANFD)
    self.channel = 0
    self.need_center = False

  def update(self, CC, sm, stale):
    request = sm['testJoystick']
    channel = request.fordChannel.raw
    if channel != self.channel:
      self.need_center = True
      self.channel = channel

    if channel or self.need_center:
      valid = (not stale and sm.valid['testJoystick'] and len(request.axes) == 2 and math.isfinite(request.axes[1])
               and sm.all_checks(['carState', 'selfdriveState', 'vehicleParameters']) and sm['carState'].canValid
               and math.isfinite(sm['carState'].vEgo) and math.isfinite(sm['carState'].steeringAngleDeg))
      if not valid or not CC.latActive:
        self.need_center = True
      elif request.axes[1] == 0.:
        self.need_center = False
      if not valid or self.need_center or (channel and (not self.supported or channel not in FORD_FIELD_LIMITS)):
        CC.latActive = False
      if channel or not CC.latActive:
        CC.actuators.torque = CC.actuators.steeringAngleDeg = CC.actuators.curvature = 0.

    if not self.supported:
      return None
    # Publish the disabled path in standard mode too, clearing any previous
    # custom path. card consumes carControlSP alongside carControl.
    msg = messaging.new_message('carControlSP')
    msg.valid = True
    path = msg.carControlSP.fordLateralPath
    path.enabled = channel != 0
    path.valid = path.enabled and CC.latActive
    if path.valid:
      # Positive joystick means left; Ford's internal path coordinates are right-positive.
      value = -float(np.clip(request.axes[1], -1., 1.))*FORD_FIELD_LIMITS[channel]
      if channel == 1:
        path.pathOffset = value
      else:
        path.pathAngle = value
    return msg


def joystickd_thread():
  params = Params()
  cloudlog.info("joystickd is waiting for CarParams")
  CP = messaging.log_from_bytes(params.get("CarParams", block=True), car.CarParams)
  VM = VehicleModel(CP)
  ford = FordJoystick(CP)

  sm = messaging.SubMaster(['carState', 'onroadEvents', 'vehicleParameters', 'selfdriveState', 'testJoystick'], frequency=1. / DT_CTRL)
  pm = messaging.PubMaster(['carControl', 'controlsState'] + (['carControlSP', 'alertDebug'] if ford.supported else []))

  rk = Ratekeeper(100, print_delay_threshold=None)
  while 1:
    sm.update(0)

    cc_msg = messaging.new_message('carControl')
    cc_msg.valid = True
    CC = cc_msg.carControl
    CC.enabled = sm['selfdriveState'].enabled
    CC.latActive = sm['selfdriveState'].active and not sm['carState'].steerFaultTemporary and not sm['carState'].steerFaultPermanent
    CC.longActive = CC.enabled and not any(e.overrideLongitudinal for e in sm['onroadEvents']) and CP.openpilotLongitudinalControl
    CC.cruiseControl.override = CC.enabled and not CC.longActive and CP.openpilotLongitudinalControl
    CC.cruiseControl.cancel = sm['carState'].cruiseState.enabled and (not CC.enabled or not CP.pcmCruise)
    CC.hudControl.leadDistanceBars = 2

    actuators = CC.actuators

    # reset joystick if it hasn't been received in a while
    should_reset_joystick = sm.recv_frame['testJoystick'] == 0 or (sm.frame - sm.recv_frame['testJoystick'])*DT_CTRL > 0.2

    if not should_reset_joystick:
      joystick_axes = sm['testJoystick'].axes
    else:
      joystick_axes = [0.0, 0.0]

    if sm['testJoystick'].fordChannel.raw and (not sm.valid['testJoystick'] or len(joystick_axes) != 2
                                               or not all(math.isfinite(axis) for axis in joystick_axes)):
      joystick_axes = [0.0, 0.0]
      should_reset_joystick = True

    if CC.longActive:
      actuators.accel = 4.0 * float(np.clip(joystick_axes[0], -1, 1))
      actuators.longControlState = LongCtrlState.stopping if should_stop(sm['carState'].vEgo, actuators.accel) else LongCtrlState.pid
      CC.cruiseControl.resume = actuators.accel > 0.0

    if CC.latActive and sm['testJoystick'].fordChannel.raw == 0:
      max_curvature = MAX_LAT_ACCEL / max(sm['carState'].vEgo ** 2, 5)
      max_angle = math.degrees(VM.get_steer_from_curvature(max_curvature, sm['carState'].vEgo, sm['vehicleParameters'].roll))

      actuators.torque = float(np.clip(joystick_axes[1], -1, 1))
      actuators.steeringAngleDeg, actuators.curvature = actuators.torque * max_angle, actuators.torque * -max_curvature

    ford_msg = ford.update(CC, sm, should_reset_joystick)
    if ford_msg is not None:
      pm.send('carControlSP', ford_msg)
      alert = messaging.new_message('alertDebug')
      alert.valid = ford.channel in FORD_FIELD_LIMITS
      if alert.valid:
        channel = f'C{ford.channel-1}'
        path = ford_msg.carControlSP.fordLateralPath
        command = f'{path.pathOffset:+.2f} m' if ford.channel == 1 else f'{path.pathAngle:+.4f} rad'
        alert.alertDebug.alertText1 = f'Joystick Mode — {channel} only'
        alert.alertDebug.alertText2 = (f'{channel}: {command} | Wheel: {sm["carState"].steeringAngleDeg:+.1f}°'
                                     if CC.latActive else 'Inactive: engage, then reset / center steering')
      pm.send('alertDebug', alert)
    pm.send('carControl', cc_msg)

    cs_msg = messaging.new_message('controlsState')
    cs_msg.valid = True
    controlsState = cs_msg.controlsState
    controlsState.lateralControlState.init('debugState')

    lp = sm['vehicleParameters']
    steer_angle_without_offset = math.radians(sm['carState'].steeringAngleDeg - lp.angleOffsetDeg)
    controlsState.curvature = -VM.calc_curvature(steer_angle_without_offset, sm['carState'].vEgo, lp.roll)

    pm.send('controlsState', cs_msg)

    rk.keep_time()


def main():
  joystickd_thread()


if __name__ == "__main__":
  main()
