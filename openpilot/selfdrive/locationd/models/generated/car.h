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
void car_err_fun(double *nom_x, double *delta_x, double *out_6263818396156197794);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_8403854160198660494);
void car_H_mod_fun(double *state, double *out_2773070206469320626);
void car_f_fun(double *state, double dt, double *out_3353722608774504922);
void car_F_fun(double *state, double dt, double *out_5992377215234180239);
void car_h_25(double *state, double *unused, double *out_9059731259054464923);
void car_H_25(double *state, double *unused, double *out_6296050856458812303);
void car_h_24(double *state, double *unused, double *out_3366975732395860410);
void car_H_24(double *state, double *unused, double *out_8592767618448416177);
void car_h_30(double *state, double *unused, double *out_4202737548822924391);
void car_H_30(double *state, double *unused, double *out_6166711909315572233);
void car_h_26(double *state, double *unused, double *out_8168308899468918369);
void car_H_26(double *state, double *unused, double *out_2554547537584756079);
void car_h_27(double *state, double *unused, double *out_2056968555261399144);
void car_H_27(double *state, double *unused, double *out_3991948597515147322);
void car_h_29(double *state, double *unused, double *out_1899781886910269999);
void car_H_29(double *state, double *unused, double *out_2278585870645596289);
void car_h_28(double *state, double *unused, double *out_979817496182933541);
void car_H_28(double *state, double *unused, double *out_2803813146423934285);
void car_h_31(double *state, double *unused, double *out_3219898774683952390);
void car_H_31(double *state, double *unused, double *out_6326696818335772731);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}