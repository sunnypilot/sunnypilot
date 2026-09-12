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
void car_err_fun(double *nom_x, double *delta_x, double *out_5070392900769873758);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3742760733154016051);
void car_H_mod_fun(double *state, double *out_5758456641177717920);
void car_f_fun(double *state, double dt, double *out_730595102125265078);
void car_F_fun(double *state, double dt, double *out_7198115545780111359);
void car_h_25(double *state, double *unused, double *out_5441109048213736058);
void car_H_25(double *state, double *unused, double *out_4766949399557973891);
void car_h_24(double *state, double *unused, double *out_2797667639827089179);
void car_H_24(double *state, double *unused, double *out_4461115786511221334);
void car_h_30(double *state, double *unused, double *out_1188271489450022901);
void car_H_30(double *state, double *unused, double *out_9152098344023969527);
void car_h_26(double *state, double *unused, double *out_6530138725336053464);
void car_H_26(double *state, double *unused, double *out_8508452718432030115);
void car_h_27(double *state, double *unused, double *out_8003961757834969913);
void car_H_27(double *state, double *unused, double *out_6977335032223544616);
void car_h_29(double *state, double *unused, double *out_1416133831358674750);
void car_H_29(double *state, double *unused, double *out_8784414385371189905);
void car_h_28(double *state, double *unused, double *out_7400645873158492396);
void car_H_28(double *state, double *unused, double *out_6820784113805863654);
void car_h_31(double *state, double *unused, double *out_1803659519959713708);
void car_H_31(double *state, double *unused, double *out_9134660820665381591);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}