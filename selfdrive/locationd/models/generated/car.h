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
void car_err_fun(double *nom_x, double *delta_x, double *out_6670847255313813537);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3529315537186539635);
void car_H_mod_fun(double *state, double *out_338496889012731866);
void car_f_fun(double *state, double dt, double *out_3923934035523038452);
void car_F_fun(double *state, double dt, double *out_4825516617134300251);
void car_h_25(double *state, double *unused, double *out_2301414804881314403);
void car_H_25(double *state, double *unused, double *out_8854691336899505371);
void car_h_24(double *state, double *unused, double *out_620520591641681701);
void car_H_24(double *state, double *unused, double *out_4845543409843537211);
void car_h_30(double *state, double *unused, double *out_8684770504579348888);
void car_H_30(double *state, double *unused, double *out_6336358378392256744);
void car_h_26(double *state, double *unused, double *out_8818463716228540293);
void car_H_26(double *state, double *unused, double *out_5850549417935990021);
void car_h_27(double *state, double *unused, double *out_2700258462779531242);
void car_H_27(double *state, double *unused, double *out_4112764307208313527);
void car_h_29(double *state, double *unused, double *out_1249627070150648075);
void car_H_29(double *state, double *unused, double *out_5826127034077864560);
void car_h_28(double *state, double *unused, double *out_5424608509547706960);
void car_H_28(double *state, double *unused, double *out_7538218022562156482);
void car_h_31(double *state, double *unused, double *out_5938864333135336753);
void car_H_31(double *state, double *unused, double *out_8824045375022544943);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}