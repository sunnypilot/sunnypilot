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
void car_err_fun(double *nom_x, double *delta_x, double *out_6009369833100329869);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4988631012282075045);
void car_H_mod_fun(double *state, double *out_8291842742918771528);
void car_f_fun(double *state, double dt, double *out_2540038828347396790);
void car_F_fun(double *state, double dt, double *out_582319150166730703);
void car_h_25(double *state, double *unused, double *out_846705907394000494);
void car_H_25(double *state, double *unused, double *out_6804065410528503604);
void car_h_24(double *state, double *unused, double *out_5408900164323158659);
void car_H_24(double *state, double *unused, double *out_5067106856589529911);
void car_h_30(double *state, double *unused, double *out_2664788043652164855);
void car_H_30(double *state, double *unused, double *out_9124345704673799385);
void car_h_26(double *state, double *unused, double *out_3734253473761684291);
void car_H_26(double *state, double *unused, double *out_3062562091654447380);
void car_h_27(double *state, double *unused, double *out_3883491958838333179);
void car_H_27(double *state, double *unused, double *out_4499963151584838623);
void car_h_29(double *state, double *unused, double *out_3608297896553827290);
void car_H_29(double *state, double *unused, double *out_2786600424715287590);
void car_h_28(double *state, double *unused, double *out_6487897279647030830);
void car_H_28(double *state, double *unused, double *out_4750230696280613841);
void car_h_31(double *state, double *unused, double *out_5924129318956350442);
void car_H_31(double *state, double *unused, double *out_6834711372405464032);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}