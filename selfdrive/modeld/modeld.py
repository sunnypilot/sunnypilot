#!/usr/bin/env python3
import os
import time
import pickle
import numpy as np
import cereal.messaging as messaging
from cereal import car, log
from pathlib import Path
from openpilot.common.threadname import setthreadname
from cereal.messaging import PubMaster, SubMaster
from msgq.visionipc import VisionIpcClient, VisionStreamType, VisionBuf
from openpilot.common.swaglog import cloudlog
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.common.numpy_fast import interp
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.realtime import config_realtime_process
from openpilot.common.transformations.camera import DEVICE_CAMERAS
from openpilot.common.transformations.model import get_warp_matrix
from openpilot.system import sentry
from openpilot.selfdrive.car.car_helpers import get_demo_car_params
from openpilot.selfdrive.controls.lib.desire_helper import DesireHelper
from openpilot.selfdrive.modeld.model_capabilities import ModelCapabilities
from openpilot.selfdrive.modeld.runners import ModelRunner, Runtime
from openpilot.selfdrive.modeld.parse_model_outputs import Parser
from openpilot.selfdrive.modeld.fill_model_msg import fill_model_msg, fill_pose_msg, PublishState
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.selfdrive.modeld.models.commonmodel_pyx import ModelFrame, CLContext
from openpilot.selfdrive.sunnypilot import get_model_generation
from openpilot.system.hardware.hw import Paths

THREAD_NAME = "selfdrive.modeld.modeld"
SEND_RAW_PRED = os.getenv('SEND_RAW_PRED')

MODEL_PATHS = {
  ModelRunner.THNEED: Path(__file__).parent / 'models/supercombo.thneed',
  ModelRunner.ONNX: Path(__file__).parent / 'models/supercombo.onnx'}

METADATA_PATH = Path(__file__).parent / 'models/supercombo_metadata.pkl'

CUSTOM_MODEL_PATH = Paths.model_root()

LaneChangeState = log.LaneChangeState


class FrameMeta:
  frame_id: int = 0
  timestamp_sof: int = 0
  timestamp_eof: int = 0

  def __init__(self, vipc=None):
    if vipc is not None:
      self.frame_id, self.timestamp_sof, self.timestamp_eof = vipc.frame_id, vipc.timestamp_sof, vipc.timestamp_eof

