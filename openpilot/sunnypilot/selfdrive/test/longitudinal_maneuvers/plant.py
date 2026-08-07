"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
import math
import time
from typing import Any

import numpy as np

from openpilot.cereal import log, messaging
from opendbc.car.interfaces import ACCEL_MAX, ACCEL_MIN
from openpilot.common.realtime import DT_CTRL, DT_MDL, Ratekeeper
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.selfdrive.controls.lib.longcontrol import LongControl, LongCtrlState
from openpilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlanner
from openpilot.selfdrive.controls.radard import _LEAD_ACCEL_TAU
from openpilot.selfdrive.test.longitudinal_maneuvers.plant import Plant, PlannerSM


LeadObservation = dict[str, Any]
LeadObservationFn = Callable[[float, str, LeadObservation], LeadObservation | None]
ModelActionFn = Callable[[float, float, float], tuple[float, bool]]
EgoObservationFn = Callable[[float, float, float], tuple[float, float]]


@dataclass(frozen=True)
class ActuatorModel:
  planner_delay: float
  transport_delay: float
  actuator_lag: float
  command_rate_limit: float
  stopping_acceleration: float
  standstill_breakaway_acceleration: float
  standstill_breakaway_time: float

  def __post_init__(self):
    nonnegative_fields = {
      "planner_delay": self.planner_delay,
      "transport_delay": self.transport_delay,
      "actuator_lag": self.actuator_lag,
      "standstill_breakaway_acceleration": self.standstill_breakaway_acceleration,
      "standstill_breakaway_time": self.standstill_breakaway_time,
    }
    if any(not math.isfinite(value) or value < 0.0 for value in nonnegative_fields.values()):
      raise ValueError(f"ActuatorModel fields must be finite and non-negative: {nonnegative_fields}")
    if not math.isfinite(self.command_rate_limit) or self.command_rate_limit <= 0.0:
      raise ValueError("command_rate_limit must be finite and positive")
    if not math.isfinite(self.stopping_acceleration) or self.stopping_acceleration > 0.0:
      raise ValueError("stopping_acceleration must be finite and non-positive")


# Conservative Prius TSS2 actuator model.
PRIUS_TSS2_ROUTE_MODEL = ActuatorModel(
  planner_delay=0.05,
  transport_delay=0.0,
  actuator_lag=0.20,
  command_rate_limit=4.0,
  stopping_acceleration=-2.0,
  standstill_breakaway_acceleration=1.0,
  standstill_breakaway_time=0.05,
)


