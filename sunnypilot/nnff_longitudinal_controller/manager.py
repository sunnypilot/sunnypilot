import json
import os
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path

from cereal import messaging
from openpilot.common.params import Params
from openpilot.common.realtime import Ratekeeper
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.test.process_replay.process_replay import get_custom_params_from_lr, replay_process_with_name
from openpilot.system.manager.process_config import managed_processes, ProcGroup
from openpilot.tools.lib.logreader import LogReader

from opendbc.car.interfaces import CarInterfaceBase
from sunnypilot.nnff_longitudinal_controller.longitudinal_nnff import LongitudinalLiveTuner


class TunerManager:
  """Manages longitudinal tuning both on-road and off-road"""
  tuners = {}  # Store tuners by car fingerprint
  training_status = {
    'progress': 0.0,
    'active': False,
    'paused': False,
    'source': 'none',  # 'onroad', 'replay', or 'none'
    'training_steps': 0,
    'target_steps': 20 * 60 * 20,  # 20 minutes at 20Hz
    'current_route': '',
    'routes_completed': 0,
    'routes_total': 0,
    'onroad_enabled': True,  # Default to enable onroad training
    'offroad_enabled': False,  # Default to disable offroad training
  }

  replay_routes = []
  training_thread = None
  OFFROAD_DAEMON_NAME = 'longitudinalTuner'

  @classmethod
  def get_tuner(cls, car_fingerprint):
    """Get tune for specific car"""
    return cls.tuners.get(car_fingerprint)

  @classmethod
  def apply_tuned_params_to_cp(cls, CP):
    """Apply all tuned parameters to the CarParams object"""
    tuner = cls.get_tuner(CP.carFingerprint)
    if tuner is not None:
      tuned_params = tuner.get_tuned_params()

      CP.vEgoStopping = tuned_params['vego_stopping']
      CP.vEgoStarting = tuned_params['vego_starting']
      CP.stoppingDecelRate = tuned_params['stopping_decel_rate']
      if hasattr(CP, 'longitudinalTuning'):
        if hasattr(CP.longitudinalTuning, 'kf'):
          CP.longitudinalTuning.kf = tuned_params['kf']
        if len(CP.longitudinalTuning.kpBP) == len(tuned_params['kpBP']):
          CP.longitudinalTuning.kpBP = tuned_params['kpBP']
        if len(CP.longitudinalTuning.kpV) == len(tuned_params['kpV']):
          CP.longitudinalTuning.kpV = tuned_params['kpV']
        if len(CP.longitudinalTuning.kiBP) == len(tuned_params['kiBP']):
          CP.longitudinalTuning.kiBP = tuned_params['kiBP']
        if len(CP.longitudinalTuning.kiV) == len(tuned_params['kiV']):
          CP.longitudinalTuning.kiV = tuned_params['kiV']

  @classmethod
  def create_tuner(cls, CP):
    """Create and store tune for a car only if live tuning is enabled"""
    params = Params()
    mode = params.get("LongitudinalLiveTuneParams", "none")
    if mode == "none":
      return None  # Live tuning disabled
    # else, live tuning enabled; proceed to create tuner
    if CP.carFingerprint not in cls.tuners:
      tuner = LongitudinalLiveTuner(CP, CP.longitudinalTuning.kpV, CP.longitudinalTuning.kiV)
      cls.tuners[CP.carFingerprint] = tuner
      CP._liveTuner = tuner
      cls.apply_tuned_params_to_cp(CP)
      return tuner
    CP._liveTuner = cls.tuners[CP.carFingerprint]
    cls.apply_tuned_params_to_cp(CP)
    return cls.tuners[CP.carFingerprint]

  @classmethod
  def check_training_status(cls):
    """Check if training should start, pause, or resume based on onroad status"""
    params = Params()
    is_onroad = params.get_bool("IsOnroad")
    mode = params.get("LongitudinalLiveTuneParams", "none")

    # When onroad but mode is not set to onroad tuning, pause any replay training
    if is_onroad and mode != "onroad":
      if cls.training_status['active'] and cls.training_status['source'] == 'replay':
        cloudlog.info("Vehicle onroad with live tuning off - pausing training")
        cls.training_status['paused'] = True
        cls.update_ui_status()
    # When offroad and mode indicates replay tuning, resume or start training
    elif not is_onroad and mode == "replay":
      if cls.training_status['paused']:
        cloudlog.info("Vehicle offroad - resuming paused training")
        cls.training_status['paused'] = False
        cls.update_ui_status()
      elif not cls.training_status['active']:
        cls.start_offroad_training()
    # Otherwise, leave training state unchanged

  @classmethod
  def start_offroad_training(cls):
    """Start training using replay data when car is parked"""
    if cls.training_thread is not None and cls.training_thread.is_alive():
      return  # Already training

    cls.training_status['active'] = True
    cls.training_status['source'] = 'replay'
    cls.training_thread = threading.Thread(target=cls._offroad_training_loop, daemon=True)
    cls.training_thread.start()
    cloudlog.info("Started offroad longitudinal training")
    cls.update_ui_status()

  @classmethod
  def _offroad_training_loop(cls):
    """Main loop for off-road training"""

    routes = cls._find_local_routes()
    if not routes:
      cloudlog.info("No local routes found for training")
      cls.training_status['active'] = False
      cls.update_ui_status()
      return

    cls.training_status['routes_total'] = len(routes)
    cls.training_status['routes_completed'] = 0
    cls.update_ui_status()

    # Load routes and train on their data
    route_index = 0
    while route_index < len(routes):
      # Check if training is paused (vehicle went onroad)
      if cls.training_status.get('paused', False):
        cloudlog.info("Training paused - waiting until vehicle is offroad again")
        cls.update_ui_status()
        # Sleep and check if we're still paused
        time.sleep(10)
        continue

      route = routes[route_index]
      cls.training_status['current_route'] = route
      cls.training_status['routes_completed'] = route_index
      cls.update_ui_status()

      cloudlog.info(f"Training on route: {route}")
      cls._train_on_route(route)
      route_index += 1

    cls.training_status['active'] = False
    cls.training_status['routes_completed'] = len(routes)
    cls.update_ui_status()
    cloudlog.info("Completed offroad longitudinal training")

  @classmethod
  def _find_local_routes(cls):
    """Find locally stored routes for training"""
    routes = []
    processed_logs = cls._load_processed_logs()

    # Look for routes in the standard locations
    route_dirs = [
      '/data/media/0/realdata/',  # Main storage location
      '/data/openpilot/selfdrive/test/process_replay/test_data/'  # Test data location
    ]

    for route_dir in route_dirs:
      if not os.path.exists(route_dir):
        continue

      route_paths = Path(route_dir).glob("*")
      for route_path in route_paths:
        if os.path.isdir(route_path) and not route_path.name.startswith('.'):
          route_id = route_path.name
          route_data = processed_logs["routes"].get(route_id, {})
          if route_data.get("fully_processed", False):
            cloudlog.debug(f"Route {route_id} already processed, skipping")
            continue
          routes.append(str(route_path))

    # Sort by modification time (newest first)
    routes.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    # Take at most 10 routes to avoid excessive training time
    return routes[:10]

  @classmethod
  def _get_processed_logs_file(cls):
    """Get the path to the file tracking processed logs"""
    return os.path.join(os.path.expanduser("~/.comma/training/"), "processed_nnff_logs.json")

  @classmethod
  def _load_processed_logs(cls):
    """Load the list of logs that have been processed already"""
    processed_logs_file = cls._get_processed_logs_file()
    if os.path.exists(processed_logs_file):
      try:
        with open(processed_logs_file) as f:
          return json.load(f)
      except OSError as e:
        cloudlog.warning(f"Error loading processed logs: {e}")

    # Return empty structure if file doesn't exist or has errors
    return {"routes": {}, "segments": {}, "last_updated": 0}

  @classmethod
  def _save_processed_logs(cls, processed_logs):
    """Save the list of logs that have been processed"""
    processed_logs_file = cls._get_processed_logs_file()
    os.makedirs(os.path.dirname(processed_logs_file), exist_ok=True)

    # Update timestamp
    processed_logs["last_updated"] = time.time()
    try:
      with open(processed_logs_file, 'w') as f:
        json.dump(processed_logs, f)
    except OSError as e:
      cloudlog.warning(f"Error saving processed logs: {e}")

  @classmethod
  def reset_processed_logs(cls):
    """Reset the list of processed logs, allowing them to be processed again"""
    processed_logs_file = cls._get_processed_logs_file()
    if os.path.exists(processed_logs_file):
      # Backup the old file with timestamp
      backup_file = f"{processed_logs_file}.{int(time.time())}.bak"
      try:
        os.rename(processed_logs_file, backup_file)
        cloudlog.info(f"Backed up processed logs to {backup_file}")
      except OSError as e:
        cloudlog.warning(f"Could not backup processed logs: {e}")
      # Write a fresh processed logs file
      cls._save_processed_logs({"routes": {}, "segments": {}, "last_updated": time.time()})
      return True
    return False

  @classmethod
  def _train_on_route(cls, route):
    """Train tuner using data from a specific route"""
    cloudlog.info(f"Starting training on route: {route}")

    # Get processed logs
    processed_logs = cls._load_processed_logs()

    # Generate a route identifier based on the folder name
    route_id = os.path.basename(route)

    # Check if this entire route has already been processed
    route_data = processed_logs["routes"].get(route_id, {})
    if route_data.get("fully_processed", False):
      cloudlog.info(f"Route {route_id} has already been fully processed, skipping")
      return

    # Look for segment files
    segment_paths = sorted(Path(route).glob("*"))

    # Track if we processed any segments in this run
    processed_any_segment = False

    # Mark this route as being processed
    if route_id not in processed_logs["routes"]:
      processed_logs["routes"][route_id] = {
        "path": route,
        "first_seen": time.time(),
        "fully_processed": False,
        "segment_count": len(segment_paths)
      }

    segment_index = 0
    while segment_index < len(segment_paths):
      # Check if we're paused
      if cls.training_status.get('paused', False):
        # Save our progress before pausing
        if processed_any_segment:
          cls._save_processed_logs(processed_logs)
        # Wait for resume
        time.sleep(1)
        continue

      segment_path = segment_paths[segment_index]
      segment_id = os.path.basename(str(segment_path))

      # Check if this segment has already been processed
      if segment_id in processed_logs.get("segments", {}) and processed_logs["segments"][segment_id].get("processed", False):
        cloudlog.debug(f"Segment {segment_id} has already been processed, skipping")
        segment_index += 1
        continue

      # Look for the log files
      for log_format in ['rlog', 'rlog.bz2', 'raw_log.bz2', 'rlog.zst', 'qlog', 'qlog.bz2', 'qlog.zst', "fcamera.hevc"]:
        log_path = os.path.join(segment_path, log_format)
        if os.path.exists(log_path):
          cloudlog.info(f"Processing segment: {segment_path}")

          try:
            # Create log reader
            lr = LogReader(log_path)

            # Extract messages by type
            car_params_msgs = [m for m in lr if m.which() == 'carParams']
            if not car_params_msgs:
              continue

            # Get car fingerprint from the first message
            car_fingerprint = car_params_msgs[0].carParams.carFingerprint

            # Setup custom params from log
            custom_params = get_custom_params_from_lr(lr)

            # Get or create tuner for this car
            tuner = cls.get_tuner(car_fingerprint)
            if tuner is None:
              # Create a new tuner with the car parameters
              CP = CarInterfaceBase.get_std_params(car_fingerprint)
              tuner = cls.create_tuner(CP)

            # Use process_replay API to run controlsd with our log data
            cloudlog.info(f"Replaying data for {car_fingerprint}")
            output_logs = replay_process_with_name(['controlsd', 'plannerd', 'radard'], lr,
                                                custom_params=custom_params)

            # Extract processed controlsd outputs
            control_outputs = [m for m in output_logs if m.which() == 'controlsState']

            # Feed processed data to the tuner
            cloudlog.info(f"Processing {len(control_outputs)} control states")
            last_train_idx = 0
            for i, cs in enumerate(control_outputs):
              # Always collect the data (lightweight operation)
              tuner.update_data(cs.controlsState.carState, cs.controlsState.actuators)

              # Only perform neural network training periodically
              if i - last_train_idx >= 60:  # Train every ~3 seconds (at 20Hz)
                tuner.force_update(cs.controlsState.carState, cs.controlsState.actuators)
                last_train_idx = i
                # Update UI
                cls.training_status['progress'] = tuner.training_progress
                cls.update_ui_status()

            # Save the tuner state after processing segment
            tuner._save_params()
            cloudlog.info(f"Completed processing segment: {segment_path}")

            # Mark the segment as processed in our tracking data
            processed_logs["segments"][segment_id] = {
              "processed": True,
              "car_fingerprint": car_fingerprint,
              "route_id": route_id,
              "processed_time": time.time(),
              "log_format": log_format
            }
            processed_any_segment = True

          except Exception as e:
            cloudlog.exception(f"Error training on segment {segment_path}: {e}")
            processed_logs["segments"][segment_id] = {
              "processed": False,
              "error": str(e),
              "error_time": time.time()
            }

          # Save our progress after each segment
          cls._save_processed_logs(processed_logs)

        # We found and processed a log, move on to next segment
        break

      # If we've processed all segments in the route, mark it.
      segment_index += 1
      segments_in_route = [s for s in processed_logs["segments"].values()
                          if s.get("route_id") == route_id and s.get("processed", False)]

      if len(segments_in_route) == len(segment_paths):
        processed_logs["routes"][route_id]["fully_processed"] = True
        cloudlog.info(f"Route {route_id} has been fully processed")

    # Save our final state for this route
    if processed_any_segment:
      cls._save_processed_logs(processed_logs)


  @classmethod
  def register_process(cls):
    """Register the longitudinal tuner process with the manager"""

    @dataclass
    class LongitudinalTunerProcessConfig:
      name = "longitudinalTuner"
      enabled = True
      onroad = False
      proc_group = ProcGroup.OFFROAD
      nice = 10

      def __init__(self):
        params = Params()
        mode = params.get("LongitudinalLiveTuneParams", "none")
        # Enable if tuning mode is set to "onroad" or "replay"
        self.enabled = mode in ["onroad", "replay"]

      def start(self):
        cloudlog.info("Starting longitudinal tuner process")
        TunerManager.start_offroad_training()

    # Register process with the manager
    managed_processes["longitudinal_tuner"] = LongitudinalTunerProcessConfig()

    # Initialize/update UI
    TunerManager.update_ui_status()

  @classmethod
  def update_data(cls, CS, actuators):
    """Update all tuners with new car state and actuator data"""
    for tuner in cls.tuners.values():
      tuner.update_data(CS, actuators)

  @classmethod
  def update_ui_status(cls):
    """Update training status for UI display"""
    params = Params()
    cls.training_status['is_onroad'] = params.get_bool("IsOnroad")
    try:
      pm = messaging.PubMaster(['longitudinalPlanSP'])
      nnfflong = messaging.new_message('longitudinalPlanSP')
      longtuning_status = nnfflong.longitudinalPlanSP.longtuningStatus

      # Set the enum based on training status
      if cls.training_status['active']:
        if cls.training_status['source'] == 'replay':
          longtuning_status.tuning = 'replay' if not cls.training_status['is_onroad'] else 'none'
        elif cls.training_status['source'] == 'onroad':
          longtuning_status.tuning = 'onroad' if cls.training_status['is_onroad'] else 'none'
        else:
          longtuning_status.tuning = 'none'
      else:
        longtuning_status.tuning = 'none'

      pm.send('longitudinalPlanSP', nnfflong)
    except Exception as e:
      cloudlog.exception(f"Error publishing longitudinal tuning status: {e}")

  @classmethod
  def should_run_offroad(cls):
    """Check if offroad training should run based on master toggle"""
    mode = Params().get("LongitudinalLiveTuneParams", "none")
    return mode == "replay"

  @classmethod
  def should_run_onroad(cls):
    """Check if onroad live tuning should run based on master toggle"""
    mode = Params().get("LongitudinalLiveTuneParams", "none")
    return mode == "onroad"

def main():
  """Main entry point for offroad training process"""
  # Check for command line arguments
  if len(sys.argv) > 1:
    if sys.argv[1] == "--reset-processed-logs":
      if TunerManager.reset_processed_logs():
        print("Successfully reset processed logs")
      else:
        print("No processed logs file found")

      sys.exit(0)
  TunerManager.register_process()

  # Load params
  params = Params()

  # Previous onroad state
  prev_onroad = params.get_bool("IsOnroad")

  # Create a rate keeper
  rk = Ratekeeper(1, print_delay_threshold=None)

  # Main loop
  while True:
    # Check for onroad/offroad transitions
    is_onroad = params.get_bool("IsOnroad")
    if is_onroad != prev_onroad:
      cloudlog.info(f"Vehicle transitioned to {'onroad' if is_onroad else 'offroad'} mode")
      TunerManager.check_training_status()
      prev_onroad = is_onroad

    if not is_onroad and TunerManager.should_run_offroad():
      if not TunerManager.training_status['active']:
        TunerManager.start_offroad_training()

    TunerManager.update_ui_status()

    # Keep the loop rate consistent
    rk.keep_time()

if __name__ == "__main__":
  main()
