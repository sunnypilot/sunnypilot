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
void car_err_fun(double *nom_x, double *delta_x, double *out_5744499419236567507);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1184805137205037163);
void car_H_mod_fun(double *state, double *out_2752971634021862652);
void car_f_fun(double *state, double dt, double *out_7658700760911629364);
void car_F_fun(double *state, double dt, double *out_6351856658156694456);
void car_h_25(double *state, double *unused, double *out_2115125997200973707);
void car_H_25(double *state, double *unused, double *out_6275952284011354329);
void car_h_24(double *state, double *unused, double *out_7937179482135297626);
void car_H_24(double *state, double *unused, double *out_8612866190895874151);
void car_h_30(double *state, double *unused, double *out_8646825364085210282);
void car_H_30(double *state, double *unused, double *out_6146613336868114259);
void car_h_26(double *state, double *unused, double *out_7195513388815643683);
void car_H_26(double *state, double *unused, double *out_2534448965137298105);
void car_h_27(double *state, double *unused, double *out_3029764065914673830);
void car_H_27(double *state, double *unused, double *out_3971850025067689348);
void car_h_29(double *state, double *unused, double *out_4733501190905998611);
void car_H_29(double *state, double *unused, double *out_6656844681182506443);
void car_h_28(double *state, double *unused, double *out_6095421901546968827);
void car_H_28(double *state, double *unused, double *out_2823911718871392259);
void car_h_31(double *state, double *unused, double *out_6524751479517568177);
void car_H_31(double *state, double *unused, double *out_6306598245888314757);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}