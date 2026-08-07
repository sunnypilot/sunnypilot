#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_228345055687174559);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_3726714603593551859);
void pose_H_mod_fun(double *state, double *out_6712772131857650620);
void pose_f_fun(double *state, double dt, double *out_2706993655191654809);
void pose_F_fun(double *state, double dt, double *out_372841931129064371);
void pose_h_4(double *state, double *unused, double *out_3997723666308670841);
void pose_H_4(double *state, double *unused, double *out_4134113474779579353);
void pose_h_10(double *state, double *unused, double *out_6627456117207891484);
void pose_H_10(double *state, double *unused, double *out_1462818273599549569);
void pose_h_13(double *state, double *unused, double *out_2824244578095522440);
void pose_H_13(double *state, double *unused, double *out_921839649447246552);
void pose_h_14(double *state, double *unused, double *out_696698419016090920);
void pose_H_14(double *state, double *unused, double *out_7216901907074951649);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}