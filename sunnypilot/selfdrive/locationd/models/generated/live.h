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
void live_H(double *in_vec, double *out_2884062108576855753);
void live_err_fun(double *nom_x, double *delta_x, double *out_5754484068726251283);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_3209734680695816841);
void live_H_mod_fun(double *state, double *out_7909147060255810501);
void live_f_fun(double *state, double dt, double *out_3690091277228807057);
void live_F_fun(double *state, double dt, double *out_2364606859518544678);
void live_h_4(double *state, double *unused, double *out_1295966562003973919);
void live_H_4(double *state, double *unused, double *out_1418004677013811315);
void live_h_9(double *state, double *unused, double *out_6825359843578642937);
void live_H_9(double *state, double *unused, double *out_1659194323643401960);
void live_h_10(double *state, double *unused, double *out_1968731444852486887);
void live_H_10(double *state, double *unused, double *out_1066863405941491734);
void live_h_12(double *state, double *unused, double *out_4499868113111901212);
void live_H_12(double *state, double *unused, double *out_6437461085045773110);
void live_h_35(double *state, double *unused, double *out_3606982398195821507);
void live_H_35(double *state, double *unused, double *out_9183024117370786819);
void live_h_32(double *state, double *unused, double *out_3414172523695010280);
void live_H_32(double *state, double *unused, double *out_4842019341637679931);
void live_h_13(double *state, double *unused, double *out_3710238881737182179);
void live_H_13(double *state, double *unused, double *out_1836792817501779739);
void live_h_14(double *state, double *unused, double *out_6825359843578642937);
void live_H_14(double *state, double *unused, double *out_1659194323643401960);
void live_h_33(double *state, double *unused, double *out_1401607201477917749);
void live_H_33(double *state, double *unused, double *out_7935223739025276295);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}