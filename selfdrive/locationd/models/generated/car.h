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
void car_err_fun(double *nom_x, double *delta_x, double *out_8152243261381841861);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1302168845595593824);
void car_H_mod_fun(double *state, double *out_720082183471150414);
void car_f_fun(double *state, double dt, double *out_1005905684588084232);
void car_F_fun(double *state, double dt, double *out_8578060064959244144);
void car_h_25(double *state, double *unused, double *out_5524927027376144470);
void car_H_25(double *state, double *unused, double *out_3613918526609956662);
void car_h_24(double *state, double *unused, double *out_2463198998502258202);
void car_H_24(double *state, double *unused, double *out_8257253740508076853);
void car_h_30(double *state, double *unused, double *out_2577201037020659509);
void car_H_30(double *state, double *unused, double *out_6132251485117205289);
void car_h_26(double *state, double *unused, double *out_6404768134986181256);
void car_H_26(double *state, double *unused, double *out_127584792264099562);
void car_h_27(double *state, double *unused, double *out_1212977297613836214);
void car_H_27(double *state, double *unused, double *out_8355845556301148506);
void car_h_29(double *state, double *unused, double *out_2424472230640186136);
void car_H_29(double *state, double *unused, double *out_6642482829431597473);
void car_h_28(double *state, double *unused, double *out_2752594053032157764);
void car_H_28(double *state, double *unused, double *out_1560083812362066899);
void car_h_31(double *state, double *unused, double *out_1245908198974206466);
void car_H_31(double *state, double *unused, double *out_3644564488486917090);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}