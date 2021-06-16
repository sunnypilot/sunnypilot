import math

from selfdrive.controls.lib.pid import LatPIDController
from selfdrive.controls.lib.drive_helpers import get_steer_max
from cereal import car, log
from common.params import Params
from decimal import Decimal


class LatControlPID():
  def __init__(self, CP):
    self.pid = LatPIDController((CP.lateralTuning.pid.kpBP, CP.lateralTuning.pid.kpV),
                                (CP.lateralTuning.pid.kiBP, CP.lateralTuning.pid.kiV),
                                (CP.lateralTuning.pid.kdBP, CP.lateralTuning.pid.kdV),
                                k_f=CP.lateralTuning.pid.kf, pos_limit=1.0, neg_limit=-1.0,
                                sat_limit=CP.steerLimitTimer)
    self.new_kf_tuned = CP.lateralTuning.pid.newKfTuned
    self.mpc_frame = 0
    self.params = Params()

    self.live_tune_enabled = self.params.get_bool("OpkrLiveTune")
    self.dead_zone = float(Decimal(self.params.get("IgnoreZone", encoding="utf8")) * Decimal('0.1'))

  def reset(self):
    self.pid.reset()

  # live tune referred to kegman's 
  def live_tune(self, CP):
    self.mpc_frame += 1
    if self.mpc_frame % 300 == 0:
      self.steerKpV = float(Decimal(self.params.get("PidKp", encoding="utf8")) * Decimal('0.01'))
      self.steerKiV = float(Decimal(self.params.get("PidKi", encoding="utf8")) * Decimal('0.001'))
      self.steerKdV = float(Decimal(self.params.get("PidKd", encoding="utf8")) * Decimal('0.01'))
      self.steerKf = float(Decimal(self.params.get("PidKf", encoding="utf8")) * Decimal('0.00001'))
      self.pid = LatPIDController((CP.lateralTuning.pid.kpBP, [0.1, self.steerKpV]),
                          (CP.lateralTuning.pid.kiBP, [0.01, self.steerKiV]),
                          (CP.lateralTuning.pid.kdBP, [self.steerKdV]),
                          k_f=self.steerKf, pos_limit=1.0)
      self.mpc_frame = 0

  def update(self, active, CS, CP, VM, params, lat_plan):
    if self.live_tune_enabled:
      self.live_tune(CP)

    pid_log = log.ControlsState.LateralPIDState.new_message()
    pid_log.steeringAngleDeg = float(CS.steeringAngleDeg)
    pid_log.steeringRateDeg = float(CS.steeringRateDeg)

    angle_steers_des_no_offset = math.degrees(VM.get_steer_from_curvature(-lat_plan.curvature, CS.vEgo))
    angle_steers_des = angle_steers_des_no_offset + params.angleOffsetDeg

    if CS.vEgo < 0.3 or not active:
      output_steer = 0.0
      pid_log.active = False
      self.pid.reset()
    else:
      steers_max = get_steer_max(CP, CS.vEgo)
      self.pid.pos_limit = steers_max
      self.pid.neg_limit = -steers_max

      # TODO: feedforward something based on lat_plan.rateSteers
      steer_feedforward = angle_steers_des_no_offset  # offset does not contribute to resistive torque
      if self.new_kf_tuned:
        _c1, _c2, _c3 = 0.35189607550172824, 7.506201251644202, 69.226826411091
        steer_feedforward *= _c1 * CS.vEgo ** 2 + _c2 * CS.vEgo + _c3
      else:
        steer_feedforward *= CS.vEgo**2  # proportional to realigning tire momentum (~ lateral accel)
      deadzone = self.dead_zone

      check_saturation = (CS.vEgo > 10) and not CS.steeringRateLimited and not CS.steeringPressed
      output_steer = self.pid.update(angle_steers_des, CS.steeringAngleDeg, check_saturation=check_saturation, override=CS.steeringPressed,
                                     feedforward=steer_feedforward, speed=CS.vEgo, deadzone=deadzone)
      pid_log.active = True
      pid_log.p = self.pid.p
      pid_log.i = self.pid.i
      pid_log.f = self.pid.f
      pid_log.output = output_steer
      pid_log.saturated = bool(self.pid.saturated)

    return output_steer, 0, pid_log
