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
void car_err_fun(double *nom_x, double *delta_x, double *out_3066078453041735876);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_7998306431651746749);
void car_H_mod_fun(double *state, double *out_8410823161376016702);
void car_f_fun(double *state, double dt, double *out_8406538155675584278);
void car_F_fun(double *state, double dt, double *out_9168420830296677739);
void car_h_25(double *state, double *unused, double *out_6925664705835598268);
void car_H_25(double *state, double *unused, double *out_842732686421297677);
void car_h_24(double *state, double *unused, double *out_611774507479316058);
void car_H_24(double *state, double *unused, double *out_7496938144529483434);
void car_h_30(double *state, double *unused, double *out_7082851374186727413);
void car_H_30(double *state, double *unused, double *out_3684963643706310521);
void car_h_26(double *state, double *unused, double *out_6139341521285064978);
void car_H_26(double *state, double *unused, double *out_2898770632452758547);
void car_h_27(double *state, double *unused, double *out_8484293316429620663);
void car_H_27(double *state, double *unused, double *out_5859726955506735432);
void car_h_29(double *state, double *unused, double *out_2081178106525881768);
void car_H_29(double *state, double *unused, double *out_3174732299391918337);
void car_h_28(double *state, double *unused, double *out_9087609201106098180);
void car_H_28(double *state, double *unused, double *out_8257131316461448911);
void car_h_31(double *state, double *unused, double *out_7580923347048146882);
void car_H_31(double *state, double *unused, double *out_3524978734686110023);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}