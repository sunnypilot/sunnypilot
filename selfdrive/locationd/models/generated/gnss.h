#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void gnss_update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_err_fun(double *nom_x, double *delta_x, double *out_2891005972447064978);
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_3707348186065527957);
void gnss_H_mod_fun(double *state, double *out_3968679355288269749);
void gnss_f_fun(double *state, double dt, double *out_399920222174142974);
void gnss_F_fun(double *state, double dt, double *out_4032596610344199094);
void gnss_h_6(double *state, double *sat_pos, double *out_7663281162910400321);
void gnss_H_6(double *state, double *sat_pos, double *out_6735513936967990127);
void gnss_h_20(double *state, double *sat_pos, double *out_113008328182865177);
void gnss_H_20(double *state, double *sat_pos, double *out_8868019487569726413);
void gnss_h_7(double *state, double *sat_pos_vel, double *out_4555536823234833923);
void gnss_H_7(double *state, double *sat_pos_vel, double *out_4061718503456001340);
void gnss_h_21(double *state, double *sat_pos_vel, double *out_4555536823234833923);
void gnss_H_21(double *state, double *sat_pos_vel, double *out_4061718503456001340);
void gnss_predict(double *in_x, double *in_P, double *in_Q, double dt);
}