#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void gnss_update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_err_fun(double *nom_x, double *delta_x, double *out_3532684675618107860);
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_4040997643746645524);
void gnss_H_mod_fun(double *state, double *out_5907768448464933327);
void gnss_f_fun(double *state, double dt, double *out_8719739038902116923);
void gnss_F_fun(double *state, double dt, double *out_6368958041110140577);
void gnss_h_6(double *state, double *sat_pos, double *out_2271110864362118697);
void gnss_H_6(double *state, double *sat_pos, double *out_1862672885827164935);
void gnss_h_20(double *state, double *sat_pos, double *out_4324669159508799845);
void gnss_H_20(double *state, double *sat_pos, double *out_2084788552121881515);
void gnss_h_7(double *state, double *sat_pos_vel, double *out_5010606036331411486);
void gnss_H_7(double *state, double *sat_pos_vel, double *out_3676152182946046175);
void gnss_h_21(double *state, double *sat_pos_vel, double *out_5010606036331411486);
void gnss_H_21(double *state, double *sat_pos_vel, double *out_3676152182946046175);
void gnss_predict(double *in_x, double *in_P, double *in_Q, double dt);
}