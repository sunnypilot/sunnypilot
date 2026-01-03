#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_2078931456649821549);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_4018826878271793945);
void pose_H_mod_fun(double *state, double *out_1512654483837860004);
void pose_f_fun(double *state, double dt, double *out_2374336605048301418);
void pose_F_fun(double *state, double dt, double *out_7174832122982687242);
void pose_h_4(double *state, double *unused, double *out_5731849632354204325);
void pose_H_4(double *state, double *unused, double *out_388519179644441129);
void pose_h_10(double *state, double *unused, double *out_6794229724487339636);
void pose_H_10(double *state, double *unused, double *out_7294889413993203975);
void pose_h_13(double *state, double *unused, double *out_6365979606409915125);
void pose_H_13(double *state, double *unused, double *out_2823754645687891672);
void pose_h_14(double *state, double *unused, double *out_7685359376293741420);
void pose_H_14(double *state, double *unused, double *out_3574721676695043400);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}