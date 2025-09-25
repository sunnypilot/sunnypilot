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
void live_H(double *in_vec, double *out_7297609826975921267);
void live_err_fun(double *nom_x, double *delta_x, double *out_4679498904975908567);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_1441875649138372155);
void live_H_mod_fun(double *state, double *out_2920781560814231797);
void live_f_fun(double *state, double dt, double *out_6680759157643157991);
void live_F_fun(double *state, double dt, double *out_1255619877366735487);
void live_h_4(double *state, double *unused, double *out_563215449651170196);
void live_H_4(double *state, double *unused, double *out_1716825727293035721);
void live_h_9(double *state, double *unused, double *out_3183219826328242102);
void live_H_9(double *state, double *unused, double *out_1475636080663445076);
void live_h_10(double *state, double *unused, double *out_8305063963410880429);
void live_H_10(double *state, double *unused, double *out_4444151992447725406);
void live_h_12(double *state, double *unused, double *out_2313401396637817391);
void live_H_12(double *state, double *unused, double *out_3302630680738926074);
void live_h_35(double *state, double *unused, double *out_5753208091518713076);
void live_H_35(double *state, double *unused, double *out_6048193713063939783);
void live_h_32(double *state, double *unused, double *out_1909441066441547943);
void live_H_32(double *state, double *unused, double *out_7041032468266184772);
void live_h_13(double *state, double *unused, double *out_721867829862767928);
void live_H_13(double *state, double *unused, double *out_3642234102767568596);
void live_h_14(double *state, double *unused, double *out_3183219826328242102);
void live_H_14(double *state, double *unused, double *out_1475636080663445076);
void live_h_33(double *state, double *unused, double *out_5764860013277887979);
void live_H_33(double *state, double *unused, double *out_4800393334718429259);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}