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
void live_H(double *in_vec, double *out_6108960324934765761);
void live_err_fun(double *nom_x, double *delta_x, double *out_5138688319610964290);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_6257573199628817064);
void live_H_mod_fun(double *state, double *out_8083599239921719366);
void live_f_fun(double *state, double dt, double *out_7643793919602016258);
void live_F_fun(double *state, double dt, double *out_4260521617827134546);
void live_h_4(double *state, double *unused, double *out_2452644479399717823);
void live_H_4(double *state, double *unused, double *out_1161040572896477752);
void live_h_9(double *state, double *unused, double *out_4605071760982415093);
void live_H_9(double *state, double *unused, double *out_5318208309251255235);
void live_h_10(double *state, double *unused, double *out_7166915440040899603);
void live_H_10(double *state, double *unused, double *out_2424141324741574485);
void live_h_12(double *state, double *unused, double *out_7882416310371039195);
void live_H_12(double *state, double *unused, double *out_539941547848884085);
void live_h_35(double *state, double *unused, double *out_5434439103979294343);
void live_H_35(double *state, double *unused, double *out_2205621484476129624);
void live_h_32(double *state, double *unused, double *out_5159489016614781586);
void live_H_32(double *state, double *unused, double *out_4989279648894547217);
void live_h_13(double *state, double *unused, double *out_4317302593675431351);
void live_H_13(double *state, double *unused, double *out_6114239333584977353);
void live_h_14(double *state, double *unused, double *out_4605071760982415093);
void live_H_14(double *state, double *unused, double *out_5318208309251255235);
void live_h_33(double *state, double *unused, double *out_7683866618272313142);
void live_H_33(double *state, double *unused, double *out_5356178489114987228);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}