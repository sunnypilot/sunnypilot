#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_427463338731457644);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_2896227888136381140);
void pose_H_mod_fun(double *state, double *out_2158205211507318632);
void pose_f_fun(double *state, double dt, double *out_1184498683811889789);
void pose_F_fun(double *state, double dt, double *out_3361969816109204330);
void pose_h_4(double *state, double *unused, double *out_4817713328626282849);
void pose_H_4(double *state, double *unused, double *out_2912366213562031239);
void pose_h_10(double *state, double *unused, double *out_8260153212022429064);
void pose_H_10(double *state, double *unused, double *out_3272792128311919869);
void pose_h_13(double *state, double *unused, double *out_972726228359974118);
void pose_H_13(double *state, double *unused, double *out_7923746651830819448);
void pose_h_14(double *state, double *unused, double *out_6022082422796717247);
void pose_H_14(double *state, double *unused, double *out_6875607069901515768);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}