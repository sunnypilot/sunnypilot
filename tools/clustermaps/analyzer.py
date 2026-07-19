from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from collections.abc import Callable
from typing import Any

import numpy as np

from openpilot.tools.lib.logreader import LogReader, ReadMode
from openpilot.tools.lib.route import SegmentRange


SCHEMA_VERSION = 2
EARTH_RADIUS_M = 6_371_007.2

SERVICE_INFO: dict[str, tuple[str, str, str | None]] = {
  "accelerometer": ("motion", "Raw three-axis accelerometer", "imu"),
  "gyroscope": ("motion", "Raw three-axis gyroscope", "imu"),
  "magnetometer": ("environment", "Raw three-axis magnetic field", "magnetic"),
  "temperatureSensor": ("environment", "IMU package temperature", "thermal"),
  "gpsLocation": ("position", "On-device GNSS position and velocity", "gps"),
  "gpsLocationExternal": ("position", "External GNSS position and velocity", "gps"),
  "liveLocationKalman": ("position", "Fused localization position and motion", "gps"),
  "qcomGnss": ("position", "Qualcomm raw satellite receiver diagnostics", None),
  "ubloxGnss": ("position", "u-blox raw satellite receiver diagnostics", None),
  "livePose": ("motion", "Fused device-frame pose and motion", "pose"),
  "cameraOdometry": ("vision", "Camera-derived translation and rotation", "visualOdometry"),
  "carState": ("vehicle", "Vehicle speed, acceleration, wheels, steering, and pedals", "vehicle"),
  "controlsState": ("vehicle", "Estimated and desired path curvature", "controls"),
  "liveParameters": ("calibration", "Learned steering, roll, and vehicle parameters", "calibration"),
  "radarState": ("objects", "Tracked lead-vehicle state", "radar"),
  "liveTracks": ("objects", "Raw radar tracks", None),
  "modelV2": ("vision", "Full vision-model path, lanes, edges, and objects", None),
  "drivingModelData": ("vision", "Compact path and lane metadata", "roadVision"),
  "soundPressure": ("environment", "A-weighted cabin sound pressure", "sound"),
  "deviceState": ("diagnostics", "Device thermal, power, storage, and utilization state", "thermal"),
  "roadCameraState": ("camera", "Road-camera frame metadata", None),
  "wideRoadCameraState": ("camera", "Wide-road-camera frame metadata", None),
  "driverCameraState": ("camera", "Driver-camera frame metadata", None),
  "roadEncodeIdx": ("camera", "Road-video frame index", None),
  "wideRoadEncodeIdx": ("camera", "Wide-road-video frame index", None),
  "driverEncodeIdx": ("camera", "Driver-video frame index", None),
  "qRoadEncodeIdx": ("camera", "Low-resolution road-video frame index", None),
  "can": ("vehicle bus", "Raw incoming vehicle-bus frames", None),
  "sendcan": ("vehicle bus", "Raw outgoing vehicle-bus frames", None),
  "driverStateV2": ("driver", "Driver-monitoring model output", None),
  "driverMonitoringState": ("driver", "Driver-monitoring policy state", None),
  "driverMonitoringStateDEPRECATED": ("driver", "Legacy driver-monitoring policy state", None),
  "pandaStates": ("diagnostics", "Vehicle-interface hardware state", None),
  "peripheralState": ("diagnostics", "Peripheral voltage, fan, and power state", None),
  "managerState": ("diagnostics", "Process manager state", None),
  "procLog": ("diagnostics", "Process resource telemetry", None),
  "clocks": ("diagnostics", "System clock correlation", None),
  "logMessage": ("diagnostics", "Software log messages", None),
  "androidLog": ("diagnostics", "Operating-system log messages", None),
}


@dataclass(frozen=True)
class AnalyzerConfig:
  minimum_speed_mps: float = 2.5
  impact_min_peak_mps2: float = 0.75
  impact_sigma: float = 6.0
  impact_merge_gap_s: float = 0.35
  rough_window_s: float = 2.0
  rough_step_s: float = 0.5
  rough_min_rms_mps2: float = 0.22
  rough_sigma: float = 2.5
  hard_accel_mps2: float = 2.0
  hard_brake_mps2: float = -2.5
  longitudinal_min_duration_s: float = 0.4
  body_motion_min_rad_s: float = 0.08
  body_motion_sigma: float = 3.0
  repeat_radius_m: float = 20.0


def _robust_sigma(values: np.ndarray) -> float:
  if len(values) == 0:
    return 0.0
  median = float(np.median(values))
  return 1.4826 * float(np.median(np.abs(values - median)))


def _lowpass(times: np.ndarray, values: np.ndarray, cutoff_hz: float) -> np.ndarray:
  if len(values) == 0:
    return values.copy()

  output = np.empty_like(values, dtype=float)
  output[0] = values[0]
  rc = 1.0 / (2.0 * math.pi * cutoff_hz)
  for i in range(1, len(values)):
    dt = float(np.clip(times[i] - times[i - 1], 1e-4, 0.25))
    alpha = dt / (rc + dt)
    output[i] = output[i - 1] + alpha * (values[i] - output[i - 1])
  return output


def _haversine_m(lat_a: float, lon_a: float, lat_b: float, lon_b: float) -> float:
  dlat = math.radians(lat_b - lat_a)
  dlon = math.radians(lon_b - lon_a)
  a = math.sin(dlat / 2.0) ** 2
  a += math.cos(math.radians(lat_a)) * math.cos(math.radians(lat_b)) * math.sin(dlon / 2.0) ** 2
  return 2.0 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def _route_id(identifier: str) -> str:
  return hashlib.sha256(identifier.encode()).hexdigest()[:16]


def _driver_id(identifier: str) -> str:
  dongle_id = identifier.replace("|", "/").split("/", 1)[0]
  return hashlib.sha256(dongle_id.encode()).hexdigest()[:8]


def _is_valid_position(latitude: float, longitude: float) -> bool:
  return -90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0 and (latitude != 0.0 or longitude != 0.0)


def _message_rate(times: list[float]) -> float:
  if len(times) < 2:
    return 0.0
  duration = times[-1] - times[0]
  return (len(times) - 1) / duration if duration > 0.0 else 0.0


def _service_catalog(service_times: dict[str, list[float]]) -> list[dict[str, Any]]:
  catalog = []
  for service, times in sorted(service_times.items()):
    category, description, layer = SERVICE_INFO.get(service, ("other", "Logged openpilot service", None))
    catalog.append({
      "service": service,
      "category": category,
      "description": description,
      "count": len(times),
      "rateHz": round(_message_rate(times), 3),
      "mapLayer": layer,
      "browserExported": layer is not None,
      "exportNote": (
        f"Downsampled into the {layer} map layer"
        if layer is not None
        else "Inventoried only; payload is bulky, redundant, transient, or privacy-sensitive"
      ),
    })
  return catalog


