#!/usr/bin/env python3
import time
import numpy as np
import cereal.messaging as messaging
from cereal import car, log
from setproctitle import setproctitle
from cereal.messaging import PubMaster, SubMaster
from msgq.visionipc import VisionIpcClient, VisionStreamType, VisionBuf
from opendbc.car.car_helpers import get_demo_car_params
from openpilot.common.swaglog import cloudlog
from openpilot.common.params import Params
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.realtime import config_realtime_process, DT_MDL
from openpilot.common.transformations.camera import DEVICE_CAMERAS
from openpilot.common.transformations.model import get_warp_matrix
from openpilot.system import sentry
from openpilot.selfdrive.controls.lib.desire_helper import DesireHelper
from openpilot.selfdrive.controls.lib.drive_helpers import get_accel_from_plan, smooth_value

from openpilot.sunnypilot.modeld_v2.fill_model_msg import fill_model_msg, fill_pose_msg, PublishState, get_curvature_from_output
from openpilot.sunnypilot.modeld_v2.constants import Plan
from openpilot.sunnypilot.modeld_v2.models.commonmodel_pyx import DrivingModelFrame, CLContext
from openpilot.sunnypilot.modeld_v2.meta_helper import load_meta_constants

from openpilot.sunnypilot.livedelay.helpers import get_lat_delay
from openpilot.sunnypilot.modeld.modeld_base import ModelStateBase
from openpilot.sunnypilot.models.helpers import get_active_bundle
from openpilot.sunnypilot.models.runners.helpers import get_model_runner

PROCESS_NAME = "selfdrive.modeld.modeld_tinygrad"


class FrameMeta:
  frame_id: int = 0
  timestamp_sof: int = 0
  timestamp_eof: int = 0

  def __init__(self, vipc=None):
    if vipc is not None:
      self.frame_id, self.timestamp_sof, self.timestamp_eof = vipc.frame_id, vipc.timestamp_sof, vipc.timestamp_eof


