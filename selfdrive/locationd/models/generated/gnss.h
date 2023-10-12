#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void gnss_update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_err_fun(double *nom_x, double *delta_x, double *out_2893903750678761352);
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_1573976658111465050);
void gnss_H_mod_fun(double *state, double *out_6669274116786942791);
void gnss_f_fun(double *state, double dt, double *out_434701726961688353);
void gnss_F_fun(double *state, double dt, double *out_4283718208164219015);
void gnss_h_6(double *state, double *sat_pos, double *out_5902373520985669561);
void gnss_H_6(double *state, double *sat_pos, double *out_3487743119837133558);
void gnss_h_20(double *state, double *sat_pos, double *out_1800868856491256789);
void gnss_H_20(double *state, double *sat_pos, double *out_6403079063733113762);
void gnss_h_7(double *state, double *sat_pos_vel, double *out_8749859653706695012);
void gnss_H_7(double *state, double *sat_pos_vel, double *out_2251765923777389959);
void gnss_h_21(double *state, double *sat_pos_vel, double *out_8749859653706695012);
void gnss_H_21(double *state, double *sat_pos_vel, double *out_2251765923777389959);
void gnss_predict(double *in_x, double *in_P, double *in_Q, double dt);
}