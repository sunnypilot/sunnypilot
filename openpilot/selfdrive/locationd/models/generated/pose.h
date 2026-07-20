#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_8799966904452395012);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_1661397671847398073);
void pose_H_mod_fun(double *state, double *out_2131008325054536789);
void pose_f_fun(double *state, double dt, double *out_884777716370448931);
void pose_F_fun(double *state, double dt, double *out_6755798908020795646);
void pose_h_4(double *state, double *unused, double *out_4561759232303120700);
void pose_H_4(double *state, double *unused, double *out_5331418226156006813);
void pose_h_10(double *state, double *unused, double *out_8855709713594721197);
void pose_H_10(double *state, double *unused, double *out_3758101988975610904);
void pose_h_13(double *state, double *unused, double *out_6255148116667054704);
void pose_H_13(double *state, double *unused, double *out_2279212982160694116);
void pose_h_14(double *state, double *unused, double *out_5422638595254952120);
void pose_H_14(double *state, double *unused, double *out_8414206658451379109);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}