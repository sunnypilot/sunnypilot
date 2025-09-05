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
void car_err_fun(double *nom_x, double *delta_x, double *out_311236628735257153);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7313915667919824068);
void car_H_mod_fun(double *state, double *out_9020713222352451970);
void car_f_fun(double *state, double dt, double *out_1159356000309350310);
void car_F_fun(double *state, double dt, double *out_8529210458665284284);
void car_h_25(double *state, double *unused, double *out_4254560804621753910);
void car_H_25(double *state, double *unused, double *out_7096198754133444274);
void car_h_24(double *state, double *unused, double *out_5260315530328507674);
void car_H_24(double *state, double *unused, double *out_4918984330526294301);
void car_h_30(double *state, double *unused, double *out_7892010332875776260);
void car_H_30(double *state, double *unused, double *out_4577865795626195647);
void car_h_26(double *state, double *unused, double *out_3494058251594147248);
void car_H_26(double *state, double *unused, double *out_3791672784372643673);
void car_h_27(double *state, double *unused, double *out_4727408367385086855);
void car_H_27(double *state, double *unused, double *out_6752629107426620558);
void car_h_29(double *state, double *unused, double *out_5328826524998450409);
void car_H_29(double *state, double *unused, double *out_4067634451311803463);
void car_h_28(double *state, double *unused, double *out_274264900275758790);
void car_H_28(double *state, double *unused, double *out_9150033468381334037);
void car_h_31(double *state, double *unused, double *out_2109033173680061951);
void car_H_31(double *state, double *unused, double *out_4417880886605995149);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}