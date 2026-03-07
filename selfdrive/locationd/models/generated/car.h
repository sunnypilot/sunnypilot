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
void car_err_fun(double *nom_x, double *delta_x, double *out_4509339408202490749);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5279638846554635965);
void car_H_mod_fun(double *state, double *out_5281375903857501390);
void car_f_fun(double *state, double dt, double *out_7805851541589707250);
void car_F_fun(double *state, double dt, double *out_8399297218245309857);
void car_h_25(double *state, double *unused, double *out_2366189864445090968);
void car_H_25(double *state, double *unused, double *out_3911812322054735847);
void car_h_24(double *state, double *unused, double *out_6229388731742918084);
void car_H_24(double *state, double *unused, double *out_5760039343842644875);
void car_h_30(double *state, double *unused, double *out_8317288952443788207);
void car_H_30(double *state, double *unused, double *out_3004878019436880908);
void car_h_26(double *state, double *unused, double *out_1147485949258922644);
void car_H_26(double *state, double *unused, double *out_7653315640928792071);
void car_h_27(double *state, double *unused, double *out_4970595185253788619);
void car_H_27(double *state, double *unused, double *out_830114707636455997);
void car_h_29(double *state, double *unused, double *out_5127781853604917764);
void car_H_29(double *state, double *unused, double *out_3515109363751273092);
void car_h_28(double *state, double *unused, double *out_6265239402201541486);
void car_H_28(double *state, double *unused, double *out_1567289653318257482);
void car_h_31(double *state, double *unused, double *out_8199281558510411463);
void car_H_31(double *state, double *unused, double *out_3881166360177775419);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}