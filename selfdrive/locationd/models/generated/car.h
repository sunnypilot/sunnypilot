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
void car_err_fun(double *nom_x, double *delta_x, double *out_651882661893372929);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_727172026312988685);
void car_H_mod_fun(double *state, double *out_5475808663598843623);
void car_f_fun(double *state, double dt, double *out_4635679633596871047);
void car_F_fun(double *state, double dt, double *out_6816757899860436014);
void car_h_25(double *state, double *unused, double *out_7319455008445036725);
void car_H_25(double *state, double *unused, double *out_654806835171789637);
void car_h_24(double *state, double *unused, double *out_5541470801123603669);
void car_H_24(double *state, double *unused, double *out_1517842763833709929);
void car_h_30(double *state, double *unused, double *out_8770086401073919892);
void car_H_30(double *state, double *unused, double *out_3173139793679038264);
void car_h_26(double *state, double *unused, double *out_4033927801554674889);
void car_H_26(double *state, double *unused, double *out_3086696483702266587);
void car_h_27(double *state, double *unused, double *out_3916379579010293380);
void car_H_27(double *state, double *unused, double *out_1649295423771875344);
void car_h_29(double *state, double *unused, double *out_3768413133413074247);
void car_H_29(double *state, double *unused, double *out_3362658150641426377);
void car_h_28(double *state, double *unused, double *out_8652079007140543148);
void car_H_28(double *state, double *unused, double *out_1399027879076100126);
void car_h_31(double *state, double *unused, double *out_548619782094685789);
void car_H_31(double *state, double *unused, double *out_685452797048750065);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}