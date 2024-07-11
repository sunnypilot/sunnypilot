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
void live_H(double *in_vec, double *out_3968303161728917014);
void live_err_fun(double *nom_x, double *delta_x, double *out_2272071300684246652);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_6655513737832844004);
void live_H_mod_fun(double *state, double *out_2664480574346858034);
void live_f_fun(double *state, double dt, double *out_8542317596133478368);
void live_F_fun(double *state, double dt, double *out_5233880457714981627);
void live_h_4(double *state, double *unused, double *out_1805535340821578222);
void live_H_4(double *state, double *unused, double *out_457939828585048603);
void live_h_9(double *state, double *unused, double *out_7913494198600153795);
void live_H_9(double *state, double *unused, double *out_2430921723695030739);
void live_h_10(double *state, double *unused, double *out_7020873721912419500);
void live_H_10(double *state, double *unused, double *out_8002342400431325140);
void live_h_12(double *state, double *unused, double *out_7485619465302991625);
void live_H_12(double *state, double *unused, double *out_7209188485097401889);
void live_h_35(double *state, double *unused, double *out_6730755509285186127);
void live_H_35(double *state, double *unused, double *out_2908722228787558773);
void live_h_32(double *state, double *unused, double *out_5288607499755203334);
void live_H_32(double *state, double *unused, double *out_5708334391868718425);
void live_h_13(double *state, double *unused, double *out_3906968967011231562);
void live_H_13(double *state, double *unused, double *out_4672330112811389025);
void live_h_14(double *state, double *unused, double *out_7913494198600153795);
void live_H_14(double *state, double *unused, double *out_2430921723695030739);
void live_h_33(double *state, double *unused, double *out_6231382423204834291);
void live_H_33(double *state, double *unused, double *out_5341435551648278414);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}