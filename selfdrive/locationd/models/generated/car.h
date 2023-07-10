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
void car_err_fun(double *nom_x, double *delta_x, double *out_4244742674272470413);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4391628682247720481);
void car_H_mod_fun(double *state, double *out_7497762910874470534);
void car_f_fun(double *state, double dt, double *out_2804212187320407990);
void car_F_fun(double *state, double dt, double *out_2566469647269033741);
void car_h_25(double *state, double *unused, double *out_3243311392062354747);
void car_H_25(double *state, double *unused, double *out_2633319286481143646);
void car_h_24(double *state, double *unused, double *out_317586459190038727);
void car_H_24(double *state, double *unused, double *out_3942252520110374455);
void car_h_30(double *state, double *unused, double *out_3097791567841699776);
void car_H_30(double *state, double *unused, double *out_7161015616608751844);
void car_h_26(double *state, double *unused, double *out_8099464835502545421);
void car_H_26(double *state, double *unused, double *out_6374822605355199870);
void car_h_27(double *state, double *unused, double *out_1758361875598490898);
void car_H_27(double *state, double *unused, double *out_4937421545424808627);
void car_h_29(double *state, double *unused, double *out_5620045352026992550);
void car_H_29(double *state, double *unused, double *out_6650784272294359660);
void car_h_28(double *state, double *unused, double *out_814852022696828463);
void car_H_28(double *state, double *unused, double *out_4687154000729033409);
void car_h_31(double *state, double *unused, double *out_4519953864758317694);
void car_H_31(double *state, double *unused, double *out_2602673324604183218);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}