#pragma once
#include "rednose/helpers/common_ekf.h"
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
void live_H(double *in_vec, double *out_4278948180830879312);
void live_err_fun(double *nom_x, double *delta_x, double *out_101980629978377551);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_6691698588704786296);
void live_H_mod_fun(double *state, double *out_7982803195828146413);
void live_f_fun(double *state, double dt, double *out_2888697787837799934);
void live_F_fun(double *state, double dt, double *out_2966344758239569925);
void live_h_4(double *state, double *unused, double *out_5208537724920653314);
void live_H_4(double *state, double *unused, double *out_2841497891759929948);
void live_h_9(double *state, double *unused, double *out_8125118292190319073);
void live_H_9(double *state, double *unused, double *out_2600308245130339303);
void live_h_10(double *state, double *unused, double *out_4918615972068948335);
void live_H_10(double *state, double *unused, double *out_5506397084936987233);
void live_h_12(double *state, double *unused, double *out_5659323724507090237);
void live_H_12(double *state, double *unused, double *out_2220398866712336281);
void live_h_35(double *state, double *unused, double *out_6010867334225541203);
void live_H_35(double *state, double *unused, double *out_525164165612677428);
void live_h_32(double *state, double *unused, double *out_6944251479825218781);
void live_H_32(double *state, double *unused, double *out_276855517012813382);
void live_h_13(double *state, double *unused, double *out_8573864059261893866);
void live_H_13(double *state, double *unused, double *out_1698812653901547110);
void live_h_14(double *state, double *unused, double *out_8125118292190319073);
void live_H_14(double *state, double *unused, double *out_2600308245130339303);
void live_h_33(double *state, double *unused, double *out_6678985265244306357);
void live_H_33(double *state, double *unused, double *out_3675721170251535032);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}