def _thin_points(points: list[dict[str, Any]], minimum_interval_s: float) -> list[dict[str, Any]]:
  if not points:
    return []
  output = [points[0]]
  for point in points[1:-1]:
    if point["t"] - output[-1]["t"] >= minimum_interval_s:
      output.append(point)
  if len(points) > 1 and points[-1] is not output[-1]:
    output.append(points[-1])
  return output


class LocationInterpolator:
  def __init__(self, points: list[dict[str, Any]]):
    self.points = points
    self.times = np.asarray([point["t"] for point in points], dtype=float)
    if len(self.times) > 1:
      median_dt = float(np.median(np.diff(self.times)))
      self.maximum_gap_s = max(1.0, median_dt * 2.5)
    else:
      self.maximum_gap_s = 0.0

  def at(self, timestamp: float) -> dict[str, float] | None:
    if len(self.points) < 2 or timestamp < self.times[0] or timestamp > self.times[-1]:
      return None

    right = int(np.searchsorted(self.times, timestamp, side="right"))
    right = min(max(right, 1), len(self.points) - 1)
    left = right - 1
    t0, t1 = self.times[left], self.times[right]
    if t1 - t0 <= 0.0 or t1 - t0 > self.maximum_gap_s:
      return None

    fraction = float((timestamp - t0) / (t1 - t0))
    p0, p1 = self.points[left], self.points[right]
    return {
      "latitude": float(p0["latitude"] + fraction * (p1["latitude"] - p0["latitude"])),
      "longitude": float(p0["longitude"] + fraction * (p1["longitude"] - p0["longitude"])),
    }


def _window_metrics(times: np.ndarray, values: np.ndarray, window_s: float, step_s: float) -> list[dict[str, float]]:
  if len(times) < 2:
    return []

  output: list[dict[str, float]] = []
  start = float(times[0])
  final_start = float(times[-1] - window_s)
  while start <= final_start:
    end = start + window_s
    left = int(np.searchsorted(times, start, side="left"))
    right = int(np.searchsorted(times, end, side="right"))
    window = values[left:right]
    if len(window) >= 4:
      output.append({
        "t": start + window_s / 2.0,
        "rms": float(np.sqrt(np.mean(np.square(window)))),
        "peak": float(np.max(np.abs(window))),
      })
    start += step_s
  return output


def _candidate_groups(times: np.ndarray, mask: np.ndarray, merge_gap_s: float) -> list[np.ndarray]:
  candidate_indices = np.flatnonzero(mask)
  if len(candidate_indices) == 0:
    return []

  groups: list[list[int]] = [[int(candidate_indices[0])]]
  for index in candidate_indices[1:]:
    index = int(index)
    if times[index] - times[groups[-1][-1]] > merge_gap_s:
      groups.append([index])
    else:
      groups[-1].append(index)
  return [np.asarray(group, dtype=int) for group in groups]


def _event_with_location(
  location: LocationInterpolator,
  timestamp: float,
  start_time: float,
  kind: str,
  severity: float,
  properties: dict[str, Any],
) -> dict[str, Any] | None:
  coordinates = location.at(timestamp)
  if coordinates is None:
    return None
  return {
    "kind": kind,
    "t": round(timestamp - start_time, 3),
    "latitude": round(coordinates["latitude"], 7),
    "longitude": round(coordinates["longitude"], 7),
    "severity": round(float(np.clip(severity, 0.0, 2.0)), 3),
    **properties,
  }


def _messages_with_progress(
  reader: LogReader,
  progress_callback: Callable[[int, int], None] | None,
):
  segment_paths = reader.logreader_identifiers
  for index, segment_path in enumerate(segment_paths):
    yield from LogReader(
      segment_path,
      default_mode=ReadMode.RLOG,
      sort_by_time=True,
      only_union_types=True,
    )
    if progress_callback is not None:
      progress_callback(index + 1, len(segment_paths))


