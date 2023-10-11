#pragma once
#include "rednose/helpers/common_ekf.h"
extern "C" {
void gnss_update_6(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_20(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_7(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_update_21(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void gnss_err_fun(double *nom_x, double *delta_x, double *out_6775506088001038527);
void gnss_inv_err_fun(double *nom_x, double *true_x, double *out_1965239601308615964);
void gnss_H_mod_fun(double *state, double *out_7340239268303197879);
void gnss_f_fun(double *state, double dt, double *out_4979886782540772425);
void gnss_F_fun(double *state, double dt, double *out_4307622071330831920);
void gnss_h_6(double *state, double *sat_pos, double *out_1019340167124243088);
void gnss_H_6(double *state, double *sat_pos, double *out_3723167288690265933);
void gnss_h_20(double *state, double *sat_pos, double *out_5850517768349837563);
void gnss_H_20(double *state, double *sat_pos, double *out_199690115275631714);
void gnss_h_7(double *state, double *sat_pos_vel, double *out_3492188585488856412);
void gnss_H_7(double *state, double *sat_pos_vel, double *out_1604423232564836340);
void gnss_h_21(double *state, double *sat_pos_vel, double *out_3492188585488856412);
void gnss_H_21(double *state, double *sat_pos_vel, double *out_1604423232564836340);
void gnss_predict(double *in_x, double *in_P, double *in_Q, double dt);
}