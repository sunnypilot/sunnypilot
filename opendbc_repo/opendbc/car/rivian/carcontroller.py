import numpy as np
from opendbc.can import CANPacker
from opendbc.car import Bus
from opendbc.car.interfaces import CarControllerBase
from opendbc.car.rivian.riviancan import create_longitudinal, create_wheel_touch, create_adas_status, create_epas_status, create_steering_control, create_longitudinal_interface, create_epas_adas_status
from opendbc.car.rivian.values import CarControllerParams

from opendbc.sunnypilot.car.rivian.mads import MadsCarController


class CarController(CarControllerBase, MadsCarController):
  def __init__(self, dbc_names, CP, CP_SP):
    CarControllerBase.__init__(self, dbc_names, CP, CP_SP)
    MadsCarController.__init__(self)
    self.packer = CANPacker(dbc_names[Bus.pt])

    self.cancel_frames = 0

  def update(self, CC, CC_SP, CS, now_nanos):
    MadsCarController.update(self, CC, CC_SP, CS)
    actuators = CC.actuators
    can_sends = []

    # Use angle-based steering control (Driver+)
    apply_angle = float(actuators.steeringAngleDeg) if self.mads.lat_active else 0.0

    if self.frame % 5 == 0:
      can_sends.append(create_wheel_touch(self.packer, CS.sccm_wheel_touch, CC.enabled))

    # Send EPAS status on bus 0
    can_sends.append(create_epas_status(self.packer, self.frame, CC.enabled))

    # Send EPAS ADAS status with EAC status on bus 0
    can_sends.append(create_epas_adas_status(self.packer, self.frame, CC.enabled))

    # Send steering control with angle command on bus 0
    can_sends.append(create_steering_control(self.packer, self.frame, apply_angle, CC.enabled))

    # Send longitudinal interface enable on bus 0
    can_sends.append(create_longitudinal_interface(self.packer, self.frame, CC.enabled))

    # Longitudinal control
    if self.CP.openpilotLongitudinalControl:
      accel = float(np.clip(actuators.accel, CarControllerParams.ACCEL_MIN, CarControllerParams.ACCEL_MAX))
      can_sends.append(create_longitudinal(self.packer, self.frame, accel, CC.enabled))
    else:
      interface_status = None
      if CC.cruiseControl.cancel:
        # if there is a noEntry, we need to send a status of "available" before the ACM will accept "unavailable"
        # send "available" right away as the VDM itself takes a few frames to acknowledge
        interface_status = 1 if self.cancel_frames < 5 else 0
        self.cancel_frames += 1
      else:
        self.cancel_frames = 0

      can_sends.append(create_adas_status(self.packer, CS.vdm_adas_status, interface_status, CC.enabled))

    new_actuators = actuators.as_builder()
    new_actuators.steeringAngleDeg = apply_angle

    self.frame += 1
    return new_actuators, can_sends
