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
void car_err_fun(double *nom_x, double *delta_x, double *out_3375727518016667978);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5057418784479902506);
void car_H_mod_fun(double *state, double *out_2753598796086644968);
void car_f_fun(double *state, double dt, double *out_2394137930301935246);
void car_F_fun(double *state, double dt, double *out_1918818007928134261);
void car_h_25(double *state, double *unused, double *out_7059075732125541656);
void car_H_25(double *state, double *unused, double *out_769381853902846709);
void car_h_24(double *state, double *unused, double *out_4890459482086578893);
void car_H_24(double *state, double *unused, double *out_4327307452705169845);
void car_h_30(double *state, double *unused, double *out_833863762758981703);
void car_H_30(double *state, double *unused, double *out_7686072195394463464);
void car_h_26(double *state, double *unused, double *out_7291003209568256499);
void car_H_26(double *state, double *unused, double *out_2972121464971209515);
void car_h_27(double *state, double *unused, double *out_6385995073923164315);
void car_H_27(double *state, double *unused, double *out_5511308883594038553);
void car_h_29(double *state, double *unused, double *out_2524311597494662663);
void car_H_29(double *state, double *unused, double *out_8196303539708855648);
void car_h_28(double *state, double *unused, double *out_3078779827779546536);
void car_H_28(double *state, double *unused, double *out_3113904522639325074);
void car_h_31(double *state, double *unused, double *out_3624403084763337519);
void car_H_31(double *state, double *unused, double *out_800027815779807137);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}