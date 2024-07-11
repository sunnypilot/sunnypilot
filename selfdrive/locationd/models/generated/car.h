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
void car_err_fun(double *nom_x, double *delta_x, double *out_5515282840857201190);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7649367513361168321);
void car_H_mod_fun(double *state, double *out_9120682032769952111);
void car_f_fun(double *state, double dt, double *out_6653043797221081730);
void car_F_fun(double *state, double dt, double *out_2733155322343162446);
void car_h_25(double *state, double *unused, double *out_4036115050903680798);
void car_H_25(double *state, double *unused, double *out_7980036622989360732);
void car_h_24(double *state, double *unused, double *out_4949789322380165994);
void car_H_24(double *state, double *unused, double *out_5720198123753681850);
void car_h_30(double *state, double *unused, double *out_7223676118347812489);
void car_H_30(double *state, double *unused, double *out_5461703664482112105);
void car_h_26(double *state, double *unused, double *out_2222002850686966844);
void car_H_26(double *state, double *unused, double *out_6725204131846134660);
void car_h_27(double *state, double *unused, double *out_4706019044014513237);
void car_H_27(double *state, double *unused, double *out_7636466976282537016);
void car_h_29(double *state, double *unused, double *out_6797707040063507594);
void car_H_29(double *state, double *unused, double *out_4951472320167719921);
void car_h_28(double *state, double *unused, double *out_7341683512281189233);
void car_H_28(double *state, double *unused, double *out_8412872736472301121);
void car_h_31(double *state, double *unused, double *out_8946784456945013104);
void car_H_31(double *state, double *unused, double *out_6098996029612783184);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}