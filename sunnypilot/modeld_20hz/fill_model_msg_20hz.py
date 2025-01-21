import os

import capnp
import numpy as np
from openpilot.selfdrive.modeld.constants import ModelConstants, Plan

from openpilot.selfdrive.controls.lib.drive_helpers import MIN_SPEED
from openpilot.selfdrive.modeld.fill_model_msg import ConfidenceClass, fill_xyzt, fill_lane_line_meta, fill_xyz_poly, fill_xyvat, PublishState

SEND_RAW_PRED = os.getenv('SEND_RAW_PRED')


class Meta20hz:
  ENGAGED = slice(0, 1)
  # next 2, 4, 6, 8, 10 seconds
  GAS_DISENGAGE = slice(1, 31, 6)
  BRAKE_DISENGAGE = slice(2, 31, 6)
  STEER_OVERRIDE = slice(3, 31, 6)
  HARD_BRAKE_3 = slice(4, 31, 6)
  HARD_BRAKE_4 = slice(5, 31, 6)
  HARD_BRAKE_5 = slice(6, 31, 6)
  # next 0, 2, 4, 6, 8, 10 seconds
  GAS_PRESS = slice(31, 55, 4)
  BRAKE_PRESS = slice(32, 55, 4)
  LEFT_BLINKER = slice(33, 55, 4)
  RIGHT_BLINKER = slice(34, 55, 4)

  def curv_from_psis(self, psi_target, psi_rate, vego, delay):
    vego = np.clip(vego, MIN_SPEED, np.inf)
    curv_from_psi = psi_target / (vego * delay)  # epsilon to prevent divide-by-zero
    return 2 * curv_from_psi - psi_rate / vego

  def get_curvature_from_plan(self, plan, vego, delay):
    psi_target = np.interp(delay, ModelConstants.T_IDXS, plan[:, Plan.T_FROM_CURRENT_EULER][:, 2])
    psi_rate = plan[:, Plan.ORIENTATION_RATE][0, 2]
    return self.curv_from_psis(psi_target, psi_rate, vego, delay)

  def fill_model_msg(self, base_msg: capnp._DynamicStructBuilder, extended_msg: capnp._DynamicStructBuilder,
                     net_output_data: dict[str, np.ndarray], v_ego: float, delay: float,
                     publish_state: PublishState, vipc_frame_id: int, vipc_frame_id_extra: int,
                     frame_id: int, frame_drop: float, timestamp_eof: int, model_execution_time: float,
                     valid: bool) -> None:
    frame_age = frame_id - vipc_frame_id if frame_id > vipc_frame_id else 0
    frame_drop_perc = frame_drop * 100
    extended_msg.valid = valid
    base_msg.valid = valid

    desired_curv = float(self.get_curvature_from_plan(net_output_data['plan'][0], v_ego, delay))

    driving_model_data = base_msg.drivingModelData

    driving_model_data.frameId = vipc_frame_id
    driving_model_data.frameIdExtra = vipc_frame_id_extra
    driving_model_data.frameDropPerc = frame_drop_perc
    driving_model_data.modelExecutionTime = model_execution_time

    action = driving_model_data.action
    action.desiredCurvature = desired_curv

    modelV2 = extended_msg.modelV2
    modelV2.frameId = vipc_frame_id
    modelV2.frameIdExtra = vipc_frame_id_extra
    modelV2.frameAge = frame_age
    modelV2.frameDropPerc = frame_drop_perc
    modelV2.timestampEof = timestamp_eof
    modelV2.modelExecutionTime = model_execution_time

    # plan
    position = modelV2.position
    fill_xyzt(position, ModelConstants.T_IDXS, *net_output_data['plan'][0, :, Plan.POSITION].T, *net_output_data['plan_stds'][0, :, Plan.POSITION].T)
    velocity = modelV2.velocity
    fill_xyzt(velocity, ModelConstants.T_IDXS, *net_output_data['plan'][0, :, Plan.VELOCITY].T)
    acceleration = modelV2.acceleration
    fill_xyzt(acceleration, ModelConstants.T_IDXS, *net_output_data['plan'][0, :, Plan.ACCELERATION].T)
    orientation = modelV2.orientation
    fill_xyzt(orientation, ModelConstants.T_IDXS, *net_output_data['plan'][0, :, Plan.T_FROM_CURRENT_EULER].T)
    orientation_rate = modelV2.orientationRate
    fill_xyzt(orientation_rate, ModelConstants.T_IDXS, *net_output_data['plan'][0, :, Plan.ORIENTATION_RATE].T)

    # temporal pose
    temporal_pose = modelV2.temporalPose
    temporal_pose.trans = net_output_data['plan'][0, 0, Plan.VELOCITY].tolist()
    temporal_pose.transStd = net_output_data['plan_stds'][0, 0, Plan.VELOCITY].tolist()
    temporal_pose.rot = net_output_data['plan'][0, 0, Plan.ORIENTATION_RATE].tolist()
    temporal_pose.rotStd = net_output_data['plan_stds'][0, 0, Plan.ORIENTATION_RATE].tolist()

    # poly path
    poly_path = driving_model_data.path
    fill_xyz_poly(poly_path, ModelConstants.POLY_PATH_DEGREE, *net_output_data['plan'][0, :, Plan.POSITION].T)

    # lateral planning
    action = modelV2.action
    action.desiredCurvature = desired_curv

    # times at X_IDXS according to model plan
    PLAN_T_IDXS = [np.nan] * ModelConstants.IDX_N
    PLAN_T_IDXS[0] = 0.0
    plan_x = net_output_data['plan'][0, :, Plan.POSITION][:, 0].tolist()
    for xidx in range(1, ModelConstants.IDX_N):
      tidx = 0
      # increment tidx until we find an element that's further away than the current xidx
      while tidx < ModelConstants.IDX_N - 1 and plan_x[tidx + 1] < ModelConstants.X_IDXS[xidx]:
        tidx += 1
      if tidx == ModelConstants.IDX_N - 1:
        # if the Plan doesn't extend far enough, set plan_t to the max value (10s), then break
        PLAN_T_IDXS[xidx] = ModelConstants.T_IDXS[ModelConstants.IDX_N - 1]
        break
      # interpolate to find `t` for the current xidx
      current_x_val = plan_x[tidx]
      next_x_val = plan_x[tidx + 1]
      p = (ModelConstants.X_IDXS[xidx] - current_x_val) / (next_x_val - current_x_val) if abs(next_x_val - current_x_val) > 1e-9 else float('nan')
      PLAN_T_IDXS[xidx] = p * ModelConstants.T_IDXS[tidx + 1] + (1 - p) * ModelConstants.T_IDXS[tidx]

    # lane lines
    modelV2.init('laneLines', 4)
    for i in range(4):
      lane_line = modelV2.laneLines[i]
      fill_xyzt(lane_line, PLAN_T_IDXS, np.array(ModelConstants.X_IDXS), net_output_data['lane_lines'][0, i, :, 0], net_output_data['lane_lines'][0, i, :, 1])
    modelV2.laneLineStds = net_output_data['lane_lines_stds'][0, :, 0, 0].tolist()
    modelV2.laneLineProbs = net_output_data['lane_lines_prob'][0, 1::2].tolist()

    lane_line_meta = driving_model_data.laneLineMeta
    fill_lane_line_meta(lane_line_meta, modelV2.laneLines, modelV2.laneLineProbs)

    # road edges
    modelV2.init('roadEdges', 2)
    for i in range(2):
      road_edge = modelV2.roadEdges[i]
      fill_xyzt(road_edge, PLAN_T_IDXS, np.array(ModelConstants.X_IDXS), net_output_data['road_edges'][0, i, :, 0], net_output_data['road_edges'][0, i, :, 1])
    modelV2.roadEdgeStds = net_output_data['road_edges_stds'][0, :, 0, 0].tolist()

    # leads
    modelV2.init('leadsV3', 3)
    for i in range(3):
      lead = modelV2.leadsV3[i]
      fill_xyvat(lead, ModelConstants.LEAD_T_IDXS, *net_output_data['lead'][0, i].T, *net_output_data['lead_stds'][0, i].T)
      lead.prob = net_output_data['lead_prob'][0, i].tolist()
      lead.probTime = ModelConstants.LEAD_T_OFFSETS[i]

    # meta
    meta = modelV2.meta
    meta.desireState = net_output_data['desire_state'][0].reshape(-1).tolist()
    meta.desirePrediction = net_output_data['desire_pred'][0].reshape(-1).tolist()
    meta.engagedProb = net_output_data['meta'][0, self.ENGAGED].item()
    meta.init('disengagePredictions')
    disengage_predictions = meta.disengagePredictions
    disengage_predictions.t = ModelConstants.META_T_IDXS
    disengage_predictions.brakeDisengageProbs = net_output_data['meta'][0, self.BRAKE_DISENGAGE].tolist()
    disengage_predictions.gasDisengageProbs = net_output_data['meta'][0, self.GAS_DISENGAGE].tolist()
    disengage_predictions.steerOverrideProbs = net_output_data['meta'][0, self.STEER_OVERRIDE].tolist()
    disengage_predictions.brake3MetersPerSecondSquaredProbs = net_output_data['meta'][0, self.HARD_BRAKE_3].tolist()
    disengage_predictions.brake4MetersPerSecondSquaredProbs = net_output_data['meta'][0, self.HARD_BRAKE_4].tolist()
    disengage_predictions.brake5MetersPerSecondSquaredProbs = net_output_data['meta'][0, self.HARD_BRAKE_5].tolist()
    disengage_predictions.gasPressProbs = net_output_data['meta'][0, self.GAS_PRESS].tolist()
    disengage_predictions.brakePressProbs = net_output_data['meta'][0, self.BRAKE_PRESS].tolist()

    publish_state.prev_brake_5ms2_probs[:-1] = publish_state.prev_brake_5ms2_probs[1:]
    publish_state.prev_brake_5ms2_probs[-1] = net_output_data['meta'][0, self.HARD_BRAKE_5][0]
    publish_state.prev_brake_3ms2_probs[:-1] = publish_state.prev_brake_3ms2_probs[1:]
    publish_state.prev_brake_3ms2_probs[-1] = net_output_data['meta'][0, self.HARD_BRAKE_3][0]
    hard_brake_predicted = (publish_state.prev_brake_5ms2_probs > ModelConstants.FCW_THRESHOLDS_5MS2).all() and \
                           (publish_state.prev_brake_3ms2_probs > ModelConstants.FCW_THRESHOLDS_3MS2).all()
    meta.hardBrakePredicted = hard_brake_predicted.item()

    # confidence
    if vipc_frame_id % (2 * ModelConstants.MODEL_FREQ) == 0:
      # any disengage prob
      brake_disengage_probs = net_output_data['meta'][0, self.BRAKE_DISENGAGE]
      gas_disengage_probs = net_output_data['meta'][0, self.GAS_DISENGAGE]
      steer_override_probs = net_output_data['meta'][0, self.STEER_OVERRIDE]
      any_disengage_probs = 1 - ((1 - brake_disengage_probs) * (1 - gas_disengage_probs) * (1 - steer_override_probs))
      # independent disengage prob for each 2s slice
      ind_disengage_probs = np.r_[any_disengage_probs[0], np.diff(any_disengage_probs) / (1 - any_disengage_probs[:-1])]
      # rolling buf for 2, 4, 6, 8, 10s
      publish_state.disengage_buffer[:-ModelConstants.DISENGAGE_WIDTH] = publish_state.disengage_buffer[ModelConstants.DISENGAGE_WIDTH:]
      publish_state.disengage_buffer[-ModelConstants.DISENGAGE_WIDTH:] = ind_disengage_probs

    score = 0.
    for i in range(ModelConstants.DISENGAGE_WIDTH):
      score += publish_state.disengage_buffer[
                 i * ModelConstants.DISENGAGE_WIDTH + ModelConstants.DISENGAGE_WIDTH - 1 - i].item() / ModelConstants.DISENGAGE_WIDTH
    if score < ModelConstants.RYG_GREEN:
      modelV2.confidence = ConfidenceClass.green
    elif score < ModelConstants.RYG_YELLOW:
      modelV2.confidence = ConfidenceClass.yellow
    else:
      modelV2.confidence = ConfidenceClass.red

    # raw prediction if enabled
    if SEND_RAW_PRED:
      modelV2.rawPredictions = net_output_data['raw_pred'].tobytes()
