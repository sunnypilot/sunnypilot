#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void gnss_update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_err_fun(double *nom_x, double *delta_x, double *out_1856399012621437567);
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_5659332400997797470);
void gnss_H_mod_fun(double *state, double *out_6521121627186908832);
void gnss_f_fun(double *state, double dt, double *out_8022750769580419123);
void gnss_F_fun(double *state, double dt, double *out_6336087931668650939);
void gnss_h_6(double *state, double *sat_pos, double *out_6727337945144809708);
void gnss_H_6(double *state, double *sat_pos, double *out_1448263778646329223);
void gnss_h_20(double *state, double *sat_pos, double *out_2137014843544135742);
void gnss_H_20(double *state, double *sat_pos, double *out_1721365513193142610);
void gnss_h_7(double *state, double *sat_pos_vel, double *out_7819726430377713612);
void gnss_H_7(double *state, double *sat_pos_vel, double *out_5800620054238539955);
void gnss_h_21(double *state, double *sat_pos_vel, double *out_7819726430377713612);
void gnss_H_21(double *state, double *sat_pos_vel, double *out_5800620054238539955);
void gnss_predict(double *in_x, double *in_P, double *in_Q, double dt);
}