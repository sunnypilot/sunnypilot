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
void car_err_fun(double *nom_x, double *delta_x, double *out_3273042440096814304);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5732845985013317398);
void car_H_mod_fun(double *state, double *out_421472006259524810);
void car_f_fun(double *state, double dt, double *out_3776724096449913501);
void car_F_fun(double *state, double dt, double *out_1353218831850316658);
void car_h_25(double *state, double *unused, double *out_1344834859822615607);
void car_H_25(double *state, double *unused, double *out_6507594322557232788);
void car_h_24(double *state, double *unused, double *out_5433380832945564861);
void car_H_24(double *state, double *unused, double *out_8680243921562732354);
void car_h_30(double *state, double *unused, double *out_7964191929203084827);
void car_H_30(double *state, double *unused, double *out_6636933269700472858);
void car_h_26(double *state, double *unused, double *out_7445766093062134104);
void car_H_26(double *state, double *unused, double *out_8197646432278262604);
void car_h_27(double *state, double *unused, double *out_7327758699128757360);
void car_H_27(double *state, double *unused, double *out_8811696581500897769);
void car_h_29(double *state, double *unused, double *out_7020682076301422392);
void car_H_29(double *state, double *unused, double *out_7921684765339102814);
void car_h_28(double *state, double *unused, double *out_4051910886381300771);
void car_H_28(double *state, double *unused, double *out_8561429036805122551);
void car_h_31(double *state, double *unused, double *out_5842118044635442722);
void car_H_31(double *state, double *unused, double *out_6476948360680272360);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}