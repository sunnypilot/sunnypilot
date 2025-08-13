#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_2669393212407968939);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_6589919633801240756);
void pose_H_mod_fun(double *state, double *out_8225234534934843580);
void pose_f_fun(double *state, double dt, double *out_3713400227530287176);
void pose_F_fun(double *state, double dt, double *out_7623311308597317329);
void pose_h_4(double *state, double *unused, double *out_1299539042272213645);
void pose_H_4(double *state, double *unused, double *out_1355781524233554350);
void pose_h_10(double *state, double *unused, double *out_4564875173987417445);
void pose_H_10(double *state, double *unused, double *out_6426002362757736416);
void pose_h_13(double *state, double *unused, double *out_8828664930147326382);
void pose_H_13(double *state, double *unused, double *out_4568055349565887151);
void pose_h_14(double *state, double *unused, double *out_960453994518179958);
void pose_H_14(double *state, double *unused, double *out_5319022380573038879);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}