class ModelState:
  frame: ModelFrame
  wide_frame: ModelFrame
  inputs: dict[str, np.ndarray]
  output: np.ndarray
  prev_desire: np.ndarray  # for tracking the rising edge of the pulse
  model: ModelRunner

  def __init__(self, context: CLContext):
    self.param_s = Params()
    self.custom_model, self.model_gen = get_model_generation(self.param_s)
    self.model_capabilities = ModelCapabilities.get_by_gen(self.model_gen)
    self.frame = ModelFrame(context)
    self.wide_frame = ModelFrame(context)
    self.prev_desire = np.zeros(ModelConstants.DESIRE_LEN, dtype=np.float32)
    # Default model, and as of time of writing, this model uses DesiredCurvatureV2
    _inputs = {
      'lateral_control_params': np.zeros(ModelConstants.LATERAL_CONTROL_PARAMS_LEN, dtype=np.float32),
      'prev_desired_curv': np.zeros(ModelConstants.PREV_DESIRED_CURV_LEN * (ModelConstants.HISTORY_BUFFER_LEN+1), dtype=np.float32),
    }
    _inputs_2 = {}
    if self.custom_model and self.model_capabilities != ModelCapabilities.Default:
      if self.model_capabilities & ModelCapabilities.LateralPlannerSolution:
        _inputs = {
          'lat_planner_state': np.zeros(ModelConstants.LAT_PLANNER_STATE_LEN, dtype=np.float32),
        }
      if self.model_capabilities & ModelCapabilities.DesiredCurvatureV1:
        _inputs = {
          'lateral_control_params': np.zeros(ModelConstants.LATERAL_CONTROL_PARAMS_LEN, dtype=np.float32),
          'prev_desired_curvs': np.zeros(ModelConstants.PREV_DESIRED_CURVS_LEN, dtype=np.float32),
        }
      if self.model_capabilities & ModelCapabilities.NoO:
        _inputs_2 = {
          'nav_features': np.zeros(ModelConstants.NAV_FEATURE_LEN, dtype=np.float32),
          'nav_instructions': np.zeros(ModelConstants.NAV_INSTRUCTION_LEN, dtype=np.float32),
        }

    self.inputs = {
      'desire': np.zeros(ModelConstants.DESIRE_LEN * (ModelConstants.HISTORY_BUFFER_LEN+1), dtype=np.float32),
      'traffic_convention': np.zeros(ModelConstants.TRAFFIC_CONVENTION_LEN, dtype=np.float32),
      **_inputs,
      **_inputs_2,
      'features_buffer': np.zeros(ModelConstants.HISTORY_BUFFER_LEN * ModelConstants.FEATURE_LEN, dtype=np.float32),
    }

    if self.custom_model and self.model_capabilities != ModelCapabilities.Default:
      _model_name = self.param_s.get("DrivingModelText", encoding="utf8")
      _model_paths = {ModelRunner.THNEED: f"{CUSTOM_MODEL_PATH}/supercombo-{_model_name}.thneed"}
      _metadata_name = self.param_s.get("DrivingModelMetadataText", encoding="utf8")
      _metadata_path = f"{CUSTOM_MODEL_PATH}/supercombo_metadata_{_metadata_name}.pkl" if _model_name else METADATA_PATH
    else:
      _model_paths = MODEL_PATHS
      _metadata_path = METADATA_PATH

    with open(_metadata_path, 'rb') as f:
      model_metadata = pickle.load(f)

    self.output_slices = model_metadata['output_slices']
    net_output_size = model_metadata['output_shapes']['outputs'][1]
    self.output = np.zeros(net_output_size, dtype=np.float32)
    self.parser = Parser()

    self.model = ModelRunner(_model_paths, self.output, Runtime.GPU, False, context)
    self.model.addInput("input_imgs", None)
    self.model.addInput("big_input_imgs", None)
    for k,v in self.inputs.items():
      self.model.addInput(k, v)

  def slice_outputs(self, model_outputs: np.ndarray) -> dict[str, np.ndarray]:
    parsed_model_outputs = {k: model_outputs[np.newaxis, v] for k,v in self.output_slices.items()}
    if SEND_RAW_PRED:
      parsed_model_outputs['raw_pred'] = model_outputs.copy()
    return parsed_model_outputs

  def run(self, buf: VisionBuf, wbuf: VisionBuf, transform: np.ndarray, transform_wide: np.ndarray,
                inputs: dict[str, np.ndarray], prepare_only: bool) -> dict[str, np.ndarray] | None:
    # Model decides when action is completed, so desire input is just a pulse triggered on rising edge
    inputs['desire'][0] = 0
    self.inputs['desire'][:-ModelConstants.DESIRE_LEN] = self.inputs['desire'][ModelConstants.DESIRE_LEN:]
    self.inputs['desire'][-ModelConstants.DESIRE_LEN:] = np.where(inputs['desire'] - self.prev_desire > .99, inputs['desire'], 0)
    self.prev_desire[:] = inputs['desire']

    self.inputs['traffic_convention'][:] = inputs['traffic_convention']
    if not (self.custom_model and self.model_capabilities & ModelCapabilities.LateralPlannerSolution):
      self.inputs['lateral_control_params'][:] = inputs['lateral_control_params']
    if self.custom_model and self.model_capabilities & ModelCapabilities.NoO:
      self.inputs['nav_features'][:] = inputs['nav_features']
      self.inputs['nav_instructions'][:] = inputs['nav_instructions']

    # if getCLBuffer is not None, frame will be None
    self.model.setInputBuffer("input_imgs", self.frame.prepare(buf, transform.flatten(), self.model.getCLBuffer("input_imgs")))
    if wbuf is not None:
      self.model.setInputBuffer("big_input_imgs", self.wide_frame.prepare(wbuf, transform_wide.flatten(), self.model.getCLBuffer("big_input_imgs")))

    if prepare_only:
      return None

    self.model.execute()
    outputs = self.parser.parse_outputs(self.slice_outputs(self.output))

    self.inputs['features_buffer'][:-ModelConstants.FEATURE_LEN] = self.inputs['features_buffer'][ModelConstants.FEATURE_LEN:]
    self.inputs['features_buffer'][-ModelConstants.FEATURE_LEN:] = outputs['hidden_state'][0, :]
    if self.custom_model and self.model_capabilities != ModelCapabilities.Default:
      if self.model_capabilities & ModelCapabilities.LateralPlannerSolution:
        self.inputs['lat_planner_state'][2] = interp(DT_MDL, ModelConstants.T_IDXS, outputs['lat_planner_solution'][0, :, 2])
        self.inputs['lat_planner_state'][3] = interp(DT_MDL, ModelConstants.T_IDXS, outputs['lat_planner_solution'][0, :, 3])
      elif self.model_capabilities & ModelCapabilities.DesiredCurvatureV1:
        self.inputs['prev_desired_curvs'][:-1] = self.inputs['prev_desired_curvs'][1:]
        self.inputs['prev_desired_curvs'][-1] = outputs['desired_curvature'][0, 0]
    else:  # Default model, and as of time of writing, this model uses DesiredCurvatureV2
      self.inputs['prev_desired_curv'][:-ModelConstants.PREV_DESIRED_CURV_LEN] = self.inputs['prev_desired_curv'][ModelConstants.PREV_DESIRED_CURV_LEN:]
      self.inputs['prev_desired_curv'][-ModelConstants.PREV_DESIRED_CURV_LEN:] = outputs['desired_curvature'][0, :]
    return outputs


