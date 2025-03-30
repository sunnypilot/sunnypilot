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
void car_err_fun(double *nom_x, double *delta_x, double *out_2733505511915312304);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_2042722913738173368);
void car_H_mod_fun(double *state, double *out_8648682746173350729);
void car_f_fun(double *state, double dt, double *out_4433059162913028335);
void car_F_fun(double *state, double dt, double *out_7479330613641780172);
void car_h_25(double *state, double *unused, double *out_9005739562334179017);
void car_H_25(double *state, double *unused, double *out_604873101623963650);
void car_h_24(double *state, double *unused, double *out_1699962084933975115);
void car_H_24(double *state, double *unused, double *out_8613805786016392741);
void car_h_30(double *state, double *unused, double *out_1559731860621323414);
void car_H_30(double *state, double *unused, double *out_3922823228503644548);
void car_h_26(double *state, double *unused, double *out_6561405128282169059);
void car_H_26(double *state, double *unused, double *out_3136630217250092574);
void car_h_27(double *state, double *unused, double *out_4267593512827365087);
void car_H_27(double *state, double *unused, double *out_6097586540304069459);
void car_h_29(double *state, double *unused, double *out_4542787575111870976);
void car_H_29(double *state, double *unused, double *out_3412591884189252364);
void car_h_28(double *state, double *unused, double *out_1663188192018667436);
void car_H_28(double *state, double *unused, double *out_1448961612623926113);
void car_h_31(double *state, double *unused, double *out_4595763231261982210);
void car_H_31(double *state, double *unused, double *out_3762838319483444050);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}