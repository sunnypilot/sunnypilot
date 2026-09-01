import math
import numpy as np

from opendbc.car.structs import car
from openpilot.common.constants import CV
from openpilot.sunnypilot.selfdrive.car.cruise_ext import VCruiseHelperSP


# WARNING: this value was determined based on the model's training distribution,
#          model predictions above this speed can be unpredictable
# V_CRUISE's are in kph
V_CRUISE_MIN = 8
V_CRUISE_MAX = 145
V_CRUISE_UNSET = 255
V_CRUISE_INITIAL = 40
V_CRUISE_INITIAL_EXPERIMENTAL_MODE = 128
IMPERIAL_INCREMENT = round(CV.MPH_TO_KPH, 1)  # round here to avoid rounding errors incrementing set speed

ButtonEvent = car.CarState.ButtonEvent
ButtonType = car.CarState.ButtonEvent.Type
CRUISE_LONG_PRESS = 50
TOYOTA_VIRTUAL_CRUISE_LONG_PRESS = 65
CRUISE_NEAREST_FUNC = {
  ButtonType.accelCruise: math.ceil,
  ButtonType.decelCruise: math.floor,
}
CRUISE_INTERVAL_SIGN = {
  ButtonType.accelCruise: +1,
  ButtonType.decelCruise: -1,
}


