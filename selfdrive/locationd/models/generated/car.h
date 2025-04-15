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
void car_err_fun(double *nom_x, double *delta_x, double *out_1648004092401022955);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_8224224676727042815);
void car_H_mod_fun(double *state, double *out_8414001810184439650);
void car_f_fun(double *state, double dt, double *out_3948327662823114415);
void car_F_fun(double *state, double dt, double *out_3295329725115080623);
void car_h_25(double *state, double *unused, double *out_2198496317441769050);
void car_H_25(double *state, double *unused, double *out_3510309984999774810);
void car_h_24(double *state, double *unused, double *out_5882476347173498120);
void car_H_24(double *state, double *unused, double *out_3906955289353634305);
void car_h_30(double *state, double *unused, double *out_926942978867358);
void car_H_30(double *state, double *unused, double *out_991977026492526183);
void car_h_26(double *state, double *unused, double *out_7436070377407568171);
void car_H_26(double *state, double *unused, double *out_205784015238974209);
void car_h_27(double *state, double *unused, double *out_4804266386351296729);
void car_H_27(double *state, double *unused, double *out_3166740338292951094);
void car_h_29(double *state, double *unused, double *out_942582909922795077);
void car_H_29(double *state, double *unused, double *out_481745682178133999);
void car_h_28(double *state, double *unused, double *out_7616818489621150112);
void car_H_28(double *state, double *unused, double *out_5564144699247664573);
void car_h_31(double *state, double *unused, double *out_8365610357412903353);
void car_H_31(double *state, double *unused, double *out_831992117472325685);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}