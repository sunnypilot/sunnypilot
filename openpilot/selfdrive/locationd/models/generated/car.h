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
void car_err_fun(double *nom_x, double *delta_x, double *out_205475353292099530);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6859088956493527341);
void car_H_mod_fun(double *state, double *out_8201686483145055601);
void car_f_fun(double *state, double dt, double *out_2204957494938772746);
void car_F_fun(double *state, double dt, double *out_2327939745960551937);
void car_h_25(double *state, double *unused, double *out_8734450240234959528);
void car_H_25(double *state, double *unused, double *out_6133161197384342845);
void car_h_24(double *state, double *unused, double *out_8806581475742121932);
void car_H_24(double *state, double *unused, double *out_5738011069733690670);
void car_h_30(double *state, double *unused, double *out_971184983414287087);
void car_H_30(double *state, double *unused, double *out_5396892534833592016);
void car_h_26(double *state, double *unused, double *out_1416855028350640224);
void car_H_26(double *state, double *unused, double *out_2391657878510286621);
void car_h_27(double *state, double *unused, double *out_5511166866350839857);
void car_H_27(double *state, double *unused, double *out_7571655846634016927);
void car_h_29(double *state, double *unused, double *out_5235972804066333968);
void car_H_29(double *state, double *unused, double *out_9161725500205983656);
void car_h_28(double *state, double *unused, double *out_7891338238985058206);
void car_H_28(double *state, double *unused, double *out_4079326483136453082);
void car_h_31(double *state, double *unused, double *out_8694811794428211892);
void car_H_31(double *state, double *unused, double *out_6163807159261303273);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}