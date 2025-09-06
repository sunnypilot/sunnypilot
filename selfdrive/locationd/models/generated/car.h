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
void car_err_fun(double *nom_x, double *delta_x, double *out_5118140892357841772);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_4745321206345718051);
void car_H_mod_fun(double *state, double *out_2596711998114896803);
void car_f_fun(double *state, double dt, double *out_6942410117250554106);
void car_F_fun(double *state, double dt, double *out_8478175790585558502);
void car_h_25(double *state, double *unused, double *out_5217460560532285521);
void car_H_25(double *state, double *unused, double *out_926268651874594874);
void car_h_24(double *state, double *unused, double *out_5731469901121999514);
void car_H_24(double *state, double *unused, double *out_7501840458466112975);
void car_h_30(double *state, double *unused, double *out_1580011032278263171);
void car_H_30(double *state, double *unused, double *out_7842958993366211629);
void car_h_26(double *state, double *unused, double *out_7458296519836978259);
void car_H_26(double *state, double *unused, double *out_1583122715984906778);
void car_h_27(double *state, double *unused, double *out_3545652929298450020);
void car_H_27(double *state, double *unused, double *out_5668195681565786718);
void car_h_29(double *state, double *unused, double *out_7065095063619095626);
void car_H_29(double *state, double *unused, double *out_8353190337680603813);
void car_h_28(double *state, double *unused, double *out_8502049626997252450);
void car_H_28(double *state, double *unused, double *out_3270791320611073239);
void car_h_31(double *state, double *unused, double *out_6261968348496233601);
void car_H_31(double *state, double *unused, double *out_956914613751555302);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}