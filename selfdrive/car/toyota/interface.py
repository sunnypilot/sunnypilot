from cereal import car
from openpilot.common.numpy_fast import clip
from openpilot.common.params import Params
from panda import Panda
from panda.python import uds
from openpilot.selfdrive.car.toyota.values import Ecu, CAR, DBC, ToyotaFlags, ToyotaFlagsSP, CarControllerParams, TSS2_CAR, RADAR_ACC_CAR, NO_DSU_CAR, \
                                        MIN_ACC_SPEED, EPS_SCALE, UNSUPPORTED_DSU_CAR, NO_STOP_TIMER_CAR, ANGLE_CONTROL_CAR
from openpilot.selfdrive.car import create_button_events, get_safety_config, create_mads_event
from openpilot.selfdrive.car.disable_ecu import disable_ecu
from openpilot.selfdrive.car.interfaces import CarInterfaceBase

ButtonType = car.CarState.ButtonEvent.Type
EventName = car.CarEvent.EventName
SteerControlType = car.CarParams.SteerControlType
GearShifter = car.CarState.GearShifter

class CarInterface(CarInterfaceBase):
  @staticmethod
  def get_pid_accel_limits(CP, current_speed, cruise_speed):
    return CarControllerParams.ACCEL_MIN, CarControllerParams.ACCEL_MAX

  @staticmethod
  def _get_params(ret, candidate, fingerprint, car_fw, experimental_long, docs):
    ret.carName = "toyota"
    ret.safetyConfigs = [get_safety_config(car.CarParams.SafetyModel.toyota)]
    ret.safetyConfigs[0].safetyParam = EPS_SCALE[candidate]

    # BRAKE_MODULE is on a different address for these cars
    if DBC[candidate]["pt"] == "toyota_new_mc_pt_generated":
      ret.safetyConfigs[0].safetyParam |= Panda.FLAG_TOYOTA_ALT_BRAKE

    if candidate in ANGLE_CONTROL_CAR:
      ret.steerControlType = SteerControlType.angle
      ret.safetyConfigs[0].safetyParam |= Panda.FLAG_TOYOTA_LTA

      # LTA control can be more delayed and winds up more often
      ret.steerActuatorDelay = 0.18
      ret.steerLimitTimer = 0.8
    else:
      CarInterfaceBase.configure_torque_tune(candidate, ret.lateralTuning)

      ret.steerActuatorDelay = 0.12  # Default delay, Prius has larger delay
      ret.steerLimitTimer = 0.4

      if 0x23 in fingerprint[0]:  # Detect if ZSS is present
        ret.spFlags |= ToyotaFlagsSP.SP_ZSS.value

    ret.stoppingControl = False  # Toyota starts braking more when it thinks you want to stop

    stop_and_go = candidate in TSS2_CAR

    # Detect smartDSU, which intercepts ACC_CMD from the DSU (or radar) allowing openpilot to send it
    # 0x2AA is sent by a similar device which intercepts the radar instead of DSU on NO_DSU_CARs
    if 0x2FF in fingerprint[0] or (0x2AA in fingerprint[0] and candidate in NO_DSU_CAR):
      ret.flags |= ToyotaFlags.SMART_DSU.value
      ret.safetyConfigs[0].safetyParam |= Panda.FLAG_TOYOTA_SDSU

    if 0x2AA in fingerprint[0] and candidate in NO_DSU_CAR:
      ret.flags |= ToyotaFlags.RADAR_CAN_FILTER.value

    # In TSS2 cars, the camera does long control
    found_ecus = [fw.ecu for fw in car_fw]
    ret.enableDsu = len(found_ecus) > 0 and Ecu.dsu not in found_ecus and candidate not in (NO_DSU_CAR | UNSUPPORTED_DSU_CAR) \
                                        and not (ret.flags & ToyotaFlags.SMART_DSU)

    if candidate == CAR.TOYOTA_PRIUS:
      zss = ret.spFlags & ToyotaFlagsSP.SP_ZSS
      stop_and_go = True
      ret.steerRatio = 15.0 if zss else 15.74   # unknown end-to-end spec
      ret.mass = 1529. if zss else 1381.
      # Only give steer angle deadzone to for bad angle sensor prius
      for fw in car_fw:
        if fw.ecu == "eps" and not fw.fwVersion == b'8965B47060\x00\x00\x00\x00\x00\x00':
          ret.steerActuatorDelay = 0.25
          CarInterfaceBase.configure_torque_tune(candidate, ret.lateralTuning, steering_angle_deadzone_deg=0.0 if zss else 0.2)

    elif candidate in (CAR.LEXUS_RX, CAR.LEXUS_RX_TSS2):
      stop_and_go = True
      ret.wheelSpeedFactor = 1.035

    elif candidate in (CAR.TOYOTA_AVALON, CAR.TOYOTA_AVALON_2019, CAR.TOYOTA_AVALON_TSS2):
      # starting from 2019, all Avalon variants have stop and go
      # https://engage.toyota.com/static/images/toyota_safety_sense/TSS_Applicability_Chart.pdf
      stop_and_go = candidate != CAR.TOYOTA_AVALON

    elif candidate in (CAR.TOYOTA_RAV4_TSS2, CAR.TOYOTA_RAV4_TSS2_2022, CAR.TOYOTA_RAV4_TSS2_2023):
      ret.lateralTuning.init('pid')
      ret.lateralTuning.pid.kiBP = [0.0]
      ret.lateralTuning.pid.kpBP = [0.0]
      ret.lateralTuning.pid.kpV = [0.6]
      ret.lateralTuning.pid.kiV = [0.1]
      ret.lateralTuning.pid.kf = 0.00007818594

      # 2019+ RAV4 TSS2 uses two different steering racks and specific tuning seems to be necessary.
      # See https://github.com/commaai/openpilot/pull/21429#issuecomment-873652891
      for fw in car_fw:
        if fw.ecu == "eps" and (fw.fwVersion.startswith(b'\x02') or fw.fwVersion in [b'8965B42181\x00\x00\x00\x00\x00\x00']):
          ret.lateralTuning.pid.kpV = [0.15]
          ret.lateralTuning.pid.kiV = [0.05]
          ret.lateralTuning.pid.kf = 0.00004
          break

    elif candidate in (CAR.TOYOTA_CHR, CAR.TOYOTA_CAMRY, CAR.TOYOTA_SIENNA, CAR.LEXUS_CTH, CAR.LEXUS_NX):
      # TODO: Some of these platforms are not advertised to have full range ACC, are they similar to SNG_WITHOUT_DSU cars?
      stop_and_go = True

    # TODO: these models can do stop and go, but unclear if it requires sDSU or unplugging DSU.
    #  For now, don't list stop and go functionality in the docs
    if ret.flags & ToyotaFlags.SNG_WITHOUT_DSU:
      stop_and_go = stop_and_go or bool(ret.flags & ToyotaFlags.SMART_DSU.value) or (ret.enableDsu and not docs)

    ret.centerToFront = ret.wheelbase * 0.44

    # TODO: Some TSS-P platforms have BSM, but are flipped based on region or driving direction.
    # Detect flipped signals and enable for C-HR and others
    ret.enableBsm = 0x3F6 in fingerprint[0] and candidate in TSS2_CAR

    # No radar dbc for cars without DSU which are not TSS 2.0
    # TODO: make an adas dbc file for dsu-less models
    ret.radarUnavailable = DBC[candidate]['radar'] is None or candidate in (NO_DSU_CAR - TSS2_CAR)

    # if the smartDSU is detected, openpilot can send ACC_CONTROL and the smartDSU will block it from the DSU or radar.
    # since we don't yet parse radar on TSS2/TSS-P radar-based ACC cars, gate longitudinal behind experimental toggle
    use_sdsu = bool(ret.flags & ToyotaFlags.SMART_DSU)
    if candidate in (RADAR_ACC_CAR | NO_DSU_CAR):
      ret.experimentalLongitudinalAvailable = use_sdsu or candidate in RADAR_ACC_CAR

      if not use_sdsu:
        # Disabling radar is only supported on TSS2 radar-ACC cars
        if experimental_long and candidate in RADAR_ACC_CAR:
          ret.flags |= ToyotaFlags.DISABLE_RADAR.value
      else:
        use_sdsu = use_sdsu and experimental_long

    # openpilot longitudinal enabled by default:
    #  - non-(TSS2 radar ACC cars) w/ smartDSU installed
    #  - cars w/ DSU disconnected
    #  - TSS2 cars with camera sending ACC_CONTROL where we can block it
    # openpilot longitudinal behind experimental long toggle:
    #  - TSS2 radar ACC cars w/ smartDSU installed
    #  - TSS2 radar ACC cars w/o smartDSU installed (disables radar)
    #  - TSS-P DSU-less cars w/ CAN filter installed (no radar parser yet)
    ret.openpilotLongitudinalControl = (use_sdsu or ret.enableDsu or candidate in (TSS2_CAR - RADAR_ACC_CAR) or bool(ret.flags & ToyotaFlags.DISABLE_RADAR.value)) and \
                                       not Params().get_bool("StockLongToyota")
    ret.autoResumeSng = ret.openpilotLongitudinalControl and candidate in NO_STOP_TIMER_CAR
    ret.enableGasInterceptorDEPRECATED = 0x201 in fingerprint[0] and ret.openpilotLongitudinalControl

    if not ret.openpilotLongitudinalControl:
      ret.safetyConfigs[0].safetyParam |= Panda.FLAG_TOYOTA_STOCK_LONGITUDINAL

    if ret.enableGasInterceptorDEPRECATED:
      ret.safetyConfigs[0].safetyParam |= Panda.FLAG_TOYOTA_GAS_INTERCEPTOR

    if candidate in UNSUPPORTED_DSU_CAR:
      ret.safetyConfigs[0].safetyParam |= Panda.FLAG_TOYOTA_UNSUPPORTED_DSU_CAR

    # min speed to enable ACC. if car can do stop and go, then set enabling speed
    # to a negative value, so it won't matter.
    ret.minEnableSpeed = -1. if (stop_and_go or ret.enableGasInterceptorDEPRECATED) else MIN_ACC_SPEED

    sp_tss2_long_tune = Params().get_bool("ToyotaTSS2Long")

    # hand tuned (July 1, 2024)
    def custom_tss2_longitudinal_tuning():
      ret.vEgoStopping = 0.01
      ret.vEgoStarting = 0.01
      ret.stoppingDecelRate = 0.35

    def default_tss2_longitudinal_tuning():
      ret.vEgoStopping = 0.25
      ret.vEgoStarting = 0.25
      ret.stoppingDecelRate = 0.3  # reach stopping target smoothly

    def default_longitudinal_tuning():
      tune.kiBP = [0., 5., 35.]
      tune.kiV = [3.6, 2.4, 1.5]

    tune = ret.longitudinalTuning
    if candidate in TSS2_CAR or ret.enableGasInterceptorDEPRECATED:
      if sp_tss2_long_tune:
        tune.kiBP = [0., 5., 12., 20., 27., 36., 50]
        tune.kiV = [0.35, 0.23, 0.20, 0.17, 0.10, 0.07, 0.01]
        custom_tss2_longitudinal_tuning()
      else:
        tune.kpV = [0.0]
        tune.kiV = [0.5]
      if candidate in TSS2_CAR:
        default_tss2_longitudinal_tuning()
    else:
      default_longitudinal_tuning()

    if Params().get_bool("ToyotaEnhancedBsm"):
      ret.spFlags |= ToyotaFlagsSP.SP_ENHANCED_BSM.value

    if candidate == CAR.TOYOTA_PRIUS_TSS2:
      ret.spFlags |= ToyotaFlagsSP.SP_NEED_DEBUG_BSM.value

    if Params().get_bool("ToyotaAutoHold") and candidate in (TSS2_CAR - RADAR_ACC_CAR):
      ret.spFlags |= ToyotaFlagsSP.SP_AUTO_BRAKE_HOLD.value

    return ret

  @staticmethod
  def init(CP, logcan, sendcan):
    # disable radar if alpha longitudinal toggled on radar-ACC car without CAN filter/smartDSU
    if CP.flags & ToyotaFlags.DISABLE_RADAR.value:
      communication_control = bytes([uds.SERVICE_TYPE.COMMUNICATION_CONTROL, uds.CONTROL_TYPE.ENABLE_RX_DISABLE_TX, uds.MESSAGE_TYPE.NORMAL])
      disable_ecu(logcan, sendcan, bus=0, addr=0x750, sub_addr=0xf, com_cont_req=communication_control)

  # returns a car.CarState
  def _update(self, c):
    ret = self.CS.update(self.cp, self.cp_cam)
    self.sp_update_params()

    buttonEvents = []
    distance_button = 0

    if self.CP.carFingerprint in (TSS2_CAR - RADAR_ACC_CAR) or (self.CP.flags & ToyotaFlags.SMART_DSU and not self.CP.flags & ToyotaFlags.RADAR_CAN_FILTER):
      buttonEvents = create_button_events(self.CS.distance_button, self.CS.prev_distance_button, {1: ButtonType.gapAdjustCruise})
      distance_button = self.CS.distance_button

    self.CS.mads_enabled = self.get_sp_cruise_main_state(ret, self.CS)

    if ret.cruiseState.available:
      if self.enable_mads:
        if not self.CS.prev_mads_enabled and self.CS.mads_enabled:
          self.CS.madsEnabled = True
        if self.lkas_toggle:
          if self.CS.lta_status_active:
            if (self.CS.prev_lkas_enabled == 16 and self.CS.lkas_enabled == 0) or \
              (self.CS.prev_lkas_enabled == 0 and self.CS.lkas_enabled == 16):
              self.CS.madsEnabled = not self.CS.madsEnabled
          else:
            if (not self.CS.prev_lkas_enabled and self.CS.lkas_enabled) or \
              (self.CS.prev_lkas_enabled == 1 and not self.CS.lkas_enabled):
              self.CS.madsEnabled = not self.CS.madsEnabled
        self.CS.madsEnabled = self.get_acc_mads(ret.cruiseState.enabled, self.CS.accEnabled, self.CS.madsEnabled)
    else:
      self.CS.madsEnabled = False

    if self.get_sp_pedal_disengage(ret):
      self.CS.madsEnabled, self.CS.accEnabled = self.get_sp_cancel_cruise_state(self.CS.madsEnabled)
      if not self.CP.pcmCruise:
        ret.cruiseState.enabled = self.CS.accEnabled

    ret, self.CS = self.get_sp_common_state(ret, self.CS, gap_button=bool(distance_button))

    # CANCEL
    if self.CS.out.cruiseState.enabled and not ret.cruiseState.enabled:
      be = car.CarState.ButtonEvent.new_message()
      be.pressed = True
      be.type = ButtonType.cancel
      buttonEvents.append(be)

    # MADS BUTTON
    if self.CS.out.madsEnabled != self.CS.madsEnabled:
      if self.mads_event_lock:
        buttonEvents.append(create_mads_event(self.mads_event_lock))
        self.mads_event_lock = False
    else:
      if not self.mads_event_lock:
        buttonEvents.append(create_mads_event(self.mads_event_lock))
        self.mads_event_lock = True

    ret.buttonEvents = buttonEvents

    # events
    events = self.create_common_events(ret, c, extra_gears=[GearShifter.sport, GearShifter.low, GearShifter.brake],
                                       pcm_enable=False)

    events, ret = self.create_sp_events(self.CS, ret, events)

    # Lane Tracing Assist control is unavailable (EPS_STATUS->LTA_STATE=0) until
    # the more accurate angle sensor signal is initialized
    if self.CP.steerControlType == SteerControlType.angle and not self.CS.accurate_steer_angle_seen:
      events.add(EventName.vehicleSensorsInvalid)

    if self.CP.openpilotLongitudinalControl:
      if ret.cruiseState.standstill and not ret.brakePressed and not self.CP.enableGasInterceptorDEPRECATED:
        events.add(EventName.resumeRequired)
      if self.CS.low_speed_lockout:
        events.add(EventName.lowSpeedLockout)
      if ret.vEgo < self.CP.minEnableSpeed:
        events.add(EventName.belowEngageSpeed)
        if c.actuators.accel > 0.3:
          # some margin on the actuator to not false trigger cancellation while stopping
          events.add(EventName.speedTooLow)
        if ret.vEgo < 0.001:
          # while in standstill, send a user alert
          events.add(EventName.manualRestart)

    # auto brake hold
    if self.CP.spFlags & ToyotaFlagsSP.SP_AUTO_BRAKE_HOLD:
      if self.CC.brake_hold_active and not ret.brakeHoldActive:
        events.add(EventName.spAutoBrakeHold)

    ret.events = events.to_msg()

    return ret
