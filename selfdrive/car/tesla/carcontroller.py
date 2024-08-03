from openpilot.common.numpy_fast import clip
from opendbc.can.packer import CANPacker
from openpilot.selfdrive.car import apply_std_steer_angle_limits
from openpilot.selfdrive.car.interfaces import CarControllerBase
from openpilot.selfdrive.car.tesla.teslacan import TeslaCAN
from openpilot.selfdrive.car.tesla.values import DBC, CarControllerParams


class CarController(CarControllerBase):
  def __init__(self, dbc_name, CP, VM):
    super().__init__(dbc_name, CP, VM)
    self.apply_angle_last = 0
    self.packer = CANPacker(dbc_name)
    self.pt_packer = CANPacker(DBC[CP.carFingerprint]['pt'])
    self.tesla_can = TeslaCAN(self.packer, self.pt_packer)
    self.pcm_cancel_cmd = False # Must be latching because of frame rate

  def update(self, CC, CS, now_nanos):
    actuators = CC.actuators

    can_sends = []

    # Temp disable steering on a hands_on_fault, and allow for user override
    hands_on_fault = CS.hands_on_level >= 3
    lkas_enabled = CC.latActive and not hands_on_fault

    if self.frame % 2 == 0:
      if lkas_enabled:
        # Angular rate limit based on speed
        apply_angle = apply_std_steer_angle_limits(actuators.steeringAngleDeg, self.apply_angle_last, CS.out.vEgo, CarControllerParams)

        # To not fault the EPS
        apply_angle = clip(apply_angle, CS.out.steeringAngleDeg - 20, CS.out.steeringAngleDeg + 20)
      else:
        apply_angle = CS.out.steeringAngleDeg

      self.apply_angle_last = apply_angle
      use_lka_mode = CS.params_list.enable_mads
      can_sends.append(self.tesla_can.create_steering_control(apply_angle, lkas_enabled, (self.frame // 2) % 16, use_lka_mode))


    self.pcm_cancel_cmd = CC.cruiseControl.cancel or not CS.accEnabled or self.pcm_cancel_cmd

    if hands_on_fault and not CS.params_list.enable_mads:
      self.pcm_cancel_cmd = True

    # Unlatch cancel command only when ACC is actually disabled
    if not CS.acc_enabled:
      self.pcm_cancel_cmd = False

    # Longitudinal control
    if self.pcm_cancel_cmd:
      # Increment counter so cancel is prioritized even with stock TACC
      counter = (CS.das_control["DAS_controlCounter"] + 1) % 8
      can_sends.append(self.tesla_can.cancel_acc(counter))
    elif self.CP.openpilotLongitudinalControl:
      acc_state = CS.das_control["DAS_accState"]
      target_accel = actuators.accel
      target_speed = max(CS.out.vEgo + (target_accel * CarControllerParams.ACCEL_TO_SPEED_MULTIPLIER), 0)
      max_accel = 0 if target_accel < 0 else target_accel
      min_accel = 0 if target_accel > 0 else target_accel

      counter = CS.das_control["DAS_controlCounter"]
      can_sends.append(self.tesla_can.create_longitudinal_commands(acc_state, target_speed, min_accel, max_accel, counter))

    # TODO: HUD control

    new_actuators = actuators.as_builder()
    new_actuators.steeringAngleDeg = self.apply_angle_last

    self.frame += 1
    return new_actuators, can_sends
