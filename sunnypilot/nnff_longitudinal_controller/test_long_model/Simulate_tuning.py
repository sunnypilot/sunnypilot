from types import SimpleNamespace

import numpy as np

from sunnypilot.nnff_longitudinal_controller.longitudinal_nnff import LongitudinalLiveTuner


# Return a test CP with minimal attributes for update.
def get_dummy_CP():
  longitudinalTuning = SimpleNamespace(
    kf=1.0,
    kpBP=[0.],
    kpV=[1.0],
    kiBP=[0.],
    kiV=[1.0]
  )
  cp = SimpleNamespace(
    carFingerprint="Sunny",
    longitudinalTuning=longitudinalTuning,
    vEgoStopping=0.5,
    vEgoStarting=0.5,
    stoppingDecelRate=0.8
  )
  return cp

#  CS with minimal attributes for update
def get_dummy_CS():
  # simulate radarState with leadOne available.
  cruiseState = SimpleNamespace(enabled=True, standstill=False)
  radarState = SimpleNamespace(leadOne=SimpleNamespace(status=True, dRel=15.0))
  out = SimpleNamespace(cruiseState=cruiseState)
  cs = SimpleNamespace(
    vEgo=10.0,
    aEgo=1.2,
    aTarget=2.0,
    out=out,
    radarState=radarState,
    brakePressed=False
  )
  return cs

# Dummy actuators
def get_dummy_actuators():
  return SimpleNamespace(accel=1.0)

def test_get_pid_gains():
  cp = get_dummy_CP()
  tuner = LongitudinalLiveTuner(cp)
  # Initially gain factors are 1.0, so result should equal the original arrays.
  orig_kp = np.array([1.0])
  orig_ki = np.array([1.0])
  new_kp, new_ki = tuner.get_pid_gains(orig_kp, orig_ki)
  np.testing.assert_array_almost_equal(new_kp, orig_kp)
  np.testing.assert_array_almost_equal(new_ki, orig_ki)

  # Modify gain factors and re-check.
  tuner.kp_gain_factor = 1.1
  tuner.ki_gain_factor = 0.9
  new_kp, new_ki = tuner.get_pid_gains(orig_kp, orig_ki)
  np.testing.assert_array_almost_equal(new_kp, orig_kp * 1.1)
  np.testing.assert_array_almost_equal(new_ki, orig_ki * 0.9)

def test_default_values():
  cp = get_dummy_CP()
  tuner = LongitudinalLiveTuner(cp)
  # Check that defaults are taken from fake_cp via CarInterfaceBase.get_std_params()
  # (Since cp.carFingerprint is "Sunny", defaults fallback to our dummy values.)
  assert tuner.vego_stopping == cp.vEgoStopping
  assert tuner.vego_starting == cp.vEgoStarting
  assert tuner.stopping_decel_rate == cp.stoppingDecelRate
  # Check training step count is initially 0.
  assert tuner.training_step_count == 0

def test_update_increments_sample_idx():
  cp = get_dummy_CP()
  tuner = LongitudinalLiveTuner(cp)
  cs = get_dummy_CS()
  actuators = get_dummy_actuators()
  initial_idx = tuner.sample_idx
  tuner.update(cs, actuators)
  # Check that sample_idx has been incremented.
  assert tuner.sample_idx == initial_idx + 1

def test_braking_event_recorded():
  cp = get_dummy_CP()
  tuner = LongitudinalLiveTuner(cp)
  # Simulate a braking event: vEgo greater than 1.0, aEgo less than -0.10.
  cs = get_dummy_CS()
  cs.vEgo = 35.0
  cs.aEgo = -1.2  # decelerating
  # Ensure cruiseState is enabled.
  cs.out.cruiseState.enabled = True
  actuators = get_dummy_actuators()
  # Call update repeatedly to trigger stop condition.
  for _ in range(120):
    tuner.update(cs, actuators)
  # After several updates, there should be at least one recorded braking event, well... maybe.
  assert len(tuner.braking_events) > 0

def test_training_cycle():
  cp = get_dummy_CP()
  tuner = LongitudinalLiveTuner(cp)
  # Force collection of enough samples
  tuner.sample_idx = tuner.BLOCK_SIZE
  # Prepare some dummy braking data in stopping_data
  tuner.stopping_data = [0.4, 0.5, 0.6, 0.4, 0.5]
  tuner.starting_data = [1.5, 0.6, 0.7]
  tuner.decel_rate_data = [0.8, 0.9, 0.85, 1.87, 2.0]
  prev_vego = tuner.vego_stopping
  tuner._process_data()
  # Check that the stopping value has been updated (smoothed)
  assert tuner.vego_stopping != prev_vego

# Test that parameter saving and loading round-trip works.
def test_save_load_params():
  # Create a temporary Params object using a dict
  class DummyParams:
    def __init__(self):
      self.store = {}
    def get(self, key):
      return self.store.get(key, None)
    def put(self, key, val):
      self.store[key] = val

  cp = get_dummy_CP()
  tuner = LongitudinalLiveTuner(cp)
  dummy_params = DummyParams()
  tuner.params = dummy_params

  # Modify some values and save
  tuner.kp_gain_factor = 1.2
  tuner.ki_gain_factor = 0.8
  tuner._save_params()
  saved = dummy_params.get("LongitudinalLiveTuneParams")
  assert saved is not None

  # Create a new tuner and load the saved values
  new_tuner = LongitudinalLiveTuner(cp)
  new_tuner.params = dummy_params
  new_tuner._load_params()
  assert abs(new_tuner.kp_gain_factor - 1.2) < 1e-6
  assert abs(new_tuner.ki_gain_factor - 0.8) < 1e-6
