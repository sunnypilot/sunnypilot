#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_1387667857402197864);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_7508820603663648737);
void pose_H_mod_fun(double *state, double *out_6469646688903378101);
void pose_f_fun(double *state, double dt, double *out_6697963188238977834);
void pose_F_fun(double *state, double dt, double *out_429527558939684598);
void pose_h_4(double *state, double *unused, double *out_7652981531568014253);
void pose_H_4(double *state, double *unused, double *out_3195424610112428848);
void pose_h_10(double *state, double *unused, double *out_6006750715563175580);
void pose_H_10(double *state, double *unused, double *out_7894245787152231876);
void pose_h_13(double *state, double *unused, double *out_8907628765272580202);
void pose_H_13(double *state, double *unused, double *out_7640688255280421839);
void pose_h_14(double *state, double *unused, double *out_3516354322614119174);
void pose_H_14(double *state, double *unused, double *out_7158665466451913377);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}