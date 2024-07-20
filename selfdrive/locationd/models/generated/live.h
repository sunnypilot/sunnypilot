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
void live_H(double *in_vec, double *out_5016230871221336976);
void live_err_fun(double *nom_x, double *delta_x, double *out_5032561234954820223);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_7628702518424614071);
void live_H_mod_fun(double *state, double *out_5936276057900918229);
void live_f_fun(double *state, double dt, double *out_7894718411447825024);
void live_F_fun(double *state, double dt, double *out_6912177265995715584);
void live_h_4(double *state, double *unused, double *out_8916029416694195025);
void live_H_4(double *state, double *unused, double *out_8350074684178610628);
void live_h_9(double *state, double *unused, double *out_6653403333976605109);
void live_H_9(double *state, double *unused, double *out_2809450454266493518);
void live_h_10(double *state, double *unused, double *out_918541340996360593);
void live_H_10(double *state, double *unused, double *out_8329946204974122037);
void live_h_12(double *state, double *unused, double *out_4614050823112628579);
void live_H_12(double *state, double *unused, double *out_5077212981498979193);
void live_h_35(double *state, double *unused, double *out_2114289615549349138);
void live_H_35(double *state, double *unused, double *out_2331649949173965484);
void live_h_32(double *state, double *unused, double *out_285597393501893108);
void live_H_32(double *state, double *unused, double *out_2644271644061410512);
void live_h_13(double *state, double *unused, double *out_1279256425300719448);
void live_H_13(double *state, double *unused, double *out_3568707709605355491);
void live_h_14(double *state, double *unused, double *out_6653403333976605109);
void live_H_14(double *state, double *unused, double *out_2809450454266493518);
void live_h_33(double *state, double *unused, double *out_8814764392384913901);
void live_H_33(double *state, double *unused, double *out_3579450327519476008);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}