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
void car_err_fun(double *nom_x, double *delta_x, double *out_4601697762902887404);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3959595646079752203);
void car_H_mod_fun(double *state, double *out_653001050605998855);
void car_f_fun(double *state, double dt, double *out_1462235041247810438);
void car_F_fun(double *state, double dt, double *out_5625707751492774003);
void car_h_25(double *state, double *unused, double *out_8183390139860994988);
void car_H_25(double *state, double *unused, double *out_4175981700595490532);
void car_h_24(double *state, double *unused, double *out_736265725996846818);
void car_H_24(double *state, double *unused, double *out_570527626371018502);
void car_h_30(double *state, double *unused, double *out_4321706663432493336);
void car_H_30(double *state, double *unused, double *out_7354072031622444329);
void car_h_26(double *state, double *unused, double *out_1020160572453537227);
void car_H_26(double *state, double *unused, double *out_434478381721434308);
void car_h_27(double *state, double *unused, double *out_5907861322247942854);
void car_H_27(double *state, double *unused, double *out_1871879441651825551);
void car_h_29(double *state, double *unused, double *out_679966604228352309);
void car_H_29(double *state, double *unused, double *out_158516714782274518);
void car_h_28(double *state, double *unused, double *out_5536120047668542983);
void car_H_28(double *state, double *unused, double *out_2122146986347600769);
void car_h_31(double *state, double *unused, double *out_3146269333088116058);
void car_H_31(double *state, double *unused, double *out_4206627662472450960);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}