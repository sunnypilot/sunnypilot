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
void car_err_fun(double *nom_x, double *delta_x, double *out_1027636603068461502);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_2498107869525935257);
void car_H_mod_fun(double *state, double *out_2880487860269583385);
void car_f_fun(double *state, double dt, double *out_8985245024092687483);
void car_F_fun(double *state, double dt, double *out_135664326016666632);
void car_h_25(double *state, double *unused, double *out_1339936627130384923);
void car_H_25(double *state, double *unused, double *out_8541205388556229655);
void car_h_24(double *state, double *unused, double *out_7843416543337357224);
void car_H_24(double *state, double *unused, double *out_4983279789753906519);
void car_h_30(double *state, double *unused, double *out_7253669653801133296);
void car_H_30(double *state, double *unused, double *out_6022872430048981028);
void car_h_26(double *state, double *unused, double *out_7856985538477610813);
void car_H_26(double *state, double *unused, double *out_5236679418795429054);
void car_h_27(double *state, double *unused, double *out_3661736640530460722);
void car_H_27(double *state, double *unused, double *out_3799278358865037811);
void car_h_29(double *state, double *unused, double *out_2211105247901577555);
void car_H_29(double *state, double *unused, double *out_5512641085734588844);
void car_h_28(double *state, double *unused, double *out_8663409908191306367);
void car_H_28(double *state, double *unused, double *out_7851703970905432198);
void car_h_31(double *state, double *unused, double *out_5201620103558886575);
void car_H_31(double *state, double *unused, double *out_1464530138044412402);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}