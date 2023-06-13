#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void gnss_update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_err_fun(double *nom_x, double *delta_x, double *out_6610478330683822785);
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_3052097266079563493);
void gnss_H_mod_fun(double *state, double *out_7863374150261741197);
void gnss_f_fun(double *state, double dt, double *out_1355891940419784179);
void gnss_F_fun(double *state, double dt, double *out_6103640977023954324);
void gnss_h_6(double *state, double *sat_pos, double *out_8639638469545015026);
void gnss_H_6(double *state, double *sat_pos, double *out_3815070702462107900);
void gnss_h_20(double *state, double *sat_pos, double *out_371384230938458631);
void gnss_H_20(double *state, double *sat_pos, double *out_5682384660731021071);
void gnss_h_7(double *state, double *sat_pos_vel, double *out_4876434118703082912);
void gnss_H_7(double *state, double *sat_pos_vel, double *out_5591453878569163415);
void gnss_h_21(double *state, double *sat_pos_vel, double *out_4876434118703082912);
void gnss_H_21(double *state, double *sat_pos_vel, double *out_5591453878569163415);
void gnss_predict(double *in_x, double *in_P, double *in_Q, double dt);
}