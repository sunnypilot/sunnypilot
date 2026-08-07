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
void car_err_fun(double *nom_x, double *delta_x, double *out_1308307769420293042);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_2556976084631402);
void car_H_mod_fun(double *state, double *out_6527467579721338563);
void car_f_fun(double *state, double dt, double *out_46405867141907835);
void car_F_fun(double *state, double dt, double *out_3458223914096858551);
void car_h_25(double *state, double *unused, double *out_5649626404835719527);
void car_H_25(double *state, double *unused, double *out_1393870453252521242);
void car_h_24(double *state, double *unused, double *out_775491211629833659);
void car_H_24(double *state, double *unused, double *out_778779145752978324);
void car_h_30(double *state, double *unused, double *out_6641670473033171960);
void car_H_30(double *state, double *unused, double *out_3912203411759769869);
void car_h_26(double *state, double *unused, double *out_7244986357709649477);
void car_H_26(double *state, double *unused, double *out_2347632865621534982);
void car_h_27(double *state, double *unused, double *out_1785517029592981286);
void car_H_27(double *state, double *unused, double *out_1737440099959344958);
void car_h_29(double *state, double *unused, double *out_9200668279867682005);
void car_H_29(double *state, double *unused, double *out_4422434756074162053);
void car_h_28(double *state, double *unused, double *out_2729026882494643721);
void car_H_28(double *state, double *unused, double *out_659964260995368521);
void car_h_31(double *state, double *unused, double *out_6026282442523481153);
void car_H_31(double *state, double *unused, double *out_2973840967854886458);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}