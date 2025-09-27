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
void car_err_fun(double *nom_x, double *delta_x, double *out_8815656279812630393);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_2634005456400563428);
void car_H_mod_fun(double *state, double *out_5776307114296964175);
void car_f_fun(double *state, double dt, double *out_3329281261028883663);
void car_F_fun(double *state, double dt, double *out_1569093053633695445);
void car_h_25(double *state, double *unused, double *out_7560488039046634277);
void car_H_25(double *state, double *unused, double *out_8687652227143085723);
void car_h_24(double *state, double *unused, double *out_221107266672237923);
void car_H_24(double *state, double *unused, double *out_6999835791273981532);
void car_h_30(double *state, double *unused, double *out_4719141994691783036);
void car_H_30(double *state, double *unused, double *out_8816991174286325793);
void car_h_26(double *state, double *unused, double *out_6539264067491314914);
void car_H_26(double *state, double *unused, double *out_6017588527692409669);
void car_h_27(double *state, double *unused, double *out_5923876036981624107);
void car_H_27(double *state, double *unused, double *out_7454989587622800912);
void car_h_29(double *state, double *unused, double *out_6078256905706434238);
void car_H_29(double *state, double *unused, double *out_5741626860753249879);
void car_h_28(double *state, double *unused, double *out_3543704664347405758);
void car_H_28(double *state, double *unused, double *out_659227843683719305);
void car_h_31(double *state, double *unused, double *out_1683110624051124240);
void car_H_31(double *state, double *unused, double *out_8657006265266125295);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}