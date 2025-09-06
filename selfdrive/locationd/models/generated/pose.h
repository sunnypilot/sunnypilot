#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_2598376982485037805);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_4512324947371561180);
void pose_H_mod_fun(double *state, double *out_2316928423571127677);
void pose_f_fun(double *state, double dt, double *out_5656120576541900457);
void pose_F_fun(double *state, double dt, double *out_4610640204669690281);
void pose_h_4(double *state, double *unused, double *out_1496184824162482188);
void pose_H_4(double *state, double *unused, double *out_3514875905454025781);
void pose_h_10(double *state, double *unused, double *out_3267969363232743915);
void pose_H_10(double *state, double *unused, double *out_4777186157283160163);
void pose_h_13(double *state, double *unused, double *out_8965969219897386723);
void pose_H_13(double *state, double *unused, double *out_318879557848498243);
void pose_h_14(double *state, double *unused, double *out_2613336441508122949);
void pose_H_14(double *state, double *unused, double *out_432087473158653485);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}