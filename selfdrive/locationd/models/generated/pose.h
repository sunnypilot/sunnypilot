#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_6822829480064316427);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_8351755903623348291);
void pose_H_mod_fun(double *state, double *out_3160786903936238065);
void pose_f_fun(double *state, double dt, double *out_3649248979314528992);
void pose_F_fun(double *state, double dt, double *out_5219362633347118737);
void pose_h_4(double *state, double *unused, double *out_7519118996374711979);
void pose_H_4(double *state, double *unused, double *out_8313305288975318800);
void pose_h_10(double *state, double *unused, double *out_6206587983423265688);
void pose_H_10(double *state, double *unused, double *out_2459625458239534432);
void pose_h_13(double *state, double *unused, double *out_6892691385862434963);
void pose_H_13(double *state, double *unused, double *out_6921164959401900015);
void pose_h_14(double *state, double *unused, double *out_7370507100637914212);
void pose_H_14(double *state, double *unused, double *out_6170197928394748287);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}