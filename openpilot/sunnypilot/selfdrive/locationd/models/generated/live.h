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
void live_H(double *in_vec, double *out_5926322025614992030);
void live_err_fun(double *nom_x, double *delta_x, double *out_5043251176595415602);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_3360739843129809304);
void live_H_mod_fun(double *state, double *out_8279386211598339514);
void live_f_fun(double *state, double dt, double *out_6890687714462639744);
void live_F_fun(double *state, double dt, double *out_7621965816561569981);
void live_h_4(double *state, double *unused, double *out_3851734767229128263);
void live_H_4(double *state, double *unused, double *out_5878769767090540838);
void live_h_9(double *state, double *unused, double *out_2694197172040937469);
void live_H_9(double *state, double *unused, double *out_1408449168173906632);
void live_h_10(double *state, double *unused, double *out_7033125878671447195);
void live_H_10(double *state, double *unused, double *out_65675330875969869);
void live_h_12(double *state, double *unused, double *out_8799002316774637565);
void live_H_12(double *state, double *unused, double *out_6186715929576277782);
void live_h_35(double *state, double *unused, double *out_2868906334315872882);
void live_H_35(double *state, double *unused, double *out_8932278961901291491);
void live_h_32(double *state, double *unused, double *out_9199462926327450350);
void live_H_32(double *state, double *unused, double *out_6730806947389842532);
void live_h_13(double *state, double *unused, double *out_3826583407417889778);
void live_H_13(double *state, double *unused, double *out_3672088104010170074);
void live_h_14(double *state, double *unused, double *out_2694197172040937469);
void live_H_14(double *state, double *unused, double *out_1408449168173906632);
void live_h_33(double *state, double *unused, double *out_6802426037572342548);
void live_H_33(double *state, double *unused, double *out_7684478583555780967);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}