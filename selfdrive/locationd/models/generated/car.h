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
void car_err_fun(double *nom_x, double *delta_x, double *out_9217969317605642867);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6393584235681603618);
void car_H_mod_fun(double *state, double *out_8159470262941037049);
void car_f_fun(double *state, double dt, double *out_5395246748545447116);
void car_F_fun(double *state, double dt, double *out_7501393170954007307);
void car_h_25(double *state, double *unused, double *out_3212620688693559532);
void car_H_25(double *state, double *unused, double *out_3368569190577985703);
void car_h_24(double *state, double *unused, double *out_8983580996630113210);
void car_H_24(double *state, double *unused, double *out_1195919591572486137);
void car_h_30(double *state, double *unused, double *out_5781578470390223898);
void car_H_30(double *state, double *unused, double *out_5886902149085234330);
void car_h_26(double *state, double *unused, double *out_5676102393679055679);
void car_H_26(double *state, double *unused, double *out_372934128296070521);
void car_h_27(double *state, double *unused, double *out_5060714363169364872);
void car_H_27(double *state, double *unused, double *out_3712138837284809419);
void car_h_29(double *state, double *unused, double *out_3947328683450635392);
void car_H_29(double *state, double *unused, double *out_6397133493399626514);
void car_h_28(double *state, double *unused, double *out_779150521925704364);
void car_H_28(double *state, double *unused, double *out_1314734476330095940);
void car_h_31(double *state, double *unused, double *out_3802642380919982425);
void car_H_31(double *state, double *unused, double *out_999142230529421997);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}