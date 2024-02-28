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
void live_H(double *in_vec, double *out_448016370503331297);
void live_err_fun(double *nom_x, double *delta_x, double *out_1664245642397186294);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_7089911323146907467);
void live_H_mod_fun(double *state, double *out_6934058908312638129);
void live_f_fun(double *state, double dt, double *out_2052326614994539115);
void live_F_fun(double *state, double dt, double *out_3700548427962440926);
void live_h_4(double *state, double *unused, double *out_2954863483610746457);
void live_H_4(double *state, double *unused, double *out_8605248598983381251);
void live_h_9(double *state, double *unused, double *out_4006723233842345991);
void live_H_9(double *state, double *unused, double *out_1318029663718933781);
void live_h_10(double *state, double *unused, double *out_983054053526589981);
void live_H_10(double *state, double *unused, double *out_8470955799509441157);
void live_h_12(double *state, double *unused, double *out_889662796816291576);
void live_H_12(double *state, double *unused, double *out_3460237097683437369);
void live_h_35(double *state, double *unused, double *out_1539433618062132231);
void live_H_35(double *state, double *unused, double *out_840229158626405747);
void live_h_32(double *state, double *unused, double *out_8198149920719328221);
void live_H_32(double *state, double *unused, double *out_6883426051321673477);
void live_h_13(double *state, double *unused, double *out_5269332807279174469);
void live_H_13(double *state, double *unused, double *out_3916234011707655409);
void live_h_14(double *state, double *unused, double *out_4006723233842345991);
void live_H_14(double *state, double *unused, double *out_1318029663718933781);
void live_h_33(double *state, double *unused, double *out_7028159383484897449);
void live_H_33(double *state, double *unused, double *out_9090386939062242934);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}