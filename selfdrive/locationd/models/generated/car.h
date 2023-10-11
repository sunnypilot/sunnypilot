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
void car_err_fun(double *nom_x, double *delta_x, double *out_3451169381060055315);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7186137212168118329);
void car_H_mod_fun(double *state, double *out_7616985092703441005);
void car_f_fun(double *state, double dt, double *out_5673807216349312269);
void car_F_fun(double *state, double dt, double *out_6905028213774737392);
void car_h_25(double *state, double *unused, double *out_8121427082764877011);
void car_H_25(double *state, double *unused, double *out_3812417976563737166);
void car_h_24(double *state, double *unused, double *out_3997942509789646952);
void car_H_24(double *state, double *unused, double *out_8681232841591444018);
void car_h_30(double *state, double *unused, double *out_1350591856414526075);
void car_H_30(double *state, double *unused, double *out_8340114306691345364);
void car_h_26(double *state, double *unused, double *out_3651081411246319570);
void car_H_26(double *state, double *unused, double *out_7553921295437793390);
void car_h_27(double *state, double *unused, double *out_3533074017312942826);
void car_H_27(double *state, double *unused, double *out_7931866455217781341);
void car_h_29(double *state, double *unused, double *out_7631377315592314690);
void car_H_29(double *state, double *unused, double *out_7829882962376953180);
void car_h_28(double *state, double *unused, double *out_4141131178418881891);
void car_H_28(double *state, double *unused, double *out_5534462094263067862);
void car_h_31(double *state, double *unused, double *out_1685439514226132721);
void car_H_31(double *state, double *unused, double *out_8180129397671144866);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}