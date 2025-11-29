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
void live_H(double *in_vec, double *out_1090098489363639051);
void live_err_fun(double *nom_x, double *delta_x, double *out_2904082445933943622);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_8407811118329706552);
void live_H_mod_fun(double *state, double *out_2316971058490898802);
void live_f_fun(double *state, double dt, double *out_4209502689207190552);
void live_F_fun(double *state, double dt, double *out_2490194559134001386);
void live_h_4(double *state, double *unused, double *out_1146097256217102184);
void live_H_4(double *state, double *unused, double *out_5674670288399641158);
void live_h_9(double *state, double *unused, double *out_8108499720342732253);
void live_H_9(double *state, double *unused, double *out_5915859935029231803);
void live_h_10(double *state, double *unused, double *out_1646539276755118713);
void live_H_10(double *state, double *unused, double *out_7527411835586412868);
void live_h_12(double *state, double *unused, double *out_8986895127881271157);
void live_H_12(double *state, double *unused, double *out_7752617377277948663);
void live_h_35(double *state, double *unused, double *out_2360858687420662016);
void live_H_35(double *state, double *unused, double *out_5007054344952934954);
void live_h_32(double *state, double *unused, double *out_4221681304362797720);
void live_H_32(double *state, double *unused, double *out_9098684953023509774);
void live_h_13(double *state, double *unused, double *out_1792336774861456961);
void live_H_13(double *state, double *unused, double *out_8566687596917925402);
void live_h_14(double *state, double *unused, double *out_8108499720342732253);
void live_H_14(double *state, double *unused, double *out_5915859935029231803);
void live_h_33(double *state, double *unused, double *out_490807840216425828);
void live_H_33(double *state, double *unused, double *out_1856497340314077350);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}