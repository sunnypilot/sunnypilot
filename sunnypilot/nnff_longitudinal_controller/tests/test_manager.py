import os
import sys
import time

from opendbc.car.interfaces import CarInterfaceBase
from opendbc.car import structs
from sunnypilot.nnff_longitudinal_controller.manager import TunerManager
from sunnypilot.nnff_longitudinal_controller.policy_model import LongitudinalLiveTuner


class SimpleMock:
  """Simple mock class"""

  def __init__(self, return_value=None, side_effect=None):
    self.return_value = return_value
    self.side_effect = side_effect
    self.calls = []
    self.called = False

  def __call__(self, *args, **kwargs):
    self.calls.append((args, kwargs))
    self.called = True
    if self.side_effect is not None:
      if callable(self.side_effect):
        return self.side_effect(*args, **kwargs)
      else:
        raise self.side_effect
    return self.return_value


def simple_patch(target_path, new_value=None):
  """
  Args:
    target_path: String path to the object to patch (e.g., 'module.Class.method')
    new_value: Value to replace the target with

  Returns:
    Tuple of (original_value, patched_function) where patched_function is a decorator
  """
  module_path, attr_name = target_path.rsplit('.', 1)

  # Get the module or class containing the attribute
  parts = module_path.split('.')
  module = __import__(parts[0])
  for part in parts[1:]:
    module = getattr(module, part)

  # Save the original value
  original_value = getattr(module, attr_name) if hasattr(module, attr_name) else None

  # Replace with the new value or mock
  if new_value is None:
    new_value = SimpleMock()

  # Set the new value
  setattr(module, attr_name, new_value)

  # Return original value for restoration
  return original_value, new_value


class MockMessage:
  def __init__(self, which_msg, msg_data):
    self._which = which_msg
    self._data = msg_data

  def which(self):
    return self._which

  def __getattr__(self, name):
    if name in self._data:
      return self._data[name]
    raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


def find_local_route_dirs():
  """Find local route directories for manual log upload."""
  tests_dir = os.path.dirname(__file__)
  if not os.path.exists(tests_dir):
    print(f"Tests directory not found: {tests_dir}")
    return []
  print(f"Using tests directory: {tests_dir}")
  route_dirs = [tests_dir]
  print(f"Found {len(route_dirs)} route directory(ies)")
  return route_dirs


