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
void live_H(double *in_vec, double *out_285400171142782786);
void live_err_fun(double *nom_x, double *delta_x, double *out_2436896259464335423);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_8871984062805370648);
void live_H_mod_fun(double *state, double *out_8228926511208625476);
void live_f_fun(double *state, double dt, double *out_4538780046133425309);
void live_F_fun(double *state, double dt, double *out_417010570473098233);
void live_h_4(double *state, double *unused, double *out_2309729505615761905);
void live_H_4(double *state, double *unused, double *out_8886506882666231613);
void live_h_9(double *state, double *unused, double *out_1348765263594904281);
void live_H_9(double *state, double *unused, double *out_8645317236036640968);
void live_h_10(double *state, double *unused, double *out_7251990229046891328);
void live_H_10(double *state, double *unused, double *out_2812694342253054382);
void live_h_12(double *state, double *unused, double *out_1162751087914723431);
void live_H_12(double *state, double *unused, double *out_3867050474634269818);
void live_h_35(double *state, double *unused, double *out_1137082034917540827);
void live_H_35(double *state, double *unused, double *out_5519844825293624237);
void live_h_32(double *state, double *unused, double *out_7169859216053261212);
void live_H_32(double *state, double *unused, double *out_7164684335004523839);
void live_h_13(double *state, double *unused, double *out_4721203745943767592);
void live_H_13(double *state, double *unused, double *out_6086407052825232130);
void live_h_14(double *state, double *unused, double *out_1348765263594904281);
void live_H_14(double *state, double *unused, double *out_8645317236036640968);
void live_h_33(double *state, double *unused, double *out_859896650697914554);
void live_H_33(double *state, double *unused, double *out_2369287820654766633);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}