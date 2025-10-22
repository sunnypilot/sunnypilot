#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_165846048707596909);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_6648002265281282693);
void pose_H_mod_fun(double *state, double *out_3826583937831985339);
void pose_f_fun(double *state, double dt, double *out_3932199691534334272);
void pose_F_fun(double *state, double dt, double *out_9115777546130168700);
void pose_h_4(double *state, double *unused, double *out_3213295537891936167);
void pose_H_4(double *state, double *unused, double *out_3101938741858735467);
void pose_h_10(double *state, double *unused, double *out_5489470472982430598);
void pose_H_10(double *state, double *unused, double *out_8922665824980314411);
void pose_h_13(double *state, double *unused, double *out_8982009317064219914);
void pose_H_13(double *state, double *unused, double *out_6314212567191068268);
void pose_h_14(double *state, double *unused, double *out_8976270627455297792);
void pose_H_14(double *state, double *unused, double *out_7065179598198219996);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}