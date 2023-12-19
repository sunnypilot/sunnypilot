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
void car_err_fun(double *nom_x, double *delta_x, double *out_5539204589909662238);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6836761615042086214);
void car_H_mod_fun(double *state, double *out_5300350899020605715);
void car_f_fun(double *state, double dt, double *out_7290139574394395979);
void car_F_fun(double *state, double dt, double *out_3369922846592360961);
void car_h_25(double *state, double *unused, double *out_213866987500689272);
void car_H_25(double *state, double *unused, double *out_8338833395014389035);
void car_h_24(double *state, double *unused, double *out_6813311767306827479);
void car_H_24(double *state, double *unused, double *out_3470018529986682183);
void car_h_30(double *state, double *unused, double *out_3161592977856174233);
void car_H_30(double *state, double *unused, double *out_3811137064886780837);
void car_h_26(double *state, double *unused, double *out_4105102830757836668);
void car_H_26(double *state, double *unused, double *out_4597330076140332811);
void car_h_27(double *state, double *unused, double *out_8017746421296364907);
void car_H_27(double *state, double *unused, double *out_1636373753086355926);
void car_h_29(double *state, double *unused, double *out_3764908862532651750);
void car_H_29(double *state, double *unused, double *out_4321368409201173021);
void car_h_28(double *state, double *unused, double *out_8845296254147321726);
void car_H_28(double *state, double *unused, double *out_6284998680766499272);
void car_h_31(double *state, double *unused, double *out_7667405663253359913);
void car_H_31(double *state, double *unused, double *out_3971121973906981335);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}