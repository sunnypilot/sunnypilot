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
void car_err_fun(double *nom_x, double *delta_x, double *out_2720831518809093631);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5669322879472346789);
void car_H_mod_fun(double *state, double *out_3032044944192446983);
void car_f_fun(double *state, double dt, double *out_22366909949606488);
void car_F_fun(double *state, double dt, double *out_5191748143905924473);
void car_h_25(double *state, double *unused, double *out_6689287487861708910);
void car_H_25(double *state, double *unused, double *out_7935736769377111823);
void car_h_24(double *state, double *unused, double *out_5847146628445868711);
void car_H_24(double *state, double *unused, double *out_493062176388395503);
void car_h_30(double *state, double *unused, double *out_2448429796822142272);
void car_H_30(double *state, double *unused, double *out_3408040439249503625);
void car_h_26(double *state, double *unused, double *out_6873790712120373805);
void car_H_26(double *state, double *unused, double *out_4194233450503055599);
void car_h_27(double *state, double *unused, double *out_6755783318186997061);
void car_H_27(double *state, double *unused, double *out_1233277127449078714);
void car_h_29(double *state, double *unused, double *out_7592657457243182691);
void car_H_29(double *state, double *unused, double *out_3918271783563895809);
void car_h_28(double *state, double *unused, double *out_8654174704078221870);
void car_H_28(double *state, double *unused, double *out_5881902055129222060);
void car_h_31(double *state, double *unused, double *out_6414093425577203021);
void car_H_31(double *state, double *unused, double *out_3568025348269704123);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}