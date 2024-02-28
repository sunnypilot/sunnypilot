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
void live_H(double *in_vec, double *out_2415049526793919177);
void live_err_fun(double *nom_x, double *delta_x, double *out_5706196193000060940);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_9108926703744599702);
void live_H_mod_fun(double *state, double *out_356631414366813232);
void live_f_fun(double *state, double dt, double *out_5027381194713311062);
void live_F_fun(double *state, double dt, double *out_5217270752603122383);
void live_h_4(double *state, double *unused, double *out_789589776125981279);
void live_H_4(double *state, double *unused, double *out_825267899877829898);
void live_h_9(double *state, double *unused, double *out_8663557896534859446);
void live_H_9(double *state, double *unused, double *out_8112486835142277368);
void live_h_10(double *state, double *unused, double *out_8481479358874119979);
void live_H_10(double *state, double *unused, double *out_6374112915837094334);
void live_h_12(double *state, double *unused, double *out_1390983478288120705);
void live_H_12(double *state, double *unused, double *out_5844724307909791693);
void live_h_35(double *state, double *unused, double *out_2887837786894849450);
void live_H_35(double *state, double *unused, double *out_4191929957250437274);
void live_h_32(double *state, double *unused, double *out_330172238438964287);
void live_H_32(double *state, double *unused, double *out_6132768294583446075);
void live_h_13(double *state, double *unused, double *out_4851542858045015951);
void live_H_13(double *state, double *unused, double *out_7388294089885170243);
void live_h_14(double *state, double *unused, double *out_8663557896534859446);
void live_H_14(double *state, double *unused, double *out_8112486835142277368);
void live_h_33(double *state, double *unused, double *out_5781095539931626463);
void live_H_33(double *state, double *unused, double *out_7342486961889294878);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}