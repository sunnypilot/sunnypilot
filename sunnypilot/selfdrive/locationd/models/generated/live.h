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
void live_H(double *in_vec, double *out_8874922630666386083);
void live_err_fun(double *nom_x, double *delta_x, double *out_4092011894738148064);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_3610681842829238307);
void live_H_mod_fun(double *state, double *out_5130319966296730339);
void live_f_fun(double *state, double dt, double *out_2214310859129023564);
void live_F_fun(double *state, double dt, double *out_5189144399212336154);
void live_h_4(double *state, double *unused, double *out_2270301433724479071);
void live_H_4(double *state, double *unused, double *out_4383608305887641023);
void live_h_9(double *state, double *unused, double *out_5090521756221145653);
void live_H_9(double *state, double *unused, double *out_4142418659258050378);
void live_h_10(double *state, double *unused, double *out_837165052252734010);
void live_H_10(double *state, double *unused, double *out_4469280347783546814);
void live_h_12(double *state, double *unused, double *out_3159041758780058505);
void live_H_12(double *state, double *unused, double *out_635848102144320772);
void live_h_35(double *state, double *unused, double *out_3376748813005317724);
void live_H_35(double *state, double *unused, double *out_1016946248515033647);
void live_h_32(double *state, double *unused, double *out_5345980412713574382);
void live_H_32(double *state, double *unused, double *out_3068789439581889453);
void live_h_13(double *state, double *unused, double *out_4372932640088220902);
void live_H_13(double *state, double *unused, double *out_8946465295904744819);
void live_h_14(double *state, double *unused, double *out_5090521756221145653);
void live_H_14(double *state, double *unused, double *out_4142418659258050378);
void live_h_33(double *state, double *unused, double *out_7657234243024747873);
void live_H_33(double *state, double *unused, double *out_2133610756123823957);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}