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
void car_err_fun(double *nom_x, double *delta_x, double *out_6316955287570611368);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_5871234739833284335);
void car_H_mod_fun(double *state, double *out_2946259916610688922);
void car_f_fun(double *state, double dt, double *out_928310023590060116);
void car_F_fun(double *state, double dt, double *out_849753637263936557);
void car_h_25(double *state, double *unused, double *out_2337915436122240747);
void car_H_25(double *state, double *unused, double *out_3550763043279341029);
void car_h_24(double *state, double *unused, double *out_7341814559737059360);
void car_H_24(double *state, double *unused, double *out_7453306437441494267);
void car_h_30(double *state, double *unused, double *out_5543357214631808438);
void car_H_30(double *state, double *unused, double *out_8078459373406949227);
void car_h_26(double *state, double *unused, double *out_7561519623191712615);
void car_H_26(double *state, double *unused, double *out_7292266362153397253);
void car_h_27(double *state, double *unused, double *out_2663757831538604898);
void car_H_27(double *state, double *unused, double *out_5854865302223006010);
void car_h_29(double *state, double *unused, double *out_2938951893823110787);
void car_H_29(double *state, double *unused, double *out_7568228029092557043);
void car_h_28(double *state, double *unused, double *out_7665431099199450543);
void car_H_28(double *state, double *unused, double *out_5796117027547463999);
void car_h_31(double *state, double *unused, double *out_5975364964376263097);
void car_H_31(double *state, double *unused, double *out_3520117081402380601);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}