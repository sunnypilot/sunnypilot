#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void gnss_update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_err_fun(double *nom_x, double *delta_x, double *out_5888416049405480502);
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_772137700245917424);
void gnss_H_mod_fun(double *state, double *out_6081254025442487169);
void gnss_f_fun(double *state, double dt, double *out_7103374999999395041);
void gnss_F_fun(double *state, double dt, double *out_3225715469495907391);
void gnss_h_6(double *state, double *sat_pos, double *out_4135186210083771617);
void gnss_H_6(double *state, double *sat_pos, double *out_2035153063914442509);
void gnss_h_20(double *state, double *sat_pos, double *out_2483402616262014693);
void gnss_H_20(double *state, double *sat_pos, double *out_8177039925481845738);
void gnss_h_7(double *state, double *sat_pos_vel, double *out_1668019775180221260);
void gnss_H_7(double *state, double *sat_pos_vel, double *out_887204893166495018);
void gnss_h_21(double *state, double *sat_pos_vel, double *out_1668019775180221260);
void gnss_H_21(double *state, double *sat_pos_vel, double *out_887204893166495018);
void gnss_predict(double *in_x, double *in_P, double *in_Q, double dt);
}