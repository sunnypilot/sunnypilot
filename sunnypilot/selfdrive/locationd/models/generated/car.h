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
void car_err_fun(double *nom_x, double *delta_x, double *out_7386474349186888019);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_1643524624122634889);
void car_H_mod_fun(double *state, double *out_3924863114412422386);
void car_f_fun(double *state, double dt, double *out_3335581872075103078);
void car_F_fun(double *state, double dt, double *out_4298495675166004229);
void car_h_25(double *state, double *unused, double *out_4842735039427911863);
void car_H_25(double *state, double *unused, double *out_4839294745646846211);
void car_h_24(double *state, double *unused, double *out_6391236564095056534);
void car_H_24(double *state, double *unused, double *out_3156043134379392427);
void car_h_30(double *state, double *unused, double *out_8704418515856413515);
void car_H_30(double *state, double *unused, double *out_7357627704154094838);
void car_h_26(double *state, double *unused, double *out_2531416071598916590);
void car_H_26(double *state, double *unused, double *out_1097791426772789987);
void car_h_27(double *state, double *unused, double *out_3338687832041835488);
void car_H_27(double *state, double *unused, double *out_5182864392353669927);
void car_h_29(double *state, double *unused, double *out_4740652290192292456);
void car_H_29(double *state, double *unused, double *out_7867859048468487022);
void car_h_28(double *state, double *unused, double *out_4881309279861547540);
void car_H_28(double *state, double *unused, double *out_2785460031398956448);
void car_h_31(double *state, double *unused, double *out_2273777257731247497);
void car_H_31(double *state, double *unused, double *out_471583324539438511);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}