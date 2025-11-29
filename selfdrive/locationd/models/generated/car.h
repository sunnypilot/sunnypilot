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
void car_err_fun(double *nom_x, double *delta_x, double *out_8556571550800620063);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_9079666833948885683);
void car_H_mod_fun(double *state, double *out_7049774927416388908);
void car_f_fun(double *state, double dt, double *out_3420217845127717081);
void car_F_fun(double *state, double dt, double *out_9037712059141071569);
void car_h_25(double *state, double *unused, double *out_720820836113428015);
void car_H_25(double *state, double *unused, double *out_4899946186403132757);
void car_h_24(double *state, double *unused, double *out_4072372206966036697);
void car_H_24(double *state, double *unused, double *out_31131321375425905);
void car_h_30(double *state, double *unused, double *out_2171452228742311182);
void car_H_30(double *state, double *unused, double *out_372249856275524559);
void car_h_26(double *state, double *unused, double *out_4084372493216736072);
void car_H_26(double *state, double *unused, double *out_1158442867529076533);
void car_h_27(double *state, double *unused, double *out_2684701214697879492);
void car_H_27(double *state, double *unused, double *out_2595843927459467776);
void car_h_29(double *state, double *unused, double *out_2830221038918534463);
void car_H_29(double *state, double *unused, double *out_882481200589916743);
void car_h_28(double *state, double *unused, double *out_7910608430533204439);
void car_H_28(double *state, double *unused, double *out_4199917816479613831);
void car_h_31(double *state, double *unused, double *out_8602093486867477200);
void car_H_31(double *state, double *unused, double *out_532234765295725057);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}