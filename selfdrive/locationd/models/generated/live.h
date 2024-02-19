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
void live_H(double *in_vec, double *out_4640959636948014038);
void live_err_fun(double *nom_x, double *delta_x, double *out_7467068823118735973);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_8618272779433270887);
void live_H_mod_fun(double *state, double *out_5706763310066995728);
void live_f_fun(double *state, double dt, double *out_5212913569150379461);
void live_F_fun(double *state, double dt, double *out_6547933205693937135);
void live_h_4(double *state, double *unused, double *out_7224261667833738994);
void live_H_4(double *state, double *unused, double *out_8970320576934456300);
void live_h_9(double *state, double *unused, double *out_5186807139601691025);
void live_H_9(double *state, double *unused, double *out_2189204561510647846);
void live_h_10(double *state, double *unused, double *out_1082825965162285702);
void live_H_10(double *state, double *unused, double *out_9016189941414358059);
void live_h_12(double *state, double *unused, double *out_4470135640924812660);
void live_H_12(double *state, double *unused, double *out_2589062199891723304);
void live_h_35(double *state, double *unused, double *out_5450177788933746815);
void live_H_35(double *state, double *unused, double *out_1711404056418119812);
void live_h_32(double *state, double *unused, double *out_2945518167078691846);
void live_H_32(double *state, double *unused, double *out_7310814469285202045);
void live_h_13(double *state, double *unused, double *out_3709304441405941971);
void live_H_13(double *state, double *unused, double *out_8569683698395746195);
void live_h_14(double *state, double *unused, double *out_5186807139601691025);
void live_H_14(double *state, double *unused, double *out_2189204561510647846);
void live_h_33(double *state, double *unused, double *out_1775299852095496333);
void live_H_33(double *state, double *unused, double *out_1439152948220737792);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}