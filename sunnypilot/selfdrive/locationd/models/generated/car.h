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
void car_err_fun(double *nom_x, double *delta_x, double *out_5613521568048131713);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5048864844330067690);
void car_H_mod_fun(double *state, double *out_5207187053897704343);
void car_f_fun(double *state, double dt, double *out_6561712789568195606);
void car_F_fun(double *state, double dt, double *out_3103747224237915436);
void car_h_25(double *state, double *unused, double *out_2123834400637475602);
void car_H_25(double *state, double *unused, double *out_5318218986837987468);
void car_h_24(double *state, double *unused, double *out_2925884447193875193);
void car_H_24(double *state, double *unused, double *out_7490868585843487034);
void car_h_30(double *state, double *unused, double *out_1848640338352969713);
void car_H_30(double *state, double *unused, double *out_2799886028330738841);
void car_h_26(double *state, double *unused, double *out_158192503617288753);
void car_H_26(double *state, double *unused, double *out_9059722305712043692);
void car_h_27(double *state, double *unused, double *out_2877838867023370043);
void car_H_27(double *state, double *unused, double *out_4974649340131163752);
void car_h_29(double *state, double *unused, double *out_3153032929307875932);
void car_H_29(double *state, double *unused, double *out_2289654684016346657);
void car_h_28(double *state, double *unused, double *out_8756124354582085131);
void car_H_28(double *state, double *unused, double *out_7372053701085877231);
void car_h_31(double *state, double *unused, double *out_5761283928891497952);
void car_H_31(double *state, double *unused, double *out_8760813665764156448);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}