def _extract_streams(
  identifier: str | list[str],
  progress_callback: Callable[[int, int], None] | None = None,
) -> dict[str, Any]:
  streams: dict[str, Any] = {
    "accelerometer": [],
    "gyroscope": [],
    "magnetometer": [],
    "temperatureSensor": [],
    "soundPressure": [],
    "carState": [],
    "livePose": [],
    "cameraOdometry": [],
    "liveParameters": [],
    "controlsState": [],
    "radarState": [],
    "drivingModelData": [],
    "deviceState": [],
    "gpsLocation": [],
    "gpsLocationExternal": [],
    "liveLocationKalman": [],
  }
  service_times: dict[str, list[float]] = {}
  metadata: dict[str, Any] = {}
  first_log_time: float | None = None
  last_log_time: float | None = None

  reader = LogReader(identifier, default_mode=ReadMode.RLOG, sort_by_time=True, only_union_types=True)
  for message in _messages_with_progress(reader, progress_callback):
    which = message.which()
    timestamp = message.logMonoTime * 1e-9
    first_log_time = timestamp if first_log_time is None else min(first_log_time, timestamp)
    last_log_time = timestamp if last_log_time is None else max(last_log_time, timestamp)
    service_times.setdefault(which, []).append(timestamp)

    if which == "accelerometer" and message.accelerometer.which() == "acceleration":
      raw = message.accelerometer.acceleration.v
      if len(raw) == 3:
        # This is the same sensor-to-device transform used by locationd.
        streams["accelerometer"].append((timestamp, -float(raw[2]), -float(raw[1]), -float(raw[0])))
    elif which == "gyroscope" and message.gyroscope.which() == "gyroUncalibrated":
      raw = message.gyroscope.gyroUncalibrated.v
      if len(raw) == 3:
        streams["gyroscope"].append((timestamp, -float(raw[2]), -float(raw[1]), -float(raw[0])))
    elif which == "magnetometer" and message.magnetometer.which() == "magneticUncalibrated":
      raw = message.magnetometer.magneticUncalibrated.v
      if len(raw) >= 3:
        streams["magnetometer"].append((timestamp, float(raw[0]), float(raw[1]), float(raw[2])))
    elif which == "temperatureSensor" and message.temperatureSensor.which() == "temperature":
      streams["temperatureSensor"].append((timestamp, float(message.temperatureSensor.temperature)))
    elif which == "soundPressure":
      sound = message.soundPressure
      streams["soundPressure"].append((
        timestamp,
        float(sound.soundPressureWeightedDb),
        float(sound.soundPressureWeighted),
      ))
    elif which == "carState":
      state = message.carState
      streams["carState"].append((
        timestamp,
        float(state.vEgo),
        float(state.aEgo),
        bool(state.gasPressed),
        bool(state.brakePressed),
        float(state.yawRate),
        float(state.steeringAngleDeg),
        float(state.steeringRateDeg),
        float(state.steeringTorque),
        float(state.wheelSpeeds.fl),
        float(state.wheelSpeeds.fr),
        float(state.wheelSpeeds.rl),
        float(state.wheelSpeeds.rr),
        bool(state.leftBlinker),
        bool(state.rightBlinker),
        bool(state.leftBlindspot),
        bool(state.rightBlindspot),
      ))
    elif which == "livePose":
      pose = message.livePose
      if pose.accelerationDevice.valid and pose.angularVelocityDevice.valid:
        streams["livePose"].append((
          timestamp,
          float(pose.accelerationDevice.x),
          float(pose.accelerationDevice.y),
          float(pose.accelerationDevice.z),
          float(pose.angularVelocityDevice.x),
          float(pose.angularVelocityDevice.y),
          float(pose.angularVelocityDevice.z),
          bool(pose.inputsOK and pose.sensorsOK),
        ))
    elif which == "cameraOdometry":
      odometry = message.cameraOdometry
      if len(odometry.trans) == 3 and len(odometry.rot) == 3:
        streams["cameraOdometry"].append((
          timestamp,
          *map(float, odometry.trans),
          *map(float, odometry.rot),
          float(np.linalg.norm(odometry.transStd)) if len(odometry.transStd) == 3 else 0.0,
          float(np.linalg.norm(odometry.rotStd)) if len(odometry.rotStd) == 3 else 0.0,
        ))
    elif which == "liveParameters":
      parameters = message.liveParameters
      streams["liveParameters"].append((
        timestamp,
        float(parameters.roll),
        float(parameters.steerRatio),
        float(parameters.stiffnessFactor),
        float(parameters.angleOffsetDeg),
        float(parameters.angleOffsetAverageDeg),
        bool(parameters.valid and parameters.sensorValid),
      ))
    elif which == "controlsState":
      controls = message.controlsState
      streams["controlsState"].append((
        timestamp,
        float(controls.curvature),
        float(controls.desiredCurvature),
        bool(controls.forceDecel),
      ))
    elif which == "radarState":
      lead = message.radarState.leadOne
      streams["radarState"].append((
        timestamp,
        bool(lead.status),
        float(lead.dRel),
        float(lead.yRel),
        float(lead.vRel),
        float(lead.aRel),
        float(lead.modelProb),
        bool(lead.radar),
      ))
    elif which == "drivingModelData":
      model = message.drivingModelData
      lane = model.laneLineMeta
      streams["drivingModelData"].append((
        timestamp,
        float(lane.leftY),
        float(lane.rightY),
        float(lane.leftProb),
        float(lane.rightProb),
        float(model.action.desiredCurvature),
        float(model.action.desiredAcceleration),
        bool(model.action.shouldStop),
        float(model.frameDropPerc),
      ))
    elif which == "deviceState":
      device = message.deviceState
      streams["deviceState"].append((
        timestamp,
        float(device.maxTempC),
        float(device.powerDrawW),
        float(device.somPowerDrawW),
        float(device.freeSpacePercent),
        float(device.memoryUsagePercent),
      ))
    elif which in ("gpsLocation", "gpsLocationExternal"):
      gps = getattr(message, which)
      latitude, longitude = float(gps.latitude), float(gps.longitude)
      if bool(gps.hasFix) and _is_valid_position(latitude, longitude):
        streams[which].append({
          "t": timestamp,
          "latitude": latitude,
          "longitude": longitude,
          "altitude": float(gps.altitude),
          "speed": float(gps.speed),
          "bearing": float(gps.bearingDeg),
          "horizontalAccuracy": float(gps.horizontalAccuracy) if gps.horizontalAccuracy > 0.0 else None,
          "verticalAccuracy": float(gps.verticalAccuracy) if gps.verticalAccuracy > 0.0 else None,
          "speedAccuracy": float(gps.speedAccuracy) if gps.speedAccuracy > 0.0 else None,
          "bearingAccuracy": float(gps.bearingAccuracyDeg) if gps.bearingAccuracyDeg > 0.0 else None,
          "satelliteCount": int(gps.satelliteCount),
          "velocityNED": [round(float(value), 4) for value in gps.vNED],
          "source": which,
        })
    elif which == "liveLocationKalman":
      location = message.liveLocationKalman
      position = location.positionGeodetic
      if position.valid and len(position.value) == 3 and str(location.status) == "valid":
        latitude, longitude, altitude = map(float, position.value)
        if _is_valid_position(latitude, longitude):
          velocity = list(location.velocityNED.value)
          speed = math.hypot(float(velocity[0]), float(velocity[1])) if len(velocity) >= 2 else 0.0
          bearing = math.degrees(math.atan2(float(velocity[1]), float(velocity[0]))) % 360.0 if speed > 0.1 else 0.0
          horizontal_accuracy = None
          if len(position.std) >= 2:
            horizontal_accuracy = math.hypot(float(position.std[0]), float(position.std[1]))
          streams["liveLocationKalman"].append({
            "t": timestamp,
            "latitude": latitude,
            "longitude": longitude,
            "altitude": altitude,
            "speed": speed,
            "bearing": bearing,
            "horizontalAccuracy": horizontal_accuracy,
            "verticalAccuracy": float(position.std[2]) if len(position.std) >= 3 else None,
            "speedAccuracy": None,
            "bearingAccuracy": None,
            "satelliteCount": None,
            "velocityNED": [round(float(value), 4) for value in velocity],
            "source": which,
          })
    elif which == "carParams" and "platform" not in metadata:
      metadata["platform"] = str(message.carParams.carFingerprint)
    elif which == "initData" and "softwareVersion" not in metadata:
      metadata["softwareVersion"] = str(message.initData.version)

  if first_log_time is None or last_log_time is None:
    raise ValueError(f"No messages found in rlog for {identifier}")

  analysis_times: list[float] = []
  for service in ("accelerometer", "gyroscope", "carState", "livePose",
                  "gpsLocationExternal", "gpsLocation", "liveLocationKalman"):
    values = streams[service]
    if not values:
      continue
    analysis_times.extend((
      float(values[0]["t"] if isinstance(values[0], dict) else values[0][0]),
      float(values[-1]["t"] if isinstance(values[-1], dict) else values[-1][0]),
    ))
  if analysis_times:
    first_log_time = min(analysis_times)
    last_log_time = max(analysis_times)

  rates = {
    service: {
      "count": len(times),
      "rateHz": round(_message_rate(times), 3),
    }
    for service, times in service_times.items()
  }
  return {
    "streams": streams,
    "rates": rates,
    "serviceCatalog": _service_catalog(service_times),
    "metadata": metadata,
    "startTime": first_log_time,
    "endTime": last_log_time,
  }


