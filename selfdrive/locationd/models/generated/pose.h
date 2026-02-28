#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_2314661006140587753);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_6192097384047082973);
void pose_H_mod_fun(double *state, double *out_1438273545813297818);
void pose_f_fun(double *state, double dt, double *out_5533301484302365435);
void pose_F_fun(double *state, double dt, double *out_8970483331473945713);
void pose_h_4(double *state, double *unused, double *out_667285240629023896);
void pose_H_4(double *state, double *unused, double *out_684112543758585211);
void pose_h_10(double *state, double *unused, double *out_6645666359799058327);
void pose_H_10(double *state, double *unused, double *out_2536663734245119922);
void pose_h_13(double *state, double *unused, double *out_2409725172809164603);
void pose_H_13(double *state, double *unused, double *out_6926518664558115718);
void pose_h_14(double *state, double *unused, double *out_8151145315765671202);
void pose_H_14(double *state, double *unused, double *out_3279128312580899318);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}