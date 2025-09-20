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
void car_err_fun(double *nom_x, double *delta_x, double *out_5951427109496666900);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_3753933029986705763);
void car_H_mod_fun(double *state, double *out_1598157310801926240);
void car_f_fun(double *state, double dt, double *out_5645298880168262869);
void car_F_fun(double *state, double dt, double *out_716541319675324393);
void car_h_25(double *state, double *unused, double *out_2904930533355629161);
void car_H_25(double *state, double *unused, double *out_1924823339187565437);
void car_h_24(double *state, double *unused, double *out_8473448618580967526);
void car_H_24(double *state, double *unused, double *out_2821685987778943597);
void car_h_30(double *state, double *unused, double *out_5318829265255205330);
void car_H_30(double *state, double *unused, double *out_4443156297694814064);
void car_h_26(double *state, double *unused, double *out_8867577960655567420);
void car_H_26(double *state, double *unused, double *out_1816679979686490787);
void car_h_27(double *state, double *unused, double *out_1961420680453966726);
void car_H_27(double *state, double *unused, double *out_6666750368878757281);
void car_h_29(double *state, double *unused, double *out_6678456796264575158);
void car_H_29(double *state, double *unused, double *out_4953387642009206248);
void car_h_28(double *state, double *unused, double *out_2320143160789693782);
void car_H_28(double *state, double *unused, double *out_129011375060324326);
void car_h_31(double *state, double *unused, double *out_8354860635895864126);
void car_H_31(double *state, double *unused, double *out_1955469301064525865);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}