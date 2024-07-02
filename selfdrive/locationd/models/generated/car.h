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
void car_err_fun(double *nom_x, double *delta_x, double *out_5388524865571385571);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7040447560413333839);
void car_H_mod_fun(double *state, double *out_2980610617701040674);
void car_f_fun(double *state, double dt, double *out_2068294276185711975);
void car_F_fun(double *state, double dt, double *out_2484699426223934627);
void car_h_25(double *state, double *unused, double *out_9047703257817053185);
void car_H_25(double *state, double *unused, double *out_9459682309458463);
void car_h_24(double *state, double *unused, double *out_3785372931671791340);
void car_H_24(double *state, double *unused, double *out_3543901091891214266);
void car_h_30(double *state, double *unused, double *out_407825781098511301);
void car_H_30(double *state, double *unused, double *out_2527792640816707090);
void car_h_26(double *state, double *unused, double *out_3220377884368364684);
void car_H_26(double *state, double *unused, double *out_3732043636564597761);
void car_h_27(double *state, double *unused, double *out_4397367548231652786);
void car_H_27(double *state, double *unused, double *out_353029329016282179);
void car_h_29(double *state, double *unused, double *out_6286111268657226389);
void car_H_29(double *state, double *unused, double *out_3038023985131099274);
void car_h_28(double *state, double *unused, double *out_7434153599675985471);
void car_H_28(double *state, double *unused, double *out_2044375031938431300);
void car_h_31(double *state, double *unused, double *out_2459875331340758022);
void car_H_31(double *state, double *unused, double *out_4358251738797949237);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}