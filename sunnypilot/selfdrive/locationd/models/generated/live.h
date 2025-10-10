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
void live_H(double *in_vec, double *out_2228758734077453113);
void live_err_fun(double *nom_x, double *delta_x, double *out_6109722366019468224);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_8198973285533712309);
void live_H_mod_fun(double *state, double *out_7958592863135401902);
void live_f_fun(double *state, double dt, double *out_1637479678516278702);
void live_F_fun(double *state, double dt, double *out_2036482552630167662);
void live_h_4(double *state, double *unused, double *out_210442290815034510);
void live_H_4(double *state, double *unused, double *out_5089203552383187410);
void live_h_9(double *state, double *unused, double *out_6633813031196510122);
void live_H_9(double *state, double *unused, double *out_4848013905753596765);
void live_h_10(double *state, double *unused, double *out_6664581404598303595);
void live_H_10(double *state, double *unused, double *out_6913007481273030652);
void live_h_12(double *state, double *unused, double *out_633841989663505737);
void live_H_12(double *state, double *unused, double *out_69747144351225615);
void live_h_35(double *state, double *unused, double *out_963417644154310879);
void live_H_35(double *state, double *unused, double *out_1722541495010580034);
void live_h_32(double *state, double *unused, double *out_6379816265712720048);
void live_H_32(double *state, double *unused, double *out_4609022917859034530);
void live_h_13(double *state, double *unused, double *out_6341279531986591003);
void live_H_13(double *state, double *unused, double *out_2242902093036612449);
void live_h_14(double *state, double *unused, double *out_6633813031196510122);
void live_H_14(double *state, double *unused, double *out_4848013905753596765);
void live_h_33(double *state, double *unused, double *out_6554272421620977698);
void live_H_33(double *state, double *unused, double *out_1428015509628277570);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}