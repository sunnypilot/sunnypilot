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
void car_err_fun(double *nom_x, double *delta_x, double *out_9168682336158195836);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5209405894281129857);
void car_H_mod_fun(double *state, double *out_8788279686404140347);
void car_f_fun(double *state, double dt, double *out_3220267060095610864);
void car_F_fun(double *state, double dt, double *out_5498270358931541556);
void car_h_25(double *state, double *unused, double *out_5568378315864805240);
void car_H_25(double *state, double *unused, double *out_2053125876532739177);
void car_h_24(double *state, double *unused, double *out_8626736192149469552);
void car_H_24(double *state, double *unused, double *out_119523722472760389);
void car_h_30(double *state, double *unused, double *out_4997093107090697191);
void car_H_30(double *state, double *unused, double *out_8969816218024355932);
void car_h_26(double *state, double *unused, double *out_34713109409403959);
void car_H_26(double *state, double *unused, double *out_5357651846293539778);
void car_h_27(double *state, double *unused, double *out_6395928148715762059);
void car_H_27(double *state, double *unused, double *out_6795052906223931021);
void car_h_29(double *state, double *unused, double *out_8413366396739767207);
void car_H_29(double *state, double *unused, double *out_5081690179354379988);
void car_h_28(double *state, double *unused, double *out_7049142657332943912);
void car_H_28(double *state, double *unused, double *out_708837715150586);
void car_h_31(double *state, double *unused, double *out_1930928787610782890);
void car_H_31(double *state, double *unused, double *out_2083771838409699605);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}