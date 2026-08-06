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
void car_err_fun(double *nom_x, double *delta_x, double *out_2367152293466283987);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5829526074669369656);
void car_H_mod_fun(double *state, double *out_1755007343641557895);
void car_f_fun(double *state, double dt, double *out_8527162516255122736);
void car_F_fun(double *state, double dt, double *out_7094558340758265304);
void car_h_25(double *state, double *unused, double *out_6286236977752489740);
void car_H_25(double *state, double *unused, double *out_4084839440865213267);
void car_h_24(double *state, double *unused, double *out_6918439556027581256);
void car_H_24(double *state, double *unused, double *out_4929836049648908666);
void car_h_30(double *state, double *unused, double *out_6443423646103618885);
void car_H_30(double *state, double *unused, double *out_6603172399372461894);
void car_h_26(double *state, double *unused, double *out_7270973478954575704);
void car_H_26(double *state, double *unused, double *out_343336121991157043);
void car_h_27(double *state, double *unused, double *out_9123721044512729191);
void car_H_27(double *state, double *unused, double *out_8826766470556405111);
void car_h_29(double *state, double *unused, double *out_2352885818162378255);
void car_H_29(double *state, double *unused, double *out_7113403743686854078);
void car_h_28(double *state, double *unused, double *out_8180211191611066756);
void car_H_28(double *state, double *unused, double *out_2031004726617323504);
void car_h_31(double *state, double *unused, double *out_5572679169480766713);
void car_H_31(double *state, double *unused, double *out_282871980242194433);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}