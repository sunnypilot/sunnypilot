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
void car_err_fun(double *nom_x, double *delta_x, double *out_4680039436617746285);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6464047771063674000);
void car_H_mod_fun(double *state, double *out_915927946953392880);
void car_f_fun(double *state, double dt, double *out_5875377148384648318);
void car_F_fun(double *state, double dt, double *out_3741941609747229027);
void car_h_25(double *state, double *unused, double *out_5013938002243898062);
void car_H_25(double *state, double *unused, double *out_4811433704179120774);
void car_h_24(double *state, double *unused, double *out_7703538372309607031);
void car_H_24(double *state, double *unused, double *out_2638784105173621208);
void car_h_30(double *state, double *unused, double *out_1376488473989875712);
void car_H_30(double *state, double *unused, double *out_7329766662686369401);
void car_h_26(double *state, double *unused, double *out_7605480698016965053);
void car_H_26(double *state, double *unused, double *out_1069930385305064550);
void car_h_27(double *state, double *unused, double *out_12264734583052417);
void car_H_27(double *state, double *unused, double *out_8893383339839238998);
void car_h_29(double *state, double *unused, double *out_3625184793670969933);
void car_H_29(double *state, double *unused, double *out_7839998007000761585);
void car_h_28(double *state, double *unused, double *out_3393257316228255090);
void car_H_28(double *state, double *unused, double *out_2757598989931231011);
void car_h_31(double *state, double *unused, double *out_2446620762004990263);
void car_H_31(double *state, double *unused, double *out_443722283071713074);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}