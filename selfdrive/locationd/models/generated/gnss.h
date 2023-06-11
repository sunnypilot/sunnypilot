#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void gnss_update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_err_fun(double *nom_x, double *delta_x, double *out_4588913850449385760);
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_361280867974834565);
void gnss_H_mod_fun(double *state, double *out_3692418476170695800);
void gnss_f_fun(double *state, double dt, double *out_3599858202863344339);
void gnss_F_fun(double *state, double dt, double *out_6614403358289748728);
void gnss_h_6(double *state, double *sat_pos, double *out_3965377368938519904);
void gnss_H_6(double *state, double *sat_pos, double *out_4010469744061131744);
void gnss_h_20(double *state, double *sat_pos, double *out_4397465078196892446);
void gnss_H_20(double *state, double *sat_pos, double *out_7230021967014098202);
void gnss_h_7(double *state, double *sat_pos_vel, double *out_8859539764878579118);
void gnss_H_7(double *state, double *sat_pos_vel, double *out_6351382189608033375);
void gnss_h_21(double *state, double *sat_pos_vel, double *out_8859539764878579118);
void gnss_H_21(double *state, double *sat_pos_vel, double *out_6351382189608033375);
void gnss_predict(double *in_x, double *in_P, double *in_Q, double dt);
}