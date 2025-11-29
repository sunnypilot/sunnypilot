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
void live_H(double *in_vec, double *out_827124386819761729);
void live_err_fun(double *nom_x, double *delta_x, double *out_5564457952994238716);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_4345509955271185666);
void live_H_mod_fun(double *state, double *out_4553690809255114721);
void live_f_fun(double *state, double dt, double *out_1977540408261569041);
void live_F_fun(double *state, double dt, double *out_8827070574154083013);
void live_h_4(double *state, double *unused, double *out_5856114628081821521);
void live_H_4(double *state, double *unused, double *out_3852960919939615670);
void live_h_9(double *state, double *unused, double *out_6403239387410293303);
void live_H_9(double *state, double *unused, double *out_7306564218505488476);
void live_h_10(double *state, double *unused, double *out_6311422882439654221);
void live_H_10(double *state, double *unused, double *out_1384821160768268928);
void live_h_12(double *state, double *unused, double *out_5077834633409350671);
void live_H_12(double *state, double *unused, double *out_2528297457103117326);
void live_h_35(double *state, double *unused, double *out_5125264146745561455);
void live_H_35(double *state, double *unused, double *out_7219622977312223046);
void live_h_32(double *state, double *unused, double *out_5394098549070521486);
void live_H_32(double *state, double *unused, double *out_7350787762252963515);
void live_h_13(double *state, double *unused, double *out_3993734890299701610);
void live_H_13(double *state, double *unused, double *out_2261808988462575604);
void live_h_14(double *state, double *unused, double *out_6403239387410293303);
void live_H_14(double *state, double *unused, double *out_7306564218505488476);
void live_h_33(double *state, double *unused, double *out_3633379495551124934);
void live_H_33(double *state, double *unused, double *out_1030534803123614141);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}