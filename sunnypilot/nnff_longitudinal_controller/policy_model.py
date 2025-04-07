"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import base64
import gzip
import json
import numpy as np
import os
import pickle
import platform
import time

from collections import deque
from typing import Any

from cereal import messaging
from opendbc.car import DT_CTRL, structs
from opendbc.car.fingerprints import MIGRATION
from opendbc.car.interfaces import CarInterfaceBase
from openpilot.common.params import Params
from sunnypilot.nnff_longitudinal_controller.learning_model import TinyNeuralNetwork
from tinygrad.tensor import Tensor


class LongitudinalLiveTuner:
  """Adaptive tuning system for longitudinal control parameters based on neural network machine learning.

  This system monitors vehicle behavior during stopping and starting to adapt
  longitudinal control parameters to the specific vehicle and driver preferences.
  """

  BLOCK_SIZE = 50   # Number of samples to gather before updating
  MIN_BLOCKS_NEEDED = 10    # Minimum blocks needed for valid calibration
  TUNE_LIMIT_PERCENT = 0.50   # Maximum percent change allowed from base value
  SMOOTH_FACTOR = 0.1   # How fast to adapt (0.1 = 10% of new value each update)
  MAX_AGE_DAYS = 120    # TODO: Don't fully reset calibration
  STOPPING_SPEED_THRESHOLD = 0.2  # m/s
  STARTING_SPEED_THRESHOLD = 0.5  # m/s

  # Safety parameters
  MIN_SAFE_LEAD_DISTANCE = 4.0    # Minimum safe distance from lead car (meters)
  IDEAL_LEAD_DISTANCE = 6.0   # Ideal distance when stopped behind lead car
  ISO_DECEL_RATE_MIN = 0.3    # Safety limit for deceleration rate (m/s^2)
  ISO_DECEL_RATE_MAX = 2.0    # Upper limit per (Horn et al., 2024), and GM interface.py
  COMFORT_JERK = 0.53   # Average comfortable jerk per (Horn et al., 2024)

  # Neural network hyperparameters
  MEMORY_SIZE = 250   # Store up to 250 braking events
  LEARNING_RATE = 0.1   # How quickly to adapt to new brake profiles

  # How many update calls to reach 20 minutes of learning (at 20Hz)
  TARGET_TRAINING_STEPS = 20 * 60 * 20  # 20 minutes * 60 seconds * 20Hz


  def __init__(self, CP: structs.CarParams, original_kpV=None, original_kiV=None):
    # Store car fingerprint for our .pkl output
    self.car_fingerprint = MIGRATION.get(CP.carFingerprint, CP.carFingerprint) if CP and hasattr(CP, 'carFingerprint') else "MOCK"

    # If car_fingerprint is None, use MOCK
    if self.car_fingerprint is None:
      self.car_fingerprint = "MOCK"

    # Create a safe version of the car fingerprint for file reference
    self.safe_fingerprint = ''.join(c if c.isalnum() else '_' for c in self.car_fingerprint)

    # Setup Default CarParams.
    std_params = CarInterfaceBase.get_std_params(self.car_fingerprint)

    # Use CP values if they exist, otherwise fall back to std_params
    self.vego_stopping_default = getattr(CP, 'vEgoStopping', std_params.vEgoStopping)
    self.vego_starting_default = getattr(CP, 'vEgoStarting', std_params.vEgoStarting)
    self.stopping_decel_rate_default = getattr(CP, 'stoppingDecelRate', std_params.stoppingDecelRate)

    long_tune = getattr(CP, 'longitudinalTuning', std_params.longitudinalTuning)
    self.kf_default = getattr(long_tune, 'kf', std_params.longitudinalTuning.kf)
    self.kpBP_default = np.array(getattr(long_tune, 'kpBP', std_params.longitudinalTuning.kpBP))
    self.kpV_default = np.array(getattr(long_tune, 'kpV', std_params.longitudinalTuning.kpV))
    self.kiBP_default = np.array(getattr(long_tune, 'kiBP', std_params.longitudinalTuning.kiBP))
    self.kiV_default = np.array(getattr(long_tune, 'kiV', std_params.longitudinalTuning.kiV))

    self.original_kpV = original_kpV if original_kpV is not None else np.array(std_params.longitudinalTuning.kpV)
    self.original_kiV = original_kiV if original_kiV is not None else np.array(std_params.longitudinalTuning.kiV)

    self.params = Params()
    self.sm = messaging.SubMaster(['longitudinalPlan', 'radarState'])
    self.kf = self.kf_default
    self.kpBP = self.kpBP_default.copy()
    self.kpV = self.kpV_default.copy()
    self.kiBP = self.kiBP_default.copy()
    self.kiV = self.kiV_default.copy()
    self.vego_stopping = self.vego_stopping_default
    self.vego_starting = self.vego_starting_default
    self.stopping_decel_rate = self.stopping_decel_rate_default

    self.kp_gain_factor = 1.0
    self.ki_gain_factor = 1.0

    # Data collection buffers
    self.stopping_data: list[float] = []
    self.starting_data: list[float] = []
    self.decel_rate_data: list[float] = []


    # Braking behavior tracking
    self.braking_events: deque[dict[str, Any]] = deque(maxlen=self.MEMORY_SIZE)
    self.current_braking_event: dict[str, Any] | None = None

    # Neural network for machine learning
    self.nn = TinyNeuralNetwork(
      input_size=10,
      hidden_size=24,
      output_size=10,
      lr=self.LEARNING_RATE,
      activation='leakyrelu',
      weight_init='he',
      dropout_rate=0.1,
      d3qn=True
    )
    # Try to load previously saved model checkpoint from pkl
    self._load_model_checkpoint()

    self.best_nn_validation_loss = float('inf')
    self.training_step_count = 0.0
    self.training_progress = 0.0  # Progress from 0.0 to 1.0

    # Training data
    self.training_data: list[dict[str, Any]] = []
    self.validation_data: list[dict[str, Any]] = []
    self.last_training_time = int(time.time())
    self.training_interval = 60.0  # seconds between training sessions

    # For tracking long control behavior
    self.last_output_accel = 0.0
    self.integral_error = 0.0
    self.prev_error = 0.0
    self.last_pid_error = 0.0
    self.last_lead_distance = 0.0

    # Current collection state
    self.is_stopping = False
    self.is_starting = False
    self.stopping_start_time = 0.0
    self.starting_start_time = 0.0
    self.prev_speed = 0.0
    self.prev_accel = 0.0
    self.sample_idx = 0.0

    # Safety validation
    self.unsafe_stops_count = 0.0
    self.total_stops_count = 0.0
    self.safety_validation_window: deque[int] = deque(maxlen=50)
    self.unsafe_param_detected = False

    # Load saved parameters if available
    self._load_params()

  def _load_model_checkpoint(self):
    """Load neural network weights from saved checkpoint if available."""
    try:
      checkpoint_path = f"{self.safe_fingerprint}_nn_longitudinal.pkl"

      # Check if model exists for current carFingerprint
      if os.path.exists(checkpoint_path):
        with open(checkpoint_path, "rb") as f:
          nn_weights = pickle.load(f)
          # Check if fingerprint matches
          if 'car_fingerprint' in nn_weights and nn_weights['car_fingerprint'] == self.car_fingerprint:
            # Restore weights to the neural network
            if all(k in nn_weights for k in ['nn_w1', 'nn_b1', 'nn_w2', 'nn_b2', 'nn_w3', 'nn_b3']):
              self.nn.W1 = Tensor(nn_weights['nn_w1'])
              self.nn.b1 = Tensor(nn_weights['nn_b1'])
              self.nn.W2 = Tensor(nn_weights['nn_w2'])
              self.nn.b2 = Tensor(nn_weights['nn_b2'])
              self.nn.W3 = Tensor(nn_weights['nn_w3'])
              self.nn.b3 = Tensor(nn_weights['nn_b3'])
              print(f"Neural network loaded checkpoint for {self.car_fingerprint}")
              return True
          else:
            print(f"Fingerprint mismatch in checkpoint file: found {nn_weights.get('car_fingerprint', 'MOCK')} vs current {self.car_fingerprint}")
            print("Creating new neural network for this vehicle")
      else:
        print(f"No existing model checkpoint for {self.car_fingerprint}, will create one")
    except Exception as e:
      print(f"Error loading model checkpoint: {e}")
    return False

  def _get_param_key(self):
    """Get the appropriate parameter key for this car fingerprint."""
    return f"LongitudinalTune_{self.safe_fingerprint}"

  def _load_params(self):
    """Load saved tuning parameters from persistent storage."""
    try:
      params_bytes = self.params.get("LongitudinalLiveTuneParams")
      print(f"_load_params: raw params value type: {type(params_bytes)}")

      # If the value is bytes, decode it to string
      if isinstance(params_bytes, bytes):
        params_bytes = params_bytes.decode('utf-8')
        print("Decoded params from bytes to string.")

      if params_bytes is not None and params_bytes != "":
        try:
          compressed = base64.b64decode(params_bytes)
          json_str = gzip.decompress(compressed).decode('utf-8')
          all_cars_data = json.loads(json_str)
          if 'cars' in all_cars_data and self.car_fingerprint in all_cars_data['cars']:
            car_data = all_cars_data['cars'][self.car_fingerprint]
            pickle_bytes = base64.b64decode(car_data['pickled_data'])
            stored_params = pickle.loads(pickle_bytes)
            print(f"Loaded parameters for {self.car_fingerprint}")
            current_time = int(time.time())
            if current_time - stored_params.get('timestamp', 0) < self.MAX_AGE_DAYS * 24 * 3600:
              self.vego_stopping = stored_params.get('vego_stopping', self.vego_stopping_default)
              self.vego_starting = stored_params.get('vego_starting', self.vego_starting_default)
              self.stopping_decel_rate = stored_params.get('stopping_decel_rate', self.stopping_decel_rate_default)
              self.kp_gain_factor = stored_params.get('kp_gain_factor', self.kp_gain_factor)
              self.ki_gain_factor = stored_params.get('ki_gain_factor', self.ki_gain_factor)
              if all(k in stored_params for k in ['nn_w1', 'nn_b1', 'nn_w2', 'nn_b2', 'nn_w3', 'nn_b3']):
                self.nn.W1 = Tensor(stored_params['nn_w1'])
                self.nn.b1 = Tensor(stored_params['nn_b1'])
                self.nn.W2 = Tensor(stored_params['nn_w2'])
                self.nn.b2 = Tensor(stored_params['nn_b2'])
                self.nn.W3 = Tensor(stored_params['nn_w3'])
                self.nn.b3 = Tensor(stored_params['nn_b3'])
              if 'braking_profiles' in stored_params:
                self.braking_events = deque(stored_params['braking_profiles'], maxlen=self.MEMORY_SIZE)
              if 'training_progress' in stored_params:
                self.training_progress = stored_params.get('training_progress', 0.0)
                self.training_step_count = stored_params.get('training_step_count', 0)
              if 'safety_metrics' in stored_params:
                safety = stored_params['safety_metrics']
                self.unsafe_stops_count = safety.get('unsafe_stops', 0)
                self.total_stops_count = safety.get('total_stops', 0)
              self._validate_params()
              return True
          else:
            print(f"No data for {self.car_fingerprint} in parameter store")
        except Exception as e:
          print(f"Error loading parameters: {e}")
      else:
        print("No parameter value found for LongitudinalLiveTuneParams")
    except Exception as e:
      print(f"Error in _load_params: {e}")

  def save_params(self):
    """Save tuning parameters to persistent storage while preserving other car data."""
    try:
      # Convert braking events to list for serialization (limit to most recent 75)
      braking_profiles = []
      try:
        braking_profiles = list(self.braking_events)[-75:] if self.braking_events else []
      except Exception as e:
        print(f"Error converting braking events: {e}")

      # Save neural network weights
      nn_weights = {}
      try:
        nn_weights = {
          'nn_w1': self.nn.W1.tolist() if hasattr(self.nn, 'W1') else [],
          'nn_b1': self.nn.b1.tolist() if hasattr(self.nn, 'b1') else [],
          'nn_w2': self.nn.W2.tolist() if hasattr(self.nn, 'W2') else [],
          'nn_b2': self.nn.b2.tolist() if hasattr(self.nn, 'b2') else [],
          'nn_w3': self.nn.W3.tolist() if hasattr(self.nn, 'W3') else [],
          'nn_b3': self.nn.b3.tolist() if hasattr(self.nn, 'b3') else [],
        }
      except Exception as e:
        print(f"Error converting NN weights: {e}")
        # Fall back to empty weights if conversion fails
        nn_weights = {
          'nn_w1': [], 'nn_b1': [],
          'nn_w2': [], 'nn_b2': [],
          'nn_w3': [], 'nn_b3': []
        }

      # Safety metrics
      safety_metrics = {
        'unsafe_stops': float(self.unsafe_stops_count),
        'total_stops': float(self.total_stops_count),
        'safety_score': 0 if self.total_stops_count == 0 else 1.0 - (
                        self.unsafe_stops_count / self.total_stops_count)
      }

      params_dict = {
        'car_fingerprint': self.car_fingerprint,
        'vego_stopping': float(self.vego_stopping),
        'vego_starting': float(self.vego_starting),
        'stopping_decel_rate': float(self.stopping_decel_rate),
        'kp_gain_factor': float(self.kp_gain_factor),
        'ki_gain_factor': float(self.ki_gain_factor),
        'braking_profiles': braking_profiles,
        'timestamp': int(time.time()),
        'training_progress': float(self.training_progress),
        'training_step_count': int(self.training_step_count),
        'safety_metrics': safety_metrics,
        **nn_weights
      }

      # Pickle the parameters for this car
      pickled_data = pickle.dumps(params_dict)

      # Load the existing parameter to preserve other cars' data
      all_cars_data = {'cars': {}}
      params_bytes = self.params.get("LongitudinalLiveTuneParams")
      if params_bytes is not None:
        try:
          # Parse existing car data
          existing_data = json.loads(params_bytes)
          if isinstance(existing_data, dict) and 'cars' in existing_data:
            all_cars_data = existing_data
        except json.JSONDecodeError:
          # If the existing data isn't valid JSON, start fresh with a new structure
          pass

      # Update/add the current car data
      all_cars_data['cars'][self.car_fingerprint] = {
        'pickled_data': base64.b64encode(pickled_data).decode('ascii'),
        'timestamp': int(time.time())
      }

      # Serialize, compress and encode before saving
      json_data = json.dumps(all_cars_data)
      compressed = gzip.compress(json_data.encode('utf-8'))
      compressed_str = base64.b64encode(compressed).decode('ascii')
      self.params.put("LongitudinalLiveTuneParams", compressed_str)
      print(f"Saved parameters for car {self.car_fingerprint} (total cars: {len(all_cars_data['cars'])})")

    except Exception as e:
      print(f"Error saving longitudinal tuning params: {e}")

  def _limit_precision(self, value, decimals=4):
    """Limit the decimal precision of values to prevent extreme values injected to pid controller."""
    if isinstance(value, np.ndarray):
      return np.round(value, decimals)
    return round(float(value), decimals)

  def _validate_params(self):
    """Ensure parameters are within acceptable ranges and meet safety criteria."""
    lower_limit = 1.0 - self.TUNE_LIMIT_PERCENT
    upper_limit = 1.0 + self.TUNE_LIMIT_PERCENT

    # Convert values to float
    vego_stopping_val = float(self.vego_stopping)
    vego_starting_val = float(self.vego_starting)
    stopping_decel_rate_val = float(self.stopping_decel_rate)
    kp_gain_factor_val = float(self.kp_gain_factor)
    ki_gain_factor_val = float(self.ki_gain_factor)

    # Safety check for stopping speed
    if vego_stopping_val < 0.1:
      vego_stopping_val = 0.2

    # Apply limits to all values
    vego_stopping_val = np.clip(vego_stopping_val, self.vego_stopping_default * lower_limit,
                                self.vego_stopping_default * upper_limit)
    vego_starting_val = np.clip(vego_starting_val, self.vego_starting_default * lower_limit,
                               self.vego_starting_default * upper_limit)
    stopping_decel_rate_val = np.clip(stopping_decel_rate_val, self.ISO_DECEL_RATE_MIN, self.ISO_DECEL_RATE_MAX)
    kp_gain_factor_val = np.clip(kp_gain_factor_val, lower_limit, upper_limit)
    ki_gain_factor_val = np.clip(ki_gain_factor_val, lower_limit, upper_limit)

    vego_stopping_val = min(vego_stopping_val, 0.5)
    stopping_decel_rate_val = min(stopping_decel_rate_val, 0.8)

    # Additional safety check: balance between stopping speed and decel rate
    if stopping_decel_rate_val < 0.2 and vego_stopping_val > 0.3:
      vego_stopping_val = min(vego_stopping_val, 0.25)

    # Update parameters with the computed float values and limit precision
    self.vego_stopping = self._limit_precision(vego_stopping_val)
    self.vego_starting = self._limit_precision(vego_starting_val)
    self.stopping_decel_rate = self._limit_precision(stopping_decel_rate_val)
    self.kp_gain_factor = self._limit_precision(kp_gain_factor_val)
    self.ki_gain_factor = self._limit_precision(ki_gain_factor_val)

    # Limit arrays element by element when they exist.. Not all cars have these values set
    if hasattr(self, 'kf') and self.kf is not None:
      kf_val = float(self.kf)
      kf_val = np.clip(kf_val, self.kf_default * lower_limit, self.kf_default * upper_limit)
      self.kf = self._limit_precision(kf_val)

    if hasattr(self, 'kpBP') and self.kpBP is not None:
      for i in range(len(self.kpBP)):
        val = float(self.kpBP[i])
        default_val = float(self.kpBP_default[i]) if i < len(self.kpBP_default) else float(self.kpBP_default[-1])
        val = np.clip(val, default_val * lower_limit, default_val * upper_limit)
        self.kpBP[i] = self._limit_precision(val)

    if hasattr(self, 'kpV') and self.kpV is not None:
      for i in range(len(self.kpV)):
        val = float(self.kpV[i])
        default_val = float(self.kpV_default[i]) if i < len(self.kpV_default) else float(self.kpV_default[-1])
        val = np.clip(val, default_val * lower_limit, default_val * upper_limit)
        self.kpV[i] = self._limit_precision(val)

    if hasattr(self, 'kiBP') and self.kiBP is not None:
      for i in range(len(self.kiBP)):
        val = float(self.kiBP[i])
        default_val = float(self.kiBP_default[i]) if i < len(self.kiBP_default) else float(self.kiBP_default[-1])
        val = np.clip(val, default_val * lower_limit, default_val * upper_limit)
        self.kiBP[i] = self._limit_precision(val)

    if hasattr(self, 'kiV') and self.kiV is not None:
      for i in range(len(self.kiV)):
        val = float(self.kiV[i])
        default_val = float(self.kiV_default[i]) if i < len(self.kiV_default) else float(self.kiV_default[-1])
        val = np.clip(val, default_val * lower_limit, default_val * upper_limit)
        self.kiV[i] = self._limit_precision(val)

  def update(self, CS: structs.CarState, actuators: structs.CarControl.Actuators):

    v_ego = CS.vEgo
    current_accel = actuators.accel

    # Calculate PID error for monitoring controller behavior
    pid_error = 0
    if hasattr(self.sm['longitudinalPlan'], 'aTarget') and hasattr(CS, 'aEgo'):
      pid_error = self.sm['longitudinalPlan'].aTarget - CS.aEgo
      self.last_pid_error = pid_error

    # Capture lead vehicle distance for safety checks
    if 'radarState' in self.sm and self.sm['radarState'].leadOne.status:
      lead_dist = self.sm['radarState'].leadOne.dRel
    else:
      lead_dist = None

    if lead_dist is not None:
      self.last_lead_distance = lead_dist

    # Start tracking a new braking event when deceleration begins
    if not self.is_stopping and CS.out.cruiseState.enabled and CS.aEgo < -0.10 and v_ego > 1.0:
      self.is_stopping = True
      self.stopping_start_time = int(time.time())
      # Initialize new braking event
      self.current_braking_event = {
        'initial_speed': v_ego,
        'decel_samples': [],
        'comfort_scores': [],
        'jerk_samples': [],
        'lead_distances': [],
        'pid_errors': [],
        'distance': 0.0,
        'duration': 0.0,
        'final_stopping_distance': 0.0,
        'timestamp': int(time.time())
      }

    # Record braking event data
    if self.is_stopping:
      # Calculate deceleration rate and jerk
      decel_rate = (self.prev_speed - v_ego) / DT_CTRL if self.prev_speed > v_ego else 0.0
      jerk = (current_accel - self.last_output_accel) / DT_CTRL

      # If jerk exceeds comfortable limits, reduce influence on deceleration update
      if abs(jerk) > self.COMFORT_JERK:
        # Reduce effective deceleration by half to smooth transitions
        decel_rate_effective = ((self.prev_speed - CS.vEgo) / DT_CTRL) * 0.5
      else:
        decel_rate_effective = (self.prev_speed - CS.vEgo) / DT_CTRL

      # Update braking event data
      if self.current_braking_event is not None:
        self.current_braking_event['decel_samples'].append(decel_rate_effective)
        self.current_braking_event['jerk_samples'].append(jerk)
        self.current_braking_event['distance'] += v_ego * DT_CTRL
        self.current_braking_event['duration'] += DT_CTRL

        # Store lead distance if available
        if lead_dist is not None:
          self.current_braking_event['lead_distances'].append(lead_dist)

        # Store PID error for controller analysis
        self.current_braking_event['pid_errors'].append(pid_error)

        # Compute a comfort score (lower jerk = more comfort)
        comfort_score = 1.0 / (1.0 + abs(jerk))
        self.current_braking_event['comfort_scores'].append(comfort_score)

      # Check if we've reached a stop
      if v_ego < self.STOPPING_SPEED_THRESHOLD:
        if self.current_braking_event is not None:
          # Calculate final metrics
          self.current_braking_event['final_speed'] = v_ego

          # Determine lead distance when stopping
          self.current_braking_event['final_stopping_distance'] = lead_dist if lead_dist is not None else 0.0

          # Safety check: track if this was an unsafe stop (too close to lead)
          self.total_stops_count += 1
          if lead_dist is not None and lead_dist < self.MIN_SAFE_LEAD_DISTANCE:
            self.unsafe_stops_count += 1
            self.safety_validation_window.append(0)  # 0 = unsafe
          else:
            self.safety_validation_window.append(1)  # 1 = safe

          # Check if we need to revert unsafe parameters
          if len(self.safety_validation_window) >= 5:  # Need at least 5 stops to evaluate
            unsafe_ratio = 1.0 - (sum(self.safety_validation_window) / len(self.safety_validation_window))
            if unsafe_ratio > 0.3:  # If more than 30% of recent stops are unsafe
              # Revert to more conservative parameters
              self.unsafe_param_detected = True
              self.vego_stopping = min(self.vego_stopping + 0.05, self.vego_stopping_default * 1.1)
              self.stopping_decel_rate = max(self.stopping_decel_rate * 0.9, self.stopping_decel_rate_default * 0.9)
              print(f"Unsafe stopping parameters detected! Reverting to safer values. Unsafe ratio: {unsafe_ratio:.2f}")

          # Store the braking event for learning
          self.braking_events.append(self.current_braking_event)
          self.current_braking_event = None

          # Process the collected data to update parameters
          self._analyze_braking_behavior()

        # Record data for basic tuning
        self.stopping_data.append(v_ego)
        self.is_stopping = False

    # Detect starting event (transitioning from standstill)
    if not self.is_starting and CS.out.cruiseState.enabled and v_ego < 0.1 < actuators.accel:
      self.is_starting = True
      self.starting_start_time = int(time.time())

    # Record starting data
    if self.is_starting:
      # Check if we've started moving
      if v_ego > self.STARTING_SPEED_THRESHOLD:
        self.starting_data.append(v_ego)
        self.is_starting = False

    # Record PID controller behavior
    self.last_output_accel = current_accel

    # Detect deceleration rate for basic tuning
    if self.prev_speed > v_ego > 0.01 and CS.out.cruiseState.enabled:
      decel_rate = (self.prev_speed - v_ego) / DT_CTRL
      self.decel_rate_data.append(decel_rate)

    self.prev_speed = v_ego
    self.prev_accel = current_accel

    # Periodically train the neural network
    current_time = int(time.time())
    if current_time - self.last_training_time > self.training_interval:
      self._train_network()
      self.last_training_time = current_time

    # Increment sample index for processing
    self.sample_idx += 1

    # Process data if we have enough samples
    if self.sample_idx >= self.BLOCK_SIZE:
      self._process_data()
      self.sample_idx = 0

    # Track progress towards fully trained model
    if self.training_step_count < self.TARGET_TRAINING_STEPS:
      self.training_step_count += 1
      self.training_progress = min(1.0, self.training_step_count / self.TARGET_TRAINING_STEPS)

  def force_update(self, CS: structs.CarState, actuators: structs.CarControl.Actuators):
    # Force an immediate data update and training trigger
    self.update(CS, actuators)
    # Ensure sample_idx is incremented even if update didn't do so
    self.sample_idx += 1

  def _train_network(self):
    """Train the neural network on collected data."""
    if len(self.braking_events) < 10:  # Need enough data for meaningful training
      return

    # Extract training features and targets
    features = []
    targets = []
    valid_features = []
    valid_targets = []

    for event in self.braking_events:
      if len(event.get('decel_samples', [])) == 0:
        continue

      # Create feature vector
      try:
        feature = [
          float(event['initial_speed']),
          float(np.mean(event['decel_samples'])),
          float(np.std(event['jerk_samples']) if event['jerk_samples'] else 0),
          float(np.mean(event['comfort_scores']) if event['comfort_scores'] else 0.5),
          float(event['final_stopping_distance'] if event.get('final_stopping_distance') is not None else 8.0),
          float(event['duration']),
          float(len(event.get('lead_distances', [])) / max(1, len(event['decel_samples']))),
          float(np.mean(self.original_kpV)),
          float(np.mean(self.original_kiV)),
          1.0  # Default feature padding to match input_size=10
        ]
        feature = np.array(feature, dtype=np.float32)
        feature = np.clip(feature, -10, 10)

        # Target values
        target = np.array([
          float((self.vego_stopping - self.vego_stopping_default * 0.5) / (self.vego_stopping_default * 0.5 + 1e-9)),
          float((self.vego_starting - self.vego_starting_default * 0.5) / (self.vego_starting_default * 0.5 + 1e-9)),
          float((self.stopping_decel_rate - self.stopping_decel_rate_default * 0.5) /
                (self.stopping_decel_rate_default * 0.5 + 1e-9)),
          float((self.kp_gain_factor - 0.75) / 0.5),
          float((self.ki_gain_factor - 0.75) / 0.5),
          0.5,
          0.5,
          0.5,
          0.5,
          0.5
        ], dtype=np.float32)

        # Only add if both are valid
        valid_features.append(feature)
        valid_targets.append(target)
      except Exception as e:
        print(f"Error processing event for neural network: {e}")
        continue

    features = valid_features
    targets = valid_targets

    # Split into training and validation sets
    if len(features) < 5 or len(targets) < 5:
      print(f"Not enough valid training examples: {len(features)} features, {len(targets)} targets")
      return

    train_size = int(len(features) * 0.8)

    # Convert to numpy arrays with explicit dtype
    try:
      train_features_np = np.array(features[:train_size], dtype=np.float32)
      train_targets_np = np.array(targets[:train_size], dtype=np.float32)
      val_features_np = np.array(features[train_size:], dtype=np.float32) if len(features) > train_size else np.array(
                                  [], dtype=np.float32)
      val_targets_np = np.array(targets[train_size:], dtype=np.float32) if len(targets) > train_size else np.array([],
                                                                                                                    dtype=np.float32)

      # Verify shapes match network expectations
      print(f"Training features shape: {train_features_np.shape}")
      print(f"Training targets shape: {train_targets_np.shape}")
    except Exception as e:
     print(f"Error creating training arrays: {e}")
     return

    try:
      # Train the model
      self.nn.train(Tensor(train_features_np), Tensor(train_targets_np), iterations=200, epochs=10)

      if len(val_features_np) > 0:
        try:
          val_pred = self.nn.forward(Tensor(val_features_np))
          val_loss = ((val_pred - Tensor(val_targets_np)) ** 2).mean().numpy()
          print(f"Neural network training: validation error = {val_loss:.6f}")

          # Print detailed prediction information to understand impact of loss changes
          if len(val_pred) > 0:
            pred_values = val_pred.numpy()[0]  # First prediction
            target_values = val_targets_np[0]  # First target
            param_names = ['vego_stopping', 'vego_starting', 'stopping_decel_rate',
                            'kp_factor', 'ki_factor', 'kf', 'kpBP', 'kpV', 'kiBP', 'kiV']

            print("\nPrediction details (normalized [0-1]):")
            for name, pred, target in zip(param_names, pred_values, target_values, strict=False):
              error = abs(pred - target)
              print(f"  {name}: pred={pred:.4f}, target={target:.4f}, error={error:.4f}")

            # Show how these translate to actual parameter values
            print("\nDenormalized parameter values:")
            # Example for a few key parameters
            vego_stopping_pred = pred_values[0] * (self.vego_stopping_default * 0.5) + (
                        self.vego_stopping_default * 0.5)
            vego_stopping_target = target_values[0] * (self.vego_stopping_default * 0.5) + (
                        self.vego_stopping_default * 0.5)
            print(
              f"  vego_stopping: current={self.vego_stopping:.4f}, pred={vego_stopping_pred:.4f}, target={vego_stopping_target:.4f}")

            decel_rate_pred = pred_values[2] * (self.stopping_decel_rate_default * 0.5) + (
                        self.stopping_decel_rate_default * 0.5)
            decel_rate_target = target_values[2] * (self.stopping_decel_rate_default * 0.5) + (
                        self.stopping_decel_rate_default * 0.5)
            print(
              f"  stopping_decel_rate: current={self.stopping_decel_rate:.4f}, pred={decel_rate_pred:.4f}, target={decel_rate_target:.4f}")

          # Track if validation loss is improving
          if val_loss < self.best_nn_validation_loss:
            # Handle the case where loss is infinity
            if np.isinf(self.best_nn_validation_loss):
              improvement = 100.0
            else:
              improvement = (self.best_nn_validation_loss - val_loss) / self.best_nn_validation_loss * 100

            self.best_nn_validation_loss = val_loss
            print(f"Validation loss improved by {improvement:.2f}%, saving checkpoint.")
            try:
              self._save_model_checkpoint()
            except Exception as e:
              print(f"Error saving model checkpoint: {e}")

          # After successful training and validation, apply the trained model
          self.apply_trained_model(direct_training_application=True)

        except Exception as e:
          print(f"Error during validation: {e}")

      # Try to save params
      try:
        self.save_params()
      except Exception as e:
        print(f"Error saving parameters: {e}")

    except Exception as e:
      print(f"Error in neural network training: {e}")

  def apply_trained_model(self, direct_training_application=False):
    """Apply the trained neural network model to update parameters."""
    if len(self.braking_events) < 5:
      print("Not enough braking events to apply model")
      return False

    # Use recent events to create representative features
    recent_events = list(self.braking_events)[-10:]

    # Calculate average metrics from recent events
    avg_speed = np.mean([event['initial_speed'] for event in recent_events])
    avg_decel = np.mean([np.mean(event.get('decel_samples', [0.8])) for event in recent_events])
    avg_jerk_std = np.mean([np.std(event.get('jerk_samples', [0.0])) for event in recent_events])
    avg_comfort = np.mean([np.mean(event.get('comfort_scores', [0.5])) for event in recent_events])
    stopping_distances = [event.get('final_stopping_distance', 8.0) for event in recent_events if
                          event.get('final_stopping_distance') is not None]
    avg_stopping_distance = np.mean(stopping_distances) if stopping_distances else 8.0
    avg_duration = np.mean([event['duration'] for event in recent_events])
    avg_lead_dist = np.mean([np.mean(event.get('lead_distances', [10.0])) for event in recent_events])

    # Create input features for the neural network
    features = np.array([
      avg_speed,
      avg_decel,
      avg_jerk_std,
      avg_comfort,
      avg_stopping_distance,
      avg_duration,
      avg_lead_dist,
      np.mean(self.original_kpV),
      np.mean(self.original_kiV),
      1.0
    ])

    # Clip features to prevent extreme values
    features = np.clip(features, -10, 10)

    # Record original values for comparison
    original_values = {
      'vego_stopping': self.vego_stopping,
      'vego_starting': self.vego_starting,
      'stopping_decel_rate': self.stopping_decel_rate,
      'kp_gain_factor': self.kp_gain_factor,
      'ki_gain_factor': self.ki_gain_factor
    }

    # Get neural network prediction with proper GPU error handling and CPU fallback
    try:
      is_macos = platform.system() == 'Darwin'

      if is_macos:
        # Try to explicitly use Metal on macOS
        original_device = os.environ.get('TINYGRAD_DEVICE', '')
        os.environ['TINYGRAD_DEVICE'] = 'METAL'
        try:
          # Add float32 conversion for Metal compatibility
          features_tensor = Tensor(features.astype(np.float32).reshape(1, -1))
          prediction = self.nn.forward(features_tensor)
          prediction_array = prediction.numpy().flatten()
          print(f"\nApplying model - Metal GPU predictions: {prediction_array}")
        except Exception as metal_error:
          print(f"Metal GPU execution failed: {metal_error}")
          # Fall back to CPU on macOS if Metal fails
          os.environ['TINYGRAD_DEVICE'] = 'CPU'
          features_tensor = Tensor(features.astype(np.float32).reshape(1, -1))
          prediction = self.nn.forward(features_tensor)
          prediction_array = prediction.numpy().flatten()
          print(f"macOS CPU fallback successful - predictions: {prediction_array}")
        finally:
          # Restore original device setting
          if original_device:
            os.environ['TINYGRAD_DEVICE'] = original_device
          else:
            os.environ.pop('TINYGRAD_DEVICE', None)
      else:
        # Standard GPU path for non-macOS systems
        features_tensor = Tensor(features.astype(np.float32).reshape(1, -1))
        prediction = self.nn.forward(features_tensor)
        prediction_array = prediction.numpy().flatten()
        print(f"\nApplying model - GPU predictions: {prediction_array}")
    except Exception as e:
      print(f"Error during model prediction: {e}")
      print("Attempting CPU fallback for prediction...")
      try:
        # Try to force CPU execution
        original_device = os.environ.get('TINYGRAD_DEVICE', '')
        os.environ['TINYGRAD_DEVICE'] = 'CPU'
        # Create a new tensor on CPU
        features_tensor = Tensor(features.astype(np.float32).reshape(1, -1))
        # Run prediction on CPU
        prediction = self.nn.forward(features_tensor)
        prediction_array = prediction.numpy().flatten()
        # Restore original device setting
        if original_device:
          os.environ['TINYGRAD_DEVICE'] = original_device
        else:
          os.environ.pop('TINYGRAD_DEVICE', None)
        print(f"CPU fallback successful - predictions: {prediction_array}")
      except Exception as cpu_error:
        print(f"CPU fallback also failed: {cpu_error}")
        print("Using default values instead")
        return False

    # Clip predictions to the expected normalized range [0, 1]
    prediction_array = np.clip(prediction_array, 0, 1)

    print(f"\nNeural network raw predictions (clipped): {prediction_array}")

    # Denormalize outputs with modified scaling for deceleration rate
    target_vego_stopping = prediction_array[0] * (self.vego_stopping_default * 0.5) + (self.vego_stopping_default * 0.5)
    target_vego_starting = prediction_array[1] * (self.vego_starting_default * 0.5) + (self.vego_starting_default * 0.5)

    # Inverse mapping: higher prediction -> lower deceleration rate
    # This will map predictions of 1.0 to 0.1 and 0.0 to default value
    target_decel_rate = self.stopping_decel_rate_default * (1.0 - prediction_array[2] * 0.875)

    target_kp_factor = prediction_array[3] * 0.5 + 0.75
    target_ki_factor = prediction_array[4] * 0.5 + 0.75

    # Use more aggressive learning rate if this is from direct training application
    learning_rate = 0.4 if direct_training_application else 0.1
    # Higher factor for decel rate (2.5x)
    decel_rate_factor = 2.5

    # Safely apply predictions
    try:
      # Denormalize predictions and apply to parameters
      self.vego_stopping = (1.0 - learning_rate) * self.vego_stopping + learning_rate * target_vego_stopping
      self.vego_starting = (1.0 - learning_rate) * self.vego_starting + learning_rate * target_vego_starting
      # Use more aggressive learning rate for deceleration rate
      self.stopping_decel_rate = (1.0 - learning_rate * decel_rate_factor) * self.stopping_decel_rate + learning_rate * decel_rate_factor * target_decel_rate
      self.kp_gain_factor = (1.0 - learning_rate) * self.kp_gain_factor + learning_rate * target_kp_factor
      self.ki_gain_factor = (1.0 - learning_rate) * self.ki_gain_factor + learning_rate * target_ki_factor

      # Limit precision of all parameters
      self.vego_stopping = self._limit_precision(self.vego_stopping)
      self.vego_starting = self._limit_precision(self.vego_starting)
      self.stopping_decel_rate = self._limit_precision(self.stopping_decel_rate)
      self.kp_gain_factor = self._limit_precision(self.kp_gain_factor)
      self.ki_gain_factor = self._limit_precision(self.ki_gain_factor)

    except Exception as e:
      print(f"Error applying model predictions: {e}")
      # Don't update parameters if there was an error
      return False

    # Log parameter changes
    print("\nParameter changes after applying trained model:")
    for param, before in original_values.items():
      after = getattr(self, param)
      change = after - before
      pct_change = (change / before) * 100 if before != 0 else float('inf')
      print(f"  {param}: {before:.4f} → {after:.4f} (Δ{change:.4f}, {pct_change:.2f}%)")

    # Validate parameters to ensure safety
    self._validate_params()
    return True

  def _process_data(self):
    """Process collected data and update parameters."""
    # Process stopping speed data
    if len(self.stopping_data) > self.MIN_BLOCKS_NEEDED:
      new_vego_stopping = np.median(self.stopping_data)

      # Apply smoothing
      self.vego_stopping = (1.0 - self.SMOOTH_FACTOR) * self.vego_stopping + self.SMOOTH_FACTOR * new_vego_stopping
      self.vego_stopping = self._limit_precision(self.vego_stopping)
      self.stopping_data = []  # Clear buffer

    # Process starting speed data
    if len(self.starting_data) > self.MIN_BLOCKS_NEEDED:
      new_vego_starting = np.median(self.starting_data)

      # Apply smoothing
      self.vego_starting = (1.0 - self.SMOOTH_FACTOR) * self.vego_starting + self.SMOOTH_FACTOR * new_vego_starting
      self.vego_starting = self._limit_precision(self.vego_starting)
      self.starting_data = []  # Clear buffer

    # Process deceleration rate data
    if len(self.decel_rate_data) > self.MIN_BLOCKS_NEEDED:
      # Take the 75th percentile for a conservative estimate
      # (higher values mean more aggressive stopping)
      new_stopping_decel_rate = np.percentile(self.decel_rate_data, 75)

      # Apply smoothing
      self.stopping_decel_rate = (1.0 - self.SMOOTH_FACTOR) * self.stopping_decel_rate + self.SMOOTH_FACTOR * new_stopping_decel_rate
      self.stopping_decel_rate = self._limit_precision(self.stopping_decel_rate)
      self.decel_rate_data = []  # Clear buffer

    # Validate and save parameters
    self._validate_params()
    self.save_params()

  def _analyze_braking_behavior(self):
    """Analyze collected braking events to optimize parameters using neural-network."""
    if len(self.braking_events) < 5:  # Need minimum data for accurate training
      return

    # Get the most recent events (more weight to recent events)
    recent_events = list(self.braking_events)[-20:]

    # Extract key metrics
    avg_comfort_scores = []
    avg_decel_rates = []
    stopping_accuracies = []
    stopping_distances = []

    for event in recent_events:
      if 'comfort_scores' in event and event['comfort_scores']:
        avg_comfort_scores.append(np.mean(event['comfort_scores']))

      if 'decel_samples' in event and event['decel_samples']:
        # Use 90th percentile for max deceleration rate
        avg_decel_rates.append(np.percentile(event['decel_samples'], 90))

      # Analyze stopping distance (critical for safety)
      if 'final_stopping_distance' in event and event['final_stopping_distance'] is not None:
        stopping_distance = event['final_stopping_distance']
        stopping_distances.append(stopping_distance)

        # Safety check - prioritize stopping at safe distance
        if stopping_distance < self.MIN_SAFE_LEAD_DISTANCE:
          # If stopping distance is too close to lead, we need more conservative params
          # Unsafe stops get a very low score
          accuracy = 0.0
        else:
          # Otherwise, optimal distance is between 5-7 meters
          # Formula gives highest score (1.0) at ideal distance and decreases as we move away
          accuracy = 1.0 / (1.0 + abs(stopping_distance - self.IDEAL_LEAD_DISTANCE) / 3.0)

        stopping_accuracies.append(accuracy)

    # Only proceed if we have valid data
    if not avg_comfort_scores or not avg_decel_rates:
      return

    # Safety check for stopping distance
    if stopping_distances and np.mean(stopping_distances) < self.MIN_SAFE_LEAD_DISTANCE:
      # If we're consistently stopping too close, make immediate corrections
      self.vego_stopping = max(self.vego_stopping * 0.7, self.vego_stopping_default * 0.65)
      self.stopping_decel_rate = min(self.stopping_decel_rate * 0.7, self.stopping_decel_rate_default * 0.65)
      print(f"Safety correction: Mean stopping distance {np.mean(stopping_distances):.2f}m is too low; applying correction.")
      self._validate_params()
      self.save_params()
      return

    # Calculate optimal decel rate based on comfort and accuracy
    # More weight to comfort for regular stops, more weight to accuracy for emergency stops
    comfort_weight = 0.75
    accuracy_weight = 0.4

    if stopping_accuracies:
      # If stopping accuracy is poor, shift weights to prioritize accuracy
      avg_accuracy = np.mean(stopping_accuracies)
      if avg_accuracy < 0.5:  # Below threshold, adjust weights
        comfort_weight = 0.3
        accuracy_weight = 0.7

    # Weighted average of metrics to determine optimal parameters
    avg_comfort = np.mean(avg_comfort_scores) if avg_comfort_scores else 0.5
    avg_decel = np.mean(avg_decel_rates) if avg_decel_rates else self.stopping_decel_rate

    # Neural-network adaptive learning:
    # Comfort score affects decel rate (higher comfort = gentler deceleration)
    comfort_factor = np.clip(avg_comfort, 0.5, 1.0)

    # Incorporate average jerk analysis:
    avg_jerk = np.mean([np.mean(event.get('jerk_samples', [0.0])) for event in recent_events])
    # If average jerk is too high, reduce deceleration aggressiveness.
    if abs(avg_jerk) > self.COMFORT_JERK:
      comfort_adjustment = 0.8
    else:
      comfort_adjustment = 1.0

    # Use the neural network if we have enough data for accurate prediction
    if len(recent_events) >= 10 and hasattr(self, 'nn'):
      # Prepare input features that represent the current driving situation
      avg_speed = np.mean([event['initial_speed'] for event in recent_events])
      avg_lead_dist = np.mean([np.mean(event.get('lead_distances', [10.0])) for event in recent_events])

      features = np.array([
        avg_speed,
        avg_decel,
        np.mean([np.std(event.get('jerk_samples', [0.0])) for event in recent_events]),  # Jerk variability
        avg_comfort, # Comfort score
        np.mean(stopping_distances) if stopping_distances else 8.0,  # Average stopping distance
        np.mean([event['duration'] for event in recent_events]),  # Average stop duration
        avg_lead_dist,
        len(stopping_distances) / max(1, len(recent_events)),  # Traffic density proxy
        np.mean(self.original_kpV),
        np.mean(self.original_kiV)
      ])

      # Normalize and clip the features to prevent training issues
      features = np.clip(features, -10, 10)

      # Get NN prediction for optimal parameters
      features_tensor = Tensor(features.astype(np.float32).reshape(1, -1))
      prediction = self.nn.forward(features_tensor)

      # Convert prediction to numpy and extract first row:
      pred_array = prediction.numpy()[0]
      print(f"\nNeural network raw predictions: {pred_array}")

      # Denormalize outputs using pred_array instead of directly indexing prediction
      target_vego_stopping = pred_array[0] * (self.vego_stopping_default * 0.5) + (self.vego_stopping_default * 0.5)
      target_vego_starting = pred_array[1] * (self.vego_starting_default * 0.5) + (self.vego_starting_default * 0.5)
      target_decel_rate = pred_array[2] * self.stopping_decel_rate_default
      target_kp_factor = pred_array[3] * 0.5 + 0.75
      target_ki_factor = pred_array[4] * 0.5 + 0.75
      target_kf = pred_array[5] * (self.kf_default * 0.5) + (self.kf_default * 0.5)
      # Epsilon for safe division
      eps = 1e-9
      kp_mean = max(eps, abs(np.mean(self.kpBP_default)))
      target_kpBP = pred_array[6] * (kp_mean * 0.5) + (kp_mean * 0.5)
      kpV_mean = max(eps, abs(np.mean(self.kpV_default)))
      target_kpV = pred_array[7] * (kpV_mean * 0.5) + (kpV_mean * 0.5)
      kiBP_mean = max(eps, abs(np.mean(self.kiBP_default)))
      target_kiBP = pred_array[8] * (kiBP_mean * 0.5) + (kiBP_mean * 0.5)
      kiV_mean = max(eps, abs(np.mean(self.kiV_default)))
      target_kiV = pred_array[9] * (kiV_mean * 0.5) + (kiV_mean * 0.5)

      # Store original values for comparison
      original_values = {
        'vego_stopping': self.vego_stopping,
        'vego_starting': self.vego_starting,
        'stopping_decel_rate': self.stopping_decel_rate,
        'kp_gain_factor': self.kp_gain_factor,
        'ki_gain_factor': self.ki_gain_factor
      }

      # Update parameters using suitable learning rates:
      safety_lr = 0.2
      comfort_lr = 0.1
      decel_lr = safety_lr * 1.5

      # Update core parameters with standard approach
      self.vego_stopping = (1.0 - safety_lr * accuracy_weight) * self.vego_stopping + (safety_lr * accuracy_weight) * target_vego_stopping
      self.stopping_decel_rate = (1.0 - decel_lr * accuracy_weight) * self.stopping_decel_rate + (decel_lr * accuracy_weight) * target_decel_rate
      self.vego_starting = (1.0 - comfort_lr * comfort_weight) * self.vego_starting + (comfort_lr * comfort_weight) * target_vego_starting
      self.kp_gain_factor = (1.0 - comfort_lr * comfort_weight) * self.kp_gain_factor + (comfort_lr * comfort_weight) * target_kp_factor
      self.ki_gain_factor = (1.0 - comfort_lr * comfort_weight) * self.ki_gain_factor + (comfort_lr * comfort_weight) * target_ki_factor

      # Apply precision limiting to 4 decimal places
      self.vego_stopping = self._limit_precision(self.vego_stopping)
      self.vego_starting = self._limit_precision(self.vego_starting)
      self.stopping_decel_rate = self._limit_precision(self.stopping_decel_rate)
      self.kp_gain_factor = self._limit_precision(self.kp_gain_factor)
      self.ki_gain_factor = self._limit_precision(self.ki_gain_factor)

      # Update kf with precision limiter
      kf_updated = (1.0 - safety_lr * accuracy_weight) * self.kf + (safety_lr * accuracy_weight) * target_kf
      self.kf = self._limit_precision(kf_updated)

      # For arrays, update each element
      for i in range(len(self.kpBP)):
        update = (1.0 - comfort_lr * comfort_weight) * self.kpBP[i]
        self.kpBP[i] = self._limit_precision(update)

      for i in range(len(self.kpV)):
        update = (1.0 - comfort_lr * comfort_weight) * self.kpV[i]
        self.kpV[i] = self._limit_precision(update)

      for i in range(len(self.kiBP)):
        update = (1.0 - comfort_lr * comfort_weight) * self.kiBP[i]
        self.kiBP[i] = self._limit_precision(update)

      for i in range(len(self.kiV)):
        update = (1.0 - comfort_lr * comfort_weight) * self.kiV[i]
        self.kiV[i] = self._limit_precision(update)

      # Log the parameter changes to see the actual effect
      print("\nParameter changes after neural network prediction:")
      for param, before in original_values.items():
        before_val = float(before.numpy()) if hasattr(before, 'numpy') else float(before)
        after = getattr(self, param)
        after_val = float(after.numpy()) if hasattr(after, 'numpy') else float(after)
        change = after_val - before_val
        # Handle division by zero
        pct_change = (change / before_val) * 100 if before_val != 0 else float('inf')
        print(f" {param}: {before_val:.4f} → {after_val:.4f} (Δ{change:.4f}, {pct_change:.2f}%)")

    else:
      # Fallback to simpler adaptive learning if neural network isn't ready
      # Adjust deceleration rate based on comfort factor
      target_decel_rate = avg_decel * comfort_adjustment * (0.85 + 0.3 * (1.0 - comfort_factor))

      # Apply learning rate to the adjustment
      self.stopping_decel_rate = (1.0 - self.LEARNING_RATE) * self.stopping_decel_rate + self.LEARNING_RATE * target_decel_rate

      # Adjust PID gain factors based on stopping performance
      if stopping_accuracies:
        avg_accuracy = np.mean(stopping_accuracies)
        # Adjust P gain based on stopping accuracy
        target_kp_factor = 1.0 + (avg_accuracy - 0.5) * 0.5  # Range ~0.75-1.25
        # Adjust I gain based on stopping comfort
        target_ki_factor = 1.0 + (comfort_factor - 0.75) * 0.5  # Range ~0.75-1.25

        # Apply learning rate to gain adjustments
        self.kp_gain_factor = (1.0 - self.LEARNING_RATE) * self.kp_gain_factor + self.LEARNING_RATE * target_kp_factor
        self.ki_gain_factor = (1.0 - self.LEARNING_RATE) * self.ki_gain_factor + self.LEARNING_RATE * target_ki_factor

    # Ensure parameters are within bounds
    self._validate_params()

    # Save more frequently when we're actively learning
    self.save_params()

  def get_tuned_params(self):
    """Return current tuned parameters."""
    return {
      'vego_stopping': self.vego_stopping,
      'vego_starting': self.vego_starting,
      'stopping_decel_rate': self.stopping_decel_rate,
      'kp_gain_factor': self.kp_gain_factor,
      'ki_gain_factor': self.ki_gain_factor,
      'kf': self.kf,
      'kpBP': self.kpBP.tolist() if isinstance(self.kpBP, np.ndarray) else self.kpBP,
      'kpV': self.kpV.tolist() if isinstance(self.kpV, np.ndarray) else self.kpV,
      'kiBP': self.kiBP.tolist() if isinstance(self.kiBP, np.ndarray) else self.kiBP,
      'kiV': self.kiV.tolist() if isinstance(self.kiV, np.ndarray) else self.kiV
    }

  def get_pid_gains(self, original_kp, original_ki):
    """Apply the learned gain adjustments to the original PID values."""
    return original_kp * self.kp_gain_factor, original_ki * self.ki_gain_factor

  def _save_model_checkpoint(self):
    """Save the neural network weights as loss improves."""
    nn_weights = {'car_fingerprint': self.car_fingerprint}
    nn_weights.update({
      'nn_w1': self.nn.W1.tolist(),
      'nn_b1': self.nn.b1.tolist(),
      'nn_w2': self.nn.W2.tolist(),
      'nn_b2': self.nn.b2.tolist(),
      'nn_w_value': self.nn.W_value.tolist(),
      'nn_b_value': self.nn.b_value.tolist(),
      'nn_w_adv': self.nn.W_adv.tolist(),
      'nn_b_adv': self.nn.b_adv.tolist(),
    })
    car_specific_path = f"{self.safe_fingerprint}_nn_longitudinal.pkl"
    with open(car_specific_path, "wb") as f:
      pickle.dump(nn_weights, f)
    print(f"Saved car-specific neural network checkpoint to {car_specific_path}")

  def update_fingerprint(self, new_fingerprint: str, CP: structs.CarParams):
    if new_fingerprint and new_fingerprint != "MOCK" and new_fingerprint != self.car_fingerprint:
      self.car_fingerprint = new_fingerprint
      self.safe_fingerprint = ''.join(c if c.isalnum() else '_' for c in new_fingerprint)
      # Update default longitudinal parameters from CP:
      self.vego_stopping_default = getattr(CP, 'vEgoStopping', self.vego_stopping_default)
      self.vego_starting_default = getattr(CP, 'vEgoStarting', self.vego_starting_default)
      self.stopping_decel_rate_default = getattr(CP, 'stoppingDecelRate', self.stopping_decel_rate_default)
      long_tune = getattr(CP, 'longitudinalTuning', None)
      if long_tune:
        self.kf_default = getattr(long_tune, 'kf', self.kf_default)
        self.kpBP_default = np.array(getattr(long_tune, 'kpBP', self.kpBP_default.tolist()))
        self.kpV_default = np.array(getattr(long_tune, 'kpV', self.kpV_default.tolist()))
        self.kiBP_default = np.array(getattr(long_tune, 'kiBP', self.kiBP_default.tolist()))
        self.kiV_default = np.array(getattr(long_tune, 'kiV', self.kiV_default.tolist()))
      print(f"Updated tuner fingerprint to {new_fingerprint} with updated CP defaults")
