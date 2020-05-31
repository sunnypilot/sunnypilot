import numpy as np
from common.realtime import sec_since_boot, DT_MDL
from common.numpy_fast import interp
from selfdrive.swaglog import cloudlog
from selfdrive.controls.lib.lateral_mpc_lib.lat_mpc import LateralMpc
from selfdrive.controls.lib.drive_helpers import CONTROL_N, MPC_COST_LAT, LAT_MPC_N, CAR_ROTATION_RADIUS
from selfdrive.controls.lib.lane_planner import LanePlanner, TRAJECTORY_SIZE
from selfdrive.controls.lib.desire_helper import DesireHelper
import cereal.messaging as messaging
from cereal import log
from common.params import Params

LaneChangeState = log.LateralPlan.LaneChangeState


class LateralPlanner:
  def __init__(self, CP, use_lanelines=True, wide_camera=False):
    self.use_lanelines = use_lanelines
    self.LP = LanePlanner(wide_camera)
    self.DH = DesireHelper()

    self.last_cloudlog_t = 0
    self.steer_rate_cost = CP.steerRateCost
    self.solution_invalid_cnt = 0

    self.path_xyz = np.zeros((TRAJECTORY_SIZE, 3))
    self.path_xyz_stds = np.ones((TRAJECTORY_SIZE, 3))
    self.plan_yaw = np.zeros((TRAJECTORY_SIZE,))
    self.t_idxs = np.arange(TRAJECTORY_SIZE)
    self.y_pts = np.zeros(TRAJECTORY_SIZE)
    self.d_path_w_lines_xyz = np.zeros((TRAJECTORY_SIZE, 3))

    self.lat_mpc = LateralMpc()
    self.reset_mpc(np.zeros(4))

    self.dynamic_lane_profile = int(Params().get("DynamicLaneProfile", encoding="utf8"))
    self.dynamic_lane_profile_status = False
    self.dynamic_lane_profile_status_buffer = False
    self.second = 0.0
    self.standstill_elapsed = 0.0
    self.stand_still = False

  def reset_mpc(self, x0=np.zeros(4)):
    self.x0 = x0
    self.lat_mpc.reset(x0=self.x0)

  def update(self, sm):
    self.second += DT_MDL
    if self.second > 1.0:
      self.use_lanelines = not Params().get_bool("EndToEndToggle")
      self.dynamic_lane_profile = int(Params().get("DynamicLaneProfile", encoding="utf8"))
      self.second = 0.0
    self.stand_still = sm['carState'].standStill
    v_ego = sm['carState'].vEgo
    measured_curvature = sm['controlsState'].curvature

    # Parse model predictions
    md = sm['modelV2']
    self.LP.parse_model(md)
    if len(md.position.x) == TRAJECTORY_SIZE and len(md.orientation.x) == TRAJECTORY_SIZE:
      self.path_xyz = np.column_stack([md.position.x, md.position.y, md.position.z])
      self.t_idxs = np.array(md.position.t)
      self.plan_yaw = list(md.orientation.z)
    if len(md.position.xStd) == TRAJECTORY_SIZE:
      self.path_xyz_stds = np.column_stack([md.position.xStd, md.position.yStd, md.position.zStd])

    # Lane change logic
    lane_change_prob = self.LP.l_lane_change_prob + self.LP.r_lane_change_prob
    self.DH.update(sm['carState'], sm['controlsState'].active, lane_change_prob)

    # Turn off lanes during lane change
    if self.DH.desire == log.LateralPlan.Desire.laneChangeRight or self.DH.desire == log.LateralPlan.Desire.laneChangeLeft:
      self.LP.lll_prob *= self.DH.lane_change_ll_prob
      self.LP.rll_prob *= self.DH.lane_change_ll_prob
    self.d_path_w_lines_xyz = self.LP.get_d_path(v_ego, self.t_idxs, self.path_xyz)

    # Calculate final driving path and set MPC costs
    if not self.get_dynamic_lane_profile(sm):
      d_path_xyz = self.d_path_w_lines_xyz
      self.lat_mpc.set_weights(MPC_COST_LAT.PATH, MPC_COST_LAT.HEADING, self.steer_rate_cost)
      self.dynamic_lane_profile_status = False
    else:
      d_path_xyz = self.path_xyz
      path_cost = np.clip(abs(self.path_xyz[0, 1] / self.path_xyz_stds[0, 1]), 0.5, 1.5) * MPC_COST_LAT.PATH
      # Heading cost is useful at low speed, otherwise end of plan can be off-heading
      heading_cost = interp(v_ego, [5.0, 10.0], [MPC_COST_LAT.HEADING, 0.0])
      self.lat_mpc.set_weights(path_cost, heading_cost, self.steer_rate_cost)
      self.dynamic_lane_profile_status = True

    y_pts = np.interp(v_ego * self.t_idxs[:LAT_MPC_N + 1], np.linalg.norm(d_path_xyz, axis=1), d_path_xyz[:, 1])
    heading_pts = np.interp(v_ego * self.t_idxs[:LAT_MPC_N + 1], np.linalg.norm(self.path_xyz, axis=1), self.plan_yaw)
    self.y_pts = y_pts

    assert len(y_pts) == LAT_MPC_N + 1
    assert len(heading_pts) == LAT_MPC_N + 1
    # self.x0[4] = v_ego
    p = np.array([v_ego, CAR_ROTATION_RADIUS])
    self.lat_mpc.run(self.x0,
                     p,
                     y_pts,
                     heading_pts)
    # init state for next
    # mpc.u_sol is the desired curvature rate given x0 curv state.
    # with x0[3] = measured_curvature, this would be the actual desired rate.
    # instead, interpolate x_sol so that x0[3] is the desired curvature for lat_control.
    self.x0[3] = interp(DT_MDL, self.t_idxs[:LAT_MPC_N + 1], self.lat_mpc.x_sol[:, 3])

    #  Check for infeasible MPC solution
    mpc_nans = np.isnan(self.lat_mpc.x_sol[:, 3]).any()
    t = sec_since_boot()
    if mpc_nans or self.lat_mpc.solution_status != 0:
      self.reset_mpc()
      self.x0[3] = measured_curvature
      if t > self.last_cloudlog_t + 5.0:
        self.last_cloudlog_t = t
        cloudlog.warning("Lateral mpc - nan: True")

    if self.lat_mpc.cost > 20000. or mpc_nans:
      self.solution_invalid_cnt += 1
    else:
      self.solution_invalid_cnt = 0

  def get_dynamic_lane_profile(self, sm):
    longitudinal_plan = sm['longitudinalPlan']
    if self.dynamic_lane_profile == 1:
      return True
    if self.dynamic_lane_profile == 0:
      return False
    elif self.dynamic_lane_profile == 2:
      # only while lane change is off
      if self.DH.lane_change_state == LaneChangeState.off:
        # laneline probability too low, we switch to laneless mode
        if (self.LP.lll_prob + self.LP.rll_prob)/2 < 0.3 \
          or longitudinal_plan.visionCurrentLatAcc > 1.0 or longitudinal_plan.visionMaxPredLatAcc > 1.4:
          self.dynamic_lane_profile_status_buffer = True
        if (self.LP.lll_prob + self.LP.rll_prob)/2 > 0.5 \
          and longitudinal_plan.visionCurrentLatAcc < 0.6 and longitudinal_plan.visionMaxPredLatAcc < 0.7:
          self.dynamic_lane_profile_status_buffer = False
        if self.dynamic_lane_profile_status_buffer: # in buffer mode, always laneless
          return True
    return False

  def publish(self, sm, pm):
    plan_solution_valid = self.solution_invalid_cnt < 2
    plan_send = messaging.new_message('lateralPlan')
    plan_send.valid = sm.all_checks(service_list=['carState', 'controlsState', 'modelV2'])

    lateralPlan = plan_send.lateralPlan
    lateralPlan.modelMonoTime = sm.logMonoTime['modelV2']
    lateralPlan.laneWidth = float(self.LP.lane_width)
    lateralPlan.dPathPoints = self.y_pts.tolist()
    lateralPlan.psis = self.lat_mpc.x_sol[0:CONTROL_N, 2].tolist()
    lateralPlan.curvatures = self.lat_mpc.x_sol[0:CONTROL_N, 3].tolist()
    lateralPlan.curvatureRates = [float(x) for x in self.lat_mpc.u_sol[0:CONTROL_N - 1]] + [0.0]
    lateralPlan.lProb = float(self.LP.lll_prob)
    lateralPlan.rProb = float(self.LP.rll_prob)
    lateralPlan.dProb = float(self.LP.d_prob)

    lateralPlan.mpcSolutionValid = bool(plan_solution_valid)
    lateralPlan.solverExecutionTime = self.lat_mpc.solve_time

    lateralPlan.desire = self.DH.desire
    lateralPlan.useLaneLines = self.use_lanelines
    lateralPlan.laneChangeState = self.DH.lane_change_state
    lateralPlan.laneChangeDirection = self.DH.lane_change_direction

    plan_send.lateralPlan.dynamicLaneProfile = bool(self.dynamic_lane_profile_status)

    if self.stand_still:
      self.standstill_elapsed += DT_MDL
    else:
      self.standstill_elapsed = 0.0
    plan_send.lateralPlan.standstillElapsed = int(self.standstill_elapsed)

    plan_send.lateralPlan.dPathWLinesX = [float(x) for x in self.d_path_w_lines_xyz[:, 0]]
    plan_send.lateralPlan.dPathWLinesY = [float(y) for y in self.d_path_w_lines_xyz[:, 1]]

    pm.send('lateralPlan', plan_send)