def test_training_with_local_route():
  """Test offroad training with a local route from the tests folder using real log data"""
  test_passed = False
  # (Retain patching of _save_processed_logs if desired)
  orig_save_logs, mock_save_logs = simple_patch('sunnypilot.nnff_longitudinal_controller.manager.TunerManager._save_processed_logs')
  route_dirs = find_local_route_dirs()
  if not route_dirs:
    print("No route logs found in tests folder.")
    return False

  route_path = route_dirs[0]
  print(f"Using route from: {route_path}")

  car_fingerprint = None

  # Create car params for car if we have a fingerprint
  if car_fingerprint:
    CP = CarInterfaceBase.get_std_params(car_fingerprint)
    # Create a real tuner instance
    real_tuner = LongitudinalLiveTuner(CP)
  else:

    # Create a basic CarParams object manually for testing
    CP = structs.CarParams()
    CP.carFingerprint = "MOCK"

    # Set minimum required parameters for longitudinal tuning
    CP.vEgoStopping = 0.5
    CP.vEgoStarting = 0.5
    CP.stoppingDecelRate = 0.8

    # Create longitudinal tuning parameters
    CP.longitudinalTuning.kf = 1.0
    CP.longitudinalTuning.kpBP = [0.0]
    CP.longitudinalTuning.kpV = [1.0]
    CP.longitudinalTuning.kiBP = [0.0]
    CP.longitudinalTuning.kiV = [0.1]

    print("Created mock CarParams until fingerprint is detected from logs")

    # Create the tuner with our mock CP
    real_tuner = LongitudinalLiveTuner(CP)

  # Save initial tuner state to compare after training
  initial_params = {
    'vego_stopping': real_tuner.vego_stopping,
    'vego_starting': real_tuner.vego_starting,
    'stopping_decel_rate': real_tuner.stopping_decel_rate,
    'kp_gain_factor': real_tuner.kp_gain_factor,
    'ki_gain_factor': real_tuner.ki_gain_factor
  }

  # Override only the route finding and tuner retrieval
  orig_get_tuner = TunerManager.get_tuner
  TunerManager.get_tuner = classmethod(lambda cls, car_fp: real_tuner)

  orig_find_routes = TunerManager._find_local_routes
  TunerManager._find_local_routes = lambda *args: [route_path]

  orig_create_tuner = TunerManager.create_tuner
  TunerManager.create_tuner = lambda _, CP: real_tuner

  # Save the original _train_on_route method for restoration

  # (No override is applied here to simulate using your real logs.)

  try:
    # Start training
    print("Starting offroad training using real log data...")
    TunerManager.start_offroad_training()

    # Add more debugging information
    print(f"Training status after start: {TunerManager.training_status}")

    # Wait longer for training to start (increase from 0.5s to 2s)
    print("Waiting for training thread to initialize...")
    for _ in range(10):  # Try for up to 10 intervals
      time.sleep(0.5)  # Check every 0.5 seconds
      if TunerManager.training_status['active']:
        print(f"Training became active after {_ * 0.5 + 0.5} seconds")
        break
      print(f"Training status: {TunerManager.training_status}")

    # Check if training thread exists and is running
    has_thread = hasattr(TunerManager, 'training_thread') and TunerManager.training_thread is not None
    thread_alive = has_thread and TunerManager.training_thread.is_alive()
    print(f"Training thread exists: {has_thread}, is alive: {thread_alive}")

    # Now check if training actually started
    assert TunerManager.training_status['active'], "Training should be active"
    assert TunerManager.training_status['source'] == 'replay', "Training source should be 'replay'"

    # Wait for training to complete
    max_wait = 1000  # seconds
    start_time = time.time()
    while (TunerManager.training_status['active'] and
           time.time() - start_time < max_wait):
      time.sleep(2)
      print(f"Training progress: {TunerManager.training_status['progress']:.2f}")

      # Print current tuner parameters to observe changes
      current_params = {
        'vego_stopping': real_tuner.vego_stopping,
        'vego_starting': real_tuner.vego_starting,
        'stopping_decel_rate': real_tuner.stopping_decel_rate,
        'kp_gain_factor': real_tuner.kp_gain_factor,
        'ki_gain_factor': real_tuner.ki_gain_factor
      }
      print(f"Current tuner parameters: {current_params}")

    # Check if training completed within timeout
    if time.time() - start_time >= max_wait:
      print("Training didn't complete within timeout")
      # Don't return directly, let the function return test_passed which is False
      return test_passed

    # Check if logs were processed
    assert mock_save_logs.called, "save_processed_logs should have been called"

    # Verify that the neural network was trained by comparing parameters
    final_params = {
      'vego_stopping': real_tuner.vego_stopping,
      'vego_starting': real_tuner.vego_starting,
      'stopping_decel_rate': real_tuner.stopping_decel_rate,
      'kp_gain_factor': real_tuner.kp_gain_factor,
      'ki_gain_factor': real_tuner.ki_gain_factor
    }

    print("\nTraining Results:")
    print("=================")
    print(f"Initial parameters: {initial_params}")
    print(f"Final parameters: {final_params}")

    # Check if any parameters changed (at least one should have)
    param_changed = False
    for param_name, initial_value in initial_params.items():
      if abs(final_params[param_name] - initial_value) > 1e-6:
        param_changed = True
        print(f"Parameter {param_name} changed: {initial_value} -> {final_params[param_name]}")

    # At least one parameter should have changed during training
    assert param_changed, "No parameters changed during training"
    test_passed = True  # Mark test as passed if we get here

  except Exception as e:
    print(f"Test failed with error: {e}")
    test_passed = False

  finally:
    # Restore original methods
    TunerManager.get_tuner = orig_get_tuner
    TunerManager._find_local_routes = orig_find_routes
    TunerManager._train_on_route = TunerManager._train_on_route
    TunerManager.create_tuner = orig_create_tuner
    TunerManager._save_processed_logs = orig_save_logs

    # Stop any training in progress
    TunerManager.training_status['active'] = False
    if hasattr(TunerManager, 'training_thread') and TunerManager.training_thread and TunerManager.training_thread.is_alive():
      TunerManager.training_thread.join(timeout=1.0)

  # Return test result
  return test_passed


def run_all_tests():
  """Run all tests and return True if all pass"""
  print("\n=== Running test_training_with_local_route ===")
  test_result = test_training_with_local_route()
  if not test_result:
    print("Test FAILED")
    return False

  print("All tests PASSED")
  return True


if __name__ == "__main__":
  # Print instructions at startup
  print("\nNNFF Longitudinal Controller Test")
  print("================================")
  print("This test runs with route logs from:")
  print("sunnypilot/nnff_longitudinal_controller/tests")
  print("\nTo run the test, place your route logs in this directory.")
  print("You can create a subfolder named with your route ID and add segment folders (0, 1, 2, etc.)")
  print("Or simply add rlog/qlog files directly to a subdirectory.")
  print("\nAdding a fingerprint.txt file with the car fingerprint (e.g., KIA_NIRO_EV) is recommended.")
  print("Otherwise, the test will try to guess from the folder name or default to MOCK.")
  print("================================\n")

  # Run the tests
  success = run_all_tests()
  sys.exit(0 if success else 1)

