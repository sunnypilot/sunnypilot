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
void car_err_fun(double *nom_x, double *delta_x, double *out_3474583283146901891);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3780042915982957382);
void car_H_mod_fun(double *state, double *out_6387042007052378269);
void car_f_fun(double *state, double dt, double *out_5471630993470310399);
void car_F_fun(double *state, double dt, double *out_8523483091456656155);
void car_h_25(double *state, double *unused, double *out_6525986448049520314);
void car_H_25(double *state, double *unused, double *out_793230131916196905);
void car_h_24(double *state, double *unused, double *out_1498456185202745162);
void car_H_24(double *state, double *unused, double *out_2965879730921696471);
void car_h_30(double *state, double *unused, double *out_6671506272270175285);
void car_H_30(double *state, double *unused, double *out_1725102826591051722);
void car_h_26(double *state, double *unused, double *out_1445599056434850338);
void car_H_26(double *state, double *unused, double *out_4534733450790253129);
void car_h_27(double *state, double *unused, double *out_6172146376165167132);
void car_H_27(double *state, double *unused, double *out_3948696897774994939);
void car_h_29(double *state, double *unused, double *out_3634720220825842600);
void car_H_29(double *state, double *unused, double *out_2235334170905443906);
void car_h_28(double *state, double *unused, double *out_1170473108504321487);
void car_H_28(double *state, double *unused, double *out_2847064846164086668);
void car_h_31(double *state, double *unused, double *out_4157492368839358861);
void car_H_31(double *state, double *unused, double *out_5160941553023604605);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}