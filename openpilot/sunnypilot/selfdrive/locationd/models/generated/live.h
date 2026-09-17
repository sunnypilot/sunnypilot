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
void live_H(double *in_vec, double *out_6359227913389949712);
void live_err_fun(double *nom_x, double *delta_x, double *out_5070973522734377332);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_1504386229041325813);
void live_H_mod_fun(double *state, double *out_8604409008290842398);
void live_f_fun(double *state, double dt, double *out_122542228347959485);
void live_F_fun(double *state, double dt, double *out_4079892232653715769);
void live_h_4(double *state, double *unused, double *out_5353206138509165465);
void live_H_4(double *state, double *unused, double *out_3934719090872387589);
void live_h_9(double *state, double *unused, double *out_8807055816776463374);
void live_H_9(double *state, double *unused, double *out_7224806047572716557);
void live_h_10(double *state, double *unused, double *out_2897072850418891434);
void live_H_10(double *state, double *unused, double *out_2938213750100159528);
void live_h_12(double *state, double *unused, double *out_6098799151588263013);
void live_H_12(double *state, double *unused, double *out_2446539286170345407);
void live_h_35(double *state, double *unused, double *out_1955422699431481948);
void live_H_35(double *state, double *unused, double *out_299023746154668302);
void live_h_32(double *state, double *unused, double *out_8406014722897533998);
void live_H_32(double *state, double *unused, double *out_7432545933185735434);
void live_h_13(double *state, double *unused, double *out_9104729345260618237);
void live_H_13(double *state, double *unused, double *out_4844093272925809884);
void live_h_14(double *state, double *unused, double *out_8807055816776463374);
void live_H_14(double *state, double *unused, double *out_7224806047572716557);
void live_h_33(double *state, double *unused, double *out_563456123860700114);
void live_H_33(double *state, double *unused, double *out_948776632190842222);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}