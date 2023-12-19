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
void live_H(double *in_vec, double *out_4549882242449710464);
void live_err_fun(double *nom_x, double *delta_x, double *out_8967192143908981963);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_27256379367550061);
void live_H_mod_fun(double *state, double *out_4824081692195624245);
void live_f_fun(double *state, double dt, double *out_2925287045854594900);
void live_F_fun(double *state, double dt, double *out_3843924678963003983);
void live_h_4(double *state, double *unused, double *out_4595523822163121539);
void live_H_4(double *state, double *unused, double *out_4041185209348209430);
void live_h_9(double *state, double *unused, double *out_8234121719314103006);
void live_H_9(double *state, double *unused, double *out_115982527006568053);
void live_h_10(double *state, double *unused, double *out_7026349636546874626);
void live_H_10(double *state, double *unused, double *out_9081879764692710014);
void live_h_12(double *state, double *unused, double *out_5365386081988364470);
void live_H_12(double *state, double *unused, double *out_4662284234395803097);
void live_h_35(double *state, double *unused, double *out_6678787183634411294);
void live_H_35(double *state, double *unused, double *out_7407847266720816806);
void live_h_32(double *state, double *unused, double *out_2417329670678050885);
void live_H_32(double *state, double *unused, double *out_3367483271847903307);
void live_h_13(double *state, double *unused, double *out_5805477272828296767);
void live_H_13(double *state, double *unused, double *out_1027302974098499320);
void live_h_14(double *state, double *unused, double *out_8234121719314103006);
void live_H_14(double *state, double *unused, double *out_115982527006568053);
void live_h_33(double *state, double *unused, double *out_7147939535237127299);
void live_H_33(double *state, double *unused, double *out_7888339802349877206);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}