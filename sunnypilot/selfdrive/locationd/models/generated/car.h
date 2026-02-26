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
void car_err_fun(double *nom_x, double *delta_x, double *out_2451474689670239473);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_604343562526300868);
void car_H_mod_fun(double *state, double *out_7527290391511332925);
void car_f_fun(double *state, double dt, double *out_5082395293757901048);
void car_F_fun(double *state, double dt, double *out_8822652265481800230);
void car_h_25(double *state, double *unused, double *out_345105324244458672);
void car_H_25(double *state, double *unused, double *out_4004241752865967777);
void car_h_24(double *state, double *unused, double *out_3988546653363688877);
void car_H_24(double *state, double *unused, double *out_7562167351668290913);
void car_h_30(double *state, double *unused, double *out_9209216749137479858);
void car_H_30(double *state, double *unused, double *out_7525811979351967084);
void car_h_26(double *state, double *unused, double *out_4235854056911226113);
void car_H_26(double *state, double *unused, double *out_262738433991911553);
void car_h_27(double *state, double *unused, double *out_3381891375688791357);
void car_H_27(double *state, double *unused, double *out_8746168782557159621);
void car_h_29(double *state, double *unused, double *out_8294017471670409323);
void car_H_29(double *state, double *unused, double *out_7015580635037574900);
void car_h_28(double *state, double *unused, double *out_1016060705592837655);
void car_H_28(double *state, double *unused, double *out_6348764421602446142);
void car_h_31(double *state, double *unused, double *out_7115453440004429653);
void car_H_31(double *state, double *unused, double *out_4034887714742928205);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}