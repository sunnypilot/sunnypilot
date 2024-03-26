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
void car_err_fun(double *nom_x, double *delta_x, double *out_9210742210888155066);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3383382481161837801);
void car_H_mod_fun(double *state, double *out_8527379894240690997);
void car_f_fun(double *state, double dt, double *out_161039606333012886);
void car_F_fun(double *state, double dt, double *out_4115038986771892062);
void car_h_25(double *state, double *unused, double *out_7382986880899433707);
void car_H_25(double *state, double *unused, double *out_2957978884612669829);
void car_h_24(double *state, double *unused, double *out_8859429626558099191);
void car_H_24(double *state, double *unused, double *out_599946714189653307);
void car_h_30(double *state, double *unused, double *out_2423879716091576025);
void car_H_30(double *state, double *unused, double *out_439645926105421202);
void car_h_26(double *state, double *unused, double *out_2577793551569269620);
void car_H_26(double *state, double *unused, double *out_6699482203486726053);
void car_h_27(double *state, double *unused, double *out_6400902787564135595);
void car_H_27(double *state, double *unused, double *out_1783948145078522015);
void car_h_29(double *state, double *unused, double *out_1480369863189913590);
void car_H_29(double *state, double *unused, double *out_70585418208970982);
void car_h_28(double *state, double *unused, double *out_1399229519903289950);
void car_H_28(double *state, double *unused, double *out_5011813598860559592);
void car_h_31(double *state, double *unused, double *out_7658180943183939596);
void car_H_31(double *state, double *unused, double *out_2927332922735709401);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}