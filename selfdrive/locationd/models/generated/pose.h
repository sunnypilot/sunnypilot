#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_920130119510719117);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_4602168207176775062);
void pose_H_mod_fun(double *state, double *out_1639299711796095424);
void pose_f_fun(double *state, double dt, double *out_1392497273260296337);
void pose_F_fun(double *state, double dt, double *out_2156255028652572290);
void pose_h_4(double *state, double *unused, double *out_3043836967836844088);
void pose_H_4(double *state, double *unused, double *out_7863082695855634850);
void pose_h_10(double *state, double *unused, double *out_7404958229428552171);
void pose_H_10(double *state, double *unused, double *out_6268263964996001431);
void pose_h_13(double *state, double *unused, double *out_5572039581656493534);
void pose_H_13(double *state, double *unused, double *out_7371387552521583965);
void pose_h_14(double *state, double *unused, double *out_4488120958675282001);
void pose_H_14(double *state, double *unused, double *out_6620420521514432237);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}