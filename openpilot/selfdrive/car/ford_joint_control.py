"""Default-off joint C0/C1 trial at the existing Ford transmit boundary.

The observer consumes decoded packets queued to panda, not tentative requests.
It estimates older-firmware state; it cannot observe ECU RAM or prove acceptance.
"""

import math

from opendbc.car.ford.values import FordFlags

# Small steering-wheel trim around the nominal inverse, in degrees. These are
# trial tuning values, not recovered PSCM constants. Entry assist is separately gated.
ANGLE_TRIM_MAX = 2.0
ANGLE_TRIM_KI = 0.2  # 1/s; error clipping limits adaptation to 0.4 deg/s.
ANGLE_TRIM_ERROR_MAX = 5.0
ANGLE_TRIM_RATE_MAX = 5.0  # deg/s: do not learn a bias from fast wheel motion.
TARGET_PREVIEW = 0.1  # seconds; causal action-trend forecast, then hold.
TURN_ENTRY_C0_MAX = 0.60  # metres; experimental post-encoder correction budget.
TURN_ENTRY_C1_MAX = 0.04  # radians; not a recovered Ford calibration value.


def turn_entry_weight(target, angle, requested_rate):
  """Fade in only for a large, growing turn request with substantial wheel lag."""
  direction = math.copysign(1.0, target)
  size = max(0.0, min(1.0, (abs(target) - 30.0) / 30.0))
  lag = max(0.0, min(1.0, (direction * (target - angle) - 25.0) / 25.0))
  growth = max(0.0, min(1.0, direction * requested_rate / 30.0))
  return size * lag * growth


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
  if not joint_control_enabled(CP, params):
    return None
  return FordJointControl(CP, turn_entry_assist=params.get_bool('FordPscmTurnEntryAssist'),
                          turn_preview=params.get_bool('FordPscmTurnPreview'))


