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
void live_H(double *in_vec, double *out_6679455493927855498);
void live_err_fun(double *nom_x, double *delta_x, double *out_5695983723643385274);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_3588514270127533634);
void live_H_mod_fun(double *state, double *out_2932919365790274675);
void live_f_fun(double *state, double dt, double *out_2701115054532165792);
void live_F_fun(double *state, double dt, double *out_6818196986365371321);
void live_h_4(double *state, double *unused, double *out_6087431662433136605);
void live_H_4(double *state, double *unused, double *out_5514786257340281372);
void live_h_9(double *state, double *unused, double *out_2582109286623506269);
void live_H_9(double *state, double *unused, double *out_1772432677924166098);
void live_h_10(double *state, double *unused, double *out_6799042237352381141);
void live_H_10(double *state, double *unused, double *out_5943753097742298423);
void live_h_12(double *state, double *unused, double *out_3604405385986132697);
void live_H_12(double *state, double *unused, double *out_495329849308319577);
void live_h_35(double *state, double *unused, double *out_4872927572806614362);
void live_H_35(double *state, double *unused, double *out_2148124199967673996);
void live_h_32(double *state, double *unused, double *out_6345159808346866113);
void live_H_32(double *state, double *unused, double *out_5602637262070841930);
void live_h_13(double *state, double *unused, double *out_5809596461011520025);
void live_H_13(double *state, double *unused, double *out_1024617938041169565);
void live_h_14(double *state, double *unused, double *out_2582109286623506269);
void live_H_14(double *state, double *unused, double *out_1772432677924166098);
void live_h_33(double *state, double *unused, double *out_8352866702288951097);
void live_H_33(double *state, double *unused, double *out_1002432804671183608);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}