#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_5712645316975978292);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_2375481713030026782);
void pose_H_mod_fun(double *state, double *out_9187572088722537132);
void pose_f_fun(double *state, double dt, double *out_6968288532191998630);
void pose_F_fun(double *state, double dt, double *out_396713754572384652);
void pose_h_4(double *state, double *unused, double *out_3828905798867891597);
void pose_H_4(double *state, double *unused, double *out_8433411086667824525);
void pose_h_10(double *state, double *unused, double *out_5109572919123009845);
void pose_H_10(double *state, double *unused, double *out_1305010934300019274);
void pose_h_13(double *state, double *unused, double *out_5661171709549975544);
void pose_H_13(double *state, double *unused, double *out_5221137261335491724);
void pose_h_14(double *state, double *unused, double *out_6329175778955850944);
void pose_H_14(double *state, double *unused, double *out_6930544554746354795);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}