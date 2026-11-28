#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_2613652145363001248);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_1002934702699052391);
void pose_H_mod_fun(double *state, double *out_3573439106494925480);
void pose_f_fun(double *state, double dt, double *out_1448694129028724109);
void pose_F_fun(double *state, double dt, double *out_5191980698119314658);
void pose_h_4(double *state, double *unused, double *out_5235289640549259173);
void pose_H_4(double *state, double *unused, double *out_2274642700257033241);
void pose_h_10(double *state, double *unused, double *out_5091836047882356691);
void pose_H_10(double *state, double *unused, double *out_4490205013045843640);
void pose_h_13(double *state, double *unused, double *out_5979871826325457693);
void pose_H_13(double *state, double *unused, double *out_937631125075299560);
void pose_h_14(double *state, double *unused, double *out_1085876952354499248);
void pose_H_14(double *state, double *unused, double *out_2709759226901916840);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}