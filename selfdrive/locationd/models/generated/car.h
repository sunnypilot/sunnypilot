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
void car_err_fun(double *nom_x, double *delta_x, double *out_1708276238722752291);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1274280650614196092);
void car_H_mod_fun(double *state, double *out_4854109873621591679);
void car_f_fun(double *state, double dt, double *out_7164062772176981129);
void car_F_fun(double *state, double dt, double *out_3676584348292578380);
void car_h_25(double *state, double *unused, double *out_5158107795025371723);
void car_H_25(double *state, double *unused, double *out_4339078352290645558);
void car_h_24(double *state, double *unused, double *out_981736047762438888);
void car_H_24(double *state, double *unused, double *out_4888986833778549667);
void car_h_30(double *state, double *unused, double *out_2302450969223516602);
void car_H_30(double *state, double *unused, double *out_8866774682418253756);
void car_h_26(double *state, double *unused, double *out_7528358185058841549);
void car_H_26(double *state, double *unused, double *out_8080581671164701782);
void car_h_27(double *state, double *unused, double *out_2553702474216674072);
void car_H_27(double *state, double *unused, double *out_6643180611234310539);
void car_h_29(double *state, double *unused, double *out_5339237020667849287);
void car_H_29(double *state, double *unused, double *out_8356543338103861572);
void car_h_28(double *state, double *unused, double *out_3903956340727170114);
void car_H_28(double *state, double *unused, double *out_6392913066538535321);
void car_h_31(double *state, double *unused, double *out_5315294463376500868);
void car_H_31(double *state, double *unused, double *out_4308432390413685130);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}