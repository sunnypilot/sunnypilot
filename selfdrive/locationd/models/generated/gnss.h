#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void gnss_update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_err_fun(double *nom_x, double *delta_x, double *out_966236154794564673);
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_1570495147257342659);
void gnss_H_mod_fun(double *state, double *out_1116987290868003958);
void gnss_f_fun(double *state, double dt, double *out_7944759911088803830);
void gnss_F_fun(double *state, double dt, double *out_6000912361546807532);
void gnss_h_6(double *state, double *sat_pos, double *out_5247022646599428476);
void gnss_H_6(double *state, double *sat_pos, double *out_6280952107920151244);
void gnss_h_20(double *state, double *sat_pos, double *out_3690994761720456636);
void gnss_H_20(double *state, double *sat_pos, double *out_9122906747733130927);
void gnss_h_7(double *state, double *sat_pos_vel, double *out_266928008761275148);
void gnss_H_7(double *state, double *sat_pos_vel, double *out_7588446133012577443);
void gnss_h_21(double *state, double *sat_pos_vel, double *out_266928008761275148);
void gnss_H_21(double *state, double *sat_pos_vel, double *out_7588446133012577443);
void gnss_predict(double *in_x, double *in_P, double *in_Q, double dt);
}