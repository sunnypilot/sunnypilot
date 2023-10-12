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
void live_H(double *in_vec, double *out_3056451431007154119);
void live_err_fun(double *nom_x, double *delta_x, double *out_1292429367592691243);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_7203208365257071560);
void live_H_mod_fun(double *state, double *out_9109133853090027472);
void live_f_fun(double *state, double dt, double *out_1380210285864909136);
void live_F_fun(double *state, double dt, double *out_2511086909557190022);
void live_h_4(double *state, double *unused, double *out_3141757845879483186);
void live_H_4(double *state, double *unused, double *out_7698807550768287321);
void live_h_9(double *state, double *unused, double *out_9112719790904260094);
void live_H_9(double *state, double *unused, double *out_3460717587676816825);
void live_h_10(double *state, double *unused, double *out_3856818945145830433);
void live_H_10(double *state, double *unused, double *out_43166413901014005);
void live_h_12(double *state, double *unused, double *out_7199739948876887136);
void live_H_12(double *state, double *unused, double *out_1317549173725554325);
void live_h_35(double *state, double *unused, double *out_1452905366377562047);
void live_H_35(double *state, double *unused, double *out_7381274465568656919);
void live_h_32(double *state, double *unused, double *out_5908105993997669270);
void live_H_32(double *state, double *unused, double *out_7250109680627916450);
void live_h_13(double *state, double *unused, double *out_6039507351919823679);
void live_H_13(double *state, double *unused, double *out_3640700776108874079);
void live_h_14(double *state, double *unused, double *out_9112719790904260094);
void live_H_14(double *state, double *unused, double *out_3460717587676816825);
void live_h_33(double *state, double *unused, double *out_8572335191748983603);
void live_H_33(double *state, double *unused, double *out_2815311827705057510);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}