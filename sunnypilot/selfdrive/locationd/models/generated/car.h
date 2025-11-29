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
void car_err_fun(double *nom_x, double *delta_x, double *out_5809845421690136483);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5502881521170119146);
void car_H_mod_fun(double *state, double *out_7849538553703122327);
void car_f_fun(double *state, double dt, double *out_2803371198255290252);
void car_F_fun(double *state, double dt, double *out_3087564586255421604);
void car_h_25(double *state, double *unused, double *out_3664987702156534339);
void car_H_25(double *state, double *unused, double *out_1404017294094192052);
void car_h_24(double *state, double *unused, double *out_8112067670215266046);
void car_H_24(double *state, double *unused, double *out_768632304911307514);
void car_h_30(double *state, double *unused, double *out_3940181764441040228);
void car_H_30(double *state, double *unused, double *out_3922350252601440679);
void car_h_26(double *state, double *unused, double *out_8748577395274773432);
void car_H_26(double *state, double *unused, double *out_2337486024779864172);
void car_h_27(double *state, double *unused, double *out_8666660969817379984);
void car_H_27(double *state, double *unused, double *out_6145944323785383896);
void car_h_29(double *state, double *unused, double *out_903395712996707543);
void car_H_29(double *state, double *unused, double *out_4432581596915832863);
void car_h_28(double *state, double *unused, double *out_2987840130260439853);
void car_H_28(double *state, double *unused, double *out_649817420153697711);
void car_h_31(double *state, double *unused, double *out_7763291000435906203);
void car_H_31(double *state, double *unused, double *out_2963694127013215648);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}