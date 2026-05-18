#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_3240425447174633819);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5810796157656117665);
void pose_H_mod_fun(double *state, double *out_1221928615010225756);
void pose_f_fun(double *state, double dt, double *out_6673196704848212167);
void pose_F_fun(double *state, double dt, double *out_9126575036203471234);
void pose_h_4(double *state, double *unused, double *out_4184048412485075607);
void pose_H_4(double *state, double *unused, double *out_1978481286091244268);
void pose_h_10(double *state, double *unused, double *out_747511093795381270);
void pose_H_10(double *state, double *unused, double *out_3506143025433361193);
void pose_h_13(double *state, double *unused, double *out_8398284471669141404);
void pose_H_13(double *state, double *unused, double *out_5632149922225456661);
void pose_h_14(double *state, double *unused, double *out_7822783238651142803);
void pose_H_14(double *state, double *unused, double *out_1984759570248240261);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}