class ModelState(ModelStateBase):
  frames: dict[str, DrivingModelFrame]
  inputs: dict[str, np.ndarray]
  prev_desire: np.ndarray  # for tracking the rising edge of the pulse
  temporal_idxs: slice | np.ndarray

  def __init__(self, context: CLContext):
    ModelStateBase.__init__(self)
    try:
      self.model_runner = get_model_runner()
      self.constants = self.model_runner.constants
    except Exception as e:
      cloudlog.exception(f"Failed to initialize model runner: {str(e)}")
      raise

    model_bundle = get_active_bundle()
    self.generation = model_bundle.generation if model_bundle is not None else None
    overrides = {override.key: override.value for override in model_bundle.overrides}

    self.LAT_SMOOTH_SECONDS = float(overrides.get('lat', ".0"))
    self.LONG_SMOOTH_SECONDS = float(overrides.get('long', ".0"))
    self.MIN_LAT_CONTROL_SPEED = 0.3

    buffer_length = 5 if self.model_runner.is_20hz else 2
    self.frames = {name: DrivingModelFrame(context, buffer_length) for name in self.model_runner.vision_input_names}
    self.prev_desire = np.zeros(self.constants.DESIRE_LEN, dtype=np.float32)

    # img buffers are managed in openCL transform code
    self.numpy_inputs = {}
    self.temporal_buffers = {}
    self.temporal_idxs_map = {}

    for key, shape in self.model_runner.input_shapes.items():
      if key not in self.frames: # Managed by opencl
        self.numpy_inputs[key] = np.zeros(shape, dtype=np.float32)
        # Temporal input: shape is [batch, history, features]
        if len(shape) == 3 and shape[1] > 1:
          buffer_history_len = shape[1] * 4 if shape[1] < 99 else shape[1]  # Allow for higher history buffers in the future
          feature_len = shape[2]
          features_buffer_shape = self.model_runner.input_shapes.get('features_buffer')
          if shape[1] in (24, 25) and features_buffer_shape is not None and features_buffer_shape[1] == 24:  # 20Hz
            buffer_history_len = (features_buffer_shape[1] + 1) * 4
            step = int(-buffer_history_len / shape[1])
            self.temporal_idxs_map[key] = np.arange(step, step * (shape[1] + 1), step)[::-1]
          elif shape[1] == 25:  # Split
            skip = buffer_history_len // shape[1]
            self.temporal_idxs_map[key] = np.arange(buffer_history_len)[-1 - (skip * (shape[1] - 1))::skip]
          elif shape[1] >= 99:  # non20hz
            self.temporal_idxs_map[key] = np.arange(shape[1])
          self.temporal_buffers[key] = np.zeros((1, buffer_history_len, feature_len), dtype=np.float32)

  @property
  def mlsim(self) -> bool:
    return bool(self.generation is not None and self.generation >= 11)

  @property
  def desire_key(self) -> str:
    return next(key for key in self.numpy_inputs if key.startswith('desire'))

  def run(self, bufs: dict[str, VisionBuf], transforms: dict[str, np.ndarray],
                inputs: dict[str, np.ndarray], prepare_only: bool) -> dict[str, np.ndarray] | None:
    # Model decides when action is completed, so desire input is just a pulse triggered on rising edge
    inputs[self.desire_key][0] = 0
    new_desire = np.where(inputs[self.desire_key] - self.prev_desire > .99, inputs[self.desire_key], 0)
    self.prev_desire[:] = inputs[self.desire_key]
    self.temporal_buffers[self.desire_key][0,:-1] = self.temporal_buffers[self.desire_key][0,1:]
    self.temporal_buffers[self.desire_key][0,-1] = new_desire

    # Roll buffer and assign based on desire.shape[1] value
    if self.temporal_buffers[self.desire_key].shape[1] > self.numpy_inputs[self.desire_key].shape[1]:
      skip = self.temporal_buffers[self.desire_key].shape[1] // self.numpy_inputs[self.desire_key].shape[1]
      self.numpy_inputs[self.desire_key][:] = (self.temporal_buffers[self.desire_key][0].reshape(
                                               self.numpy_inputs[self.desire_key].shape[0], self.numpy_inputs[self.desire_key].shape[1], skip, -1).max(axis=2))
    else:
      self.numpy_inputs[self.desire_key][:] = self.temporal_buffers[self.desire_key][0, self.temporal_idxs_map[self.desire_key]]

    for key in self.numpy_inputs:
      if key in inputs and key not in [self.desire_key]:
        self.numpy_inputs[key][:] = inputs[key]

    imgs_cl = {name: self.frames[name].prepare(bufs[name], transforms[name].flatten()) for name in self.model_runner.vision_input_names}

    # Prepare inputs using the model runner
    self.model_runner.prepare_inputs(imgs_cl, self.numpy_inputs, self.frames)

    if prepare_only:
      return None

    # Run model inference
    outputs = self.model_runner.run_model()

    # Update features_buffer
    self.temporal_buffers['features_buffer'][0, :-1] = self.temporal_buffers['features_buffer'][0, 1:]
    self.temporal_buffers['features_buffer'][0, -1] = outputs['hidden_state'][0, :]
    self.numpy_inputs['features_buffer'][:] = self.temporal_buffers['features_buffer'][0, self.temporal_idxs_map['features_buffer']]

    if "desired_curvature" in outputs:
      input_name_prev = None
      if "prev_desired_curvs" in self.numpy_inputs.keys():
        input_name_prev = 'prev_desired_curvs'
      elif "prev_desired_curv" in self.numpy_inputs.keys():
        input_name_prev = 'prev_desired_curv'
      if input_name_prev and input_name_prev in self.temporal_buffers:
        self.process_desired_curvature(outputs, input_name_prev)
    return outputs

  def process_desired_curvature(self, outputs, input_name_prev):
    self.temporal_buffers[input_name_prev][0,:-1] = self.temporal_buffers[input_name_prev][0,1:]
    self.temporal_buffers[input_name_prev][0,-1,:] = outputs['desired_curvature'][0, :]
    self.numpy_inputs[input_name_prev][:] = self.temporal_buffers[input_name_prev][0, self.temporal_idxs_map[input_name_prev]]
    if self.mlsim:
      self.numpy_inputs[input_name_prev][:] = 0*self.temporal_buffers[input_name_prev][0, self.temporal_idxs_map[input_name_prev]]

  def get_action_from_model(self, model_output: dict[str, np.ndarray], prev_action: log.ModelDataV2.Action,
                            lat_action_t: float, long_action_t: float, v_ego: float) -> log.ModelDataV2.Action:
    plan = model_output['plan'][0]
    desired_accel, should_stop = get_accel_from_plan(plan[:, Plan.VELOCITY][:, 0], plan[:, Plan.ACCELERATION][:, 0], self.constants.T_IDXS,
                                                     action_t=long_action_t)
    desired_accel = smooth_value(desired_accel, prev_action.desiredAcceleration, self.LONG_SMOOTH_SECONDS)

    desired_curvature = get_curvature_from_output(model_output, v_ego, lat_action_t, self.mlsim)
    if self.generation is not None and self.generation >= 10: # smooth curvature for post FOF models
      if v_ego > self.MIN_LAT_CONTROL_SPEED:
        desired_curvature = smooth_value(desired_curvature, prev_action.desiredCurvature, self.LAT_SMOOTH_SECONDS)
      else:
        desired_curvature = prev_action.desiredCurvature

    return log.ModelDataV2.Action(desiredCurvature=float(desired_curvature),desiredAcceleration=float(desired_accel), shouldStop=bool(should_stop))


