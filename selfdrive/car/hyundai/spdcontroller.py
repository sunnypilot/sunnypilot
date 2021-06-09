#this was initiated by atom(conan)
#partially modified by opkr
import math
import numpy as np

from cereal import log
import cereal.messaging as messaging

from selfdrive.config import Conversions as CV
from selfdrive.controls.lib.speed_smoother import speed_smoother
from selfdrive.controls.lib.long_mpc import LongitudinalMpc
from selfdrive.controls.lib.lane_planner import TRAJECTORY_SIZE
from selfdrive.car.hyundai.values import Buttons
from common.numpy_fast import clip, interp
from common.params import Params

from selfdrive.config import RADAR_TO_CAMERA

import common.log as trace1
import common.CTime1000 as tm
import common.MoveAvg as moveavg1


MAX_SPEED = 255.0
MIN_CURVE_SPEED = 30.

LON_MPC_STEP = 0.2  # first step is 0.2s
MAX_SPEED_ERROR = 2.0
AWARENESS_DECEL = -0.2     # car smoothly decel at .2m/s^2 when user is distracted

# lookup tables VS speed to determine min and max accels in cruise
# make sure these accelerations are smaller than mpc limits
_A_CRUISE_MIN_V = [-1.0, -.8, -.67, -.5, -.30]
_A_CRUISE_MIN_BP = [0., 5.,  10., 20.,  40.]

# need fast accel at very low speed for stop and go
# make sure these accelerations are smaller than mpc limits
_A_CRUISE_MAX_V = [1.2, 1.2, 0.65, .4]
_A_CRUISE_MAX_V_FOLLOWING = [1.6, 1.6, 0.65, .4]
_A_CRUISE_MAX_BP = [0.,  6.4, 22.5, 40.]

# Lookup table for turns
_A_TOTAL_MAX_V = [1.7, 3.2]
_A_TOTAL_MAX_BP = [20., 40.]

# 75th percentile
SPEED_PERCENTILE_IDX = 7

def limit_accel_in_turns(v_ego, angle_steers, a_target, steerRatio, wheelbase):
    """
    This function returns a limited long acceleration allowed, depending on the existing lateral acceleration
    this should avoid accelerating when losing the target in turns
    """

    a_total_max = interp(v_ego, _A_TOTAL_MAX_BP, _A_TOTAL_MAX_V)
    a_y = v_ego**2 * angle_steers * CV.DEG_TO_RAD / (steerRatio * wheelbase)
    a_x_allowed = math.sqrt(max(a_total_max**2 - a_y**2, 0.))

    return [a_target[0], min(a_target[1], a_x_allowed)]


