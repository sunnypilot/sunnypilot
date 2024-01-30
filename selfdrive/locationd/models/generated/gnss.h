#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void gnss_update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_err_fun(double *nom_x, double *delta_x, double *out_8052698219636447439);
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_414007979716982857);
void gnss_H_mod_fun(double *state, double *out_1658508881837957111);
void gnss_f_fun(double *state, double dt, double *out_2765158645351032639);
void gnss_F_fun(double *state, double dt, double *out_3889898511770947762);
void gnss_h_6(double *state, double *sat_pos, double *out_3151616376493060002);
void gnss_H_6(double *state, double *sat_pos, double *out_8521601814755962792);
void gnss_h_20(double *state, double *sat_pos, double *out_1001695644916733854);
void gnss_H_20(double *state, double *sat_pos, double *out_3587922318809976588);
void gnss_h_7(double *state, double *sat_pos_vel, double *out_1581577151931372281);
void gnss_H_7(double *state, double *sat_pos_vel, double *out_8392593010464093728);
void gnss_h_21(double *state, double *sat_pos_vel, double *out_1581577151931372281);
void gnss_H_21(double *state, double *sat_pos_vel, double *out_8392593010464093728);
void gnss_predict(double *in_x, double *in_P, double *in_Q, double dt);
}