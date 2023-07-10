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
void live_H(double *in_vec, double *out_3454628234171720373);
void live_err_fun(double *nom_x, double *delta_x, double *out_8087679064943425206);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_4504426754731950156);
void live_H_mod_fun(double *state, double *out_762305413404034059);
void live_f_fun(double *state, double dt, double *out_8821406288611470667);
void live_F_fun(double *state, double dt, double *out_266359796230143370);
void live_h_4(double *state, double *unused, double *out_3255905342375760594);
void live_H_4(double *state, double *unused, double *out_221772926452997362);
void live_h_9(double *state, double *unused, double *out_5281234058047696814);
void live_H_9(double *state, double *unused, double *out_7508991861717444832);
void live_h_10(double *state, double *unused, double *out_3725997940119829611);
void live_H_10(double *state, double *unused, double *out_5425411622832804022);
void live_h_12(double *state, double *unused, double *out_1018743334405146622);
void live_H_12(double *state, double *unused, double *out_6159485450589735634);
void live_h_35(double *state, double *unused, double *out_544127603871537797);
void live_H_35(double *state, double *unused, double *out_3588434983825604738);
void live_h_32(double *state, double *unused, double *out_5366371885754649380);
void live_H_32(double *state, double *unused, double *out_2010975429041477495);
void live_h_13(double *state, double *unused, double *out_8661152646959363324);
void live_H_13(double *state, double *unused, double *out_5706544133092284167);
void live_h_14(double *state, double *unused, double *out_5281234058047696814);
void live_H_14(double *state, double *unused, double *out_7508991861717444832);
void live_h_33(double *state, double *unused, double *out_5908015058610712007);
void live_H_33(double *state, double *unused, double *out_4661722796610232449);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}