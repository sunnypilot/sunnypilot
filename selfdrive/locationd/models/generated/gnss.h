#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void gnss_update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_err_fun(double *nom_x, double *delta_x, double *out_2474256111087528474);
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_7051622024455451737);
void gnss_H_mod_fun(double *state, double *out_7896233018555451228);
void gnss_f_fun(double *state, double dt, double *out_4333426533206936818);
void gnss_F_fun(double *state, double dt, double *out_2869766722226837856);
void gnss_h_6(double *state, double *sat_pos, double *out_1024352917879833673);
void gnss_H_6(double *state, double *sat_pos, double *out_6472797684402021181);
void gnss_h_20(double *state, double *sat_pos, double *out_501984527921721025);
void gnss_H_20(double *state, double *sat_pos, double *out_1676448818287402981);
void gnss_h_7(double *state, double *sat_pos_vel, double *out_517986936952942546);
void gnss_H_7(double *state, double *sat_pos_vel, double *out_579701802137747330);
void gnss_h_21(double *state, double *sat_pos_vel, double *out_517986936952942546);
void gnss_H_21(double *state, double *sat_pos_vel, double *out_579701802137747330);
void gnss_predict(double *in_x, double *in_P, double *in_Q, double dt);
}