def _select_track(streams: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
  for source, minimum_interval in (
    ("liveLocationKalman", 0.2),
    ("gpsLocationExternal", 0.1),
    ("gpsLocation", 0.2),
  ):
    points = streams[source]
    if len(points) >= 2:
      return source, _thin_points(points, minimum_interval)
  raise ValueError("The rlog has no usable absolute-position stream")


def _downsample_rows(rows: list[tuple[Any, ...]], minimum_interval_s: float) -> list[tuple[Any, ...]]:
  output: list[tuple[Any, ...]] = []
  last_time = -math.inf
  for row in rows:
    if float(row[0]) - last_time < minimum_interval_s:
      continue
    output.append(row)
    last_time = float(row[0])
  return output


def _mapped_sample(
  row: tuple[Any, ...],
  location: LocationInterpolator,
  start_time: float,
  properties: dict[str, Any],
) -> dict[str, Any] | None:
  coordinates = location.at(float(row[0]))
  if coordinates is None:
    return None
  return {
    "t": round(float(row[0]) - start_time, 3),
    "latitude": round(coordinates["latitude"], 7),
    "longitude": round(coordinates["longitude"], 7),
    **properties,
  }


def _build_telemetry_layers(
  streams: dict[str, Any],
  location: LocationInterpolator,
  start_time: float,
) -> dict[str, list[dict[str, Any]]]:
  telemetry: dict[str, list[dict[str, Any]]] = {
    "imu": [],
    "vehicle": [],
    "pose": [],
    "visualOdometry": [],
    "controls": [],
    "calibration": [],
    "roadVision": [],
    "radar": [],
    "sound": [],
    "magnetic": [],
    "thermal": [],
  }

  accelerometer = np.asarray(streams["accelerometer"], dtype=float)
  gyroscope = np.asarray(streams["gyroscope"], dtype=float)
  if len(accelerometer):
    times = accelerometer[:, 0]
    baseline = np.column_stack([_lowpass(times, accelerometer[:, axis], 0.8) for axis in range(1, 4)])
    linear = accelerometer[:, 1:4] - baseline
    gyro_values = np.zeros((len(times), 3), dtype=float)
    if len(gyroscope):
      for axis in range(3):
        gyro_values[:, axis] = np.interp(times, gyroscope[:, 0], gyroscope[:, axis + 1])
    last_time = -math.inf
    for index, row in enumerate(accelerometer):
      if row[0] - last_time < 0.2:
        continue
      sample = _mapped_sample(tuple(row), location, start_time, {
        "service": "accelerometer + gyroscope",
        "linearAccelX": round(float(linear[index, 0]), 3),
        "linearAccelY": round(float(linear[index, 1]), 3),
        "linearAccelZ": round(float(linear[index, 2]), 3),
        "rawAccelMagnitude": round(float(np.linalg.norm(row[1:4])), 3),
        "gyroX": round(float(gyro_values[index, 0]), 4),
        "gyroY": round(float(gyro_values[index, 1]), 4),
        "gyroZ": round(float(gyro_values[index, 2]), 4),
      })
      if sample is not None:
        telemetry["imu"].append(sample)
      last_time = float(row[0])

  for row in _downsample_rows(streams["carState"], 0.5):
    sample = _mapped_sample(row, location, start_time, {
      "service": "carState",
      "speedMps": round(float(row[1]), 3),
      "accelerationMps2": round(float(row[2]), 3),
      "gasPressed": bool(row[3]),
      "brakePressed": bool(row[4]),
      "yawRateRadS": round(float(row[5]), 4),
      "steeringAngleDeg": round(float(row[6]), 2),
      "steeringRateDegS": round(float(row[7]), 2),
      "steeringTorque": round(float(row[8]), 2),
      "wheelSpeedsMps": [round(float(value), 3) for value in row[9:13]],
      "leftBlinker": bool(row[13]),
      "rightBlinker": bool(row[14]),
      "leftBlindspot": bool(row[15]),
      "rightBlindspot": bool(row[16]),
    })
    if sample is not None:
      telemetry["vehicle"].append(sample)

  for row in _downsample_rows(streams["livePose"], 0.5):
    sample = _mapped_sample(row, location, start_time, {
      "service": "livePose",
      "accelerationDevice": [round(float(value), 4) for value in row[1:4]],
      "angularVelocityDevice": [round(float(value), 5) for value in row[4:7]],
      "inputsValid": bool(row[7]),
    })
    if sample is not None:
      telemetry["pose"].append(sample)

  for row in _downsample_rows(streams["cameraOdometry"], 0.5):
    sample = _mapped_sample(row, location, start_time, {
      "service": "cameraOdometry",
      "translationDeviceMps": [round(float(value), 4) for value in row[1:4]],
      "rotationDeviceRadS": [round(float(value), 5) for value in row[4:7]],
      "translationStdNorm": round(float(row[7]), 4),
      "rotationStdNorm": round(float(row[8]), 5),
    })
    if sample is not None:
      telemetry["visualOdometry"].append(sample)

  for row in _downsample_rows(streams["controlsState"], 0.5):
    sample = _mapped_sample(row, location, start_time, {
      "service": "controlsState",
      "curvaturePerM": round(float(row[1]), 7),
      "desiredCurvaturePerM": round(float(row[2]), 7),
      "forceDecel": bool(row[3]),
    })
    if sample is not None:
      telemetry["controls"].append(sample)

  for row in _downsample_rows(streams["liveParameters"], 1.0):
    sample = _mapped_sample(row, location, start_time, {
      "service": "liveParameters",
      "rollRad": round(float(row[1]), 5),
      "steerRatio": round(float(row[2]), 4),
      "stiffnessFactor": round(float(row[3]), 4),
      "angleOffsetDeg": round(float(row[4]), 4),
      "averageAngleOffsetDeg": round(float(row[5]), 4),
      "valid": bool(row[6]),
    })
    if sample is not None:
      telemetry["calibration"].append(sample)

  for row in _downsample_rows(streams["drivingModelData"], 0.5):
    sample = _mapped_sample(row, location, start_time, {
      "service": "drivingModelData",
      "leftLaneY": round(float(row[1]), 3),
      "rightLaneY": round(float(row[2]), 3),
      "leftLaneProbability": round(float(row[3]), 3),
      "rightLaneProbability": round(float(row[4]), 3),
      "desiredCurvaturePerM": round(float(row[5]), 7),
      "desiredAccelerationMps2": round(float(row[6]), 3),
      "shouldStop": bool(row[7]),
      "frameDropPercent": round(float(row[8]), 3),
    })
    if sample is not None:
      telemetry["roadVision"].append(sample)

  for row in _downsample_rows(streams["radarState"], 1.0):
    sample = _mapped_sample(row, location, start_time, {
      "service": "radarState",
      "leadDetected": bool(row[1]),
      "leadDistanceM": round(float(row[2]), 2),
      "leadLateralM": round(float(row[3]), 2),
      "leadRelativeSpeedMps": round(float(row[4]), 3),
      "leadRelativeAccelerationMps2": round(float(row[5]), 3),
      "modelProbability": round(float(row[6]), 3),
      "radarConfirmed": bool(row[7]),
    })
    if sample is not None:
      telemetry["radar"].append(sample)

  for row in _downsample_rows(streams["soundPressure"], 0.5):
    sample = _mapped_sample(row, location, start_time, {
      "service": "soundPressure",
      "weightedDb": round(float(row[1]), 2),
      "weightedPressure": round(float(row[2]), 6),
    })
    if sample is not None:
      telemetry["sound"].append(sample)

  for row in _downsample_rows(streams["magnetometer"], 1.0):
    vector = np.asarray(row[1:4], dtype=float)
    sample = _mapped_sample(row, location, start_time, {
      "service": "magnetometer",
      "magnetic": [round(float(value), 3) for value in vector],
      "magnitude": round(float(np.linalg.norm(vector)), 3),
    })
    if sample is not None:
      telemetry["magnetic"].append(sample)

  for row in _downsample_rows(streams["temperatureSensor"], 2.0):
    sample = _mapped_sample(row, location, start_time, {
      "service": "temperatureSensor",
      "imuTemperatureC": round(float(row[1]), 2),
    })
    if sample is not None:
      telemetry["thermal"].append(sample)
  for row in _downsample_rows(streams["deviceState"], 2.0):
    sample = _mapped_sample(row, location, start_time, {
      "service": "deviceState",
      "maximumTemperatureC": round(float(row[1]), 2),
      "powerDrawW": round(float(row[2]), 2),
      "somPowerDrawW": round(float(row[3]), 2),
      "freeSpacePercent": round(float(row[4]), 2),
      "memoryUsagePercent": round(float(row[5]), 2),
    })
    if sample is not None:
      telemetry["thermal"].append(sample)

  return telemetry


def _analyze_impacts(
  accelerometer: list[tuple[float, ...]],
  car_state: list[tuple[float, ...]],
  location: LocationInterpolator,
  start_time: float,
  config: AnalyzerConfig,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, float]]:
  if len(accelerometer) < 4:
    return [], [], {"thresholdMps2": 0.0, "noiseSigmaMps2": 0.0}

  accelerometer_array = np.asarray(accelerometer, dtype=float)
  times = accelerometer_array[:, 0]
  vertical = accelerometer_array[:, 3]
  vertical_highpass = vertical - _lowpass(times, vertical, cutoff_hz=0.8)
  impact_amplitude = np.abs(vertical_highpass)
  noise_sigma = _robust_sigma(impact_amplitude)
  threshold = max(
    config.impact_min_peak_mps2,
    float(np.median(impact_amplitude)) + config.impact_sigma * noise_sigma,
  )

  if car_state:
    car_state_array = np.asarray(car_state, dtype=float)
    speeds = np.interp(times, car_state_array[:, 0], car_state_array[:, 1])
  else:
    speeds = np.full_like(times, config.minimum_speed_mps)

  mask = (impact_amplitude >= threshold) & (speeds >= config.minimum_speed_mps)
  events: list[dict[str, Any]] = []
  for group in _candidate_groups(times, mask, config.impact_merge_gap_s):
    peak_index = int(group[np.argmax(impact_amplitude[group])])
    peak = float(impact_amplitude[peak_index])
    event = _event_with_location(
      location,
      float(times[peak_index]),
      start_time,
      "impact",
      peak / threshold,
      {
        "peakVerticalMps2": round(peak, 3),
        "speedMps": round(float(speeds[peak_index]), 3),
        "thresholdMps2": round(threshold, 3),
      },
    )
    if event is not None:
      events.append(event)

  rough_windows = _window_metrics(times, vertical_highpass, config.rough_window_s, config.rough_step_s)
  rough_values = np.asarray([window["rms"] for window in rough_windows], dtype=float)
  rough_sigma = _robust_sigma(rough_values)
  rough_threshold = max(
    config.rough_min_rms_mps2,
    (float(np.median(rough_values)) + config.rough_sigma * rough_sigma) if len(rough_values) else 0.0,
  )
  roughness: list[dict[str, Any]] = []
  for window in rough_windows:
    coordinates = location.at(window["t"])
    if coordinates is None:
      continue
    speed = float(np.interp(window["t"], times, speeds))
    roughness.append({
      "t": round(window["t"] - start_time, 3),
      "latitude": round(coordinates["latitude"], 7),
      "longitude": round(coordinates["longitude"], 7),
      "rmsMps2": round(window["rms"], 3),
      "peakMps2": round(window["peak"], 3),
      "score": round(window["rms"] / rough_threshold if rough_threshold > 0.0 else 0.0, 3),
      "speedMps": round(speed, 3),
      "isRough": bool(window["rms"] >= rough_threshold and speed >= config.minimum_speed_mps),
    })

  diagnostics = {
    "thresholdMps2": round(threshold, 3),
    "noiseSigmaMps2": round(noise_sigma, 3),
    "roughThresholdRmsMps2": round(rough_threshold, 3),
  }
  return events, roughness, diagnostics


