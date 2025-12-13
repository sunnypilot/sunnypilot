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
void car_err_fun(double *nom_x, double *delta_x, double *out_7495940335269469155);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5520063280539916794);
void car_H_mod_fun(double *state, double *out_3346004364672146647);
void car_f_fun(double *state, double dt, double *out_3411977274093571316);
void car_F_fun(double *state, double dt, double *out_596183322901807921);
void car_h_25(double *state, double *unused, double *out_5290066488755964360);
void car_H_25(double *state, double *unused, double *out_8249696189856811487);
void car_h_24(double *state, double *unused, double *out_3886677677528841363);
void car_H_24(double *state, double *unused, double *out_4267373038459043589);
void car_h_30(double *state, double *unused, double *out_4660016903689847264);
void car_H_30(double *state, double *unused, double *out_3280357542361123374);
void car_h_26(double *state, double *unused, double *out_341656363970998381);
void car_H_26(double *state, double *unused, double *out_4508192870982755263);
void car_h_27(double *state, double *unused, double *out_8930573726579513678);
void car_H_27(double *state, double *unused, double *out_5455120854161548285);
void car_h_29(double *state, double *unused, double *out_1739024613724001882);
void car_H_29(double *state, double *unused, double *out_7168483581031099318);
void car_h_28(double *state, double *unused, double *out_4778024297623224008);
void car_H_28(double *state, double *unused, double *out_6195861475608921724);
void car_h_31(double *state, double *unused, double *out_5275404934199538071);
void car_H_31(double *state, double *unused, double *out_8280342151733771915);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}