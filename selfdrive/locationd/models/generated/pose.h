#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_2708976385256854938);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5039075117443556308);
void pose_H_mod_fun(double *state, double *out_4768576861501722562);
void pose_f_fun(double *state, double dt, double *out_3365426939231918965);
void pose_F_fun(double *state, double dt, double *out_6077984892743029865);
void pose_h_4(double *state, double *unused, double *out_7953710333148623088);
void pose_H_4(double *state, double *unused, double *out_4733805546150007712);
void pose_h_10(double *state, double *unused, double *out_8638301772534799194);
void pose_H_10(double *state, double *unused, double *out_7550312672629139090);
void pose_h_13(double *state, double *unused, double *out_4921048176335829394);
void pose_H_13(double *state, double *unused, double *out_5298407465831851816);
void pose_h_14(double *state, double *unused, double *out_5016646202722718585);
void pose_H_14(double *state, double *unused, double *out_1651017113854635416);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}