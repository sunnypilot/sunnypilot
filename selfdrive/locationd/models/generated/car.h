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
void car_err_fun(double *nom_x, double *delta_x, double *out_4404972482043756320);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1878142591409797047);
void car_H_mod_fun(double *state, double *out_8303006938306786866);
void car_f_fun(double *state, double dt, double *out_4068599896429511203);
void car_F_fun(double *state, double dt, double *out_6707421618485807550);
void car_h_25(double *state, double *unused, double *out_6170927995150476655);
void car_H_25(double *state, double *unused, double *out_1911527141633227669);
void car_h_24(double *state, double *unused, double *out_5813330457683306165);
void car_H_24(double *state, double *unused, double *out_498498893594818832);
void car_h_30(double *state, double *unused, double *out_5895733932865970766);
void car_H_30(double *state, double *unused, double *out_606805816874020958);
void car_h_26(double *state, double *unused, double *out_4205286098130289806);
void car_H_26(double *state, double *unused, double *out_5653030460507283893);
void car_h_27(double *state, double *unused, double *out_1169254727489631010);
void car_H_27(double *state, double *unused, double *out_1567957494926403953);
void car_h_29(double *state, double *unused, double *out_894060665205125121);
void car_H_29(double *state, double *unused, double *out_1117037161188413142);
void car_h_28(double *state, double *unused, double *out_2112764580391293445);
void car_H_28(double *state, double *unused, double *out_3965361855881117432);
void car_h_31(double *state, double *unused, double *out_6013741326799347510);
void car_H_31(double *state, double *unused, double *out_6279238562740635369);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}