class PlantSP(Plant):
  """Closed-loop plant with configurable observations and actuator response."""

  def __init__(
    self,
    lead_relevancy=False,
    speed=0.0,
    distance_lead=2.0,
    enabled=True,
    only_lead2=False,
    only_radar=False,
    e2e=False,
    personality=0,
    force_decel=False,
    lead_observation_fn: LeadObservationFn | None = None,
    model_action_fn: ModelActionFn | None = None,
    ego_observation_fn: EgoObservationFn | None = None,
    actuator_delay: float | None = None,
    actuator_lag: float = 0.0,
    actuator_model: ActuatorModel | None = None,
    run_long_control: bool = False,
  ):
    if actuator_delay is not None and (not math.isfinite(actuator_delay) or actuator_delay < 0.0):
      raise ValueError("actuator_delay must be finite and non-negative")
    if not math.isfinite(actuator_lag) or actuator_lag < 0.0:
      raise ValueError("actuator_lag must be finite and non-negative")

    self.rate = 1.0 / DT_MDL

    if not Plant.messaging_initialized:
      Plant.radar = messaging.pub_sock('radarState')
      Plant.controls_state = messaging.pub_sock('controlsState')
      Plant.selfdrive_state = messaging.pub_sock('selfdriveState')
      Plant.car_state = messaging.pub_sock('carState')
      Plant.plan = messaging.sub_sock('longitudinalPlan')
      Plant.messaging_initialized = True

    self.v_lead_prev = 0.0

    self.distance = 0.0
    self.speed = speed
    self.should_stop = False
    self.acceleration = 0.0
    self.a_target = 0.0
    self.actuator_command = 0.0
    self.applied_actuator_command = 0.0
    self.breakaway_confirmed = False
    self._breakaway_timer = 0.0

    # lead car
    self.lead_relevancy = lead_relevancy
    self.distance_lead = distance_lead
    self.enabled = enabled
    self.only_lead2 = only_lead2
    self.only_radar = only_radar
    self.e2e = e2e
    self.personality = personality
    self.force_decel = force_decel
    self.lead_observation_fn = lead_observation_fn
    self.model_action_fn = model_action_fn
    self.ego_observation_fn = ego_observation_fn
    self.actuator_model = actuator_model
    self.actuator_delay = actuator_model.planner_delay if actuator_model is not None else actuator_delay
    self.transport_delay = actuator_model.transport_delay if actuator_model is not None else actuator_delay
    self.actuator_lag = actuator_model.actuator_lag if actuator_model is not None else actuator_lag
    self.publish_realized_a_ego = any((lead_observation_fn is not None, model_action_fn is not None, ego_observation_fn is not None,
                                      actuator_delay is not None, actuator_lag > 0.0, actuator_model is not None, run_long_control))

    self.rk = Ratekeeper(self.rate, print_delay_threshold=100.0)
    self.ts = 1.0 / self.rate
    time.sleep(0.1)
    self.sm = messaging.SubMaster(['longitudinalPlan'])

    from opendbc.car.honda.values import CAR
    from opendbc.car.honda.interface import CarInterface

    CP = CarInterface.get_non_essential_params(CAR.HONDA_CIVIC)
    if self.actuator_delay is not None:
      CP.longitudinalActuatorDelay = self.actuator_delay
    CP_SP = CarInterface.get_non_essential_params_sp(CP, CAR.HONDA_CIVIC)
    self.planner = LongitudinalPlanner(CP, CP_SP, init_v=self.speed)
    self.long_control = LongControl(CP, CP_SP) if run_long_control else None

    if self.actuator_model is not None and self.speed >= 0.01:
      self.breakaway_confirmed = True
    self.integration_dt = DT_CTRL if run_long_control else self.ts
    delay_steps = 0 if self.transport_delay is None else round(self.transport_delay / self.integration_dt)
    self._actuator_delay_queue = deque([self.acceleration] * delay_steps)

  @staticmethod
  def _lead_message(observation: LeadObservation):
    lead = log.RadarState.LeadData.new_message()
    for field, value in observation.items():
      setattr(lead, field, value)
    return lead

  def _observe_lead(self, lead_name: str, truth: LeadObservation, present_by_default: bool) -> LeadObservation | None:
    if self.lead_observation_fn is None:
      return dict(truth) if present_by_default else None

    observed = self.lead_observation_fn(self.current_time, lead_name, dict(truth))
    if observed is None:
      return None

    complete_observation = dict(truth)
    complete_observation.update(observed)
    return complete_observation

  def _update_actuator(self, command: float) -> tuple[float, float]:
    if self._actuator_delay_queue:
      self._actuator_delay_queue.append(command)
      delayed_command = self._actuator_delay_queue.popleft()
    else:
      delayed_command = command

    if self.actuator_model is not None:
      max_command_delta = self.actuator_model.command_rate_limit * self.integration_dt
      self.applied_actuator_command = float(np.clip(delayed_command,
                                                   self.applied_actuator_command - max_command_delta,
                                                   self.applied_actuator_command + max_command_delta))

      if self.speed < 0.01:
        if self.applied_actuator_command <= 0.0:
          self.breakaway_confirmed = False
          self._breakaway_timer = 0.0
        elif not self.breakaway_confirmed:
          breakaway_ready = self.applied_actuator_command + 1e-9 >= self.actuator_model.standstill_breakaway_acceleration
          if breakaway_ready:
            self._breakaway_timer += self.integration_dt
          else:
            self._breakaway_timer = 0.0

          self.breakaway_confirmed = breakaway_ready and self._breakaway_timer + 1e-9 >= self.actuator_model.standstill_breakaway_time
        if not self.breakaway_confirmed:
          self.acceleration = 0.0
          return delayed_command, self.acceleration
      else:
        self.breakaway_confirmed = True

      response_command = self.applied_actuator_command
    else:
      self.applied_actuator_command = delayed_command
      response_command = delayed_command

    if self.actuator_lag > 0.0:
      alpha = 1.0 - math.exp(-self.integration_dt / self.actuator_lag)
      self.acceleration += alpha * (response_command - self.acceleration)
    else:
      self.acceleration = response_command
    return delayed_command, self.acceleration

  def _integrate_ego(self, dt: float, stop_at_standstill: bool = False) -> None:
    self.speed += self.acceleration * dt
    if self.speed <= 0.0 or stop_at_standstill and self.speed < 0.01 and self.actuator_command <= 0.0:
      self.speed = self.acceleration = 0.0
    self.distance += self.speed * dt

  def step(self, v_lead=0.0, prob_lead=1.0, v_cruise=50.0, pitch=0.0, prob_throttle=1.0):
    # ******** publish a fake model going straight and fake calibration ********
    # note that this is worst case for MPC, since model will delay long mpc by one time step
    radar = messaging.new_message('radarState')
    control = messaging.new_message('controlsState')
    ss = messaging.new_message('selfdriveState')
    car_state = messaging.new_message('carState')
    lp = messaging.new_message('liveParameters')
    car_control = messaging.new_message('carControl')
    model = messaging.new_message('modelV2')
    car_state_sp = messaging.new_message('carStateSP')
    live_map_data_sp = messaging.new_message('liveMapDataSP')
    gps_data = messaging.new_message('gpsLocation')
    a_lead = (v_lead - self.v_lead_prev) / self.ts
    self.v_lead_prev = v_lead

    if self.lead_relevancy:
      d_rel = np.maximum(0.0, self.distance_lead - self.distance)
      v_rel = v_lead - self.speed
      if self.only_radar:
        status = True
      elif prob_lead > 0.5:
        status = True
      else:
        status = False
    else:
      d_rel = 200.0
      v_rel = 0.0
      prob_lead = 0.0
      status = False

    truth_lead: LeadObservation = {
      "dRel": float(d_rel),
      "yRel": 0.0,
      "vRel": float(v_rel),
      "vLead": float(v_lead),
      "vLeadK": float(v_lead),
      "aLeadK": float(a_lead),
      "present": bool(status),
      # TODO use real radard logic for this
      "aLeadTau": float(_LEAD_ACCEL_TAU),
      "modelProb": float(prob_lead),
      "radar": bool(self.only_radar),
      "radarTrackId": -1,
    }
    lead_one_observation = self._observe_lead("leadOne", truth_lead, not self.only_lead2)
    lead_two_observation = self._observe_lead("leadTwo", truth_lead, True)
    if lead_one_observation is not None:
      radar.radarState.leadOne = self._lead_message(lead_one_observation)
    if lead_two_observation is not None:
      radar.radarState.leadTwo = self._lead_message(lead_two_observation)

    # Simulate model predicting slightly faster speed
    # this is to ensure lead policy is effective when model
    # does not predict slowdown in e2e mode
    position = log.XYZTData.new_message()
    position.x = [float(x) for x in (self.speed + 0.5) * np.array(ModelConstants.T_IDXS)]
    model.modelV2.position = position
    if self.model_action_fn is None:
      model_acceleration, model_should_stop = self.acceleration + 0.1, False
    else:
      model_acceleration, model_should_stop = self.model_action_fn(self.current_time, self.speed, self.acceleration)
    model.modelV2.action.desiredAcceleration = float(model_acceleration)
    model.modelV2.action.shouldStop = bool(model_should_stop)
    velocity = log.XYZTData.new_message()
    velocity.x = [float(x) for x in (self.speed + 0.5) * np.ones_like(ModelConstants.T_IDXS)]
    velocity.x[0] = float(self.speed)  # always start at current speed
    model.modelV2.velocity = velocity
    acceleration = log.XYZTData.new_message()
    acceleration.x = [float(x) for x in np.zeros_like(ModelConstants.T_IDXS)]
    model.modelV2.acceleration = acceleration
    model.modelV2.meta.disengagePredictions.gasPressProbs = [float(prob_throttle) for _ in range(6)]

    control.controlsState.longControlState = self.long_control.long_control_state if self.long_control is not None else (
      LongCtrlState.pid if self.enabled else LongCtrlState.off)
    ss.selfdriveState.experimentalMode = self.e2e
    ss.selfdriveState.personality = self.personality
    control.controlsState.forceDecel = self.force_decel
    true_v_ego = self.speed
    true_a_ego = self.acceleration
    published_v_ego = true_v_ego
    published_a_ego = true_a_ego if self.publish_realized_a_ego else 0.0
    if self.ego_observation_fn is not None:
      published_v_ego, published_a_ego = self.ego_observation_fn(self.current_time, true_v_ego, true_a_ego)
    car_state.carState.vEgo = float(published_v_ego)
    car_state.carState.aEgo = float(published_a_ego)
    car_state.carState.standstill = bool(self.speed < 0.01)
    car_state.carState.vCruise = float(v_cruise * 3.6)
    car_control.carControl.orientationNED = [0.0, float(pitch), 0.0]

    # ******** get controlsState messages for plotting ***
    sm = PlannerSM(self.rk.frame, {
      'radarState': radar.radarState,
      'carState': car_state.carState,
      'carControl': car_control.carControl,
      'controlsState': control.controlsState,
      'selfdriveState': ss.selfdriveState,
      'liveParameters': lp.liveParameters,
      'modelV2': model.modelV2,
      'carStateSP': car_state_sp.carStateSP,
      'liveMapDataSP': live_map_data_sp.liveMapDataSP,
      'gpsLocation': gps_data.gpsLocation,
    })
    self.planner.update(sm)
    self.a_target = self.planner.output_a_target
    if self.long_control is None:
      self.actuator_command = self.a_target
      if self.planner.output_should_stop:
        stopping_acceleration = -0.5 if self.actuator_model is None else self.actuator_model.stopping_acceleration
        self.actuator_command = min(stopping_acceleration, self.actuator_command)
      self._update_actuator(self.actuator_command)
      self._integrate_ego(self.ts)
    else:
      for _ in range(round(self.ts / DT_CTRL)):
        car_state.carState.vEgo = self.speed
        car_state.carState.aEgo = self.acceleration
        car_state.carState.standstill = self.speed < 0.01
        self.actuator_command = self.long_control.update(
          self.enabled, car_state.carState, self.a_target, self.planner.output_should_stop, (ACCEL_MIN, ACCEL_MAX),
        )
        self._update_actuator(self.actuator_command)
        self._integrate_ego(DT_CTRL, stop_at_standstill=True)
    self.should_stop = self.planner.output_should_stop
    fcw = self.planner.fcw
    self.distance_lead = self.distance_lead + v_lead * self.ts

    # *** radar model ***
    if self.lead_relevancy:
      d_rel = np.maximum(0.0, self.distance_lead - self.distance)
      v_rel = v_lead - self.speed
    else:
      d_rel = 200.0
      v_rel = 0.0

    # print at 5hz
    # if (self.rk.frame % (self.rate // 5)) == 0:
    #   print("%2.2f sec   %6.2f m  %6.2f m/s  %6.2f m/s2   lead_rel: %6.2f m  %6.2f m/s"
    #         % (self.current_time, self.distance, self.speed, self.acceleration, d_rel, v_rel))

    # ******** update prevs ********
    self.rk.monitor_time()

    accel_controller = self.planner.accel_controller
    lead_plan = accel_controller._held_lead_plan
    target_state = accel_controller.target_state
    return {
      "distance": self.distance,
      "speed": self.speed,
      "acceleration": self.acceleration,
      "realized_acceleration": self.acceleration,
      "a_target": self.a_target,
      "actuator_command": self.actuator_command,
      "applied_actuator_command": self.applied_actuator_command,
      "published_a_ego": published_a_ego,
      "published_v_ego": published_v_ego,
      "breakaway_confirmed": self.breakaway_confirmed,
      "should_stop": self.should_stop,
      "long_control_state": (int(self.long_control.long_control_state) if self.long_control is not None
                             else control.controlsState.longControlState.raw),
      "distance_lead": self.distance_lead,
      "fcw": fcw,
      "mpc_source": self.planner.mpc.source,
      "dec_mode": self.planner.dec.mode(),
      "controller_target": accel_controller.output_v_target,
      "base_target": self.planner.output_v_target,
      "raw_energy_cap": lead_plan.cap if lead_plan is not None else math.inf,
      "live_filtered_cap": target_state.filtered_cap,
      "model_action": {
        "desiredAcceleration": float(model_acceleration),
        "shouldStop": bool(model_should_stop),
      },
      "truth_lead": dict(truth_lead),
      "lead_one_observation": None if lead_one_observation is None else dict(lead_one_observation),
      "lead_two_observation": None if lead_two_observation is None else dict(lead_two_observation),
    }
