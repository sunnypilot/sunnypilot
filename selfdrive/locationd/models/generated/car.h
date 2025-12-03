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
void car_err_fun(double *nom_x, double *delta_x, double *out_3207417457809524571);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3515746883089040082);
void car_H_mod_fun(double *state, double *out_5464135792795430340);
void car_f_fun(double *state, double dt, double *out_922667799000140176);
void car_F_fun(double *state, double dt, double *out_1603663595887720009);
void car_h_25(double *state, double *unused, double *out_5388406355713042527);
void car_H_25(double *state, double *unused, double *out_8078916455729456436);
void car_h_24(double *state, double *unused, double *out_6432920327898982140);
void car_H_24(double *state, double *unused, double *out_1592935210167924286);
void car_h_30(double *state, double *unused, double *out_2510020824812508111);
void car_H_30(double *state, double *unused, double *out_1162226114237839681);
void car_h_26(double *state, double *unused, double *out_1030092720238161151);
void car_H_26(double *state, double *unused, double *out_6626324299106038956);
void car_h_27(double *state, double *unused, double *out_4942736310776689390);
void car_H_27(double *state, double *unused, double *out_8063725359036430199);
void car_h_29(double *state, double *unused, double *out_1547309068256673095);
void car_H_29(double *state, double *unused, double *out_7698024058558304322);
void car_h_28(double *state, double *unused, double *out_5546052195453166907);
void car_H_28(double *state, double *unused, double *out_8313992903732205417);
void car_h_31(double *state, double *unused, double *out_1402622765726020128);
void car_H_31(double *state, double *unused, double *out_8048270493852496008);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}