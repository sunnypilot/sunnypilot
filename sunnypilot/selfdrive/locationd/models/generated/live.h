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
void live_H(double *in_vec, double *out_4525523317234808222);
void live_err_fun(double *nom_x, double *delta_x, double *out_7138208668679610358);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_3307709339563338493);
void live_H_mod_fun(double *state, double *out_1864781167376667639);
void live_f_fun(double *state, double dt, double *out_2449424950935866129);
void live_F_fun(double *state, double dt, double *out_2603449106570772975);
void live_h_4(double *state, double *unused, double *out_7893101065619996125);
void live_H_4(double *state, double *unused, double *out_1306552893182037148);
void live_h_9(double *state, double *unused, double *out_9871292012933694);
void live_H_9(double *state, double *unused, double *out_1065363246552446503);
void live_h_10(double *state, double *unused, double *out_5425693842452838702);
void live_H_10(double *state, double *unused, double *out_5990727075293735464);
void live_h_12(double *state, double *unused, double *out_8690976610146208597);
void live_H_12(double *state, double *unused, double *out_3712903514849924647);
void live_h_35(double *state, double *unused, double *out_1294366448589926883);
void live_H_35(double *state, double *unused, double *out_6458466547174938356);
void live_h_32(double *state, double *unused, double *out_2077769351407935424);
void live_H_32(double *state, double *unused, double *out_2117461771441831468);
void live_h_13(double *state, double *unused, double *out_2901512021675294468);
void live_H_13(double *state, double *unused, double *out_3138151074213774646);
void live_h_14(double *state, double *unused, double *out_9871292012933694);
void live_H_14(double *state, double *unused, double *out_1065363246552446503);
void live_h_33(double *state, double *unused, double *out_5634273569944497788);
void live_H_33(double *state, double *unused, double *out_8837720521895755656);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}