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
void car_err_fun(double *nom_x, double *delta_x, double *out_2055827145629245641);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5357743043563844621);
void car_H_mod_fun(double *state, double *out_3260931406444101209);
void car_f_fun(double *state, double dt, double *out_7842303097555582420);
void car_F_fun(double *state, double dt, double *out_4745107738599081994);
void car_h_25(double *state, double *unused, double *out_6483180039600536938);
void car_H_25(double *state, double *unused, double *out_262049243545390468);
void car_h_24(double *state, double *unused, double *out_7077662757578670640);
void car_H_24(double *state, double *unused, double *out_2439263667152540441);
void car_h_30(double *state, double *unused, double *out_5032548646971653771);
void car_H_30(double *state, double *unused, double *out_2780382202052639095);
void car_h_26(double *state, double *unused, double *out_8072328190851867282);
void car_H_26(double *state, double *unused, double *out_3479454075328665756);
void car_h_27(double *state, double *unused, double *out_2152949263878450231);
void car_H_27(double *state, double *unused, double *out_5003976273236582312);
void car_h_29(double *state, double *unused, double *out_8412522159077052200);
void car_H_29(double *state, double *unused, double *out_3290613546367031279);
void car_h_28(double *state, double *unused, double *out_7154622531539295876);
void car_H_28(double *state, double *unused, double *out_1791785470702499295);
void car_h_31(double *state, double *unused, double *out_1398092611153512247);
void car_H_31(double *state, double *unused, double *out_4105662177562017232);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}