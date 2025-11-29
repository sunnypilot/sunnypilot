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
void car_err_fun(double *nom_x, double *delta_x, double *out_2505009923289236322);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_693928023623824221);
void car_H_mod_fun(double *state, double *out_4242968391530992008);
void car_f_fun(double *state, double dt, double *out_1159864094741656085);
void car_F_fun(double *state, double dt, double *out_8150880409629162514);
void car_h_25(double *state, double *unused, double *out_1560242497889987579);
void car_H_25(double *state, double *unused, double *out_7765949041520483685);
void car_h_24(double *state, double *unused, double *out_440354277390915404);
void car_H_24(double *state, double *unused, double *out_7122869433386744795);
void car_h_30(double *state, double *unused, double *out_8148070424366282742);
void car_H_30(double *state, double *unused, double *out_3238252711392875487);
void car_h_26(double *state, double *unused, double *out_4540688735349530918);
void car_H_26(double *state, double *unused, double *out_4024445722646427461);
void car_h_27(double *state, double *unused, double *out_628045144811002679);
void car_H_27(double *state, double *unused, double *out_5461846782576818704);
void car_h_29(double *state, double *unused, double *out_5297000381682423229);
void car_H_29(double *state, double *unused, double *out_3748484055707267671);
void car_h_28(double *state, double *unused, double *out_6386030058804740635);
void car_H_28(double *state, double *unused, double *out_1333914961362262903);
void car_h_31(double *state, double *unused, double *out_2680928216743251404);
void car_H_31(double *state, double *unused, double *out_7796595003397444113);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}