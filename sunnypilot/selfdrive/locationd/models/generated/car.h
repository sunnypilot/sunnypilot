#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void car_update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_30(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_31(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_err_fun(double *nom_x, double *delta_x, double *out_4033566628567507317);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5990136425401933100);
void car_H_mod_fun(double *state, double *out_9104365257016194246);
void car_f_fun(double *state, double dt, double *out_6902401556560306947);
void car_F_fun(double *state, double dt, double *out_5718491602786937955);
void car_h_25(double *state, double *unused, double *out_789803669906526962);
void car_H_25(double *state, double *unused, double *out_1183027224042334441);
void car_h_24(double *state, double *unused, double *out_2222181505745557291);
void car_H_24(double *state, double *unused, double *out_5471178234065851316);
void car_h_30(double *state, double *unused, double *out_8671076320660576147);
void car_H_30(double *state, double *unused, double *out_5710723554169942639);
void car_h_26(double *state, double *unused, double *out_4813287755367682237);
void car_H_26(double *state, double *unused, double *out_4924530542916390665);
void car_h_27(double *state, double *unused, double *out_5791476937567372607);
void car_H_27(double *state, double *unused, double *out_7885486865970367550);
void car_h_29(double *state, double *unused, double *out_8793583659713677357);
void car_H_29(double *state, double *unused, double *out_5200492209855550455);
void car_h_28(double *state, double *unused, double *out_4067104454337337601);
void car_H_28(double *state, double *unused, double *out_8163852846784470587);
void car_h_31(double *state, double *unused, double *out_8553068926727199403);
void car_H_31(double *state, double *unused, double *out_5550738645149742141);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}