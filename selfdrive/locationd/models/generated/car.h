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
void car_err_fun(double *nom_x, double *delta_x, double *out_8249429775729676839);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_830104287538898022);
void car_H_mod_fun(double *state, double *out_4361542019279921949);
void car_f_fun(double *state, double dt, double *out_2834190715000315846);
void car_F_fun(double *state, double dt, double *out_8944307819367133251);
void car_h_25(double *state, double *unused, double *out_4307604535579416709);
void car_H_25(double *state, double *unused, double *out_7813441128818867203);
void car_h_24(double *state, double *unused, double *out_6273662611818280039);
void car_H_24(double *state, double *unused, double *out_5886793617924175379);
void car_h_30(double *state, double *unused, double *out_5931642792047228057);
void car_H_30(double *state, double *unused, double *out_896750787327250448);
void car_h_26(double *state, double *unused, double *out_6116059764248474413);
void car_H_26(double *state, double *unused, double *out_6891799626016628189);
void car_h_27(double *state, double *unused, double *out_4488704928686580431);
void car_H_27(double *state, double *unused, double *out_8329200685947019432);
void car_h_29(double *state, double *unused, double *out_8350388405115082083);
void car_H_29(double *state, double *unused, double *out_7432548731647715089);
void car_h_28(double *state, double *unused, double *out_2722204557567641080);
void car_H_28(double *state, double *unused, double *out_8579468230642794650);
void car_h_31(double *state, double *unused, double *out_4150417867228287564);
void car_H_31(double *state, double *unused, double *out_7782795166941906775);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}