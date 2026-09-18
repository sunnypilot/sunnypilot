"""Default-off joint C0/C1 trial at the existing Ford transmit boundary.

The observer consumes decoded packets queued to panda, not tentative requests.
It estimates older-firmware state; it cannot observe ECU RAM or prove acceptance.
"""

import math

from opendbc.car.ford.values import FordFlags


def joint_control_enabled(CP, params):
  return bool(
    CP.brand == 'ford'
    and CP.flags & FordFlags.CANFD
    and params.get_bool('FordModelActionController')
    and params.get_bool('FordPscmJointControl')
    and not params.get_bool('FordGeometryReference')
    and not params.get_bool('JoystickDebugMode')
  )


def select_joint_control(CP, params):
  # No calibration or native-library load on the normal/default path.
  return FordJointControl(CP) if joint_control_enabled(CP, params) else None


class FordJointControl:
  def __init__(self, CP):
    from opendbc.can import CANParser
    from opendbc.car.ford.fordcan import CanBus
    from openpilot.selfdrive.controls.lib.ford_joint.model import MainRequest
    from openpilot.selfdrive.controls.lib.ford_joint.angle import AngleModel
    from openpilot.selfdrive.controls.lib.ford_joint.encoder import PairedRelease

    self.wheelbase, self.ratio = CP.wheelbase, CP.steerRatio
    if not all(math.isfinite(v) and v > 0 for v in (self.wheelbase, self.ratio)):
      raise ValueError('Joint control requires finite positive vehicle geometry')
    self.request = MainRequest(native_lookup=True)
    self.angle = AngleModel(self.request.cal)
    self.encoder = PairedRelease(self.request, preserve_now=True)
    self.bus = CanBus(CP).main
    self.parser = CANParser('ford_lincoln_base_pt', [('LateralMotionControl2', 100)], self.bus)
    self.last_time = None
    self.last_sent_time = None
    self.phase = 0.0
    self.sent = (0.0, 0.0, False)
    self.measurement = (0.0, 0.0, 0.0)
    self.fault = ''
    self.diagnostics = {'hypothesis': 'ford-joint-v24', 'status': 'inactive'}

  def advance(self, now):
    """Retain channel/filter state through inactive commands and driver override."""
    if self.last_time is not None:
      elapsed = now - self.last_time
      if not 0.0 <= elapsed <= 0.1:
        # Lost command history cannot be repaired by pretending the held state
        # reset. Disable this trial until the next onroad process start.
        self.fault = 'command_timing_gap'
      else:
        self.phase += elapsed
        ticks = int((self.phase + 1e-12) / 0.008)
        self.phase -= ticks * 0.008
        speed, angle, yaw = self.measurement
        for _ in range(ticks):
          r = self.request.step(speed, self.sent[0], self.sent[1], active=self.sent[2], freeze_i=True)
          self.angle.step(speed, r['filtered_curvature'], angle, yaw, yaw * speed / 3.6, self.wheelbase, self.ratio)
    self.last_time = now

  def prepare(self, CC, CC_SP, CS, now, *, fresh=True, pscm_status=None):
    from openpilot.selfdrive.controls.lib.ford_joint.inverse import invert_angle

    self.advance(now)
    path = CC_SP.fordLateralPath
    target = float(CC.actuators.steeringAngleDeg)
    finite = all(math.isfinite(v) for v in (CS.vEgo, CS.steeringAngleDeg, CS.yawRate, target))
    if finite:
      # The route extractor negated carState.yawRate; the audited inverse negated
      # it back. Native carState yaw and wheel angle already share our CAN sign.
      self.measurement = (max(0.0, CS.vEgo * 3.6), CS.steeringAngleDeg, CS.yawRate)
    status_fresh = pscm_status is not None and pscm_status.valid and pscm_status.canMonoTime > 0 and -0.005 <= now - pscm_status.canMonoTime * 1e-9 <= 0.15
    override = bool(CS.steeringPressed or (status_fresh and (pscm_status.limit == 3 or pscm_status.denied)))
    valid = bool(
      fresh
      and CS.canValid
      and finite
      and 0.3 <= CS.vEgo <= 55
      and abs(CS.yawRate) <= 3
      and path.enabled
      and path.valid
      and not CS.steerFaultTemporary
      and not CS.steerFaultPermanent
    )
    # A missing previous transmit receipt means the prediction is not synchronized.
    if self.last_sent_time is not None and now - self.last_sent_time > 0.1:
      self.fault = 'missing_transmit_history'
    active = bool(CC.latActive and valid and not override and not self.fault)
    command = (0.0, 0.0)
    details = {}
    if active:
      try:
        speed, angle, yaw = self.measurement
        inverse = invert_angle(self.angle, speed, target, angle, yaw, yaw * speed / 3.6, self.wheelbase, self.ratio)
        # Firmware phase is estimated from elapsed time. Cover the 1/2 firmware
        # ticks before the next nominal 100 Hz transmit; all phases are tested.
        ticks = max(1, min(2, int((self.phase + 0.01 + 1e-12) / 0.008)))
        command, info = self.encoder.choose(speed, inverse['curvature'], phase=0 if ticks == 2 else 2)
        details = {
          'requested_angle': target,
          'reachable_angle': inverse['reachable_target'],
          'target_curvature': inverse['curvature'],
          'predicted_curvature': float(info['first_state'][3]),
          'accel_limited': inverse['accel_limited'],
        }
      except (ValueError, OverflowError, ArithmeticError):
        self.fault = 'invalid_prediction'
        active = False
        command = (0.0, 0.0)
    # The inverse operates in CAN/pinion coordinates. CarController negates
    # FordLateralPath on TX, so negate here exactly once to retain the tested sign.
    path.pathOffset, path.pathAngle = -float(command[0]), -float(command[1])
    path.curvature = path.curvatureRate = 0.0
    path.valid = active
    cc = CC.as_reader().as_builder() if hasattr(CC, 'as_reader') else CC.as_builder()
    cc.latActive = active
    self.diagnostics = {
      'hypothesis': 'ford-joint-v24',
      'status': self.fault or ('active' if active else 'inactive'),
      'driver_override': override,
      'held_c0': self.request.c0,
      'held_c1': self.request.c1,
      'filtered_curvature': self.request.filtered,
      'wire_command': tuple(map(float, command)),
      **details,
    }
    # Preserve card's reader contract: CarController copies actuators with
    # as_builder(), which is only available on a Cap'n Proto reader.
    return cc.as_reader()

  def record_sent(self, can_sends, now_nanos):
    packets = [msg for msg in can_sends if msg[0] == 0x3D6 and msg[2] == self.bus]
    if not packets:
      return
    self.parser.update([now_nanos, packets])
    values = self.parser.vl['LateralMotionControl2']
    if values['LatCtlCurv_No_Actl'] != 0.0 or values['LatCtlCrv_NoRate2_Actl'] != 0.0:
      self.fault = 'unexpected_curvature_channel'
    self.sent = (values['LatCtlPathOffst_L_Actl'], values['LatCtlPath_An_Actl'], values['LatCtl_D2_Rq'] == 2)
    self.last_sent_time = now_nanos * 1e-9
    self.diagnostics['wire_sent'] = self.sent
