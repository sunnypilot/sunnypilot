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
void live_H(double *in_vec, double *out_8203131164402972389);
void live_err_fun(double *nom_x, double *delta_x, double *out_1957522185556653502);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_2218034120604549013);
void live_H_mod_fun(double *state, double *out_5892505030250534795);
void live_f_fun(double *state, double dt, double *out_6366066928495396638);
void live_F_fun(double *state, double dt, double *out_5260294225347430873);
void live_h_4(double *state, double *unused, double *out_9136075254134184284);
void live_H_4(double *state, double *unused, double *out_6706164734653291533);
void live_h_9(double *state, double *unused, double *out_6537610669533985347);
void live_H_9(double *state, double *unused, double *out_6947354381282882178);
void live_h_10(double *state, double *unused, double *out_7452618607263494130);
void live_H_10(double *state, double *unused, double *out_5225212987013231017);
void live_h_12(double *state, double *unused, double *out_6305006523324619448);
void live_H_12(double *state, double *unused, double *out_6721122931024298288);
void live_h_35(double *state, double *unused, double *out_8119733230946222476);
void live_H_35(double *state, double *unused, double *out_3975559898699284579);
void live_h_32(double *state, double *unused, double *out_2598739843097813655);
void live_H_32(double *state, double *unused, double *out_1191901734280866986);
void live_h_13(double *state, double *unused, double *out_4789517878592471353);
void live_H_13(double *state, double *unused, double *out_8146386519211414745);
void live_h_14(double *state, double *unused, double *out_6537610669533985347);
void live_H_14(double *state, double *unused, double *out_6947354381282882178);
void live_h_33(double *state, double *unused, double *out_3677023698050406213);
void live_H_33(double *state, double *unused, double *out_825002894060426975);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}