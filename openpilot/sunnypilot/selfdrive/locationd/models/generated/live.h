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
void live_H(double *in_vec, double *out_4922214811027217685);
void live_err_fun(double *nom_x, double *delta_x, double *out_7434125209633488399);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_1376336959776558370);
void live_H_mod_fun(double *state, double *out_8801007618684466748);
void live_f_fun(double *state, double dt, double *out_3269391286936835133);
void live_F_fun(double *state, double dt, double *out_2711488877295008015);
void live_h_4(double *state, double *unused, double *out_2259820625927437819);
void live_H_4(double *state, double *unused, double *out_1708880319344801415);
void live_h_9(double *state, double *unused, double *out_7001809530031144101);
void live_H_9(double *state, double *unused, double *out_1950069965974392060);
void live_h_10(double *state, double *unused, double *out_6133210041243969029);
void live_H_10(double *state, double *unused, double *out_4718735531010379103);
void live_h_12(double *state, double *unused, double *out_601969928710242479);
void live_H_12(double *state, double *unused, double *out_6728336727376763210);
void live_h_35(double *state, double *unused, double *out_3447771954735638656);
void live_H_35(double *state, double *unused, double *out_5075542376717408791);
void live_h_32(double *state, double *unused, double *out_6586402662949442783);
void live_H_32(double *state, double *unused, double *out_7016380714050417592);
void live_h_13(double *state, double *unused, double *out_8899300894619263614);
void live_H_13(double *state, double *unused, double *out_8828197360342113585);
void live_h_14(double *state, double *unused, double *out_7001809530031144101);
void live_H_14(double *state, double *unused, double *out_1950069965974392060);
void live_h_33(double *state, double *unused, double *out_101115914477833922);
void live_H_33(double *state, double *unused, double *out_8226099381356266395);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}