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
void car_err_fun(double *nom_x, double *delta_x, double *out_5824625824693245396);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_827571073640092976);
void car_H_mod_fun(double *state, double *out_5176602298372304418);
void car_f_fun(double *state, double dt, double *out_3449864392992608841);
void car_F_fun(double *state, double dt, double *out_5579800985270018693);
void car_h_25(double *state, double *unused, double *out_7875926850580227468);
void car_H_25(double *state, double *unused, double *out_4018744907348973114);
void car_h_24(double *state, double *unused, double *out_5156118782180595319);
void car_H_24(double *state, double *unused, double *out_2289881788171659045);
void car_h_30(double *state, double *unused, double *out_1105091624229876532);
void car_H_30(double *state, double *unused, double *out_7511308824868961747);
void car_h_26(double *state, double *unused, double *out_3896581643430969113);
void car_H_26(double *state, double *unused, double *out_277241588474916890);
void car_h_27(double *state, double *unused, double *out_5569143955468478503);
void car_H_27(double *state, double *unused, double *out_8760671937040164958);
void car_h_29(double *state, double *unused, double *out_6106764891890722177);
void car_H_29(double *state, double *unused, double *out_7001077480554569563);
void car_h_28(double *state, double *unused, double *out_6512653808370140938);
void car_H_28(double *state, double *unused, double *out_6363267576085451479);
void car_h_31(double *state, double *unused, double *out_2807551966308651707);
void car_H_31(double *state, double *unused, double *out_4049390869225933542);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}