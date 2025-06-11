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
void car_err_fun(double *nom_x, double *delta_x, double *out_4158925373118689754);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4984125863451852969);
void car_H_mod_fun(double *state, double *out_7144135399215499310);
void car_f_fun(double *state, double dt, double *out_4290930710925439296);
void car_F_fun(double *state, double dt, double *out_6422410295062662532);
void car_h_25(double *state, double *unused, double *out_278399437397340579);
void car_H_25(double *state, double *unused, double *out_1620022460843769287);
void car_h_24(double *state, double *unused, double *out_2140840430466241598);
void car_H_24(double *state, double *unused, double *out_552627138161730279);
void car_h_30(double *state, double *unused, double *out_7182159326851547746);
void car_H_30(double *state, double *unused, double *out_4138355419351017914);
void car_h_26(double *state, double *unused, double *out_6038677531022678923);
void car_H_26(double *state, double *unused, double *out_2121480858030286937);
void car_h_27(double *state, double *unused, double *out_5423289500512988116);
void car_H_27(double *state, double *unused, double *out_1963592107550593003);
void car_h_29(double *state, double *unused, double *out_6578843442175070229);
void car_H_29(double *state, double *unused, double *out_4648586763665410098);
void car_h_28(double *state, double *unused, double *out_8131199048761675284);
void car_H_28(double *state, double *unused, double *out_433812253404120476);
void car_h_31(double *state, double *unused, double *out_435586105748469724);
void car_H_31(double *state, double *unused, double *out_2747688960263638413);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}