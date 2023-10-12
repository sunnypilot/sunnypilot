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
void car_err_fun(double *nom_x, double *delta_x, double *out_4478115031684730111);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_977820433766164866);
void car_H_mod_fun(double *state, double *out_3399376930338853021);
void car_f_fun(double *state, double dt, double *out_4607110025418154468);
void car_F_fun(double *state, double dt, double *out_3068422806702534156);
void car_h_25(double *state, double *unused, double *out_8030843570930631638);
void car_H_25(double *state, double *unused, double *out_4054472870645857943);
void car_h_24(double *state, double *unused, double *out_5199469125424995696);
void car_H_24(double *state, double *unused, double *out_5164206016994498448);
void car_h_30(double *state, double *unused, double *out_1260008344580280702);
void car_H_30(double *state, double *unused, double *out_473223459481750255);
void car_h_26(double *state, double *unused, double *out_3741664923080564943);
void car_H_26(double *state, double *unused, double *out_312969551771801719);
void car_h_27(double *state, double *unused, double *out_6340395736194950678);
void car_H_27(double *state, double *unused, double *out_2647986771282175166);
void car_h_29(double *state, double *unused, double *out_5950901141673940809);
void car_H_29(double *state, double *unused, double *out_37007884832641929);
void car_h_28(double *state, double *unused, double *out_7690649602705446720);
void car_H_28(double *state, double *unused, double *out_5045391132236888645);
void car_h_31(double *state, double *unused, double *out_2522961007894396619);
void car_H_31(double *state, double *unused, double *out_313238550461549757);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}