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
void car_err_fun(double *nom_x, double *delta_x, double *out_2237090466909891562);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7921264511585388702);
void car_H_mod_fun(double *state, double *out_4309360915425036189);
void car_f_fun(double *state, double dt, double *out_6525599712203705111);
void car_F_fun(double *state, double dt, double *out_8055578706737644462);
void car_h_25(double *state, double *unused, double *out_6597204507449544518);
void car_H_25(double *state, double *unused, double *out_9213052740609701029);
void car_h_24(double *state, double *unused, double *out_6958676434988343269);
void car_H_24(double *state, double *unused, double *out_3085832238448018832);
void car_h_30(double *state, double *unused, double *out_5078704339909656162);
void car_H_30(double *state, double *unused, double *out_6715358374592601960);
void car_h_26(double *state, double *unused, double *out_3941839072530820280);
void car_H_26(double *state, double *unused, double *out_5929165363339049986);
void car_h_27(double *state, double *unused, double *out_7764948308525686255);
void car_H_27(double *state, double *unused, double *out_8890121686393026871);
void car_h_29(double *state, double *unused, double *out_1479826874621175208);
void car_H_29(double *state, double *unused, double *out_6205127030278209776);
void car_h_28(double *state, double *unused, double *out_6937398475674729436);
void car_H_28(double *state, double *unused, double *out_7159218026361811266);
void car_h_31(double *state, double *unused, double *out_2042672969268997366);
void car_H_31(double *state, double *unused, double *out_6555373465572401462);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}