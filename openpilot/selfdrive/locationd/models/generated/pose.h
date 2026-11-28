#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_8585539421584719708);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_6468830226543666520);
void pose_H_mod_fun(double *state, double *out_2349771934270070487);
void pose_f_fun(double *state, double dt, double *out_872855095581035755);
void pose_F_fun(double *state, double dt, double *out_3872170684396481521);
void pose_h_4(double *state, double *unused, double *out_8985748621613840114);
void pose_H_4(double *state, double *unused, double *out_8197853741022029208);
void pose_h_10(double *state, double *unused, double *out_4789509988246305805);
void pose_H_10(double *state, double *unused, double *out_4835060174289664588);
void pose_h_13(double *state, double *unused, double *out_8593399093047740463);
void pose_H_13(double *state, double *unused, double *out_4985579915689696407);
void pose_h_14(double *state, double *unused, double *out_4024064767553809233);
void pose_H_14(double *state, double *unused, double *out_4234612884682544679);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}