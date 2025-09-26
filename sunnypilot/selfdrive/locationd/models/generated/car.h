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
void car_err_fun(double *nom_x, double *delta_x, double *out_3178351787780867479);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6240253129487023512);
void car_H_mod_fun(double *state, double *out_7483116987311173272);
void car_f_fun(double *state, double dt, double *out_5651695903721239210);
void car_F_fun(double *state, double dt, double *out_13263414419101982);
void car_h_25(double *state, double *unused, double *out_4287938734280851291);
void car_H_25(double *state, double *unused, double *out_7820602372196285352);
void car_h_24(double *state, double *unused, double *out_967862149043042631);
void car_H_24(double *state, double *unused, double *out_402210738519358459);
void car_h_30(double *state, double *unused, double *out_4012744671996345402);
void car_H_30(double *state, double *unused, double *out_7949941319339525422);
void car_h_26(double *state, double *unused, double *out_3069234819094682967);
void car_H_26(double *state, double *unused, double *out_6884638382639210040);
void car_h_27(double *state, double *unused, double *out_7156042635635634546);
void car_H_27(double *state, double *unused, double *out_8322039442569601283);
void car_h_29(double *state, double *unused, double *out_3409428787319867885);
void car_H_29(double *state, double *unused, double *out_6608676715700050250);
void car_h_28(double *state, double *unused, double *out_976713301355686606);
void car_H_28(double *state, double *unused, double *out_1526277698630519676);
void car_h_31(double *state, double *unused, double *out_3605000760603672068);
void car_H_31(double *state, double *unused, double *out_7789956410319324924);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}