#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void gnss_update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_err_fun(double *nom_x, double *delta_x, double *out_1087418696294830103);
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_746412675603881976);
void gnss_H_mod_fun(double *state, double *out_6902851921478182689);
void gnss_f_fun(double *state, double dt, double *out_5347949339748000854);
void gnss_F_fun(double *state, double dt, double *out_3634795260627257152);
void gnss_h_6(double *state, double *sat_pos, double *out_4914217899585156638);
void gnss_H_6(double *state, double *sat_pos, double *out_9069722082748577789);
void gnss_h_20(double *state, double *sat_pos, double *out_4990935818312259304);
void gnss_H_20(double *state, double *sat_pos, double *out_3839852145693933779);
void gnss_h_7(double *state, double *sat_pos_vel, double *out_5214992409236640740);
void gnss_H_7(double *state, double *sat_pos_vel, double *out_1614394445830539317);
void gnss_h_21(double *state, double *sat_pos_vel, double *out_5214992409236640740);
void gnss_H_21(double *state, double *sat_pos_vel, double *out_1614394445830539317);
void gnss_predict(double *in_x, double *in_P, double *in_Q, double dt);
}