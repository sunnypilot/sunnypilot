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
void live_H(double *in_vec, double *out_5452829107469162780);
void live_err_fun(double *nom_x, double *delta_x, double *out_3220790007633989495);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_4938944413096769859);
void live_H_mod_fun(double *state, double *out_3163350226954137755);
void live_f_fun(double *state, double dt, double *out_906380554342107344);
void live_F_fun(double *state, double dt, double *out_8771576855209840709);
void live_h_4(double *state, double *unused, double *out_5673006619389236486);
void live_H_4(double *state, double *unused, double *out_1461864924616712124);
void live_h_9(double *state, double *unused, double *out_2928313839239557547);
void live_H_9(double *state, double *unused, double *out_5825354010647735346);
void live_h_10(double *state, double *unused, double *out_4937947399891705567);
void live_H_10(double *state, double *unused, double *out_6853151491969528711);
void live_h_12(double *state, double *unused, double *out_8953356214902748655);
void live_H_12(double *state, double *unused, double *out_3557591483415249671);
void live_h_35(double *state, double *unused, double *out_2130568491963600512);
void live_H_35(double *state, double *unused, double *out_6303154515740263380);
void live_h_32(double *state, double *unused, double *out_1026443349713726609);
void live_H_32(double *state, double *unused, double *out_6342285185761675678);
void live_h_13(double *state, double *unused, double *out_5536550817418961602);
void live_H_13(double *state, double *unused, double *out_1205943401545293765);
void live_h_14(double *state, double *unused, double *out_2928313839239557547);
void live_H_14(double *state, double *unused, double *out_5825354010647735346);
void live_h_33(double *state, double *unused, double *out_4511517793756921927);
void live_H_33(double *state, double *unused, double *out_8993032553330430632);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}