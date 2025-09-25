#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_7318184160914923263);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_8130026506067701099);
void pose_H_mod_fun(double *state, double *out_5907612673153772883);
void pose_f_fun(double *state, double dt, double *out_4351928450748542819);
void pose_F_fun(double *state, double dt, double *out_1555904624671315142);
void pose_h_4(double *state, double *unused, double *out_6344336926878520260);
void pose_H_4(double *state, double *unused, double *out_7105560155036670987);
void pose_h_10(double *state, double *unused, double *out_1404827797723103364);
void pose_H_10(double *state, double *unused, double *out_7149609403250573740);
void pose_h_13(double *state, double *unused, double *out_7533459209982952318);
void pose_H_13(double *state, double *unused, double *out_3271804691734146963);
void pose_h_14(double *state, double *unused, double *out_2121789093779121634);
void pose_H_14(double *state, double *unused, double *out_4022771722741298691);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}