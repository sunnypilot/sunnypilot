#!/usr/bin/env python3
from cereal import car
from selfdrive.config import Conversions as CV
from selfdrive.car.hyundai.values import CAR, Buttons
from selfdrive.car import STD_CARGO_KG, scale_rot_inertia, scale_tire_stiffness, gen_empty_fingerprint
from selfdrive.car.interfaces import CarInterfaceBase
from common.params import Params
from decimal import Decimal

EventName = car.CarEvent.EventName
ButtonType = car.CarState.ButtonEvent.Type

class CarInterface(CarInterfaceBase):
  def __init__(self, CP, CarController, CarState):
    super().__init__(CP, CarController, CarState)
    self.cp2 = self.CS.get_can2_parser(CP)
    self.lkas_button_alert = False

    self.blinker_status = 0
    self.blinker_timer = 0
    self.mad_mode_enabled = Params().get_bool('MadModeEnabled')

  @staticmethod
  def compute_gb(accel, speed):
    return float(accel) / 3.0

  @staticmethod
  def get_params(candidate, fingerprint=gen_empty_fingerprint(), car_fw=[]):  # pylint: disable=dangerous-default-value
    ret = CarInterfaceBase.get_std_params(candidate, fingerprint)

    ret.carName = "hyundai"
    ret.safetyModel = car.CarParams.SafetyModel.hyundai

    params = Params()
    PidKp = float(Decimal(params.get("PidKp", encoding="utf8")) * Decimal('0.01'))
    PidKi = float(Decimal(params.get("PidKi", encoding="utf8")) * Decimal('0.001'))
    PidKd = float(Decimal(params.get("PidKd", encoding="utf8")) * Decimal('0.01'))
    PidKf = float(Decimal(params.get("PidKf", encoding="utf8")) * Decimal('0.00001'))
    InnerLoopGain = float(Decimal(params.get("InnerLoopGain", encoding="utf8")) * Decimal('0.1'))
    OuterLoopGain = float(Decimal(params.get("OuterLoopGain", encoding="utf8")) * Decimal('0.1'))
    TimeConstant = float(Decimal(params.get("TimeConstant", encoding="utf8")) * Decimal('0.1'))
    ActuatorEffectiveness = float(Decimal(params.get("ActuatorEffectiveness", encoding="utf8")) * Decimal('0.1'))
    Scale = float(Decimal(params.get("Scale", encoding="utf8")) * Decimal('1.0'))
    LqrKi = float(Decimal(params.get("LqrKi", encoding="utf8")) * Decimal('0.001'))
    DcGain = float(Decimal(params.get("DcGain", encoding="utf8")) * Decimal('0.0001'))
    SteerMaxV = float(Decimal(params.get("SteerMaxvAdj", encoding="utf8")) * Decimal('0.1'))

    # Most Hyundai car ports are community features for now
    ret.communityFeature = False

    tire_stiffness_factor = float(Decimal(params.get("TireStiffnessFactorAdj", encoding="utf8")) * Decimal('0.01'))
    ret.steerActuatorDelay = float(Decimal(params.get("SteerActuatorDelayAdj", encoding="utf8")) * Decimal('0.01'))
    ret.steerRateCost = float(Decimal(params.get("SteerRateCostAdj", encoding="utf8")) * Decimal('0.01'))
    ret.steerLimitTimer = float(Decimal(params.get("SteerLimitTimerAdj", encoding="utf8")) * Decimal('0.01'))
    ret.steerRatio = float(Decimal(params.get("SteerRatioAdj", encoding="utf8")) * Decimal('0.0001'))

    lat_control_method = int(params.get("LateralControlMethod", encoding="utf8"))
    shane_feed_forward = params.get_bool("ShaneFeedForward")
    if lat_control_method == 0:
      ret.lateralTuning.pid.kf = PidKf
      ret.lateralTuning.pid.kpBP = [0., 9.]
      ret.lateralTuning.pid.kpV = [0.1, PidKp]
      ret.lateralTuning.pid.kiBP = [0., 9.]
      ret.lateralTuning.pid.kiV = [0.01, PidKi]
      ret.lateralTuning.pid.kdBP = [0.]
      ret.lateralTuning.pid.kdV = [PidKd]
      ret.lateralTuning.pid.newKfTuned = True if shane_feed_forward else False # Shane's feedforward
    elif lat_control_method == 1:
      ret.lateralTuning.init('indi')
      ret.lateralTuning.indi.innerLoopGainBP = [0., 9.]
      ret.lateralTuning.indi.innerLoopGainV = [3.0, InnerLoopGain] # third tune. Highest value that still gives smooth control. Effects turning into curves.
      ret.lateralTuning.indi.outerLoopGainBP = [0., 9.]
      ret.lateralTuning.indi.outerLoopGainV = [1.5, OuterLoopGain] # forth tune. Highest value that still gives smooth control. Effects lane centering.
      ret.lateralTuning.indi.timeConstantBP = [0., 9.]
      ret.lateralTuning.indi.timeConstantV = [2.0, TimeConstant] # second tune. Lowest value with smooth actuation. Avoid the noise of actuator gears thrashing.
      ret.lateralTuning.indi.actuatorEffectivenessBP = [0., 9.]
      ret.lateralTuning.indi.actuatorEffectivenessV = [3.0, ActuatorEffectiveness] # first tune. Lowest value without oversteering. May vary with speed.
      # lateralTuning.indi.actuatorEffectiveness
        # As effectiveness increases, actuation strength decreases
        # Too high: weak, sloppy lane centering, slow oscillation, can't follow high curvature, high steering error causes snappy corrections
        # Too low: overpower, saturation, jerky, fast oscillation
        # Just right: Highest still able to maintain good lane centering.
      # lateralTuning.indi.timeConstant
        # Extend exponential decay of prior output steer
        # Too high: sloppy lane centering
        # Too low: noisy actuation, responds to every bump, maybe unable to maintain lane center due to rapid actuation
        # Just right: above noisy actuation and lane centering instability
      # lateralTuning.indi.innerLoopGain
        # Steer rate error gain
        # Too high: jerky oscillation in high curvature
        # Too low: sloppy, cannot accomplish desired steer angle
        # Just right: brief snap on entering high curvature
      # lateralTuning.indi.outerLoopGain
        # Steer error gain
        # Too high: twitchy hyper lane centering, oversteering
        # Too low: sloppy, all over lane
        # Just right: crisp lane centering
    elif lat_control_method == 2:
      ret.lateralTuning.init('lqr')
      ret.lateralTuning.lqr.scale = Scale
      ret.lateralTuning.lqr.ki = LqrKi
      ret.lateralTuning.lqr.a = [0., 1., -0.22619643, 1.21822268]
      ret.lateralTuning.lqr.b = [-1.92006585e-04, 3.95603032e-05]
      ret.lateralTuning.lqr.c = [1., 0.]
      ret.lateralTuning.lqr.k = [-110., 451.]
      ret.lateralTuning.lqr.l = [0.33, 0.318]
      ret.lateralTuning.lqr.dcGain = DcGain

    ret.steerMaxV = [SteerMaxV]
    ret.steerMaxBP = [0.]

    if candidate == CAR.GENESIS:
      ret.mass = 1900. + STD_CARGO_KG
      ret.wheelbase = 3.01
    elif candidate == CAR.GENESIS_G70:
      ret.mass = 1640. + STD_CARGO_KG
      ret.wheelbase = 2.84
    elif candidate == CAR.GENESIS_G80:
      ret.mass = 1855. + STD_CARGO_KG
      ret.wheelbase = 3.01
    elif candidate == CAR.GENESIS_G90:
      ret.mass = 2200
      ret.wheelbase = 3.15
    elif candidate == CAR.SANTA_FE:
      ret.mass = 1694 + STD_CARGO_KG
      ret.wheelbase = 2.765
    elif candidate in [CAR.SONATA, CAR.SONATA_HEV]:
      ret.mass = 1513. + STD_CARGO_KG
      ret.wheelbase = 2.84
    elif candidate == CAR.SONATA_LF:
      ret.mass = 4497. * CV.LB_TO_KG
      ret.wheelbase = 2.804
    elif candidate == CAR.SONATA_LF_TURBO:
      ret.mass = 1470. + STD_CARGO_KG
      ret.wheelbase = 2.805
    elif candidate == CAR.SONATA_LF_HEV:
      ret.mass = 1595. + STD_CARGO_KG
      ret.wheelbase = 2.805
    elif candidate == CAR.PALISADE:
      ret.mass = 1999. + STD_CARGO_KG
      ret.wheelbase = 2.90
    elif candidate == CAR.AVANTE:
      ret.mass = 1245. + STD_CARGO_KG
      ret.wheelbase = 2.72
    elif candidate == CAR.I30:
      ret.mass = 1380. + STD_CARGO_KG
      ret.wheelbase = 2.65
    elif candidate == CAR.KONA:
      ret.mass = 1275. + STD_CARGO_KG
      ret.wheelbase = 2.7
    elif candidate in [CAR.KONA_HEV, CAR.KONA_EV]:
      ret.mass = 1425. + STD_CARGO_KG
      ret.wheelbase = 2.6
    elif candidate in [CAR.IONIQ_HEV, CAR.IONIQ_EV]:
      ret.mass = 1490. + STD_CARGO_KG   #weight per hyundai site https://www.hyundaiusa.com/ioniq-electric/specifications.aspx
      ret.wheelbase = 2.7
    elif candidate in [CAR.GRANDEUR_IG, CAR.GRANDEUR_IG_HEV]:
      ret.mass = 1675. + STD_CARGO_KG
      ret.wheelbase = 2.845
    elif candidate in [CAR.GRANDEUR_IG_FL, CAR.GRANDEUR_IG_FL_HEV]:
      ret.mass = 1725. + STD_CARGO_KG
      ret.wheelbase = 2.885
    elif candidate == CAR.VELOSTER:
      ret.mass = 3558. * CV.LB_TO_KG
      ret.wheelbase = 2.80
    elif candidate == CAR.NEXO:
      ret.mass = 1885. + STD_CARGO_KG
      ret.wheelbase = 2.79
    # kia
    elif candidate == CAR.SORENTO:
      ret.mass = 1985. + STD_CARGO_KG
      ret.wheelbase = 2.78
    elif candidate in [CAR.K5, CAR.K5_HEV]:
      ret.wheelbase = 2.805
      ret.mass = 1600. + STD_CARGO_KG
    elif candidate == CAR.STINGER:
      ret.mass = 1825.0 + STD_CARGO_KG
      ret.wheelbase = 2.906 # https://www.kia.com/us/en/stinger/specs
    elif candidate == CAR.K3:
      ret.mass = 1260. + STD_CARGO_KG
      ret.wheelbase = 2.70
    elif candidate == CAR.CEED:
      ret.mass = 1350. + STD_CARGO_KG
      ret.wheelbase = 2.65
    elif candidate == CAR.SPORTAGE:
      ret.mass = 1985. + STD_CARGO_KG
      ret.wheelbase = 2.78
    elif candidate in [CAR.NIRO_HEV, CAR.NIRO_EV]:
      ret.mass = 1737. + STD_CARGO_KG
      ret.wheelbase = 2.7
    elif candidate in [CAR.K7, CAR.K7_HEV]:
      ret.mass = 1680. + STD_CARGO_KG
      ret.wheelbase = 2.855
    elif candidate == CAR.SELTOS:
      ret.mass = 1310. + STD_CARGO_KG
      ret.wheelbase = 2.6
    elif candidate == CAR.SOUL_EV:
      ret.mass = 1375. + STD_CARGO_KG
      ret.wheelbase = 2.6

    ret.radarTimeStep = 0.05
    ret.centerToFront = ret.wheelbase * 0.4

    # TODO: get actual value, for now starting with reasonable value for
    # civic and scaling by mass and wheelbase
    ret.rotationalInertia = scale_rot_inertia(ret.mass, ret.wheelbase)

    # TODO: start from empirically derived lateral slip stiffness for the civic and scale by
    # mass and CG position, so all cars will have approximately similar dyn behaviors
    ret.tireStiffnessFront, ret.tireStiffnessRear = scale_tire_stiffness(ret.mass, ret.wheelbase, ret.centerToFront,
                                                                         tire_stiffness_factor=tire_stiffness_factor)

    # no rear steering, at least on the listed cars above
    ret.steerRatioRear = 0.
    ret.steerControlType = car.CarParams.SteerControlType.torque

    # TODO: adjust?
    ret.gasMaxBP = [0., 4., 9., 17., 23., 31.]    # m/s
    ret.gasMaxV = [1.5, 1.1, 0.6, 0.5, 0.4, 0.3]    # max gas allowed
    ret.brakeMaxBP = [0., 8.]  # m/s
    ret.brakeMaxV = [0.7, 3.0]   # max brake allowed

    ret.longitudinalTuning.kpBP = [0., 4., 9., 17., 23., 31.]
    ret.longitudinalTuning.kpV = [0.6, 0.7, 0.54, 0.38, 0.28, 0.19]
    ret.longitudinalTuning.kiBP = [0., 4., 9., 17., 23., 31.]
    ret.longitudinalTuning.kiV = [0.015, 0.025, 0.025, 0.02, 0.018, 0.016]

    ret.longitudinalTuning.deadzoneBP = [0., 9., 17.]
    ret.longitudinalTuning.deadzoneV = [0., 0.1, 0.05]
    ret.longitudinalTuning.kdBP = [0., 4., 9., 17., 23., 31.]
    ret.longitudinalTuning.kdV = [0.8, 0.7, 0.7, 0.7, 0.45, 0.35]
    ret.longitudinalTuning.kfBP = [0., 4., 9., 17., 23., 31.]
    ret.longitudinalTuning.kfV = [1., 1.1, 1.2, 1., 0.9, 0.7]

    ret.enableCamera = True
    ret.enableBsm = 0x58b in fingerprint[0]

    ret.stoppingControl = True
    ret.startAccel = 0.3

    ret.standStill = False
    ret.vCruisekph = 0

    # ignore CAN2 address if L-CAN on the same BUS
    ret.mdpsBus = 1 if 593 in fingerprint[1] and 1296 not in fingerprint[1] else 0
    ret.sasBus = 1 if 688 in fingerprint[1] and 1296 not in fingerprint[1] else 0
    ret.sccBus = 0 if 1056 in fingerprint[0] else 1 if 1056 in fingerprint[1] and 1296 not in fingerprint[1] \
                                                                     else 2 if 1056 in fingerprint[2] else -1
    ret.fcaBus = 0 if 909 in fingerprint[0] else 2 if 909 in fingerprint[2] else -1
    ret.bsmAvailable = True if 1419 in fingerprint[0] else False
    ret.lfaAvailable = True if 1157 in fingerprint[2] else False
    ret.lvrAvailable = True if 871 in fingerprint[0] else False
    ret.evgearAvailable = True if 882 in fingerprint[0] else False
    ret.emsAvailable = True if 608 and 809 in fingerprint[0] else False

    ret.radarOffCan = ret.sccBus == -1
    ret.openpilotLongitudinalControl = ret.sccBus == 2
    
    # enableCruise is true
    ret.enableCruise = not ret.radarOffCan
    
    # set safety_hyundai_community only for non-SCC, MDPS harrness or SCC harrness cars or cars that have unknown issue
    if ret.radarOffCan or ret.mdpsBus == 1 or ret.openpilotLongitudinalControl or ret.sccBus == 1 or params.get_bool("MadModeEnabled"):
      ret.safetyModel = car.CarParams.SafetyModel.hyundaiCommunity
    return ret

  def update(self, c, can_strings):
    self.cp.update_strings(can_strings)
    self.cp2.update_strings(can_strings)
    self.cp_cam.update_strings(can_strings)

    ret = self.CS.update(self.cp, self.cp2, self.cp_cam)
    ret.canValid = self.cp.can_valid and self.cp2.can_valid and self.cp_cam.can_valid
    ret.steeringRateLimited = self.CC.steer_rate_limited if self.CC is not None else False

    if self.CP.enableCruise and not self.CC.scc_live:
      self.CP.enableCruise = False
    elif self.CC.scc_live and not self.CP.enableCruise:
      self.CP.enableCruise = True

    # most HKG cars has no long control, it is safer and easier to engage by main on
    if self.mad_mode_enabled:
      ret.cruiseState.enabled = ret.cruiseState.available


    # low speed steer alert hysteresis logic (only for cars with steer cut off above 10 m/s)
    if ret.vEgo < (self.CP.minSteerSpeed + 0.2) and self.CP.minSteerSpeed > 10.:
      self.low_speed_alert = True
    if ret.vEgo > (self.CP.minSteerSpeed + 0.7):
      self.low_speed_alert = False

    buttonEvents = []
    if self.CS.cruise_buttons != self.CS.prev_cruise_buttons:
      be = car.CarState.ButtonEvent.new_message()
      be.pressed = self.CS.cruise_buttons != 0
      but = self.CS.cruise_buttons if be.pressed else self.CS.prev_cruise_buttons
      if but == Buttons.RES_ACCEL:
        be.type = ButtonType.accelCruise
      elif but == Buttons.SET_DECEL:
        be.type = ButtonType.decelCruise
      elif but == Buttons.GAP_DIST:
        be.type = ButtonType.gapAdjustCruise
      #elif but == Buttons.CANCEL:
      #  be.type = ButtonType.cancel
      else:
        be.type = ButtonType.unknown
      buttonEvents.append(be)
    if self.CS.cruise_main_button != self.CS.prev_cruise_main_button:
      be = car.CarState.ButtonEvent.new_message()
      be.type = ButtonType.altButton3
      be.pressed = bool(self.CS.cruise_main_button)
      buttonEvents.append(be)
    ret.buttonEvents = buttonEvents

    events = self.create_common_events(ret)

    if self.CC.longcontrol and self.CS.cruise_unavail:
      events.add(EventName.brakeUnavailable)
    #if abs(ret.steeringAngle) > 90. and EventName.steerTempUnavailable not in events.events:
    #  events.add(EventName.steerTempUnavailable)
    if self.low_speed_alert and not self.CS.mdps_bus:
      events.add(EventName.belowSteerSpeed)
    if self.mad_mode_enabled and EventName.pedalPressed in events.events:
      events.events.remove(EventName.pedalPressed)
    if self.CC.lanechange_manual_timer and ret.vEgo > 0.3:
      events.add(EventName.laneChangeManual)
    if self.CC.emergency_manual_timer:
      events.add(EventName.emgButtonManual)
    #if self.CC.driver_steering_torque_above_timer:
    #  events.add(EventName.driverSteering)
    if self.CC.need_brake and not self.CC.longcontrol:
      events.add(EventName.needBrake)
    if self.CS.cruiseState_standstill or self.CC.standstill_status == 1:
      #events.add(EventName.standStill)
      self.CP.standStill = True
    else:
      self.CP.standStill = False
    if self.CC.v_cruise_kph_auto_res > 30:
      self.CP.vCruisekph = self.CC.v_cruise_kph_auto_res
    else:
      self.CP.vCruisekph = 0

    if self.CC.mode_change_timer and self.CS.out.cruiseState.modeSel == 0:
      events.add(EventName.modeChangeOpenpilot)
    elif self.CC.mode_change_timer and self.CS.out.cruiseState.modeSel == 1:
      events.add(EventName.modeChangeDistcurv)
    elif self.CC.mode_change_timer and self.CS.out.cruiseState.modeSel == 2:
      events.add(EventName.modeChangeDistance)
    elif self.CC.mode_change_timer and self.CS.out.cruiseState.modeSel == 3:
      events.add(EventName.modeChangeOneway)
    elif self.CC.mode_change_timer and self.CS.out.cruiseState.modeSel == 4:
      events.add(EventName.modeChangeMaponly)

  # handle button presses
    for b in ret.buttonEvents:
      # do disable on button down
      if b.type == ButtonType.cancel and b.pressed:
        events.add(EventName.buttonCancel)
      if self.CC.longcontrol and not self.CC.scc_live:
        # do enable on both accel and decel buttons
        if b.type in [ButtonType.accelCruise, ButtonType.decelCruise] and not b.pressed:
          events.add(EventName.buttonEnable)
        if EventName.wrongCarMode in events.events:
          events.events.remove(EventName.wrongCarMode)
        if EventName.pcmDisable in events.events:
          events.events.remove(EventName.pcmDisable)
      elif not self.CC.longcontrol and ret.cruiseState.enabled:
        # do enable on decel button only
        if b.type == ButtonType.decelCruise and not b.pressed:
          events.add(EventName.buttonEnable)

    ret.events = events.to_msg()

    self.CS.out = ret.as_reader()
    return self.CS.out

  def apply(self, c, sm):
    can_sends = self.CC.update(c.enabled, self.CS, self.frame, c.actuators,
                               c.cruiseControl.cancel, c.hudControl.visualAlert, c.hudControl.leftLaneVisible,
                               c.hudControl.rightLaneVisible, c.hudControl.leftLaneDepart, c.hudControl.rightLaneDepart,
                               c.hudControl.setSpeed, c.hudControl.leadVisible, c.hudControl.leadDistance,
                               c.hudControl.leadvRel, c.hudControl.leadyRel, sm)
    self.frame += 1
    return can_sends
