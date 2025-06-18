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
void car_err_fun(double *nom_x, double *delta_x, double *out_6475690049946676788);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_2648638800343186983);
void car_H_mod_fun(double *state, double *out_3737699923818243103);
void car_f_fun(double *state, double dt, double *out_6948342231464486417);
void car_F_fun(double *state, double dt, double *out_2362643557470783203);
void car_h_25(double *state, double *unused, double *out_7765488061907301122);
void car_H_25(double *state, double *unused, double *out_2788579001789760894);
void car_h_24(double *state, double *unused, double *out_6031389446812726956);
void car_H_24(double *state, double *unused, double *out_769346597012562242);
void car_h_30(double *state, double *unused, double *out_2239430625356278009);
void car_H_30(double *state, double *unused, double *out_4128111339701855861);
void car_h_26(double *state, double *unused, double *out_4007020432103895459);
void car_H_26(double *state, double *unused, double *out_6530082320663817118);
void car_h_27(double *state, double *unused, double *out_5038526140721293659);
void car_H_27(double *state, double *unused, double *out_5092681260733425875);
void car_h_29(double *state, double *unused, double *out_4763332078436787770);
void car_H_29(double *state, double *unused, double *out_2407686604618608780);
void car_h_28(double *state, double *unused, double *out_7425294093682116204);
void car_H_28(double *state, double *unused, double *out_444056333053282529);
void car_h_31(double *state, double *unused, double *out_4769095137073389962);
void car_H_31(double *state, double *unused, double *out_2757933039912800466);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}