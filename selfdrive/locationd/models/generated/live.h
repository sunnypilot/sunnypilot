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
void live_H(double *in_vec, double *out_1705590173802957792);
void live_err_fun(double *nom_x, double *delta_x, double *out_2360402206574617959);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_4539811509280113021);
void live_H_mod_fun(double *state, double *out_3998354333387872453);
void live_f_fun(double *state, double dt, double *out_6164175281085870497);
void live_F_fun(double *state, double dt, double *out_4815907768218277041);
void live_h_4(double *state, double *unused, double *out_7961739201317865100);
void live_H_4(double *state, double *unused, double *out_4351790703970074386);
void live_h_9(double *state, double *unused, double *out_6666237163126750011);
void live_H_9(double *state, double *unused, double *out_4592980350599665031);
void live_h_10(double *state, double *unused, double *out_3295456728395727948);
void live_H_10(double *state, double *unused, double *out_2761766956048973774);
void live_h_12(double *state, double *unused, double *out_6229943248680522981);
void live_H_12(double *state, double *unused, double *out_9075496961707515435);
void live_h_35(double *state, double *unused, double *out_4958689945564525375);
void live_H_35(double *state, double *unused, double *out_6329933929382501726);
void live_h_32(double *state, double *unused, double *out_410212729802688028);
void live_H_32(double *state, double *unused, double *out_972416037003074665);
void live_h_13(double *state, double *unused, double *out_4031627545452802049);
void live_H_13(double *state, double *unused, double *out_1643735551917084066);
void live_h_14(double *state, double *unused, double *out_6666237163126750011);
void live_H_14(double *state, double *unused, double *out_4592980350599665031);
void live_h_33(double *state, double *unused, double *out_1039274227832299569);
void live_H_33(double *state, double *unused, double *out_3179376924743644122);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}