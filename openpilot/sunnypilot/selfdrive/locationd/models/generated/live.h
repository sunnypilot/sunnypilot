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
void live_H(double *in_vec, double *out_2772122295686760629);
void live_err_fun(double *nom_x, double *delta_x, double *out_6423955222691101398);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_719794691562319521);
void live_H_mod_fun(double *state, double *out_126498273849915804);
void live_f_fun(double *state, double dt, double *out_309423444720901128);
void live_F_fun(double *state, double dt, double *out_1032010961160371620);
void live_h_4(double *state, double *unused, double *out_390901647692918293);
void live_H_4(double *state, double *unused, double *out_5503350273553476542);
void live_h_9(double *state, double *unused, double *out_7608991673321319985);
void live_H_9(double *state, double *unused, double *out_5262160626923885897);
void live_h_10(double *state, double *unused, double *out_1303176786126841938);
void live_H_10(double *state, double *unused, double *out_163299894457592615);
void live_h_12(double *state, double *unused, double *out_9079169607037095226);
void live_H_12(double *state, double *unused, double *out_483893865521514747);
void live_h_35(double *state, double *unused, double *out_2930488141765413477);
void live_H_35(double *state, double *unused, double *out_2261669166803498962);
void live_h_32(double *state, double *unused, double *out_2212806671509093227);
void live_H_32(double *state, double *unused, double *out_2079335608929607926);
void live_h_13(double *state, double *unused, double *out_1599053777318742698);
void live_H_13(double *state, double *unused, double *out_4211853044970865788);
void live_h_14(double *state, double *unused, double *out_7608991673321319985);
void live_H_14(double *state, double *unused, double *out_5262160626923885897);
void live_h_33(double *state, double *unused, double *out_4867598165434144742);
void live_H_33(double *state, double *unused, double *out_5412226171442356566);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}