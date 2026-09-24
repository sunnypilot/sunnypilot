#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_7117000844039973656);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5738271447995775317);
void pose_H_mod_fun(double *state, double *out_4131332949940298666);
void pose_f_fun(double *state, double dt, double *out_6388120990768684370);
void pose_F_fun(double *state, double dt, double *out_7678082896540462195);
void pose_h_4(double *state, double *unused, double *out_285865806461862263);
void pose_H_4(double *state, double *unused, double *out_2311634224034001805);
void pose_h_10(double *state, double *unused, double *out_3345721551474225191);
void pose_H_10(double *state, double *unused, double *out_7600016663620136720);
void pose_h_13(double *state, double *unused, double *out_3239845409590022619);
void pose_H_13(double *state, double *unused, double *out_5523908049366334606);
void pose_h_14(double *state, double *unused, double *out_8238467406184066972);
void pose_H_14(double *state, double *unused, double *out_6274875080373486334);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}