class FordJointControl:
  def __init__(self, CP, *, turn_entry_assist=False, turn_preview=False):
    from opendbc.can import CANParser
    from opendbc.car.ford.fordcan import CanBus
    from openpilot.selfdrive.controls.lib.ford_joint.model import MainRequest
    from openpilot.selfdrive.controls.lib.ford_joint.angle import AngleModel
    from openpilot.selfdrive.controls.lib.ford_joint.encoder import PairedRelease

    self.turn_entry_assist = turn_entry_assist
    self.turn_preview = turn_preview
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
    self.angle_trim = 0.0
    self.wheel_rate = 0.0
    self.last_target = None
    self.requested_rate = 0.0
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

  def prepare(self, CC, CC_SP, CS, now, *, fresh=True, pscm_status=None, turn_preview=None):
    from openpilot.selfdrive.controls.lib.ford_joint.inverse import C0_BOUND, C1_BOUND, invert_angle, quantize

    dt = now - self.last_time if self.last_time is not None else 0.0
    self.advance(now)
    path = CC_SP.fordLateralPath
    target = float(CC.actuators.steeringAngleDeg)
    # controlsd publishes calibrated car-frame motion and gates the path on its
    # health/freshness. Raw Ford CAN yaw has a zero offset on the audited truck.
    # Calibrated Z is opposite the CAN/pinion sign used by the recovered model.
    yaw = -float(CC.angularVelocity[2]) if len(CC.angularVelocity) == 3 else math.nan
    finite = all(math.isfinite(v) for v in (CS.vEgo, CS.steeringAngleDeg, CS.yawRate, yaw, target))
    if finite:
      # Ford does not populate CarState.steeringRateDeg. Derive motion from the
      # measured angle; 0.1 s filtering suppresses its 0.1-degree quantization.
      if 0.0 < dt <= 0.1:
        rate = (CS.steeringAngleDeg - self.measurement[1]) / dt
        self.wheel_rate += dt / (0.1 + dt) * (rate - self.wheel_rate)
      self.measurement = (max(0.0, CS.vEgo * 3.6), CS.steeringAngleDeg, yaw)
    else:
      self.wheel_rate = 0.0
    status_fresh = pscm_status is not None and pscm_status.valid and pscm_status.canMonoTime > 0 and -0.005 <= now - pscm_status.canMonoTime * 1e-9 <= 0.15
    # Like upstream Ford, steeringPressed alone does not zero the path. Retain
    # disengagement/fault gates and the PSCM's explicit override/denial status.
    override = bool(status_fresh and (pscm_status.limit == 3 or pscm_status.denied))
    valid = bool(
      fresh
      and CS.canValid
      and finite
      and 0.3 <= CS.vEgo <= 55
      and abs(CS.yawRate) <= 3
      and abs(yaw) <= 3
      and path.enabled
      and path.valid
      and not CS.steerFaultTemporary
      and not CS.steerFaultPermanent
    )
    # A missing previous transmit receipt means the prediction is not synchronized.
    if self.last_sent_time is not None and now - self.last_sent_time > 0.1:
      self.fault = 'missing_transmit_history'
    active = bool(CC.latActive and valid and not override and not self.fault)
    if not active:
      self.angle_trim = 0.0
      self.last_target = None
      self.requested_rate = 0.0
    command = (0.0, 0.0)
    details = {}
    if active:
      try:
        speed, angle, yaw = self.measurement
        if self.last_target is not None and 0.0 < dt <= 0.1:
          rate = (target - self.last_target) / dt
          self.requested_rate += dt / (0.1 + dt) * (rate - self.requested_rate)
        self.last_target = target
        error = target - angle
        settling = abs(error) <= ANGLE_TRIM_ERROR_MAX and abs(self.wheel_rate) <= ANGLE_TRIM_RATE_MAX
        # Brief wheel motion freezes learning but does not invalidate a learned
        # bias. Clear opposing trim for a large error or a fast-moving request.
        release = abs(error) > ANGLE_TRIM_ERROR_MAX or abs(self.requested_rate) > ANGLE_TRIM_RATE_MAX
        if not CS.steeringPressed and release and error * self.angle_trim < 0.0:
          self.angle_trim = 0.0
        trimmed_target = target + self.angle_trim
        entry_lead, cue = 0.0, 0.0
        if self.turn_preview and not CS.steeringPressed and not (status_fresh and pscm_status.limit >= 2):
          from openpilot.selfdrive.controls.lib.ford_turn_preview import turn_preview_lead
          entry_lead, cue = turn_preview_lead(self.requested_rate, turn_preview, now)
          signal = int(CS.leftBlinker) - int(CS.rightBlinker)
          if signal * entry_lead <= 0.0:
            entry_lead = 0.0
        inverse_target = trimmed_target + entry_lead
        inverse = invert_angle(self.angle, speed, inverse_target, angle, yaw, yaw * speed / 3.6, self.wheelbase, self.ratio)
        # Firmware phase is estimated from elapsed time. Cover the 1/2 firmware
        # ticks before the next nominal 100 Hz transmit; all phases are tested.
        ticks = max(1, min(2, int((self.phase + 0.01 + 1e-12) / 0.008)))
        command, info = self.encoder.choose(
          speed, inverse['curvature'], phase=0 if ticks == 2 else 2,
          curvature_rate=self.requested_rate / inverse['slope_per_curvature'], preview=TARGET_PREVIEW,
          curvature_bound=inverse['allowance'] / (speed / 3.6)**2,
        )
        base_command = command
        entry_weight = 0.0
        if self.turn_entry_assist and not CS.steeringPressed and not inverse['accel_limited'] and not (status_fresh and pscm_status.limit >= 2):
          entry_weight = turn_entry_weight(target, angle, self.requested_rate)
        if entry_weight:
          extra = math.copysign(entry_weight, target)
          command = quantize((command[0] + extra * TURN_ENTRY_C0_MAX, command[1] + extra * TURN_ENTRY_C1_MAX))
        # Apply after selection so nominal slew equivalence cannot discard the
        # added request. record_sent/advance still observe the actual packets;
        # their retained state can affect later commands after this term clears.
        details = {
          'geometry_lead': entry_lead,
          'geometry_cue': cue,
          'inverse_target': inverse_target,
          'base_wire_command': tuple(map(float, base_command)),
          'turn_entry_weight': entry_weight,
          'turn_entry_c0': float(command[0] - base_command[0]),
          'turn_entry_c1': float(command[1] - base_command[1]),
          'requested_angle': target,
          'trimmed_angle': trimmed_target,
          'angle_trim': self.angle_trim,
          'wheel_rate': self.wheel_rate,
          'requested_rate': self.requested_rate,
          'target_preview_seconds': TARGET_PREVIEW,
          'target_preview_delta': self.requested_rate * TARGET_PREVIEW,
          'target_preview_limited': info['preview_limited'],
          'reachable_angle': inverse['reachable_target'],
          'target_curvature': inverse['curvature'],
          'predicted_curvature': float(info['first_state'][3]),  # Encoder prediction before optional entry assist.
          'accel_limited': inverse['accel_limited'],
        }
        # Learn only small residual errors while the wheel is settling. Large
        # entry lag and saturated actuation must not wind up a centering trim.
        # Opposing error can still bleed existing trim toward zero. A light
        # touch freezes learning; it does not cut the base command or held trim.
        limited = inverse['accel_limited'] or (status_fresh and pscm_status.limit == 2) or abs(command[0]) >= C0_BOUND or abs(command[1]) >= C1_BOUND
        learning = CS.vEgo >= 2.0 and settling and not limited
        if not CS.steeringPressed:
          increment = ANGLE_TRIM_KI * max(-ANGLE_TRIM_MAX, min(ANGLE_TRIM_MAX, error)) * dt
          if not learning:
            increment = max(min(-self.angle_trim, 0.0), min(max(-self.angle_trim, 0.0), increment))
          self.angle_trim = max(-ANGLE_TRIM_MAX, min(ANGLE_TRIM_MAX, self.angle_trim + increment))
        details['trim_learning'] = bool(learning and not CS.steeringPressed)
      except (ValueError, OverflowError, ArithmeticError):
        self.fault = 'invalid_prediction'
        self.angle_trim = 0.0
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
      'hypothesis': 'ford-joint-signaled-preview-v1' if self.turn_preview else ('ford-joint-turn-entry-v1' if self.turn_entry_assist else 'ford-joint-v24'),
      'turn_preview_enabled': self.turn_preview,
      'turn_entry_enabled': self.turn_entry_assist,
      'turn_entry_weight': 0.0,
      'turn_entry_c0': 0.0,
      'turn_entry_c1': 0.0,
      'status': self.fault or ('active' if active else 'inactive'),
      'driver_override': override,
      'driver_pressed': bool(CS.steeringPressed),
      'yaw_source': 'calibrated_pose',
      'yaw_rate': yaw if math.isfinite(yaw) else None,
      'can_yaw_rate': float(CS.yawRate) if math.isfinite(CS.yawRate) else None,
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
