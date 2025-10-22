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
void car_err_fun(double *nom_x, double *delta_x, double *out_8269169211827911365);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1061083252181456560);
void car_H_mod_fun(double *state, double *out_6549540021929294116);
void car_f_fun(double *state, double dt, double *out_5904193651585035956);
void car_F_fun(double *state, double dt, double *out_8258638883296957904);
void car_h_25(double *state, double *unused, double *out_7047596049686412249);
void car_H_25(double *state, double *unused, double *out_6993512226595592660);
void car_h_24(double *state, double *unused, double *out_8355860068355601473);
void car_H_24(double *state, double *unused, double *out_853841784278429402);
void car_h_30(double *state, double *unused, double *out_276760823336061313);
void car_H_30(double *state, double *unused, double *out_6925535516986350758);
void car_h_26(double *state, double *unused, double *out_5239140821017354545);
void car_H_26(double *state, double *unused, double *out_7711728528239902732);
void car_h_27(double *state, double *unused, double *out_7001195942741510355);
void car_H_27(double *state, double *unused, double *out_4750772205185925847);
void car_h_29(double *state, double *unused, double *out_3906516822321848122);
void car_H_29(double *state, double *unused, double *out_7435766861300742942);
void car_h_28(double *state, double *unused, double *out_8632996027698187878);
void car_H_28(double *state, double *unused, double *out_9047346940843482423);
void car_h_31(double *state, double *unused, double *out_7204782718037541394);
void car_H_31(double *state, double *unused, double *out_7085520426006551256);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}