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
void live_H(double *in_vec, double *out_6574843044755662276);
void live_err_fun(double *nom_x, double *delta_x, double *out_1575979086870887545);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_6506776409850105096);
void live_H_mod_fun(double *state, double *out_5856833465841616276);
void live_f_fun(double *state, double dt, double *out_2159418628523068413);
void live_F_fun(double *state, double dt, double *out_6328431180555769297);
void live_h_4(double *state, double *unused, double *out_28415465931567147);
void live_H_4(double *state, double *unused, double *out_7924499476379241845);
void live_h_9(double *state, double *unused, double *out_7591785345487952686);
void live_H_9(double *state, double *unused, double *out_7683309829749651200);
void live_h_10(double *state, double *unused, double *out_77538467729374005);
void live_H_10(double *state, double *unused, double *out_2161526107976246779);
void live_h_12(double *state, double *unused, double *out_5140514060197600805);
void live_H_12(double *state, double *unused, double *out_2905043068347280050);
void live_h_35(double *state, double *unused, double *out_5096424971374996650);
void live_H_35(double *state, double *unused, double *out_4557837419006634469);
void live_h_32(double *state, double *unused, double *out_7250233404591987997);
void live_H_32(double *state, double *unused, double *out_1243466953200978089);
void live_h_13(double *state, double *unused, double *out_3309697738183265489);
void live_H_13(double *state, double *unused, double *out_6233964999209152223);
void live_h_14(double *state, double *unused, double *out_7591785345487952686);
void live_H_14(double *state, double *unused, double *out_7683309829749651200);
void live_h_33(double *state, double *unused, double *out_1052640795815345304);
void live_H_33(double *state, double *unused, double *out_1407280414367776865);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}