#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_7899872685628621531);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_1215289726053279423);
void pose_H_mod_fun(double *state, double *out_420741753375595218);
void pose_f_fun(double *state, double dt, double *out_5996963235034927992);
void pose_F_fun(double *state, double dt, double *out_78320000076568703);
void pose_h_4(double *state, double *unused, double *out_2403402202974529453);
void pose_H_4(double *state, double *unused, double *out_5573260138414675953);
void pose_h_10(double *state, double *unused, double *out_1415940429779603810);
void pose_H_10(double *state, double *unused, double *out_5540918162512642087);
void pose_h_13(double *state, double *unused, double *out_8116494657900557165);
void pose_H_13(double *state, double *unused, double *out_8785533963747008754);
void pose_h_14(double *state, double *unused, double *out_2556692697037776409);
void pose_H_14(double *state, double *unused, double *out_8910243078955391134);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}