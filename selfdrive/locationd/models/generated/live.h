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
void live_H(double *in_vec, double *out_7574157216459850782);
void live_err_fun(double *nom_x, double *delta_x, double *out_4055774789120932026);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_4730548230420475348);
void live_H_mod_fun(double *state, double *out_5813799317262680088);
void live_f_fun(double *state, double dt, double *out_8261305250467109423);
void live_F_fun(double *state, double dt, double *out_7969107683281141771);
void live_h_4(double *state, double *unused, double *out_19229563063502244);
void live_H_4(double *state, double *unused, double *out_7119898973221844350);
void live_h_9(double *state, double *unused, double *out_5405768222819323892);
void live_H_9(double *state, double *unused, double *out_167319962042603120);
void live_h_10(double *state, double *unused, double *out_7122991885274472666);
void live_H_10(double *state, double *unused, double *out_8001066680165645977);
void live_h_12(double *state, double *unused, double *out_7324409554195996501);
void live_H_12(double *state, double *unused, double *out_4945586723444974270);
void live_h_35(double *state, double *unused, double *out_4015600202884045942);
void live_H_35(double *state, double *unused, double *out_3753236915849236974);
void live_h_32(double *state, double *unused, double *out_8212171515907450875);
void live_H_32(double *state, double *unused, double *out_1812398578516228173);
void live_h_13(double *state, double *unused, double *out_4851467518136304959);
void live_H_13(double *state, double *unused, double *out_1024824958168971694);
void live_h_14(double *state, double *unused, double *out_5405768222819323892);
void live_H_14(double *state, double *unused, double *out_167319962042603120);
void live_h_33(double *state, double *unused, double *out_3544878753551304046);
void live_H_33(double *state, double *unused, double *out_6443349377424477455);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}