#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_6859609651364947806);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_1490819210114812961);
void pose_H_mod_fun(double *state, double *out_1066489817404091299);
void pose_f_fun(double *state, double dt, double *out_5163101270829834523);
void pose_F_fun(double *state, double dt, double *out_2904788492881068911);
void pose_h_4(double *state, double *unused, double *out_7771273734247816938);
void pose_H_4(double *state, double *unused, double *out_6914571624156050020);
void pose_h_10(double *state, double *unused, double *out_6177822575693060145);
void pose_H_10(double *state, double *unused, double *out_2577262322223255437);
void pose_h_13(double *state, double *unused, double *out_3327759072994423416);
void pose_H_13(double *state, double *unused, double *out_3702297798823717219);
void pose_h_14(double *state, double *unused, double *out_4339241047534864282);
void pose_H_14(double *state, double *unused, double *out_2951330767816565491);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}