#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_264984234156022510);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_4459356063444070539);
void pose_H_mod_fun(double *state, double *out_7005986214264108234);
void pose_f_fun(double *state, double dt, double *out_4717377945151750388);
void pose_F_fun(double *state, double dt, double *out_4729405661658211402);
void pose_h_4(double *state, double *unused, double *out_5738722976826185665);
void pose_H_4(double *state, double *unused, double *out_8862099202367372115);
void pose_h_10(double *state, double *unused, double *out_2388008800197743067);
void pose_H_10(double *state, double *unused, double *out_8909533314766452476);
void pose_h_13(double *state, double *unused, double *out_9149861557909701017);
void pose_H_13(double *state, double *unused, double *out_5649825377035039314);
void pose_h_14(double *state, double *unused, double *out_3251330187002382357);
void pose_H_14(double *state, double *unused, double *out_9149528344697295902);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}