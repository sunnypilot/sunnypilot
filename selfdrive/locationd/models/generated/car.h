#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void car_update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_30(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_31(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_err_fun(double *nom_x, double *delta_x, double *out_2634337573502312531);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_364624501276122878);
void car_H_mod_fun(double *state, double *out_8283385258124076174);
void car_f_fun(double *state, double dt, double *out_1842212169269794394);
void car_F_fun(double *state, double dt, double *out_844160246145237490);
void car_h_25(double *state, double *unused, double *out_1303483449461821305);
void car_H_25(double *state, double *unused, double *out_8922345036839792704);
void car_h_24(double *state, double *unused, double *out_1550963005683787860);
void car_H_24(double *state, double *unused, double *out_6745130613232642731);
void car_h_30(double *state, double *unused, double *out_7891311375938116468);
void car_H_30(double *state, double *unused, double *out_6404012078332544077);
void car_h_26(double *state, double *unused, double *out_8834821228839778903);
void car_H_26(double *state, double *unused, double *out_5782895717995702688);
void car_h_27(double *state, double *unused, double *out_5701435530743450317);
void car_H_27(double *state, double *unused, double *out_8578775390132968988);
void car_h_29(double *state, double *unused, double *out_4854525324493783783);
void car_H_29(double *state, double *unused, double *out_5893780734018151893);
void car_h_28(double *state, double *unused, double *out_697605986670398829);
void car_H_28(double *state, double *unused, double *out_7470564322621869149);
void car_h_31(double *state, double *unused, double *out_1460670117812950450);
void car_H_31(double *state, double *unused, double *out_5156687615762351212);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}