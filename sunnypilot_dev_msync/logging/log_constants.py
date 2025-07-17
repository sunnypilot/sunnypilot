MESSAGE_TYPES = ['liveMpcDEPRECATED','androidLog','orbFeaturesSummaryDEPRECATED',
 'roadCameraState', 'ubloxGnss', 'deviceState', 'sendcan',
 'gpsLocationExternal', 'sensorEventsDEPRECATED',
 'pandaStateDEPRECATED', 'gpsLocation', 'carControl', 'carState',
 'gpsNMEA', 'longitudinalPlan', 'qcomGnss', 'roadEncodeIdx',
 'procLog', 'logMessage', 'radarState', 'controlsState',
 'ubloxRaw', 'clocks', 'uiLayoutStateDEPRECATED',
 'driverStateDEPRECATED', 'liveTracksDEPRECATED',
 'liveCalibration', 'liveLongitudinalMpcDEPRECATED', 'model',
 'can']

# Message type descriptions (from Copilot - not verified):
# 'liveMpcDEPRECATED'         : Deprecated; previously contained live Model Predictive Control data.
# 'androidLog'                : Logs from the Android system (e.g., debug, error, info).
# 'orbFeaturesSummaryDEPRECATED': Deprecated; summary of ORB (feature detection) results.
# 'roadCameraState'           : State and metadata from the road-facing camera.
# 'ubloxGnss'                 : GNSS (GPS) data from u-blox receiver.
# 'deviceState'               : Information about the device's hardware and status.
# 'sendcan'                   : CAN messages to be sent to the vehicle.
# 'gpsLocationExternal'       : GPS location data from an external source.
# 'sensorEventsDEPRECATED'    : Deprecated; previously contained raw sensor events.
# 'pandaStateDEPRECATED'      : Deprecated; previously contained Panda hardware state.
# 'gpsLocation'               : GPS location data from the main GNSS source.
# 'carControl'                : Commands to control the car (steering, throttle, brake).
# 'carState'                  : Current state of the car (speed, gear, etc.).
# 'gpsNMEA'                   : Raw NMEA sentences from GPS.
# 'longitudinalPlan'          : Planned longitudinal (speed/distance) trajectory.
# 'qcomGnss'                  : GNSS data from Qualcomm receiver.
# 'roadEncodeIdx'             : Indexing information for encoded road camera frames.
# 'procLog'                   : Logs from various processes.
# 'logMessage'                : General log messages (info, warning, error).
# 'radarState'                : Processed radar data and object tracking.
# 'controlsState'             : State of the vehicle's control system.
# 'ubloxRaw'                  : Raw data from u-blox GNSS receiver.
# 'clocks'                    : Timing and clock synchronization data.
# 'uiLayoutStateDEPRECATED'   : Deprecated; previously contained UI layout state.
# 'driverStateDEPRECATED'     : Deprecated; previously contained driver monitoring state.
# 'liveTracksDEPRECATED'      : Deprecated; previously contained live object tracks.
# 'liveCalibration'           : Live calibration data for sensors and cameras.
# 'liveLongitudinalMpcDEPRECATED': Deprecated; previously contained longitudinal MPC data.
# 'model'                     : Neural network model predictions (e.g., path, lane lines).
# 'can'                       : Raw CAN messages received from the vehicle.
