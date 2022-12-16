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
void car_err_fun(double *nom_x, double *delta_x, double *out_6879141421579502993);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5117966674436304926);
void car_H_mod_fun(double *state, double *out_474615079286262384);
void car_f_fun(double *state, double dt, double *out_7000723790512890111);
void car_F_fun(double *state, double dt, double *out_2040835191970999270);
void car_h_25(double *state, double *unused, double *out_2447891744252367846);
void car_H_25(double *state, double *unused, double *out_7470380649254261837);
void car_h_24(double *state, double *unused, double *out_1536598539730519785);
void car_H_24(double *state, double *unused, double *out_4322157966347104022);
void car_h_30(double *state, double *unused, double *out_9218726970602718782);
void car_H_30(double *state, double *unused, double *out_7341041702111021767);
void car_h_26(double *state, double *unused, double *out_8275217117701056347);
void car_H_26(double *state, double *unused, double *out_8127234713364573741);
void car_h_27(double *state, double *unused, double *out_1950060337029261166);
void car_H_27(double *state, double *unused, double *out_5166278390310596856);
void car_h_29(double *state, double *unused, double *out_8615411085926241265);
void car_H_29(double *state, double *unused, double *out_7851273046425413951);
void car_h_28(double *state, double *unused, double *out_6951733604690106811);
void car_H_28(double *state, double *unused, double *out_8631840755718811414);
void car_h_31(double *state, double *unused, double *out_1600981538002701312);
void car_H_31(double *state, double *unused, double *out_7501026611131222265);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}