def _analyze_longitudinal(
  car_state: list[tuple[float, ...]],
  location: LocationInterpolator,
  start_time: float,
  config: AnalyzerConfig,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
  if len(car_state) < 4:
    return [], []

  state = np.asarray(car_state, dtype=float)
  times, speeds, acceleration = state[:, 0], state[:, 1], state[:, 2]
  filtered_acceleration = _lowpass(times, acceleration, cutoff_hz=1.0)
  events: list[dict[str, Any]] = []
  definitions = (
    ("hardAcceleration", filtered_acceleration >= config.hard_accel_mps2, config.hard_accel_mps2, np.argmax),
    ("hardBraking", filtered_acceleration <= config.hard_brake_mps2, abs(config.hard_brake_mps2), np.argmin),
  )
  for kind, mask, threshold, peak_function in definitions:
    for group in _candidate_groups(times, mask, merge_gap_s=0.2):
      duration = float(times[group[-1]] - times[group[0]])
      if duration < config.longitudinal_min_duration_s:
        continue
      peak_index = int(group[int(peak_function(filtered_acceleration[group]))])
      peak = float(filtered_acceleration[peak_index])
      event = _event_with_location(
        location,
        float(times[peak_index]),
        start_time,
        kind,
        abs(peak) / threshold,
        {
          "peakAccelerationMps2": round(peak, 3),
          "durationS": round(duration, 3),
          "speedMps": round(float(speeds[peak_index]), 3),
        },
      )
      if event is not None:
        events.append(event)

  samples: list[dict[str, Any]] = []
  for window in _window_metrics(times, filtered_acceleration, window_s=1.0, step_s=1.0):
    coordinates = location.at(window["t"])
    if coordinates is None:
      continue
    left = int(np.searchsorted(times, window["t"] - 0.5, side="left"))
    right = int(np.searchsorted(times, window["t"] + 0.5, side="right"))
    values = filtered_acceleration[left:right]
    if len(values) == 0:
      continue
    samples.append({
      "t": round(window["t"] - start_time, 3),
      "latitude": round(coordinates["latitude"], 7),
      "longitude": round(coordinates["longitude"], 7),
      "meanMps2": round(float(np.mean(values)), 3),
      "minimumMps2": round(float(np.min(values)), 3),
      "maximumMps2": round(float(np.max(values)), 3),
    })
  return events, samples


def _analyze_body_motion(
  live_pose: list[tuple[float, ...]],
  location: LocationInterpolator,
  start_time: float,
  config: AnalyzerConfig,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, float]]:
  if len(live_pose) < 4:
    return [], [], {"thresholdRadS": 0.0}

  pose = np.asarray(live_pose, dtype=float)
  times = pose[:, 0]
  roll_pitch_rate = np.hypot(pose[:, 4], pose[:, 5])
  windows = _window_metrics(times, roll_pitch_rate, window_s=1.0, step_s=0.5)
  rms_values = np.asarray([window["rms"] for window in windows], dtype=float)
  threshold = max(
    config.body_motion_min_rad_s,
    (float(np.median(rms_values)) + config.body_motion_sigma * _robust_sigma(rms_values)) if len(rms_values) else 0.0,
  )

  samples: list[dict[str, Any]] = []
  for window in windows:
    coordinates = location.at(window["t"])
    if coordinates is None:
      continue
    samples.append({
      "t": round(window["t"] - start_time, 3),
      "latitude": round(coordinates["latitude"], 7),
      "longitude": round(coordinates["longitude"], 7),
      "rmsRadS": round(window["rms"], 4),
      "peakRadS": round(window["peak"], 4),
      "score": round(window["rms"] / threshold if threshold > 0.0 else 0.0, 3),
      "isExcessive": bool(window["rms"] >= threshold),
    })

  mask = roll_pitch_rate >= threshold
  events: list[dict[str, Any]] = []
  for group in _candidate_groups(times, mask, merge_gap_s=0.5):
    peak_index = int(group[np.argmax(roll_pitch_rate[group])])
    peak = float(roll_pitch_rate[peak_index])
    event = _event_with_location(
      location,
      float(times[peak_index]),
      start_time,
      "bodyMotion",
      peak / threshold,
      {"peakRollPitchRateRadS": round(peak, 4)},
    )
    if event is not None:
      events.append(event)

  return events, samples, {"thresholdRadS": round(threshold, 4)}


