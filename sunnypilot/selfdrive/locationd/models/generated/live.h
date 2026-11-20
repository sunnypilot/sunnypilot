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
void live_H(double *in_vec, double *out_6687864835776943566);
void live_err_fun(double *nom_x, double *delta_x, double *out_5748113535829923716);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_1479304479137130355);
void live_H_mod_fun(double *state, double *out_3591261265835578447);
void live_f_fun(double *state, double dt, double *out_2021985224307685705);
void live_F_fun(double *state, double dt, double *out_6178907986112954469);
void live_h_4(double *state, double *unused, double *out_4254426259869329665);
void live_H_4(double *state, double *unused, double *out_7390073645737859734);
void live_h_9(double *state, double *unused, double *out_5205173692069641597);
void live_H_9(double *state, double *unused, double *out_7148883999108269089);
void live_h_10(double *state, double *unused, double *out_7807680097706281633);
void live_H_10(double *state, double *unused, double *out_1790918198485243232);
void live_h_12(double *state, double *unused, double *out_282125164966214349);
void live_H_12(double *state, double *unused, double *out_2370617237705897939);
void live_h_35(double *state, double *unused, double *out_4227275693812207765);
void live_H_35(double *state, double *unused, double *out_4023411588365252358);
void live_h_32(double *state, double *unused, double *out_7089588856929551250);
void live_H_32(double *state, double *unused, double *out_3158603959037533363);
void live_h_13(double *state, double *unused, double *out_1295957034058120237);
void live_H_13(double *state, double *unused, double *out_2692890126249257773);
void live_h_14(double *state, double *unused, double *out_5205173692069641597);
void live_H_14(double *state, double *unused, double *out_7148883999108269089);
void live_h_33(double *state, double *unused, double *out_2366480781245220040);
void live_H_33(double *state, double *unused, double *out_872854583726394754);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}