class VCruiseHelper(VCruiseHelperSP):
  def __init__(self, CP, CP_SP):
    VCruiseHelperSP.__init__(self, CP, CP_SP)
    self.CP = CP
    self.v_cruise_kph = V_CRUISE_UNSET
    self.v_cruise_cluster_kph = V_CRUISE_UNSET
    self.v_cruise_kph_last = 0
    self.button_timers = {ButtonType.decelCruise: 0, ButtonType.accelCruise: 0}
    self.button_change_states = {btn: {"standstill": False, "enabled": False} for btn in self.button_timers}

  @property
  def v_cruise_initialized(self):
    return self.v_cruise_kph != V_CRUISE_UNSET

  @property
  def software_pcm_cruise_speed(self) -> bool:
    return self.CP.brand == "toyota" and self.CP.pcmCruise and self.CP.openpilotLongitudinalControl and not self.CP_SP.pcmCruiseSpeed

  @property
  def cruise_long_press_frames(self) -> int:
    return TOYOTA_VIRTUAL_CRUISE_LONG_PRESS if self.software_pcm_cruise_speed else CRUISE_LONG_PRESS

  @property
  def software_pcm_cruise_initialized(self) -> bool:
    return 0 < self.v_cruise_kph < V_CRUISE_UNSET and 0 < self.v_cruise_cluster_kph < V_CRUISE_UNSET

  def _apply_software_pcm_cruise_delta(self, delta_kph: float, is_metric: bool) -> None:
    """Move Toyota's planner/display targets together while respecting both targets' bounds."""
    cluster_min_kph = self.v_cruise_min if is_metric else self.v_cruise_min * CV.MPH_TO_KPH
    min_delta = max(V_CRUISE_MIN - self.v_cruise_kph, cluster_min_kph - self.v_cruise_cluster_kph)
    max_delta = min(V_CRUISE_MAX - self.v_cruise_kph, V_CRUISE_MAX - self.v_cruise_cluster_kph)
    if delta_kph > 0:
      applied_delta = min(delta_kph, max(0., max_delta))
    else:
      applied_delta = max(delta_kph, min(0., min_delta))
    self.v_cruise_kph = round(self.v_cruise_kph + applied_delta, 1)
    self.v_cruise_cluster_kph = round(self.v_cruise_cluster_kph + applied_delta, 1)

  def update_v_cruise(self, CS, enabled, is_metric):
    self.v_cruise_kph_last = self.v_cruise_kph

    self.get_minimum_set_speed(is_metric)

    _enabled = self.update_enabled_state(CS, enabled)

    if CS.cruiseState.available:
      software_pcm_enabled = not self.CP_SP.pcmCruiseSpeed and _enabled
      if self.software_pcm_cruise_speed:
        software_pcm_enabled = software_pcm_enabled and self.software_pcm_cruise_initialized

      if not self.CP.pcmCruise or software_pcm_enabled:
        # if stock cruise is completely disabled, then we can use our own set speed logic
        self._update_v_cruise_non_pcm(CS, _enabled, is_metric)
        v_cruise_kph_before_sla = self.v_cruise_kph
        self.update_speed_limit_assist_v_cruise_non_pcm()
        if self.software_pcm_cruise_speed:
          sla_delta_kph = self.v_cruise_kph - v_cruise_kph_before_sla
          self.v_cruise_kph = v_cruise_kph_before_sla
          self._apply_software_pcm_cruise_delta(sla_delta_kph, is_metric)
        else:
          self.v_cruise_cluster_kph = self.v_cruise_kph
      else:
        self.v_cruise_kph = CS.cruiseState.speed * CV.MS_TO_KPH
        self.v_cruise_cluster_kph = CS.cruiseState.speedCluster * CV.MS_TO_KPH
        if CS.cruiseState.speed == 0:
          self.v_cruise_kph = V_CRUISE_UNSET
          self.v_cruise_cluster_kph = V_CRUISE_UNSET
        elif CS.cruiseState.speed == -1:
          self.v_cruise_kph = -1
          self.v_cruise_cluster_kph = -1
    else:
      self.v_cruise_kph = V_CRUISE_UNSET
      self.v_cruise_cluster_kph = V_CRUISE_UNSET

    if not self.CP.pcmCruise or not self.CP_SP.pcmCruiseSpeed:
      self.update_button_timers(CS, enabled)

  def _update_v_cruise_non_pcm(self, CS, enabled, is_metric):
    # handle button presses. TODO: this should be in state_control, but a decelCruise press
    # would have the effect of both enabling and changing speed is checked after the state transition
    if not enabled:
      return

    long_press = False
    button_type = None

    v_cruise_delta = 1. if is_metric else IMPERIAL_INCREMENT

    for b in CS.buttonEvents:
      if b.type.raw in self.button_timers and not b.pressed:
        if self.button_timers[b.type.raw] > self.cruise_long_press_frames:
          return  # end long press
        button_type = b.type.raw
        break
    else:
      for k, timer in self.button_timers.items():
        if timer and timer % self.cruise_long_press_frames == 0:
          button_type = k
          long_press = True
          break

    if button_type is None:
      return

    # Don't adjust speed when pressing resume to exit standstill
    cruise_standstill = self.button_change_states[button_type]["standstill"] or CS.cruiseState.standstill
    if button_type == ButtonType.accelCruise and cruise_standstill:
      return

    # Don't adjust speed if we've enabled since the button was depressed (some ports enable on rising edge)
    if not self.button_change_states[button_type]["enabled"]:
      return

    # Speed Limit Assist for Non PCM long cars.
    # True: Disallow set speed changes when user confirmed the target set speed during preActive state
    # False: Allow set speed changes as SLA is not requesting user confirmation
    if self.update_speed_limit_assist_pre_active_confirmed(button_type):
      return

    long_press, v_cruise_delta = VCruiseHelperSP.update_v_cruise_delta(self, long_press, v_cruise_delta)
    # Toyota's canonical PCM set speed and displayed cluster set speed can differ. In
    # software-owned PCM mode, round the value the driver sees and apply the same delta
    # to both targets so the planner/cluster calibration offset remains intact.
    v_cruise_reference = self.v_cruise_cluster_kph if self.software_pcm_cruise_speed else self.v_cruise_kph
    if long_press and v_cruise_reference % v_cruise_delta != 0:  # partial interval
      v_cruise_reference_new = CRUISE_NEAREST_FUNC[button_type](v_cruise_reference / v_cruise_delta) * v_cruise_delta
    else:
      v_cruise_reference_new = v_cruise_reference + v_cruise_delta * CRUISE_INTERVAL_SIGN[button_type]

    if self.software_pcm_cruise_speed:
      delta_kph = v_cruise_reference_new - v_cruise_reference

      # If SET is pressed while overriding, do not lower the target below the current speed.
      if CS.gasPressed and button_type in (ButtonType.decelCruise, ButtonType.setCruise):
        delta_kph = max(delta_kph, CS.vEgo * CV.MS_TO_KPH - self.v_cruise_kph)

      self._apply_software_pcm_cruise_delta(delta_kph, is_metric)
      return

    self.v_cruise_kph += v_cruise_reference_new - v_cruise_reference

    # If set is pressed while overriding, clip cruise speed to minimum of vEgo
    if CS.gasPressed and button_type in (ButtonType.decelCruise, ButtonType.setCruise):
      self.v_cruise_kph = max(self.v_cruise_kph, CS.vEgo * CV.MS_TO_KPH)

    self.v_cruise_kph = np.clip(round(self.v_cruise_kph, 1), self.v_cruise_min, V_CRUISE_MAX)

  def update_button_timers(self, CS, enabled):
    if self.software_pcm_cruise_speed and (not enabled or not CS.cruiseState.available or not self.software_pcm_cruise_initialized):
      for k in self.button_timers:
        self.button_timers[k] = 0
        self.button_change_states[k] = {"standstill": False, "enabled": False}
      return

    # increment timer for buttons still pressed
    for k in self.button_timers:
      if self.button_timers[k] > 0:
        self.button_timers[k] += 1

    for b in CS.buttonEvents:
      if b.type.raw in self.button_timers:
        # Start/end timer and store current state on change of button pressed
        self.button_timers[b.type.raw] = 1 if b.pressed else 0
        self.button_change_states[b.type.raw] = {"standstill": CS.cruiseState.standstill, "enabled": enabled}

  def initialize_v_cruise(self, CS, experimental_mode: bool, dynamic_experimental_control: bool) -> None:
    # initializing is handled by the PCM
    if self.CP.pcmCruise:
      return

    initial_experimental_mode = experimental_mode and not dynamic_experimental_control
    initial = V_CRUISE_INITIAL_EXPERIMENTAL_MODE if initial_experimental_mode else V_CRUISE_INITIAL

    if any(b.type in (ButtonType.accelCruise, ButtonType.resumeCruise) for b in CS.buttonEvents) and self.v_cruise_initialized:
      self.v_cruise_kph = self.v_cruise_kph_last
    else:
      self.v_cruise_kph = int(round(np.clip(CS.vEgo * CV.MS_TO_KPH, initial, V_CRUISE_MAX)))

    self.v_cruise_cluster_kph = self.v_cruise_kph