def main(demo=False):
  cloudlog.warning("modeld init")

  sentry.set_tag("daemon", PROCESS_NAME)
  cloudlog.bind(daemon=PROCESS_NAME)
  setproctitle(PROCESS_NAME)
  config_realtime_process(7, 54)

  cloudlog.warning("setting up CL context")
  cl_context = CLContext()
  cloudlog.warning("CL context ready; loading model")
  model = ModelState(cl_context)
  cloudlog.warning("models loaded, modeld starting")

  # visionipc clients
  while True:
    available_streams = VisionIpcClient.available_streams("camerad", block=False)
    if available_streams:
      use_extra_client = VisionStreamType.VISION_STREAM_WIDE_ROAD in available_streams and VisionStreamType.VISION_STREAM_ROAD in available_streams
      main_wide_camera = VisionStreamType.VISION_STREAM_ROAD not in available_streams
      break
    time.sleep(.1)

  vipc_client_main_stream = VisionStreamType.VISION_STREAM_WIDE_ROAD if main_wide_camera else VisionStreamType.VISION_STREAM_ROAD
  vipc_client_main = VisionIpcClient("camerad", vipc_client_main_stream, True, cl_context)
  vipc_client_extra = VisionIpcClient("camerad", VisionStreamType.VISION_STREAM_WIDE_ROAD, False, cl_context)
  cloudlog.warning(f"vision stream set up, main_wide_camera: {main_wide_camera}, use_extra_client: {use_extra_client}")

  while not vipc_client_main.connect(False):
    time.sleep(0.1)
  while use_extra_client and not vipc_client_extra.connect(False):
    time.sleep(0.1)

  cloudlog.warning(f"connected main cam with buffer size: {vipc_client_main.buffer_len} ({vipc_client_main.width} x {vipc_client_main.height})")
  if use_extra_client:
    cloudlog.warning(f"connected extra cam with buffer size: {vipc_client_extra.buffer_len} ({vipc_client_extra.width} x {vipc_client_extra.height})")

  # messaging
  pm = PubMaster(["modelV2", "drivingModelData", "cameraOdometry", "modelDataV2SP"])
  sm = SubMaster(["deviceState", "carState", "roadCameraState", "liveCalibration", "driverMonitoringState", "carControl", "liveDelay"])

  publish_state = PublishState()
  params = Params()

  # setup filter to track dropped frames
  frame_dropped_filter = FirstOrderFilter(0., 10., 1. / model.constants.MODEL_FREQ)
  frame_id = 0
  last_vipc_frame_id = 0
  run_count = 0

  model_transform_main = np.zeros((3, 3), dtype=np.float32)
  model_transform_extra = np.zeros((3, 3), dtype=np.float32)
  live_calib_seen = False
  buf_main, buf_extra = None, None
  meta_main = FrameMeta()
  meta_extra = FrameMeta()


  if demo:
    CP = get_demo_car_params()
  else:
    CP = messaging.log_from_bytes(params.get("CarParams", block=True), car.CarParams)
  cloudlog.info("modeld got CarParams: %s", CP.brand)

  # TODO Move smooth seconds to action function
  long_delay = CP.longitudinalActuatorDelay + model.LONG_SMOOTH_SECONDS
  prev_action = log.ModelDataV2.Action()

  DH = DesireHelper()

  while True:
    # Keep receiving frames until we are at least 1 frame ahead of previous extra frame
    while meta_main.timestamp_sof < meta_extra.timestamp_sof + 25000000:
      buf_main = vipc_client_main.recv()
      meta_main = FrameMeta(vipc_client_main)
      if buf_main is None:
        break

    if buf_main is None:
      cloudlog.debug("vipc_client_main no frame")
      continue

    if use_extra_client:
      # Keep receiving extra frames until frame id matches main camera
      while True:
        buf_extra = vipc_client_extra.recv()
        meta_extra = FrameMeta(vipc_client_extra)
        if buf_extra is None or meta_main.timestamp_sof < meta_extra.timestamp_sof + 25000000:
          break

      if buf_extra is None:
        cloudlog.debug("vipc_client_extra no frame")
        continue

      if abs(meta_main.timestamp_sof - meta_extra.timestamp_sof) > 10000000:
        cloudlog.error(f"frames out of sync! main: {meta_main.frame_id} ({meta_main.timestamp_sof / 1e9:.5f}),\
                       extra: {meta_extra.frame_id} ({meta_extra.timestamp_sof / 1e9:.5f})")

    else:
      # Use single camera
      buf_extra = buf_main
      meta_extra = meta_main

    sm.update(0)
    desire = DH.desire
    is_rhd = sm["driverMonitoringState"].isRHD
    frame_id = sm["roadCameraState"].frameId
    v_ego = max(sm["carState"].vEgo, 0.)
    if sm.frame % 60 == 0:
      model.lat_delay = get_lat_delay(params, sm["liveDelay"].lateralDelay)
    lat_delay = model.lat_delay + model.LAT_SMOOTH_SECONDS
    if sm.updated["liveCalibration"] and sm.seen['roadCameraState'] and sm.seen['deviceState']:
      device_from_calib_euler = np.array(sm["liveCalibration"].rpyCalib, dtype=np.float32)
      dc = DEVICE_CAMERAS[(str(sm['deviceState'].deviceType), str(sm['roadCameraState'].sensor))]
      model_transform_main = get_warp_matrix(device_from_calib_euler, dc.ecam.intrinsics if main_wide_camera else dc.fcam.intrinsics,
                                             False).astype(np.float32)
      model_transform_extra = get_warp_matrix(device_from_calib_euler, dc.ecam.intrinsics, True).astype(np.float32)
      live_calib_seen = True

    traffic_convention = np.zeros(2)
    traffic_convention[int(is_rhd)] = 1

    vec_desire = np.zeros(model.constants.DESIRE_LEN, dtype=np.float32)
    if desire >= 0 and desire < model.constants.DESIRE_LEN:
      vec_desire[desire] = 1

    # tracked dropped frames
    vipc_dropped_frames = max(0, meta_main.frame_id - last_vipc_frame_id - 1)
    frames_dropped = frame_dropped_filter.update(min(vipc_dropped_frames, 10))
    if run_count < 10: # let frame drops warm up
      frame_dropped_filter.x = 0.
      frames_dropped = 0.
    run_count = run_count + 1

    frame_drop_ratio = frames_dropped / (1 + frames_dropped)
    prepare_only = vipc_dropped_frames > 0
    if prepare_only:
      cloudlog.error(f"skipping model eval. Dropped {vipc_dropped_frames} frames")

    bufs = {name: buf_extra if 'big' in name else buf_main for name in model.model_runner.vision_input_names}
    transforms = {name: model_transform_extra if 'big' in name else model_transform_main for name in model.model_runner.vision_input_names}
    inputs:dict[str, np.ndarray] = {
      model.desire_key: vec_desire,
      'traffic_convention': traffic_convention,
    }

    if "lateral_control_params" in model.numpy_inputs.keys():
      inputs['lateral_control_params'] = np.array([v_ego, lat_delay], dtype=np.float32)

    mt1 = time.perf_counter()
    model_output = model.run(bufs, transforms, inputs, prepare_only)
    mt2 = time.perf_counter()
    model_execution_time = mt2 - mt1

    if model_output is not None:
      modelv2_send = messaging.new_message('modelV2')
      drivingdata_send = messaging.new_message('drivingModelData')
      posenet_send = messaging.new_message('cameraOdometry')
      mdv2sp_send = messaging.new_message('modelDataV2SP')

      action = model.get_action_from_model(model_output, prev_action, lat_delay + DT_MDL, long_delay + DT_MDL, v_ego)
      prev_action = action
      fill_model_msg(drivingdata_send, modelv2_send, model_output, action,
                     publish_state, meta_main.frame_id, meta_extra.frame_id, frame_id,
                     frame_drop_ratio, meta_main.timestamp_eof, model_execution_time, live_calib_seen, load_meta_constants())

      desire_state = modelv2_send.modelV2.meta.desireState
      l_lane_change_prob = desire_state[log.Desire.laneChangeLeft]
      r_lane_change_prob = desire_state[log.Desire.laneChangeRight]
      lane_change_prob = l_lane_change_prob + r_lane_change_prob
      DH.update(sm['carState'], sm['carControl'].latActive, lane_change_prob)
      modelv2_send.modelV2.meta.laneChangeState = DH.lane_change_state
      modelv2_send.modelV2.meta.laneChangeDirection = DH.lane_change_direction
      mdv2sp_send.modelDataV2SP.laneTurnDirection = DH.lane_turn_direction
      drivingdata_send.drivingModelData.meta.laneChangeState = DH.lane_change_state
      drivingdata_send.drivingModelData.meta.laneChangeDirection = DH.lane_change_direction

      fill_pose_msg(posenet_send, model_output, meta_main.frame_id, vipc_dropped_frames, meta_main.timestamp_eof, live_calib_seen)
      pm.send('modelV2', modelv2_send)
      pm.send('drivingModelData', drivingdata_send)
      pm.send('cameraOdometry', posenet_send)
      pm.send('modelDataV2SP', mdv2sp_send)
    last_vipc_frame_id = meta_main.frame_id


if __name__ == "__main__":
  try:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--demo', action='store_true', help='A boolean for demo mode.')
    args = parser.parse_args()
    main(demo=args.demo)
  except KeyboardInterrupt:
    cloudlog.warning(f"child {PROCESS_NAME} got SIGINT")
  except Exception:
    sentry.capture_exception()
    raise
