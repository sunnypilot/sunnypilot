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
void live_H(double *in_vec, double *out_604043209846572052);
void live_err_fun(double *nom_x, double *delta_x, double *out_5815918021574383256);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_405016028537791310);
void live_H_mod_fun(double *state, double *out_6060298500008698159);
void live_f_fun(double *state, double dt, double *out_234054100436222404);
void live_F_fun(double *state, double dt, double *out_98640869369304068);
void live_h_4(double *state, double *unused, double *out_1697093702201744346);
void live_H_4(double *state, double *unused, double *out_643021930242067437);
void live_h_9(double *state, double *unused, double *out_2936430445939327715);
void live_H_9(double *state, double *unused, double *out_401832283612476792);
void live_h_10(double *state, double *unused, double *out_4514559468563206809);
void live_H_10(double *state, double *unused, double *out_1343937887048594844);
void live_h_12(double *state, double *unused, double *out_4782454166066213906);
void live_H_12(double *state, double *unused, double *out_4376434477789894358);
void live_h_35(double *state, double *unused, double *out_973169168518443631);
void live_H_35(double *state, double *unused, double *out_7121997510114908067);
void live_h_32(double *state, double *unused, double *out_7758322852165358824);
void live_H_32(double *state, double *unused, double *out_207133006420791711);
void live_h_13(double *state, double *unused, double *out_7312642582867837773);
void live_H_13(double *state, double *unused, double *out_8325270915890510603);
void live_h_14(double *state, double *unused, double *out_2936430445939327715);
void live_H_14(double *state, double *unused, double *out_401832283612476792);
void live_h_33(double *state, double *unused, double *out_1511145513146314395);
void live_H_33(double *state, double *unused, double *out_8174189558955785945);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}