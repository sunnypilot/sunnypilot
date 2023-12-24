#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void gnss_update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_err_fun(double *nom_x, double *delta_x, double *out_7759149317582249240);
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_9118422902961757933);
void gnss_H_mod_fun(double *state, double *out_1633358768098501879);
void gnss_f_fun(double *state, double dt, double *out_436651591053660649);
void gnss_F_fun(double *state, double dt, double *out_7304280096771648861);
void gnss_h_6(double *state, double *sat_pos, double *out_4764504202269866901);
void gnss_H_6(double *state, double *sat_pos, double *out_4085363850207817832);
void gnss_h_20(double *state, double *sat_pos, double *out_6801986365944636663);
void gnss_H_20(double *state, double *sat_pos, double *out_7866410108663176377);
void gnss_h_7(double *state, double *sat_pos_vel, double *out_4005211607259102508);
void gnss_H_7(double *state, double *sat_pos_vel, double *out_2701243593729319356);
void gnss_h_21(double *state, double *sat_pos_vel, double *out_4005211607259102508);
void gnss_H_21(double *state, double *sat_pos_vel, double *out_2701243593729319356);
void gnss_predict(double *in_x, double *in_P, double *in_Q, double dt);
}