def _selected_identifiers(identifier: str, segment_indexes: list[int] | None) -> tuple[str | list[str], list[int], str]:
  segment_range = SegmentRange(identifier)
  base_identifier = f"{segment_range.dongle_id}/{segment_range.log_id}"
  available_indexes = segment_range.seg_idxs
  if segment_indexes is None:
    return identifier, available_indexes, identifier

  selected_indexes = sorted(set(segment_indexes))
  if not selected_indexes or any(index not in available_indexes for index in selected_indexes):
    raise ValueError("Selected segments must be a non-empty subset of the route's available segments")
  if selected_indexes == available_indexes:
    return base_identifier, selected_indexes, base_identifier

  groups: list[list[int]] = []
  for index in selected_indexes:
    if not groups or index != groups[-1][-1] + 1:
      groups.append([index])
    else:
      groups[-1].append(index)
  identifiers = [
    f"{base_identifier}/{group[0]}" if len(group) == 1 else f"{base_identifier}/{group[0]}:{group[-1] + 1}"
    for group in groups
  ]
  source_identifier: str | list[str] = identifiers[0] if len(identifiers) == 1 else identifiers
  cache_key = f"{base_identifier}/segments={','.join(map(str, selected_indexes))}"
  return source_identifier, selected_indexes, cache_key


