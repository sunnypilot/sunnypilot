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
void car_err_fun(double *nom_x, double *delta_x, double *out_8852971544794429466);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5565710821617854915);
void car_H_mod_fun(double *state, double *out_3163685400089475165);
void car_f_fun(double *state, double dt, double *out_1059011955327416614);
void car_F_fun(double *state, double dt, double *out_3203946852622260196);
void car_h_25(double *state, double *unused, double *out_5888820655433728672);
void car_H_25(double *state, double *unused, double *out_1740006425095189675);
void car_h_24(double *state, double *unused, double *out_7698655859731977364);
void car_H_24(double *state, double *unused, double *out_1343361120741330180);
void car_h_30(double *state, double *unused, double *out_8836546645789213633);
void car_H_30(double *state, double *unused, double *out_4258339383602438302);
void car_h_26(double *state, double *unused, double *out_7752730088945658857);
void car_H_26(double *state, double *unused, double *out_2001496893778866549);
void car_h_27(double *state, double *unused, double *out_4529810036305668007);
void car_H_27(double *state, double *unused, double *out_6481933454786381519);
void car_h_29(double *state, double *unused, double *out_7146098811053532673);
void car_H_29(double *state, double *unused, double *out_4768570727916830486);
void car_h_28(double *state, double *unused, double *out_471863231355177638);
void car_H_28(double *state, double *unused, double *out_313828289152700088);
void car_h_31(double *state, double *unused, double *out_1992451995320320513);
void car_H_31(double *state, double *unused, double *out_2627704996012218025);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}