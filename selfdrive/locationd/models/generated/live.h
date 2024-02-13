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
void live_H(double *in_vec, double *out_4480635192079699808);
void live_err_fun(double *nom_x, double *delta_x, double *out_3007286517137113995);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_7534001024210217417);
void live_H_mod_fun(double *state, double *out_3346680914993009624);
void live_f_fun(double *state, double dt, double *out_7931205588750418001);
void live_F_fun(double *state, double dt, double *out_2150237613912517696);
void live_h_4(double *state, double *unused, double *out_1746009882312017569);
void live_H_4(double *state, double *unused, double *out_2034715154603224858);
void live_h_9(double *state, double *unused, double *out_7692971224182445809);
void live_H_9(double *state, double *unused, double *out_9124809983841879288);
void live_h_10(double *state, double *unused, double *out_4686363176672063733);
void live_H_10(double *state, double *unused, double *out_2151571996051208579);
void live_h_12(double *state, double *unused, double *out_5354991903500146857);
void live_H_12(double *state, double *unused, double *out_7054171562635186653);
void live_h_35(double *state, double *unused, double *out_6077143654978502653);
void live_H_35(double *state, double *unused, double *out_5401377211975832234);
void live_h_32(double *state, double *unused, double *out_4851193230152119277);
void live_H_32(double *state, double *unused, double *out_7342215549308841035);
void live_h_13(double *state, double *unused, double *out_2404142402348874032);
void live_H_13(double *state, double *unused, double *out_2071794297598648389);
void live_h_14(double *state, double *unused, double *out_7692971224182445809);
void live_H_14(double *state, double *unused, double *out_9124809983841879288);
void live_h_33(double *state, double *unused, double *out_1939992138062658578);
void live_H_33(double *state, double *unused, double *out_8551934216614689838);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}