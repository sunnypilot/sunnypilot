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
void car_err_fun(double *nom_x, double *delta_x, double *out_4489976497373888968);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7372567849217778160);
void car_H_mod_fun(double *state, double *out_6447089845340017966);
void car_f_fun(double *state, double dt, double *out_2240279400731128408);
void car_F_fun(double *state, double dt, double *out_1078793132522145231);
void car_h_25(double *state, double *unused, double *out_1533821598204291139);
void car_H_25(double *state, double *unused, double *out_1543398020155353126);
void car_h_24(double *state, double *unused, double *out_715741241444623657);
void car_H_24(double *state, double *unused, double *out_5525721171553121024);
void car_h_30(double *state, double *unused, double *out_5632124896483663003);
void car_H_30(double *state, double *unused, double *out_974934938351895501);
void car_h_26(double *state, double *unused, double *out_7812945909565042968);
void car_H_26(double *state, double *unused, double *out_1761127949605447475);
void car_h_27(double *state, double *unused, double *out_7930953303498419712);
void car_H_27(double *state, double *unused, double *out_3198529009535838718);
void car_h_29(double *state, double *unused, double *out_1160118077148068776);
void car_H_29(double *state, double *unused, double *out_1485166282666287685);
void car_h_28(double *state, double *unused, double *out_5514117502550286259);
void car_H_28(double *state, double *unused, double *out_3597232734403242889);
void car_h_31(double *state, double *unused, double *out_932403440590927585);
void car_H_31(double *state, double *unused, double *out_1134919847372095999);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}