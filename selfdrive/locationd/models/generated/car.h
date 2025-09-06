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
void car_err_fun(double *nom_x, double *delta_x, double *out_605231361500348121);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1750721289063579832);
void car_H_mod_fun(double *state, double *out_4455056590274498868);
void car_f_fun(double *state, double dt, double *out_6628753160686287132);
void car_F_fun(double *state, double dt, double *out_2264722656215431531);
void car_h_25(double *state, double *unused, double *out_7426226088437493508);
void car_H_25(double *state, double *unused, double *out_2224639529561806043);
void car_h_24(double *state, double *unused, double *out_3037239344096390205);
void car_H_24(double *state, double *unused, double *out_51989930556306477);
void car_h_30(double *state, double *unused, double *out_4205599215429103046);
void car_H_30(double *state, double *unused, double *out_2303056800565802155);
void car_h_26(double *state, double *unused, double *out_5652982176475607162);
void car_H_26(double *state, double *unused, double *out_1516863789312250181);
void car_h_27(double *state, double *unused, double *out_2200318872602168561);
void car_H_27(double *state, double *unused, double *out_4477820112366227066);
void car_h_29(double *state, double *unused, double *out_8483159944286710614);
void car_H_29(double *state, double *unused, double *out_1792825456251409971);
void car_h_28(double *state, double *unused, double *out_2225042042696062972);
void car_H_28(double *state, double *unused, double *out_170804815313916280);
void car_h_31(double *state, double *unused, double *out_7988568567903780367);
void car_H_31(double *state, double *unused, double *out_2143071891545601657);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}