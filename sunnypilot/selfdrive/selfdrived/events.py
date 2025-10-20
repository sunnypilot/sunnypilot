import cereal.messaging as messaging
from cereal import log, car, custom
from openpilot.common.constants import CV
from openpilot.sunnypilot.selfdrive.selfdrived.events_base import EventsBase, Priority, ET, Alert, \
  NoEntryAlert, ImmediateDisableAlert, EngagementAlert, NormalPermanentAlert, AlertCallbackType, wrong_car_mode_alert
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit import PCM_LONG_REQUIRED_MAX_SET_SPEED, CONFIRM_SPEED_THRESHOLD


AlertSize = log.SelfdriveState.AlertSize
AlertStatus = log.SelfdriveState.AlertStatus
VisualAlert = car.CarControl.HUDControl.VisualAlert
AudibleAlert = car.CarControl.HUDControl.AudibleAlert
AudibleAlertSP = custom.SelfdriveStateSP.AudibleAlert
EventNameSP = custom.OnroadEventSP.EventName


# get event name from enum
EVENT_NAME_SP = {v: k for k, v in EventNameSP.schema.enumerants.items()}


def speed_limit_adjust_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  speedLimit = sm['longitudinalPlanSP'].speedLimit.resolver.speedLimit
  speed = round(speedLimit * (CV.MS_TO_KPH if metric else CV.MS_TO_MPH))
  message = f'Adjusting to {speed} {"km/h" if metric else "mph"} speed limit'
  return Alert(
    message,
    "",
    AlertStatus.normal, AlertSize.small,
    Priority.LOW, VisualAlert.none, AudibleAlert.none, 4.)


def speed_limit_pre_active_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  speed_conv = CV.MS_TO_KPH if metric else CV.MS_TO_MPH
  speed_limit_final_last = sm['longitudinalPlanSP'].speedLimit.resolver.speedLimitFinalLast
  speed_limit_final_last_conv = round(speed_limit_final_last * speed_conv)
  alert_1_str = ""
  alert_2_str = ""
  alert_size = AlertSize.none

  if CP.openpilotLongitudinalControl and CP.pcmCruise:
    # PCM long
    cst_low, cst_high = PCM_LONG_REQUIRED_MAX_SET_SPEED[metric]
    pcm_long_required_max = cst_low if speed_limit_final_last_conv < CONFIRM_SPEED_THRESHOLD[metric] else cst_high
    pcm_long_required_max_set_speed_conv = round(pcm_long_required_max * speed_conv)
    speed_unit = "km/h" if metric else "mph"

    alert_1_str = "Speed Limit Assist: Activation Required"
    alert_2_str = f"Manually change set speed to {pcm_long_required_max_set_speed_conv} {speed_unit} to activate"
    alert_size = AlertSize.mid

  return Alert(
    alert_1_str,
    alert_2_str,
    AlertStatus.normal, alert_size,
    Priority.LOW, VisualAlert.none, AudibleAlertSP.promptSingleLow, .1)


class EventsSP(EventsBase):
  def __init__(self):
    super().__init__()
    self.event_counters = dict.fromkeys(EVENTS_SP.keys(), 0)

  def get_events_mapping(self) -> dict[int, dict[str, Alert | AlertCallbackType]]:
    return EVENTS_SP

  def get_event_name(self, event: int):
    return EVENT_NAME_SP[event]

  def get_event_msg_type(self):
    return custom.OnroadEventSP.Event


