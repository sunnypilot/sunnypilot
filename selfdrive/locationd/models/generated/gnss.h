#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void gnss_update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_err_fun(double *nom_x, double *delta_x, double *out_5150571341583167615);
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_4922120609791221850);
void gnss_H_mod_fun(double *state, double *out_6843723691525215114);
void gnss_f_fun(double *state, double dt, double *out_17408948005989977);
void gnss_F_fun(double *state, double dt, double *out_2909713697722566302);
void gnss_h_6(double *state, double *sat_pos, double *out_7716397383098239831);
void gnss_H_6(double *state, double *sat_pos, double *out_8734299093550610133);
void gnss_h_20(double *state, double *sat_pos, double *out_3187395134236655731);
void gnss_H_20(double *state, double *sat_pos, double *out_778578650651897423);
void gnss_h_7(double *state, double *sat_pos_vel, double *out_7558782949651559266);
void gnss_H_7(double *state, double *sat_pos_vel, double *out_1226120805724173486);
void gnss_h_21(double *state, double *sat_pos_vel, double *out_7558782949651559266);
void gnss_H_21(double *state, double *sat_pos_vel, double *out_1226120805724173486);
void gnss_predict(double *in_x, double *in_P, double *in_Q, double dt);
}