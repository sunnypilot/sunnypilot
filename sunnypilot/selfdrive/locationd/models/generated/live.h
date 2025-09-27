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
void live_H(double *in_vec, double *out_5845230607952208531);
void live_err_fun(double *nom_x, double *delta_x, double *out_4782575507534006830);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_1880356144175221690);
void live_H_mod_fun(double *state, double *out_7042100268426138493);
void live_f_fun(double *state, double dt, double *out_5407506710844957937);
void live_F_fun(double *state, double dt, double *out_6949928349319319856);
void live_h_4(double *state, double *unused, double *out_8963914388288055049);
void live_H_4(double *state, double *unused, double *out_7580435479770056035);
void live_h_9(double *state, double *unused, double *out_5328174192617228916);
void live_H_9(double *state, double *unused, double *out_3423267743415278552);
void live_h_10(double *state, double *unused, double *out_7277400042590755687);
void live_H_10(double *state, double *unused, double *out_3008283334411580690);
void live_h_12(double *state, double *unused, double *out_2580626886274515368);
void live_H_12(double *state, double *unused, double *out_8201534504817649702);
void live_h_35(double *state, double *unused, double *out_3740913222535607260);
void live_H_35(double *state, double *unused, double *out_7499646536566888205);
void live_h_32(double *state, double *unused, double *out_4468125116457218761);
void live_H_32(double *state, double *unused, double *out_1698342164359275647);
void live_h_13(double *state, double *unused, double *out_3056542314696115631);
void live_H_13(double *state, double *unused, double *out_6944888124567630958);
void live_h_14(double *state, double *unused, double *out_5328174192617228916);
void live_H_14(double *state, double *unused, double *out_3423267743415278552);
void live_h_33(double *state, double *unused, double *out_3671765815232051329);
void live_H_33(double *state, double *unused, double *out_4349089531928030601);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}