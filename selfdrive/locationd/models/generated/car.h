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
void car_err_fun(double *nom_x, double *delta_x, double *out_853408928340835901);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7742796402997516638);
void car_H_mod_fun(double *state, double *out_6309495207021630516);
void car_f_fun(double *state, double dt, double *out_514567004980479814);
void car_F_fun(double *state, double dt, double *out_5656357106442317914);
void car_h_25(double *state, double *unused, double *out_5718536217680117524);
void car_H_25(double *state, double *unused, double *out_1405803381836965676);
void car_h_24(double *state, double *unused, double *out_5378089274505107240);
void car_H_24(double *state, double *unused, double *out_1876260863880304400);
void car_h_30(double *state, double *unused, double *out_2044729039140554917);
void car_H_30(double *state, double *unused, double *out_1535142328980205746);
void car_h_26(double *state, double *unused, double *out_992057012303777768);
void car_H_26(double *state, double *unused, double *out_5147306700711021900);
void car_h_27(double *state, double *unused, double *out_5935964882397702313);
void car_H_27(double *state, double *unused, double *out_3709905640780630657);
void car_h_29(double *state, double *unused, double *out_3870901714593307419);
void car_H_29(double *state, double *unused, double *out_1024910984665813562);
void car_h_28(double *state, double *unused, double *out_2660117069650245724);
void car_H_28(double *state, double *unused, double *out_3459638096084855439);
void car_h_31(double *state, double *unused, double *out_8629904557750062228);
void car_H_31(double *state, double *unused, double *out_1375157419960005248);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}