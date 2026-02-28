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
void live_H(double *in_vec, double *out_7940008779561346579);
void live_err_fun(double *nom_x, double *delta_x, double *out_4356908199141187096);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_7462466927673472652);
void live_H_mod_fun(double *state, double *out_6035666987448830151);
void live_f_fun(double *state, double dt, double *out_6088395859798878017);
void live_F_fun(double *state, double dt, double *out_129130950091074990);
void live_h_4(double *state, double *unused, double *out_4296089219630731783);
void live_H_4(double *state, double *unused, double *out_5578297719609831410);
void live_h_9(double *state, double *unused, double *out_8286363450814908849);
void live_H_9(double *state, double *unused, double *out_5581227418835272736);
void live_h_10(double *state, double *unused, double *out_3355184863950689108);
void live_H_10(double *state, double *unused, double *out_2376774004631062580);
void live_h_12(double *state, double *unused, double *out_5664618317210899058);
void live_H_12(double *state, double *unused, double *out_802960657432901586);
void live_h_35(double *state, double *unused, double *out_1379084731878268664);
void live_H_35(double *state, double *unused, double *out_1942602374892112123);
void live_h_32(double *state, double *unused, double *out_7438364445163062736);
void live_H_32(double *state, double *unused, double *out_2398402400840994765);
void live_h_13(double *state, double *unused, double *out_3382034717119816688);
void live_H_13(double *state, double *unused, double *out_7605206871927944164);
void live_h_14(double *state, double *unused, double *out_8286363450814908849);
void live_H_14(double *state, double *unused, double *out_5581227418835272736);
void live_h_33(double *state, double *unused, double *out_2022790126819529762);
void live_H_33(double *state, double *unused, double *out_5093159379530969727);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}