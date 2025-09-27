#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_3055639861342664638);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_2233443736881945674);
void pose_H_mod_fun(double *state, double *out_5454317104155112741);
void pose_f_fun(double *state, double dt, double *out_4996223981732405570);
void pose_F_fun(double *state, double dt, double *out_5891913618111355049);
void pose_h_4(double *state, double *unused, double *out_1832779376905477896);
void pose_H_4(double *state, double *unused, double *out_4792122085581214108);
void pose_h_10(double *state, double *unused, double *out_4235949127536262679);
void pose_H_10(double *state, double *unused, double *out_692750502701317014);
void pose_h_13(double *state, double *unused, double *out_3117911153244826867);
void pose_H_13(double *state, double *unused, double *out_2818509122735486821);
void pose_h_14(double *state, double *unused, double *out_622989207303169877);
void pose_H_14(double *state, double *unused, double *out_828881229241729579);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}