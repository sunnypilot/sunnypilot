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
void live_H(double *in_vec, double *out_60055599982763171);
void live_err_fun(double *nom_x, double *delta_x, double *out_2890310553193968983);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_5964322799655509379);
void live_H_mod_fun(double *state, double *out_4103618298147941781);
void live_f_fun(double *state, double dt, double *out_565895874060121939);
void live_F_fun(double *state, double dt, double *out_8349867893640015586);
void live_h_4(double *state, double *unused, double *out_544511329400754313);
void live_H_4(double *state, double *unused, double *out_4156932733994318606);
void live_h_9(double *state, double *unused, double *out_4735757724495822498);
void live_H_9(double *state, double *unused, double *out_7002592404450785540);
void live_h_10(double *state, double *unused, double *out_8030119702667863507);
void live_H_10(double *state, double *unused, double *out_4542302805244622984);
void live_h_12(double *state, double *unused, double *out_3053709128935159890);
void live_H_12(double *state, double *unused, double *out_2224325643048414390);
void live_h_35(double *state, double *unused, double *out_5408671365165603736);
void live_H_35(double *state, double *unused, double *out_6524791899358257506);
void live_h_32(double *state, double *unused, double *out_7317752695546348775);
void live_H_32(double *state, double *unused, double *out_3819767386456507569);
void live_h_13(double *state, double *unused, double *out_409451640935608624);
void live_H_13(double *state, double *unused, double *out_8833677818440145415);
void live_h_14(double *state, double *unused, double *out_4735757724495822498);
void live_H_14(double *state, double *unused, double *out_7002592404450785540);
void live_h_33(double *state, double *unused, double *out_412744366635792256);
void live_H_33(double *state, double *unused, double *out_3374234894719399902);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}