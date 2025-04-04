import time
from collections import deque

import numpy as np

from sunnypilot.nnff_longitudinal_controller.policy_model import LongitudinalLiveTuner
from opendbc.car.hyundai.values import CAR


# Dummy classes to simulate dependent structures
class DummyLongitudinalPlan:
  aTarget = 0.0

class DummyLeadOne:
  status = True
  dRel = 1.0

class DummyRadarState:
  leadOne = DummyLeadOne()

class DummyOut:
  class CruiseState:
    enabled = True
  cruiseState = CruiseState()

# Minimal dummy struct for CarState
class DummyCarState:
  def __init__(self, vEgo, aEgo):
    self.vEgo = vEgo
    self.aEgo = aEgo
    self.out = DummyOut()

# Minimal dummy struct for CarControl.Actuators
class DummyActuators:
  def __init__(self, accel):
    self.accel = accel

# Minimal dummy for CarParams and nested tuning values
class DummyLongitudinalTuning:
  kf = 1.0
  kpBP = [0.0]
  kpV = [1.0]
  kiBP = [0.0]
  kiV = [1.0]

class DummyCarParams:
  def __init__(self):
    self.carFingerprint = CAR.KIA_NIRO_EV
    self.longitudinalTuning = DummyLongitudinalTuning()
    self.vEgoStarting = 0.1


# Dummy Params class to bypass persistent storage issues
class DummyParams:
  def __init__(self):
    self.store = {}
  def get(self, key):
    return self.store.get(key)
  def put(self, key, value):
    self.store[key] = value

def tuner():
  cp = DummyCarParams()
  tuner = LongitudinalLiveTuner(cp)
  tuner.params = DummyParams()
  tuner.sm = {
    'longitudinalPlan': DummyLongitudinalPlan(),
    'radarState': DummyRadarState()
  }
  return tuner

def test_braking_event(tuner):
  initial_speed = 20.0
  speeds = np.linspace(initial_speed, 5.0, num=15)
  accel = -2.0

  # First update to trigger braking event
  CS = DummyCarState(vEgo=speeds[0], aEgo=0.0)
  actuators = DummyActuators(accel=accel)
  tuner.update(CS, actuators)

  for v in speeds[1:]:
    CS = DummyCarState(vEgo=v, aEgo=accel)
    tuner.update(CS, actuators)
    time.sleep(0.125)        # try to mimic generic 50hz delay

  tuned_params = tuner.get_tuned_params()
  assert 'vego_stopping' in tuned_params
  assert 'stopping_decel_rate' in tuned_params
  print("Tuned parameters after braking event:", tuned_params, flush=True)

def test_starting_event(tuner):
  # Initial stopped state
  CS = DummyCarState(vEgo=0.0, aEgo=0.0)
  actuators = DummyActuators(accel=0.0)
  tuner.update(CS, actuators)

  # Trigger starting event
  CS = DummyCarState(vEgo=0.0, aEgo=0.0)
  actuators = DummyActuators(accel=0.3)
  tuner.update(CS, actuators)

  # Simulate car starting
  CS = DummyCarState(vEgo=0.6, aEgo=0.3)
  actuators = DummyActuators(accel=0.3)
  tuner.update(CS, actuators)
  assert len(tuner.starting_data) >= 1
  print("Starting data recorded:", tuner.starting_data, flush=True)

def test_force_update(tuner):
  CS = DummyCarState(vEgo=15.0, aEgo=-0.5)
  actuators = DummyActuators(accel=-0.5)
  prev_idx = tuner.sample_idx
  tuner.force_update(CS, actuators)
  assert tuner.sample_idx > prev_idx
  print("Force update sample index:", tuner.sample_idx, flush=True)

def simulate_multiple_events(tuner):
  # Simulate multiple braking events to collect data for training
  for _ in range(10):
    speeds = np.linspace(20.0, 0.0, num=75)
    accel = -1.0
    CS = DummyCarState(vEgo=speeds[0], aEgo=0.0)
    actuators = DummyActuators(accel=accel)
    tuner.update(CS, actuators)
    for v in speeds[1:]:
      CS = DummyCarState(vEgo=v, aEgo=accel)
      tuner.update(CS, actuators)
  # Simulate multiple starting events
  for _ in range(200):
    # Initial stopped state
    CS = DummyCarState(vEgo=0.0, aEgo=0.0)
    actuators = DummyActuators(accel=0.0)
    tuner.update(CS, actuators)
    # Apply positive acceleration while still stopped
    CS = DummyCarState(vEgo=0.0, aEgo=0.0)
    actuators = DummyActuators(accel=0.3)
    tuner.update(CS, actuators)
    # Car starts moving
    CS = DummyCarState(vEgo=0.6, aEgo=0.3)
    actuators = DummyActuators(accel=0.3)
    tuner.update(CS, actuators)

def test_nn_training_directly(tuner):
  # Create dummy braking events with required keys for training
  dummy_event = {
    'initial_speed': 20.0,
    'decel_samples': [1.0, 0.9, 1.1],
    'jerk_samples': [0.2, 0.3, 0.2],
    'comfort_scores': [0.8, 0.85, 0.9],
    'final_stopping_distance': 5.0,
    'duration': 10.0,
    'lead_distances': [7.0, 6.5, 5.0],
    'pid_errors': [0.1, -0.05, 0.0],
    'timestamp': int(time.time())
  }
  # Populate braking_events with 10 dummy events
  tuner.braking_events = deque([dummy_event] * 10, maxlen=tuner.MEMORY_SIZE)
  # Trigger network training directly from longitudinal_trainer
  tuner._train_network()
  print("Neural network training complete. Best validation loss:", tuner.best_nn_validation_loss, flush=True)

def main():
  tuner_inst = tuner()
  print("Initial tuner state:", vars(tuner_inst))
  print("\nRunning test_braking_event:")
  test_braking_event(tuner_inst)
  print("\nRunning test_starting_event:")
  test_starting_event(tuner_inst)
  print("\nRunning test_force_update:")
  test_force_update(tuner_inst)
  print("\nSimulating multiple events for training...")
  simulate_multiple_events(tuner_inst)
  print("\nFinal tuner state before NN training:")
  print("tuned parameters:", tuner_inst.get_tuned_params())
  print("starting data:", tuner_inst.starting_data)
  print("sample index:", tuner_inst.sample_idx)

  print("\nRunning neural network training test directly from longitudinal_trainer:")
  test_nn_training_directly(tuner_inst)

  print("\nFinal tuner state after NN training:")
  print("tuned parameters:", tuner_inst.get_tuned_params())

if __name__ == "__main__":
  main()