def main(demo=False):
  cloudlog.warning("modeld init")

  sentry.set_tag("daemon", THREAD_NAME)
  cloudlog.bind(daemon=THREAD_NAME)
  setthreadname("modeld")
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

  params = Params()
  custom_model, model_gen = get_model_generation(params)
  model_capabilities = ModelCapabilities.get_by_gen(model_gen)

  # messaging
  extended_svs = ["lateralPlanDEPRECATED", "lateralPlanSPDEPRECATED"]
  if custom_model and model_capabilities & ModelCapabilities.NoO:
    extended_svs += ["navModelDEPRECATED", "navInstruction"]
  pm = PubMaster(["modelV2", "modelV2SP", "cameraOdometry"])
  sm = SubMaster(["deviceState", "carState", "roadCameraState", "liveCalibration", "driverMonitoringState", "carControl"] + extended_svs)

  publish_state = PublishState()

  # setup filter to track dropped frames
  frame_dropped_filter = FirstOrderFilter(0., 10., 1. / ModelConstants.MODEL_FREQ)
  frame_id = 0
  last_vipc_frame_id = 0
  run_count = 0

  model_transform_main = np.zeros((3, 3), dtype=np.float32)
  model_transform_extra = np.zeros((3, 3), dtype=np.float32)
  live_calib_seen = False
  if custom_model and model_capabilities & ModelCapabilities.LateralPlannerSolution:
    driving_style = np.array([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0], dtype=np.float32)
  if custom_model and model_capabilities & ModelCapabilities.NoO:
    nav_features = np.zeros(ModelConstants.NAV_FEATURE_LEN, dtype=np.float32)
    nav_instructions = np.zeros(ModelConstants.NAV_INSTRUCTION_LEN, dtype=np.float32)
  buf_main, buf_extra = None, None
  meta_main = FrameMeta()
  meta_extra = FrameMeta()


  if demo:
    CP = get_demo_car_params()
  else:
    with car.CarParams.from_bytes(params.get("CarParams", block=True)) as msg:
      CP = msg
  cloudlog.info("modeld got CarParams: %s", CP.carName)

  # TODO this needs more thought, use .2s extra for now to estimate other delays
  steer_delay = CP.steerActuatorDelay + .2

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
    desire = sm["lateralPlanDEPRECATED"].desire.raw if custom_model and model_capabilities & ModelCapabilities.LateralPlannerSolution else DH.desire
    is_rhd = sm["driverMonitoringState"].isRHD
    frame_id = sm["roadCameraState"].frameId
    if not (custom_model and model_capabilities & ModelCapabilities.LateralPlannerSolution):
      lateral_control_params = np.array([sm["carState"].vEgo, steer_delay], dtype=np.float32)
    if sm.updated["liveCalibration"] and sm.seen['roadCameraState'] and sm.seen['deviceState']:
      device_from_calib_euler = np.array(sm["liveCalibration"].rpyCalib, dtype=np.float32)
      dc = DEVICE_CAMERAS[(str(sm['deviceState'].deviceType), str(sm['roadCameraState'].sensor))]
      model_transform_main = get_warp_matrix(device_from_calib_euler, dc.ecam.intrinsics if main_wide_camera else dc.fcam.intrinsics, False).astype(np.float32)
      model_transform_extra = get_warp_matrix(device_from_calib_euler, dc.ecam.intrinsics, True).astype(np.float32)
      live_calib_seen = True

    traffic_convention = np.zeros(2)
    traffic_convention[int(is_rhd)] = 1

    vec_desire = np.zeros(ModelConstants.DESIRE_LEN, dtype=np.float32)
    if desire >= 0 and desire < ModelConstants.DESIRE_LEN:
      vec_desire[desire] = 1

    timestamp_llk = 0
    nav_enabled = False
    if custom_model and model_capabilities & ModelCapabilities.NoO:
      # Enable/disable nav features
      timestamp_llk = sm["navModelDEPRECATED"].locationMonoTime
      nav_valid = sm.valid["navModelDEPRECATED"] # and (nanos_since_boot() - timestamp_llk < 1e9)
      nav_enabled = nav_valid

      if not nav_enabled:
        nav_features[:] = 0
        nav_instructions[:] = 0

      if nav_enabled and sm.updated["navModelDEPRECATED"]:
        nav_features = np.array(sm["navModelDEPRECATED"].features)

      if nav_enabled and sm.updated["navInstruction"]:
        nav_instructions[:] = 0
        for maneuver in sm["navInstruction"].allManeuvers:
          distance_idx = 25 + int(maneuver.distance / 20)
          direction_idx = 0
          if maneuver.modifier in ("left", "slight left", "sharp left"):
            direction_idx = 1
          if maneuver.modifier in ("right", "slight right", "sharp right"):
            direction_idx = 2
          if 0 <= distance_idx < 50:
            nav_instructions[distance_idx*3 + direction_idx] = 1

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

    if custom_model and model_capabilities & ModelCapabilities.LateralPlannerSolution:
      _inputs = {
        'driving_style': driving_style
      }
    else:
      _inputs = {
        'lateral_control_params': lateral_control_params
      }
    if custom_model and model_capabilities & ModelCapabilities.NoO:
      _inputs_2 = {
        'nav_features': nav_features,
        'nav_instructions': nav_instructions
      }
    else:
      _inputs_2 = {}

    inputs:dict[str, np.ndarray] = {
      'desire': vec_desire,
      'traffic_convention': traffic_convention,
      **_inputs,
      **_inputs_2,
      }

    mt1 = time.perf_counter()
    model_output = model.run(buf_main, buf_extra, model_transform_main, model_transform_extra, inputs, prepare_only)
    mt2 = time.perf_counter()
    model_execution_time = mt2 - mt1

    lat_plan_sp = sm['lateralPlanSPDEPRECATED']

    if model_output is not None:
      modelv2_send = messaging.new_message('modelV2')
      posenet_send = messaging.new_message('cameraOdometry')
      fill_model_msg(modelv2_send, model_output, publish_state, meta_main.frame_id, meta_extra.frame_id, frame_id, frame_drop_ratio,
                      meta_main.timestamp_eof, timestamp_llk, model_execution_time, nav_enabled, live_calib_seen,
                      custom_model and model_capabilities & ModelCapabilities.LateralPlannerSolution, custom_model and model_capabilities & ModelCapabilities.NoO)

      if not (custom_model and model_capabilities & ModelCapabilities.LateralPlannerSolution):
        desire_state = modelv2_send.modelV2.meta.desireState
        l_lane_change_prob = desire_state[log.Desire.laneChangeLeft]
        r_lane_change_prob = desire_state[log.Desire.laneChangeRight]
        lane_change_prob = l_lane_change_prob + r_lane_change_prob
        DH.update(sm['carState'], sm['carControl'].latActive, lane_change_prob, lat_plan_sp=lat_plan_sp)
        modelv2_send.modelV2.meta.laneChangeState = DH.lane_change_state
        modelv2_send.modelV2.meta.laneChangeDirection = DH.lane_change_direction

      fill_pose_msg(posenet_send, model_output, meta_main.frame_id, vipc_dropped_frames, meta_main.timestamp_eof, live_calib_seen)
      pm.send('modelV2', modelv2_send)
      pm.send('cameraOdometry', posenet_send)

      modelv2_sp_send = messaging.new_message('modelV2SP')
      modelv2_sp_send.valid = True
      if not (custom_model and model_capabilities & ModelCapabilities.LateralPlannerSolution):
        modelv2_sp_send.modelV2SP.laneChangePrev = DH.prev_lane_change
        modelv2_sp_send.modelV2SP.laneChangeEdgeBlock = lat_plan_sp.laneChangeEdgeBlockDEPRECATED
      pm.send('modelV2SP', modelv2_sp_send)

    last_vipc_frame_id = meta_main.frame_id


if __name__ == "__main__":
  try:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--demo', action='store_true', help='A boolean for demo mode.')
    args = parser.parse_args()
    main(demo=args.demo)
  except KeyboardInterrupt:
    cloudlog.warning(f"child {THREAD_NAME} got SIGINT")
  except Exception:
    sentry.capture_exception()
    raise
