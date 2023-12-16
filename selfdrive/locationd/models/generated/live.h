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
void live_H(double *in_vec, double *out_6723270188322560730);
void live_err_fun(double *nom_x, double *delta_x, double *out_4473607639701987721);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_4669519886941048090);
void live_H_mod_fun(double *state, double *out_5199872580074790941);
void live_f_fun(double *state, double dt, double *out_600262745402749110);
void live_F_fun(double *state, double dt, double *out_5123365299883911278);
void live_h_4(double *state, double *unused, double *out_4387115819840874865);
void live_H_4(double *state, double *unused, double *out_9026498161771385970);
void live_h_9(double *state, double *unused, double *out_428366524812042299);
void live_H_9(double *state, double *unused, double *out_9179056265308575001);
void live_h_10(double *state, double *unused, double *out_132396485967147845);
void live_H_10(double *state, double *unused, double *out_8768831841606438093);
void live_h_12(double *state, double *unused, double *out_4720485780193781256);
void live_H_12(double *state, double *unused, double *out_4400789503906203851);
void live_h_35(double *state, double *unused, double *out_6828849116840194903);
void live_H_35(double *state, double *unused, double *out_1655226471581190142);
void live_h_32(double *state, double *unused, double *out_808476979379320652);
void live_H_32(double *state, double *unused, double *out_5996231247314297030);
void live_h_13(double *state, double *unused, double *out_6513017278277276756);
void live_H_13(double *state, double *unused, double *out_4863404896131074);
void live_h_14(double *state, double *unused, double *out_428366524812042299);
void live_H_14(double *state, double *unused, double *out_9179056265308575001);
void live_h_33(double *state, double *unused, double *out_782504987709470049);
void live_H_33(double *state, double *unused, double *out_2903026849926700666);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}