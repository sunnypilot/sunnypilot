from cereal import car
from panda import Panda
from openpilot.common.conversions import Conversions as CV
from openpilot.selfdrive.car import get_safety_config, create_mads_event
from openpilot.selfdrive.car.ford.fordcan import CanBus
from openpilot.common.params import Params
from openpilot.selfdrive.car.ford.values import CANFD_CAR, Ecu, BUTTON_STATES, FordFlagsSP
from openpilot.selfdrive.car.interfaces import CarInterfaceBase

ButtonType = car.CarState.ButtonEvent.Type
TransmissionType = car.CarParams.TransmissionType
GearShifter = car.CarState.GearShifter


class CarInterface(CarInterfaceBase):
  def __init__(self, CP, CarController, CarState):
    super().__init__(CP, CarController, CarState)

    self.buttonStatesPrev = BUTTON_STATES.copy()

  @staticmethod
  def _get_params(ret, candidate, fingerprint, car_fw, experimental_long, docs):
    ret.carName = "ford"

    ret.radarUnavailable = candidate not in CANFD_CAR
    ret.steerControlType = car.CarParams.SteerControlType.angle
    ret.steerActuatorDelay = 0.2
    ret.steerLimitTimer = 1.0

    ret.longitudinalTuning.kpBP = [0.]
    ret.longitudinalTuning.kpV = [0.5]
    ret.longitudinalTuning.kiV = [0.]

    CAN = CanBus(fingerprint=fingerprint)
    cfgs = [get_safety_config(car.CarParams.SafetyModel.ford)]
    if CAN.main >= 4:
      cfgs.insert(0, get_safety_config(car.CarParams.SafetyModel.noOutput))
    ret.safetyConfigs = cfgs

    ret.experimentalLongitudinalAvailable = True
    if experimental_long:
      ret.safetyConfigs[-1].safetyParam |= Panda.FLAG_FORD_LONG_CONTROL
      ret.openpilotLongitudinalControl = True

    if candidate in CANFD_CAR:
      ret.safetyConfigs[-1].safetyParam |= Panda.FLAG_FORD_CANFD

    if ret.spFlags & FordFlagsSP.SP_ENHANCED_LAT_CONTROL:
      ret.safetyConfigs[-1].safetyParam |= Panda.FLAG_FORD_ENHANCED_LAT_CONTROL

    if Params().get("DongleId", encoding='utf8') in ("4fde83db16dc0802", "112e4d6e0cad05e1", "e36b272d5679115f", "24574459dd7fb3e0", "83a4e056c7072678"):
      ret.spFlags |= FordFlagsSP.SP_ENHANCED_LAT_CONTROL.value

    ret.longitudinalTuning.kpBP = [0.]
    ret.longitudinalTuning.kpV = [0.5]
    ret.longitudinalTuning.kiV = [0.]
    ret.longitudinalTuning.deadzoneBP = [0., 9.]
    ret.longitudinalTuning.deadzoneV = [.0, .20]

    # Auto Transmission: 0x732 ECU or Gear_Shift_by_Wire_FD1
    found_ecus = [fw.ecu for fw in car_fw]
    if Ecu.shiftByWire in found_ecus or 0x5A in fingerprint[CAN.main] or docs:
      ret.transmissionType = TransmissionType.automatic
    else:
      ret.transmissionType = TransmissionType.manual
      ret.minEnableSpeed = 20.0 * CV.MPH_TO_MS

    # BSM: Side_Detect_L_Stat, Side_Detect_R_Stat
    # TODO: detect bsm in car_fw?
    ret.enableBsm = 0x3A6 in fingerprint[CAN.main] and 0x3A7 in fingerprint[CAN.main]

    # LCA can steer down to zero
    ret.minSteerSpeed = 0.

    ret.autoResumeSng = ret.minEnableSpeed == -1.
    ret.centerToFront = ret.wheelbase * 0.44
    return ret

  def _update(self, c):
    ret = self.CS.update(self.cp, self.cp_cam)
    self.CS = self.sp_update_params(self.CS)

    buttonEvents = []

    for button in self.CS.buttonStates:
      if self.CS.buttonStates[button] != self.buttonStatesPrev[button]:
        be = car.CarState.ButtonEvent.new_message()
        be.type = button
        be.pressed = self.CS.buttonStates[button]
        buttonEvents.append(be)

    self.CS.mads_enabled = self.get_sp_cruise_main_state(ret, self.CS)

    self.CS.accEnabled, buttonEvents = self.get_sp_v_cruise_non_pcm_state(ret, self.CS.accEnabled,
                                                                          buttonEvents, c.vCruise)

    if ret.cruiseState.available:
      if self.enable_mads:
        if not self.CS.prev_mads_enabled and self.CS.mads_enabled:
          self.CS.madsEnabled = True
        if not self.CS.prev_lkas_enabled and self.CS.lkas_enabled:
          self.CS.madsEnabled = not self.CS.madsEnabled
        self.CS.madsEnabled = self.get_acc_mads(ret.cruiseState.enabled, self.CS.accEnabled, self.CS.madsEnabled)
      ret, self.CS = self.toggle_gac(ret, self.CS, self.CS.buttonStates["gapAdjustCruise"], 1, 3, 4, "-")
    else:
      self.CS.madsEnabled = False

    if not self.CP.pcmCruise or (self.CP.pcmCruise and self.CP.minEnableSpeed > 0):
      if any(b.type == ButtonType.cancel for b in buttonEvents):
        self.CS.madsEnabled, self.CS.accEnabled = self.get_sp_cancel_cruise_state(self.CS.madsEnabled)
    if self.get_sp_pedal_disengage(ret):
      self.CS.madsEnabled, self.CS.accEnabled = self.get_sp_cancel_cruise_state(self.CS.madsEnabled)
      ret.cruiseState.enabled = False if self.CP.pcmCruise else self.CS.accEnabled

    if self.CP.pcmCruise and self.CP.minEnableSpeed > 0 and self.CP.pcmCruiseSpeed:
      if ret.gasPressed and not ret.cruiseState.enabled:
        self.CS.accEnabled = False
      self.CS.accEnabled = ret.cruiseState.enabled or self.CS.accEnabled

    ret, self.CS = self.get_sp_common_state(ret, self.CS)

    if self.CS.out.madsEnabled != self.CS.madsEnabled:
      if self.mads_event_lock:
        buttonEvents.append(create_mads_event(self.mads_event_lock))
        self.mads_event_lock = False
    else:
      if not self.mads_event_lock:
        buttonEvents.append(create_mads_event(self.mads_event_lock))
        self.mads_event_lock = True

    ret.buttonEvents = buttonEvents

    events = self.create_common_events(ret, c, extra_gears=[GearShifter.manumatic], pcm_enable=False)

    events, ret = self.create_sp_events(self.CS, ret, events)

    if not self.CS.vehicle_sensors_valid:
      events.add(car.CarEvent.EventName.vehicleSensorsInvalid)

    ret.events = events.to_msg()

    # update previous car states
    self.buttonStatesPrev = self.CS.buttonStates.copy()

    return ret

  def apply(self, c, now_nanos):
    return self.CC.update(c, self.CS, now_nanos)
