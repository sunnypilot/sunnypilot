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
void car_err_fun(double *nom_x, double *delta_x, double *out_7044851216775548991);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7289501170211592416);
void car_H_mod_fun(double *state, double *out_7606443429705972179);
void car_f_fun(double *state, double dt, double *out_7610697498145313227);
void car_F_fun(double *state, double dt, double *out_6340369697461232580);
void car_h_25(double *state, double *unused, double *out_187386210251484366);
void car_H_25(double *state, double *unused, double *out_3477348954605252497);
void car_h_24(double *state, double *unused, double *out_6741112897477616196);
void car_H_24(double *state, double *unused, double *out_7122041108230277057);
void car_h_30(double *state, double *unused, double *out_3450063318002537984);
void car_H_30(double *state, double *unused, double *out_1050347375522355701);
void car_h_26(double *state, double *unused, double *out_1551609949658307661);
void car_H_26(double *state, double *unused, double *out_264154364268803727);
void car_h_27(double *state, double *unused, double *out_1484421420982351135);
void car_H_27(double *state, double *unused, double *out_3225110687322780612);
void car_h_29(double *state, double *unused, double *out_8451736585663383629);
void car_H_29(double *state, double *unused, double *out_540116031207963517);
void car_h_28(double *state, double *unused, double *out_4167682114597479486);
void car_H_28(double *state, double *unused, double *out_1423514240357362734);
void car_h_31(double *state, double *unused, double *out_7273172553997403959);
void car_H_31(double *state, double *unused, double *out_890362466502155203);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}