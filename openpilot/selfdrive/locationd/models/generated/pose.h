#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_5688174754372622748);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_598026621986152539);
void pose_H_mod_fun(double *state, double *out_2381892679141553073);
void pose_f_fun(double *state, double dt, double *out_1702484166209795754);
void pose_F_fun(double *state, double dt, double *out_2610723520316632485);
void pose_h_4(double *state, double *unused, double *out_1625499965422042150);
void pose_H_4(double *state, double *unused, double *out_5582302580243023097);
void pose_h_10(double *state, double *unused, double *out_2139046532052679128);
void pose_H_10(double *state, double *unused, double *out_280379430924529525);
void pose_h_13(double *state, double *unused, double *out_4130601663238522497);
void pose_H_13(double *state, double *unused, double *out_2028328628073677832);
void pose_h_14(double *state, double *unused, double *out_5394061988893492228);
void pose_H_14(double *state, double *unused, double *out_8665091012538395393);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}