class SpdController():
    def __init__(self, CP=None):
        self.long_control_state = 0  # initialized to off

        self.seq_step_debug = ""
        self.long_curv_timer = 0

        self.path_x = np.arange(192)

        self.traceSC = trace1.Loger("SPD_CTRL")

        self.v_model = 0
        self.a_model = 0
        self.v_cruise = 0
        self.a_cruise = 0

        self.l_poly = []
        self.r_poly = []

        self.movAvg = moveavg1.MoveAvg()
        self.Timer1 = tm.CTime1000("SPD")
        self.time_no_lean = 0

        self.wait_timer2 = 0

        self.cruise_set_speed_kph = 0
        self.curise_set_first = 0
        self.curise_sw_check = 0
        self.prev_clu_CruiseSwState = 0    

        self.prev_VSetDis  = 0
        
        self.sc_clu_speed = 0
        self.btn_type = Buttons.NONE
        self.active_time = 0

        self.old_model_speed = 0
        self.old_model_init = 0

        self.curve_speed = 0
        self.curvature_gain = 1

        self.params = Params()
        self.cruise_set_mode = int(self.params.get("CruiseStatemodeSelInit", encoding="utf8"))
        self.map_spd_limit_offset = int(self.params.get("OpkrSpeedLimitOffset", encoding="utf8"))

        self.map_spd_enable = False
        self.map_spd_camera = 0

    def reset(self):
        self.v_model = 0
        self.a_model = 0
        self.v_cruise = 0
        self.a_cruise = 0

    def cal_curve_speed(self, sm, v_ego):
        md = sm['modelV2']
        if md is not None and len(md.position.x) == TRAJECTORY_SIZE and len(md.position.y) == TRAJECTORY_SIZE:
            x = md.position.x
            y = md.position.y
            dy = np.gradient(y, x)
            d2y = np.gradient(dy, x)
            curv = d2y / (1 + dy ** 2) ** 1.5
            curv = curv[5:TRAJECTORY_SIZE-10]
            a_y_max = 2.975 - v_ego * 0.0375  # ~1.85 @ 75mph, ~2.6 @ 25mph
            v_curvature = np.sqrt(a_y_max / np.clip(np.abs(curv), 1e-4, None))
            model_speed = np.mean(v_curvature) * 0.9 * self.curvature_gain
            self.curve_speed = float(max(model_speed, MIN_CURVE_SPEED * CV.KPH_TO_MS))
            # if model_speed < v_ego:
            #     self.curve_speed = float(max(model_speed, MIN_CURVE_SPEED * CV.KPH_TO_MS))
            # else:
            #     self.curve_speed = MAX_SPEED
            if np.isnan(self.curve_speed):
                self.curve_speed = MAX_SPEED
        else:
            self.curve_speed = MAX_SPEED

        return min(MAX_SPEED, self.curve_speed * CV.MS_TO_KPH)

    def calc_laneProb(self, prob, v_ego):
        if len(prob) > 1:
            path = list(prob)

            # TODO: compute max speed without using a list of points and without numpy
            y_p = 3 * path[0] * self.path_x**2 + \
                2 * path[1] * self.path_x + path[2]
            y_pp = 6 * path[0] * self.path_x + 2 * path[1]
            curv = y_pp / (1. + y_p**2)**1.5

            #print( 'curv = {}'.format( curv) )

            a_y_max = 2.975 - v_ego * 0.0375  # ~1.85 @ 75mph, ~2.6 @ 25mph
            v_curvature = np.sqrt(a_y_max / np.clip(np.abs(curv), 1e-4, None))
            model_speed = np.min(v_curvature)
            # Don't slow down below 20mph

            model_speed *= CV.MS_TO_KPH
            model_speed = max(MIN_CURVE_SPEED, model_speed)
           # print( 'v_curvature = {}'.format( v_curvature) )
            #print( 'model_speed = {}  '.format( model_speed) )

            
            if model_speed > MAX_SPEED:
               model_speed = MAX_SPEED
        else:
            model_speed = MAX_SPEED
          

        return  model_speed


    def cal_model_speed(self, sm, v_ego):
        md = sm['modelV2']
        #print('{}'.format( md ) )
        if len(md.path.poly):
            self.prob = list(md.path.poly)

            model_speed = self.calc_laneProb( self.prob, v_ego )
    
            delta_model = model_speed - self.old_model_speed
            if self.old_model_init < 10:
                self.old_model_init += 1
                self.old_model_speed = model_speed
            elif self.old_model_speed == model_speed:
                pass
            elif delta_model < -1:
                self.old_model_speed -= 0.5  #model_speed
            elif delta_model > 0:
                self.old_model_speed += 0.1

            else:
                self.old_model_speed = model_speed

        return self.old_model_speed


    def update_cruiseSW(self, CS):
        set_speed_kph = int(round(self.cruise_set_speed_kph))
        delta_vsetdis = 0
        if CS.acc_active:
            delta_vsetdis = abs(int(CS.VSetDis) - self.prev_VSetDis)
            if self.prev_clu_CruiseSwState != CS.cruise_buttons:
                if CS.cruise_buttons == Buttons.RES_ACCEL or CS.cruise_buttons == Buttons.SET_DECEL:
                    self.prev_VSetDis = int(CS.VSetDis)
                elif CS.driverOverride:
                    set_speed_kph = int(CS.VSetDis)
                elif self.prev_clu_CruiseSwState == Buttons.RES_ACCEL:   # up 
                    if self.curise_set_first:
                        self.curise_set_first = 0
                        set_speed_kph =  int(CS.VSetDis)
                    elif delta_vsetdis > 0:
                        set_speed_kph = int(CS.VSetDis)
                    elif not self.curise_sw_check:
                        set_speed_kph += 1
                elif self.prev_clu_CruiseSwState == Buttons.SET_DECEL:  # dn
                    if self.curise_set_first:
                        self.curise_set_first = 0
                        set_speed_kph = int(CS.VSetDis)
                    elif delta_vsetdis > 0:
                        set_speed_kph = int(CS.VSetDis)
                    elif not self.curise_sw_check:
                        set_speed_kph -= 1

                self.prev_clu_CruiseSwState = CS.cruise_buttons
            elif (CS.cruise_buttons == Buttons.RES_ACCEL or CS.cruise_buttons == Buttons.SET_DECEL) and delta_vsetdis > 0:
                self.curise_sw_check = True
                set_speed_kph = int(CS.VSetDis)
        else:
            self.curise_sw_check = False
            self.curise_set_first = 1
            self.prev_VSetDis = int(CS.VSetDis)
            set_speed_kph = int(CS.VSetDis)
            if self.prev_clu_CruiseSwState != CS.cruise_buttons:  # MODE 전환.
                if CS.cruise_buttons == Buttons.GAP_DIST and not CS.acc_active and CS.out.cruiseState.available:
                    self.cruise_set_mode += 1
                if self.cruise_set_mode > 4:
                    self.cruise_set_mode = 0
                self.prev_clu_CruiseSwState = CS.cruise_buttons
            

        if set_speed_kph <= 30:
            set_speed_kph = 30

        self.cruise_set_speed_kph = set_speed_kph
        return self.cruise_set_mode, set_speed_kph


    @staticmethod
    def get_lead(sm):
        plan = sm['longitudinalPlan']
        if 0 < plan.dRel1 < 149:
            dRel = int(plan.dRel1) #EON Lead
            yRel = int(plan.yRel1) #EON Lead
            vRel = int(plan.vRel1 * 3.6 + 0.5) #EON Lead
        else:
            dRel = 150
            yRel = 0
            vRel = 0


        return dRel, yRel, vRel



    def get_tm_speed(self, CS, set_time, add_val, safety_dis=5):
        time = int(set_time)

        delta_speed = int(CS.VSetDis) - int(round(CS.clu_Vanz))
        set_speed = int(CS.VSetDis) + add_val
        
        if add_val > 0:  # 증가
            if delta_speed > safety_dis:
              time = int(set_time)

        else:
            if delta_speed < -safety_dis:
              time = int(set_time)

        return time, set_speed

    # returns a 
    def update_lead(self, c, can_strings):
        raise NotImplementedError

    def update_curv(self, CS, sm, curve_speed):
        raise NotImplementedError

    def update_log(self, CS, set_speed, target_set_speed, long_wait_cmd):
        str3 = 'M={:3.0f} DST={:3.0f} VSD={:.0f} DA={:.0f}/{:.0f}/{:.0f} DG={:s} DO={:.0f}'.format(
            CS.out.cruiseState.modeSel, target_set_speed, CS.VSetDis, CS.driverAcc_time, long_wait_cmd, self.long_curv_timer, self.seq_step_debug, CS.driverOverride )
        str4 = ' CS={:.1f}/{:.1f} '.format(  CS.lead_distance, CS.lead_objspd )
        str5 = str3 +  str4
        trace1.printf2( str5 )

    def lead_control(self, CS, sm, CC):
        dRel = CC.dRel
        yRel = CC.yRel
        vRel = CC.vRel
        active_time = 10
        btn_type = Buttons.NONE
        #lead_1 = sm['radarState'].leadOne
        long_wait_cmd = 500
        set_speed = int(round(self.cruise_set_speed_kph))

        if self.long_curv_timer < 600:
            self.long_curv_timer += 1


        # 선행 차량 거리유지
        lead_wait_cmd, lead_set_speed = self.update_lead( sm, CS, dRel, yRel, vRel, CC)

        # 커브 감속.
        curve_speed = CC.curve_speed   #cal_curve_speed(sm, CS.out.vEgo)
        curv_wait_cmd, curv_set_speed = self.update_curv(CS, sm, curve_speed)

        if curv_wait_cmd != 0:
            if lead_set_speed > curv_set_speed:
                set_speed = curv_set_speed
                long_wait_cmd = curv_wait_cmd
            else:
                set_speed = lead_set_speed
                long_wait_cmd = lead_wait_cmd
        else:
            set_speed = lead_set_speed
            long_wait_cmd = lead_wait_cmd

        if set_speed >= int(round(self.cruise_set_speed_kph)):
            set_speed = int(round(self.cruise_set_speed_kph))
        elif set_speed <= 30:
            set_speed = 30

        # control process
        target_set_speed = set_speed
        delta = int(round(set_speed)) - int(CS.VSetDis)
        dec_step_cmd = 1

        camspeed = Params().get("LimitSetSpeedCamera", encoding="utf8")
        if camspeed is not None:
            self.map_spd_camera = int(float(camspeed.rstrip('\n')))
            self.map_spd_enable = self.map_spd_camera > 29
        else:
            self.map_spd_enable = False
            self.map_spd_camera = 0

        if self.long_curv_timer < long_wait_cmd:
            pass
        elif delta > 0:
            if ((self.map_spd_camera+round(self.map_spd_camera*0.01*self.map_spd_limit_offset)) == int(CS.VSetDis)) and self.map_spd_enable:
                set_speed = int(CS.VSetDis) + 0
                btn_type = Buttons.NONE
                self.long_curv_timer = 0
            else:
                set_speed = int(CS.VSetDis) + dec_step_cmd
                btn_type = Buttons.RES_ACCEL
                self.long_curv_timer = 0
        elif delta < 0:
            set_speed = int(CS.VSetDis) - dec_step_cmd
            btn_type = Buttons.SET_DECEL
            self.long_curv_timer = 0
        if self.cruise_set_mode == 0:
            btn_type = Buttons.NONE


        self.update_log( CS, set_speed, target_set_speed, long_wait_cmd )


        return btn_type, set_speed, active_time



    def update(self, CS, sm, CC):
        self.cruise_set_mode = CS.out.cruiseState.modeSel
        #self.cruise_set_speed_kph = int(round(CS.out.cruiseState.speed * CV.MS_TO_KPH))
        self.cruise_set_speed_kph = int(round(CC.vCruiseSet))
        if CS.driverOverride == 2 or not CS.acc_active or CS.cruise_buttons == Buttons.RES_ACCEL or CS.cruise_buttons == Buttons.SET_DECEL:
            self.resume_cnt = 0
            self.btn_type = Buttons.NONE
            self.wait_timer2 = 10
            self.active_timer2 = 0
        elif self.wait_timer2:
            self.wait_timer2 -= 1
        else:
            btn_type, clu_speed, active_time = self.lead_control( CS, sm, CC )   # speed controller spdcontroller.py

            if (0 <= int(CS.clu_Vanz) <= 1 or 7 < int(CS.clu_Vanz) < 15) and CC.vRel <= 0:
                self.btn_type = Buttons.NONE
            elif self.btn_type != Buttons.NONE:
                pass
            elif btn_type != Buttons.NONE:
                self.resume_cnt = 0
                self.active_timer2 = 0
                self.btn_type = btn_type
                self.sc_clu_speed = clu_speed                
                self.active_time = max( 5, active_time )

            if self.btn_type != Buttons.NONE:
                self.active_timer2 += 1
                if self.active_timer2 > self.active_time:
                    self.wait_timer2 = 5
                    self.resume_cnt = 0
                    self.active_timer2 = 0
                    self.btn_type = Buttons.NONE          
                else:
                    return 1
        return  0   