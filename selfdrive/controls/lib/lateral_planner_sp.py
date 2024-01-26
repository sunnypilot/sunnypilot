import numpy as np
from openpilot.selfdrive.controls.lib.desire_helper import DesireHelper
import cereal.messaging as messaging
from cereal import log

TRAJECTORY_SIZE = 33
CAMERA_OFFSET = 0.04

class LateralPlannerSP:
  """Library is a stop-gap solution until we do a better assesment 
  whether we need or not this info published this way.
  MR269."""
  
  def __init__(self):
    self.DH = DesireHelper()
    self.l_lane_change_prob = 0.0
    self.r_lane_change_prob = 0.0
    self.d_path_w_lines_xyz = np.zeros((TRAJECTORY_SIZE, 3))

  def update(self, sm):
    md = sm['modelV2']

    # Lane change logic
    desire_state = md.meta.desireState
    if len(desire_state):
      self.l_lane_change_prob = desire_state[log.LateralPlan.Desire.laneChangeLeft]
      self.r_lane_change_prob = desire_state[log.LateralPlan.Desire.laneChangeRight]
    lane_change_prob = self.l_lane_change_prob + self.r_lane_change_prob
    self.DH.update(sm['carState'], sm['carControl'].latActive, lane_change_prob)

  def publish(self, sm, pm):
    plan_sp_send = messaging.new_message('lateralPlanSPDEPRECATED')
    plan_sp_send.valid = sm.all_checks(service_list=['carState', 'controlsState', 'modelV2'])

    lateralPlanSPDEPRECATED = plan_sp_send.lateralPlanSPDEPRECATED
    lateralPlanSPDEPRECATED.laneChangePrev = self.DH.prev_lane_change

    lateralPlanSPDEPRECATED.dPathWLinesX = [float(x) for x in self.d_path_w_lines_xyz[:, 0]]
    lateralPlanSPDEPRECATED.dPathWLinesY = [float(y) for y in self.d_path_w_lines_xyz[:, 1]]

    pm.send('lateralPlanSPDEPRECATED', plan_sp_send)