def analyze_route(
  identifier: str,
  label: str | None = None,
  config: AnalyzerConfig | None = None,
  segment_indexes: list[int] | None = None,
  progress_callback: Callable[[int, int], None] | None = None,
  log_files: list[str] | None = None,
) -> dict[str, Any]:
  config = config or AnalyzerConfig()
  if log_files is None:
    source_identifier, selected_indexes, cache_key = _selected_identifiers(identifier, segment_indexes)
  else:
    if not log_files:
      raise ValueError("At least one local rlog file is required")
    source_identifier = log_files
    selected_indexes = segment_indexes if segment_indexes is not None else list(range(len(log_files)))
    cache_key = identifier
  cache_id = _route_id(cache_key)
  segment_count = len(selected_indexes)
  extracted = _extract_streams(source_identifier, progress_callback)
  streams = extracted["streams"]
  track_source, track = _select_track(streams)
  location = LocationInterpolator(track)
  start_time = extracted["startTime"]

  impacts, roughness, impact_diagnostics = _analyze_impacts(
    streams["accelerometer"], streams["carState"], location, start_time, config,
  )
  longitudinal_events, longitudinal_samples = _analyze_longitudinal(
    streams["carState"], location, start_time, config,
  )
  body_events, body_samples, body_diagnostics = _analyze_body_motion(
    streams["livePose"], location, start_time, config,
  )
  telemetry = _build_telemetry_layers(streams, location, start_time)
  events = sorted(impacts + longitudinal_events + body_events, key=lambda event: event["t"])

  distance_m = sum(
    _haversine_m(a["latitude"], a["longitude"], b["latitude"], b["longitude"])
    for a, b in zip(track, track[1:], strict=False)
  )
  bounds = {
    "south": min(point["latitude"] for point in track),
    "west": min(point["longitude"] for point in track),
    "north": max(point["latitude"] for point in track),
    "east": max(point["longitude"] for point in track),
  }
  event_counts = {
    kind: sum(event["kind"] == kind for event in events)
    for kind in ("impact", "hardAcceleration", "hardBraking", "bodyMotion")
  }
  event_counts["roughRoad"] = sum(point["isRough"] for point in roughness)

  normalized_track = [
    {
      **point,
      "t": round(point["t"] - start_time, 3),
      "latitude": round(point["latitude"], 7),
      "longitude": round(point["longitude"], 7),
      "altitude": round(point["altitude"], 2),
      "speed": round(point["speed"], 3),
      "bearing": round(point["bearing"], 2),
      "horizontalAccuracy": round(point["horizontalAccuracy"], 2) if point["horizontalAccuracy"] is not None else None,
      "verticalAccuracy": round(point["verticalAccuracy"], 2) if point["verticalAccuracy"] is not None else None,
      "speedAccuracy": round(point["speedAccuracy"], 3) if point["speedAccuracy"] is not None else None,
      "bearingAccuracy": round(point["bearingAccuracy"], 2) if point["bearingAccuracy"] is not None else None,
    }
    for point in track
  ]

  return {
    "schemaVersion": SCHEMA_VERSION,
    "id": cache_id,
    "routeName": identifier,
    "label": label or identifier,
    "driverId": _driver_id(identifier),
    "metadata": {**extracted["metadata"], "segmentCount": segment_count},
    "source": {
      "logType": "rlog",
      "locationService": track_source,
      "serviceStats": extracted["rates"],
      "serviceCatalog": extracted["serviceCatalog"],
    },
    "summary": {
      "durationS": round(extracted["endTime"] - start_time, 2),
      "distanceM": round(distance_m, 1),
      "maximumSpeedMps": round(max((point["speed"] for point in track), default=0.0), 2),
      "eventCounts": event_counts,
    },
    "bounds": {key: round(value, 7) for key, value in bounds.items()},
    "track": normalized_track,
    "layers": {
      "roughness": roughness,
      "longitudinal": longitudinal_samples,
      "bodyMotion": body_samples,
      "events": events,
      "telemetry": telemetry,
    },
    "diagnostics": {
      "impact": impact_diagnostics,
      "bodyMotion": body_diagnostics,
      "config": asdict(config),
    },
  }


def merge_segment_routes(
  identifier: str,
  segment_routes: list[dict[str, Any]],
  label: str | None = None,
  cache_key: str | None = None,
  segment_indexes: list[int] | None = None,
) -> dict[str, Any]:
  if not segment_routes:
    raise ValueError("At least one analyzed segment is required")
  if segment_indexes is None:
    segment_indexes = list(range(len(segment_routes)))
  if len(segment_indexes) != len(segment_routes):
    raise ValueError("segment_indexes must match the number of analyzed segments")

  merged_track: list[dict[str, Any]] = []
  merged_layers: dict[str, Any] = {
    "roughness": [],
    "longitudinal": [],
    "bodyMotion": [],
    "events": [],
    "telemetry": {key: [] for key in segment_routes[0]["layers"]["telemetry"]},
  }
  offsets: list[float] = []
  elapsed = 0.0
  for segment in segment_routes:
    offsets.append(elapsed)
    for point in segment["track"]:
      merged_track.append({**point, "t": round(point["t"] + elapsed, 3)})
    for layer_name in ("roughness", "longitudinal", "bodyMotion", "events"):
      merged_layers[layer_name].extend(
        {**point, "t": round(point["t"] + elapsed, 3)}
        for point in segment["layers"][layer_name]
      )
    for layer_name, points in segment["layers"]["telemetry"].items():
      merged_layers["telemetry"].setdefault(layer_name, []).extend(
        {**point, "t": round(point["t"] + elapsed, 3)}
        for point in points
      )
    elapsed += float(segment["summary"]["durationS"])

  service_stats: dict[str, dict[str, Any]] = {}
  service_catalog: dict[str, dict[str, Any]] = {}
  for segment in segment_routes:
    for service, stats in segment["source"]["serviceStats"].items():
      aggregate = service_stats.setdefault(service, {"count": 0, "rateHz": 0.0})
      aggregate["count"] += stats["count"]
      aggregate["rateHz"] = max(aggregate["rateHz"], stats["rateHz"])
    for entry in segment["source"]["serviceCatalog"]:
      aggregate = service_catalog.setdefault(entry["service"], {**entry, "count": 0, "rateHz": 0.0})
      aggregate["count"] += entry["count"]
      aggregate["rateHz"] = max(aggregate["rateHz"], entry["rateHz"])

  event_counts = {
    kind: sum(segment["summary"]["eventCounts"][kind] for segment in segment_routes)
    for kind in ("impact", "hardAcceleration", "hardBraking", "bodyMotion", "roughRoad")
  }
  location_services = {segment["source"]["locationService"] for segment in segment_routes}
  return {
    "schemaVersion": SCHEMA_VERSION,
    "id": _route_id(cache_key or identifier),
    "routeName": identifier,
    "label": label or identifier,
    "driverId": _driver_id(identifier),
    "metadata": {
      **segment_routes[0]["metadata"],
      "segmentCount": len(segment_routes),
    },
    "source": {
      "logType": "rlog",
      "locationService": next(iter(location_services)) if len(location_services) == 1 else "mixed",
      "serviceStats": service_stats,
      "serviceCatalog": sorted(service_catalog.values(), key=lambda entry: entry["service"]),
    },
    "summary": {
      "durationS": round(elapsed, 2),
      "distanceM": round(sum(segment["summary"]["distanceM"] for segment in segment_routes), 1),
      "maximumSpeedMps": max(segment["summary"]["maximumSpeedMps"] for segment in segment_routes),
      "eventCounts": event_counts,
    },
    "bounds": {
      "south": min(segment["bounds"]["south"] for segment in segment_routes),
      "west": min(segment["bounds"]["west"] for segment in segment_routes),
      "north": max(segment["bounds"]["north"] for segment in segment_routes),
      "east": max(segment["bounds"]["east"] for segment in segment_routes),
    },
    "track": merged_track,
    "layers": merged_layers,
    "diagnostics": {
      "config": segment_routes[0]["diagnostics"]["config"],
      "segments": [
        {
          "index": index,
          "offsetS": round(offset, 2),
          "impact": segment["diagnostics"]["impact"],
          "bodyMotion": segment["diagnostics"]["bodyMotion"],
        }
        for index, offset, segment in zip(segment_indexes, offsets, segment_routes, strict=True)
      ],
    },
  }


