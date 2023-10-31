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
void car_err_fun(double *nom_x, double *delta_x, double *out_1402676562040383198);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1091897287188278870);
void car_H_mod_fun(double *state, double *out_5989277925452116934);
void car_f_fun(double *state, double dt, double *out_5951520236264327024);
void car_F_fun(double *state, double dt, double *out_1308759087996720471);
void car_h_25(double *state, double *unused, double *out_6923278227618494131);
void car_H_25(double *state, double *unused, double *out_2092904441014244631);
void car_h_24(double *state, double *unused, double *out_2165850182353595939);
void car_H_24(double *state, double *unused, double *out_5650830039816567767);
void car_h_30(double *state, double *unused, double *out_7886016317837035135);
void car_H_30(double *state, double *unused, double *out_4611237399521493258);
void car_h_26(double *state, double *unused, double *out_6942506464935372700);
void car_H_26(double *state, double *unused, double *out_1648598877859811593);
void car_h_27(double *state, double *unused, double *out_511865206810206682);
void car_H_27(double *state, double *unused, double *out_2436474087721068347);
void car_h_29(double *state, double *unused, double *out_236671144525700793);
void car_H_29(double *state, double *unused, double *out_5121468743835885442);
void car_h_28(double *state, double *unused, double *out_4489808060850638963);
void car_H_28(double *state, double *unused, double *out_39069726766354868);
void car_h_31(double *state, double *unused, double *out_4062907081842169160);
void car_H_31(double *state, double *unused, double *out_2274806980093163069);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}