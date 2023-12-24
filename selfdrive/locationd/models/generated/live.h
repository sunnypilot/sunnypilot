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
void live_H(double *in_vec, double *out_6543170510918427396);
void live_err_fun(double *nom_x, double *delta_x, double *out_9062015891362533785);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_4758141739877846608);
void live_H_mod_fun(double *state, double *out_2686832696856623219);
void live_f_fun(double *state, double dt, double *out_3822263192861325508);
void live_F_fun(double *state, double dt, double *out_6455895415279509978);
void live_h_4(double *state, double *unused, double *out_3494769867212102904);
void live_H_4(double *state, double *unused, double *out_1451768599627278965);
void live_h_9(double *state, double *unused, double *out_6878791664417266905);
void live_H_9(double *state, double *unused, double *out_1210578952997688320);
void live_h_10(double *state, double *unused, double *out_4380493807452258420);
void live_H_10(double *state, double *unused, double *out_1918065783372193268);
void live_h_12(double *state, double *unused, double *out_1827589486894337029);
void live_H_12(double *state, double *unused, double *out_830669574579685298);
void live_h_35(double *state, double *unused, double *out_8082777464406159763);
void live_H_35(double *state, double *unused, double *out_1914893457745328411);
void live_h_32(double *state, double *unused, double *out_3678648917755286173);
void live_H_32(double *state, double *unused, double *out_7716197829952940969);
void live_h_13(double *state, double *unused, double *out_2018478861536013333);
void live_H_13(double *state, double *unused, double *out_3066565144776721745);
void live_h_14(double *state, double *unused, double *out_6878791664417266905);
void live_H_14(double *state, double *unused, double *out_1210578952997688320);
void live_h_33(double *state, double *unused, double *out_5620049043069576208);
void live_H_33(double *state, double *unused, double *out_5065450462384186015);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}