def route_to_geojson(route: dict[str, Any]) -> dict[str, Any]:
  features: list[dict[str, Any]] = [{
    "type": "Feature",
    "geometry": {
      "type": "LineString",
      "coordinates": [[point["longitude"], point["latitude"]] for point in route["track"]],
    },
    "properties": {
      "featureType": "route",
      "routeId": route["id"],
      "label": route["label"],
      "driverId": route["driverId"],
      **route["summary"],
    },
  }]

  for event in route["layers"]["events"]:
    properties = {key: value for key, value in event.items() if key not in ("latitude", "longitude")}
    features.append({
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [event["longitude"], event["latitude"]]},
      "properties": {"featureType": "event", "routeId": route["id"], **properties},
    })

  for roughness in route["layers"]["roughness"]:
    if not roughness["isRough"]:
      continue
    properties = {key: value for key, value in roughness.items() if key not in ("latitude", "longitude")}
    features.append({
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [roughness["longitude"], roughness["latitude"]]},
      "properties": {"featureType": "roughRoad", "routeId": route["id"], **properties},
    })

  return {"type": "FeatureCollection", "features": features}


def _cluster_problem_locations(routes: list[dict[str, Any]], radius_m: float) -> list[dict[str, Any]]:
  observations: list[dict[str, Any]] = []
  for route in routes:
    for event in route["layers"]["events"]:
      if event["kind"] == "impact":
        observations.append({
          **event,
          "routeId": route["id"],
          "driverId": route["driverId"],
          "problemType": "impact",
        })
    for sample in route["layers"]["roughness"]:
      if sample["isRough"]:
        observations.append({
          **sample,
          "severity": sample["score"],
          "routeId": route["id"],
          "driverId": route["driverId"],
          "problemType": "roughRoad",
        })

  clusters: list[dict[str, Any]] = []
  for observation in sorted(observations, key=lambda item: item["severity"], reverse=True):
    best_cluster = None
    best_distance = float("inf")
    for cluster in clusters:
      distance = _haversine_m(
        observation["latitude"], observation["longitude"], cluster["latitude"], cluster["longitude"],
      )
      if distance <= radius_m and distance < best_distance:
        best_cluster = cluster
        best_distance = distance
    if best_cluster is None:
      clusters.append({
        "latitude": observation["latitude"],
        "longitude": observation["longitude"],
        "observations": [observation],
      })
    else:
      best_cluster["observations"].append(observation)
      count = len(best_cluster["observations"])
      best_cluster["latitude"] += (observation["latitude"] - best_cluster["latitude"]) / count
      best_cluster["longitude"] += (observation["longitude"] - best_cluster["longitude"]) / count

  repeated: list[dict[str, Any]] = []
  for cluster in clusters:
    route_ids = sorted({observation["routeId"] for observation in cluster["observations"]})
    if len(route_ids) < 2:
      continue
    driver_ids = sorted({observation["driverId"] for observation in cluster["observations"]})
    problem_types = sorted({observation["problemType"] for observation in cluster["observations"]})
    repeated.append({
      "latitude": round(cluster["latitude"], 7),
      "longitude": round(cluster["longitude"], 7),
      "observationCount": len(cluster["observations"]),
      "routeCount": len(route_ids),
      "driverCount": len(driver_ids),
      "routeIds": route_ids,
      "driverIds": driver_ids,
      "problemTypes": problem_types,
      "maximumSeverity": round(max(observation["severity"] for observation in cluster["observations"]), 3),
    })
  return repeated


def rebuild_index(cache_dir: Path, config: AnalyzerConfig | None = None) -> dict[str, Any]:
  config = config or AnalyzerConfig()
  route_files = sorted((cache_dir / "routes").glob("*.json"))
  routes = [json.loads(path.read_text()) for path in route_files]
  repeated_locations = _cluster_problem_locations(routes, config.repeat_radius_m)
  index_routes = [{
    "id": route["id"],
    "file": f"routes/{route['id']}.json",
    "geojsonFile": f"geojson/{route['id']}.geojson",
    "label": route["label"],
    "driverId": route["driverId"],
    "metadata": route["metadata"],
    "summary": route["summary"],
    "bounds": route["bounds"],
  } for route in routes]

  index = {
    "schemaVersion": SCHEMA_VERSION,
    "generatedAt": datetime.now(UTC).isoformat(),
    "routeCount": len(routes),
    "driverCount": len({route["driverId"] for route in routes}),
    "routes": index_routes,
    "repeatedLocations": repeated_locations,
  }
  cache_dir.mkdir(parents=True, exist_ok=True)
  (cache_dir / "index.json").write_text(json.dumps(index, separators=(",", ":")))

  cluster_geojson = {
    "type": "FeatureCollection",
    "features": [{
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [cluster["longitude"], cluster["latitude"]]},
      "properties": {"featureType": "repeatedProblem", **{
        key: value for key, value in cluster.items() if key not in ("latitude", "longitude")
      }},
    } for cluster in repeated_locations],
  }
  (cache_dir / "repeated_locations.geojson").write_text(json.dumps(cluster_geojson, separators=(",", ":")))
  return index


def _json_safe(value: Any) -> Any:
  if isinstance(value, float) and not math.isfinite(value):
    return None
  if isinstance(value, dict):
    return {key: _json_safe(item) for key, item in value.items()}
  if isinstance(value, list):
    return [_json_safe(item) for item in value]
  return value


def write_route_cache(route: dict[str, Any], cache_dir: Path, config: AnalyzerConfig | None = None) -> tuple[Path, Path]:
  routes_dir = cache_dir / "routes"
  geojson_dir = cache_dir / "geojson"
  routes_dir.mkdir(parents=True, exist_ok=True)
  geojson_dir.mkdir(parents=True, exist_ok=True)

  route_path = routes_dir / f"{route['id']}.json"
  geojson_path = geojson_dir / f"{route['id']}.geojson"
  safe_route = _json_safe(route)
  route_path.write_text(json.dumps(safe_route, separators=(",", ":"), allow_nan=False))
  geojson_path.write_text(json.dumps(route_to_geojson(safe_route), separators=(",", ":"), allow_nan=False))
  rebuild_index(cache_dir, config)
  return route_path, geojson_path
