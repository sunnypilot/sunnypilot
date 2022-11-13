#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void gnss_update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_err_fun(double *nom_x, double *delta_x, double *out_3708978687379214111);
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_2153812957683424211);
void gnss_H_mod_fun(double *state, double *out_4628416537597784978);
void gnss_f_fun(double *state, double dt, double *out_7298165946464525334);
void gnss_F_fun(double *state, double dt, double *out_7533698438399796741);
void gnss_h_6(double *state, double *sat_pos, double *out_7098435553514511068);
void gnss_H_6(double *state, double *sat_pos, double *out_279244630454215938);
void gnss_h_20(double *state, double *sat_pos, double *out_4723154202215786973);
void gnss_H_20(double *state, double *sat_pos, double *out_7530708677883952507);
void gnss_h_7(double *state, double *sat_pos_vel, double *out_7180798933054063665);
void gnss_H_7(double *state, double *sat_pos_vel, double *out_6334088002612665567);
void gnss_h_21(double *state, double *sat_pos_vel, double *out_7180798933054063665);
void gnss_H_21(double *state, double *sat_pos_vel, double *out_6334088002612665567);
void gnss_predict(double *in_x, double *in_P, double *in_Q, double dt);
}