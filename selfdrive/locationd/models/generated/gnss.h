#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void gnss_update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_err_fun(double *nom_x, double *delta_x, double *out_6208051589904680687);
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_980651649795713821);
void gnss_H_mod_fun(double *state, double *out_8761108313881456199);
void gnss_f_fun(double *state, double dt, double *out_6985979927194349446);
void gnss_F_fun(double *state, double dt, double *out_5398596809828011208);
void gnss_h_6(double *state, double *sat_pos, double *out_854109254235318073);
void gnss_H_6(double *state, double *sat_pos, double *out_4878360041893525515);
void gnss_h_20(double *state, double *sat_pos, double *out_3910060068815622044);
void gnss_H_20(double *state, double *sat_pos, double *out_7601181949165199926);
void gnss_h_7(double *state, double *sat_pos_vel, double *out_7752585033610334316);
void gnss_H_7(double *state, double *sat_pos_vel, double *out_8389742934130346329);
void gnss_h_21(double *state, double *sat_pos_vel, double *out_7752585033610334316);
void gnss_H_21(double *state, double *sat_pos_vel, double *out_8389742934130346329);
void gnss_predict(double *in_x, double *in_P, double *in_Q, double dt);
}