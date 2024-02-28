#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void live_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_9(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_12(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_35(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_32(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_33(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_H(double *in_vec, double *out_2221680810211877007);
void live_err_fun(double *nom_x, double *delta_x, double *out_9058537909689266592);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_7576143246016953659);
void live_H_mod_fun(double *state, double *out_815593853557770859);
void live_f_fun(double *state, double dt, double *out_1987600578531036294);
void live_F_fun(double *state, double dt, double *out_8763257145105801012);
void live_h_4(double *state, double *unused, double *out_4393751991820450146);
void live_H_4(double *state, double *unused, double *out_1749816418172289953);
void live_h_9(double *state, double *unused, double *out_7635015471942411802);
void live_H_9(double *state, double *unused, double *out_5537402517092157517);
void live_h_10(double *state, double *unused, double *out_4654836922306288541);
void live_H_10(double *state, double *unused, double *out_7114843905500366371);
void live_h_12(double *state, double *unused, double *out_8455142581421422448);
void live_H_12(double *state, double *unused, double *out_8131074795215022949);
void live_h_35(double *state, double *unused, double *out_5602094957643603974);
void live_H_35(double *state, double *unused, double *out_1616845639200317423);
void live_h_32(double *state, double *unused, double *out_5255635781881463689);
void live_H_32(double *state, double *unused, double *out_2989652337278612786);
void live_h_13(double *state, double *unused, double *out_2909743526958408903);
void live_H_13(double *state, double *unused, double *out_4042123882687789281);
void live_h_14(double *state, double *unused, double *out_7635015471942411802);
void live_H_14(double *state, double *unused, double *out_5537402517092157517);
void live_h_33(double *state, double *unused, double *out_3725526701855033401);
void live_H_33(double *state, double *unused, double *out_6633312141235519764);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}