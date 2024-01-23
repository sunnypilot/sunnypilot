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
void car_err_fun(double *nom_x, double *delta_x, double *out_810329987946403557);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5716896811801670801);
void car_H_mod_fun(double *state, double *out_4260664193875322727);
void car_f_fun(double *state, double dt, double *out_1338751046029408378);
void car_F_fun(double *state, double dt, double *out_5413251715551156627);
void car_h_25(double *state, double *unused, double *out_124630543568800147);
void car_H_25(double *state, double *unused, double *out_4993281568702638206);
void car_h_24(double *state, double *unused, double *out_8120860186226682358);
void car_H_24(double *state, double *unused, double *out_2820631969697138640);
void car_h_30(double *state, double *unused, double *out_3072356533924285108);
void car_H_30(double *state, double *unused, double *out_7511614527209886833);
void car_h_26(double *state, double *unused, double *out_2090272440588986996);
void car_H_26(double *state, double *unused, double *out_1251778249828581982);
void car_h_27(double *state, double *unused, double *out_5126303811229645792);
void car_H_27(double *state, double *unused, double *out_5336851215409461922);
void car_h_29(double *state, double *unused, double *out_3675672418600762625);
void car_H_29(double *state, double *unused, double *out_8021845871524279017);
void car_h_28(double *state, double *unused, double *out_8258220002250123303);
void car_H_28(double *state, double *unused, double *out_2939446854454748443);
void car_h_31(double *state, double *unused, double *out_7756642107185249038);
void car_H_31(double *state, double *unused, double *out_625570147595230506);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}