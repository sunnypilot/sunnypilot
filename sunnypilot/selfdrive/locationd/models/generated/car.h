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
void car_err_fun(double *nom_x, double *delta_x, double *out_6017625978963375894);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6841210236025661412);
void car_H_mod_fun(double *state, double *out_1041246729861882300);
void car_f_fun(double *state, double dt, double *out_4989810676465268701);
void car_F_fun(double *state, double dt, double *out_5356911169490671165);
void car_h_25(double *state, double *unused, double *out_5800435846139545547);
void car_H_25(double *state, double *unused, double *out_5944938555046547140);
void car_h_24(double *state, double *unused, double *out_5732265362808196766);
void car_H_24(double *state, double *unused, double *out_5474481073003208416);
void car_h_30(double *state, double *unused, double *out_156371015655145690);
void car_H_30(double *state, double *unused, double *out_1417242224918938942);
void car_h_26(double *state, double *unused, double *out_6034656503213860778);
void car_H_26(double *state, double *unused, double *out_2203435236172490916);
void car_h_27(double *state, double *unused, double *out_2122012912675332539);
void car_H_27(double *state, double *unused, double *out_3640836296102882159);
void car_h_29(double *state, double *unused, double *out_8562027835299372343);
void car_H_29(double *state, double *unused, double *out_1927473569233331126);
void car_h_28(double *state, double *unused, double *out_4124438144784840929);
void car_H_28(double *state, double *unused, double *out_3891103840798657377);
void car_h_31(double *state, double *unused, double *out_1019066314689231588);
void car_H_31(double *state, double *unused, double *out_5975584516923507568);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}