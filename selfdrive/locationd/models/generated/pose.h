#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_3306664206309014289);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_570891515664221910);
void pose_H_mod_fun(double *state, double *out_8375847635798993256);
void pose_f_fun(double *state, double dt, double *out_8983403032593092745);
void pose_F_fun(double *state, double dt, double *out_564215406758229092);
void pose_h_4(double *state, double *unused, double *out_7331136994390451530);
void pose_H_4(double *state, double *unused, double *out_3761220598869676892);
void pose_h_10(double *state, double *unused, double *out_6890323315298812884);
void pose_H_10(double *state, double *unused, double *out_8621903665340213317);
void pose_h_13(double *state, double *unused, double *out_3221209345999227064);
void pose_H_13(double *state, double *unused, double *out_3849410609447024037);
void pose_h_14(double *state, double *unused, double *out_6812638219376417230);
void pose_H_14(double *state, double *unused, double *out_202020257469807637);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}