EVENTS_SP: dict[int, dict[str, Alert | AlertCallbackType]] = {
  # sunnypilot
  EventNameSP.lkasEnable: {
    ET.ENABLE: EngagementAlert(AudibleAlert.engage),
  },

  EventNameSP.lkasDisable: {
    ET.USER_DISABLE: EngagementAlert(AudibleAlert.disengage),
  },

  EventNameSP.manualSteeringRequired: {
    ET.USER_DISABLE: Alert(
      "Automatic Lane Centering is OFF",
      "Manual Steering Required",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.disengage, 1.),
  },

  EventNameSP.manualLongitudinalRequired: {
    ET.WARNING: Alert(
      "Smart/Adaptive Cruise Control: OFF",
      "Manual Speed Control Required",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 1.),
  },

  EventNameSP.silentLkasEnable: {
    ET.ENABLE: EngagementAlert(AudibleAlert.none),
  },

  EventNameSP.silentLkasDisable: {
    ET.USER_DISABLE: EngagementAlert(AudibleAlert.none),
  },

  EventNameSP.silentBrakeHold: {
    ET.WARNING: EngagementAlert(AudibleAlert.none),
    ET.NO_ENTRY: NoEntryAlert("Brake Hold Active"),
  },

  EventNameSP.silentWrongGear: {
    ET.WARNING: Alert(
      "",
      "",
      AlertStatus.normal, AlertSize.none,
      Priority.LOWEST, VisualAlert.none, AudibleAlert.none, 0.),
    ET.NO_ENTRY: Alert(
      "Gear not D",
      "openpilot Unavailable",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 0.),
  },

  EventNameSP.silentReverseGear: {
    ET.PERMANENT: Alert(
      "Reverse\nGear",
      "",
      AlertStatus.normal, AlertSize.full,
      Priority.LOWEST, VisualAlert.none, AudibleAlert.none, .2, creation_delay=0.5),
    ET.NO_ENTRY: NoEntryAlert("Reverse Gear"),
  },

  EventNameSP.silentDoorOpen: {
    ET.WARNING: Alert(
      "",
      "",
      AlertStatus.normal, AlertSize.none,
      Priority.LOWEST, VisualAlert.none, AudibleAlert.none, 0.),
    ET.NO_ENTRY: NoEntryAlert("Door Open"),
  },

  EventNameSP.silentSeatbeltNotLatched: {
    ET.WARNING: Alert(
      "",
      "",
      AlertStatus.normal, AlertSize.none,
      Priority.LOWEST, VisualAlert.none, AudibleAlert.none, 0.),
    ET.NO_ENTRY: NoEntryAlert("Seatbelt Unlatched"),
  },

  EventNameSP.silentParkBrake: {
    ET.WARNING: Alert(
      "",
      "",
      AlertStatus.normal, AlertSize.none,
      Priority.LOWEST, VisualAlert.none, AudibleAlert.none, 0.),
    ET.NO_ENTRY: NoEntryAlert("Parking Brake Engaged"),
  },

  EventNameSP.controlsMismatchLateral: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("Controls Mismatch: Lateral"),
    ET.NO_ENTRY: NoEntryAlert("Controls Mismatch: Lateral"),
  },

  EventNameSP.experimentalModeSwitched: {
    ET.WARNING: NormalPermanentAlert("Experimental Mode Switched", duration=1.5)
  },

  EventNameSP.wrongCarModeAlertOnly: {
    ET.WARNING: wrong_car_mode_alert,
  },

  EventNameSP.pedalPressedAlertOnly: {
    ET.WARNING: NoEntryAlert("Pedal Pressed")
  },

  EventNameSP.laneTurnLeft: {
    ET.WARNING: Alert(
      "Turning Left",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 1.),
  },

  EventNameSP.laneTurnRight: {
    ET.WARNING: Alert(
      "Turning Right",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 1.),
  },

  EventNameSP.speedLimitActive: {
    ET.WARNING: Alert(
      "Automatically adjusting to the posted speed limit",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlertSP.promptSingleHigh, 5.),
  },

  EventNameSP.speedLimitChanged: {
    ET.WARNING: Alert(
      "Set speed changed",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlertSP.promptSingleHigh, 5.),
  },

  EventNameSP.speedLimitPreActive: {
    ET.WARNING: speed_limit_pre_active_alert,
  },

  EventNameSP.speedLimitPending: {
    ET.WARNING: Alert(
      "Automatically adjusting to the last speed limit",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlertSP.promptSingleHigh, 5.),
  },

  EventNameSP.e2eChime: {
    ET.PERMANENT: Alert(
      "",
      "",
      AlertStatus.normal, AlertSize.none,
      Priority.MID, VisualAlert.none, AudibleAlert.prompt, 3.),
  },
}
