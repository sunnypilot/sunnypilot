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
void car_err_fun(double *nom_x, double *delta_x, double *out_7675945724591624261);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_9175739039507983624);
void car_H_mod_fun(double *state, double *out_4679052084973721620);
void car_f_fun(double *state, double dt, double *out_2673333106136537243);
void car_F_fun(double *state, double dt, double *out_5868321442563579311);
void car_h_25(double *state, double *unused, double *out_417479862903067851);
void car_H_25(double *state, double *unused, double *out_2343775444601259513);
void car_h_24(double *state, double *unused, double *out_2649485575402304942);
void car_H_24(double *state, double *unused, double *out_4516425043606759079);
void car_h_30(double *state, double *unused, double *out_9057357339621609735);
void car_H_30(double *state, double *unused, double *out_6871471774728867711);
void car_h_26(double *state, double *unused, double *out_6244805236351756352);
void car_H_26(double *state, double *unused, double *out_6085278763475315737);
void car_h_27(double *state, double *unused, double *out_3454265914347400536);
void car_H_27(double *state, double *unused, double *out_4647877703544924494);
void car_h_29(double *state, double *unused, double *out_8221642933011800144);
void car_H_29(double *state, double *unused, double *out_6361240430414475527);
void car_h_28(double *state, double *unused, double *out_1167920115108707778);
void car_H_28(double *state, double *unused, double *out_4397610158849149276);
void car_h_31(double *state, double *unused, double *out_692673925187573740);
void car_H_31(double *state, double *unused, double *out_2313129482724299085);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}