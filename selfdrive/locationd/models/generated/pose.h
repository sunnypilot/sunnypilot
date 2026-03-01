#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_9115622508544891145);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_112942660134600720);
void pose_H_mod_fun(double *state, double *out_1372883240507492868);
void pose_f_fun(double *state, double dt, double *out_8885506350385188796);
void pose_F_fun(double *state, double dt, double *out_6694399137447510067);
void pose_h_4(double *state, double *unused, double *out_3136727019084366089);
void pose_H_4(double *state, double *unused, double *out_6525401625546573603);
void pose_h_10(double *state, double *unused, double *out_198014718045503526);
void pose_H_10(double *state, double *unused, double *out_1683049892870523227);
void pose_h_13(double *state, double *unused, double *out_7309627388739009073);
void pose_H_13(double *state, double *unused, double *out_8709068622830645212);
void pose_h_14(double *state, double *unused, double *out_6553607367466278032);
void pose_H_14(double *state, double *unused, double *out_7958101591823493484);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}