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
void car_err_fun(double *nom_x, double *delta_x, double *out_5059320499403781563);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_8028694691748550712);
void car_H_mod_fun(double *state, double *out_1011613483250515043);
void car_f_fun(double *state, double dt, double *out_2197439487468085332);
void car_F_fun(double *state, double dt, double *out_7087540084366041403);
void car_h_25(double *state, double *unused, double *out_7407988264137374316);
void car_H_25(double *state, double *unused, double *out_3892078341934149797);
void car_h_24(double *state, double *unused, double *out_8835218896431103117);
void car_H_24(double *state, double *unused, double *out_2235142160227532400);
void car_h_30(double *state, double *unused, double *out_7565174932488503461);
void car_H_30(double *state, double *unused, double *out_6410411300441398424);
void car_h_26(double *state, double *unused, double *out_1416794239518337304);
void car_H_26(double *state, double *unused, double *out_7196604311694950398);
void car_h_27(double *state, double *unused, double *out_2406314996476528671);
void car_H_27(double *state, double *unused, double *out_8634005371625341641);
void car_h_29(double *state, double *unused, double *out_8277163820412350504);
void car_H_29(double *state, double *unused, double *out_6920642644755790608);
void car_h_28(double *state, double *unused, double *out_5218867099746382054);
void car_H_28(double *state, double *unused, double *out_1838243627686260034);
void car_h_31(double *state, double *unused, double *out_7683182326421880205);
void car_H_31(double *state, double *unused, double *out_7477990481263584566);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}