#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void gnss_update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_err_fun(double *nom_x, double *delta_x, double *out_6747998805596484752);
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_6535890535670437130);
void gnss_H_mod_fun(double *state, double *out_4448015362564357721);
void gnss_f_fun(double *state, double dt, double *out_9118525254568713176);
void gnss_F_fun(double *state, double dt, double *out_6402003280863482888);
void gnss_h_6(double *state, double *sat_pos, double *out_5846375561327839295);
void gnss_H_6(double *state, double *sat_pos, double *out_2124454474474073235);
void gnss_h_20(double *state, double *sat_pos, double *out_963325950330645553);
void gnss_H_20(double *state, double *sat_pos, double *out_963608637703027460);
void gnss_h_7(double *state, double *sat_pos_vel, double *out_9158958912499879745);
void gnss_H_7(double *state, double *sat_pos_vel, double *out_1177645737388839302);
void gnss_h_21(double *state, double *sat_pos_vel, double *out_9158958912499879745);
void gnss_H_21(double *state, double *sat_pos_vel, double *out_1177645737388839302);
void gnss_predict(double *in_x, double *in_P, double *in_Q, double dt);
}