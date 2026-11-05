#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_1372154176746733435);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_1523580565963320994);
void pose_H_mod_fun(double *state, double *out_7104221342799173532);
void pose_f_fun(double *state, double dt, double *out_7349931890006772642);
void pose_F_fun(double *state, double dt, double *out_1064691538495726265);
void pose_h_4(double *state, double *unused, double *out_5786601062018184200);
void pose_H_4(double *state, double *unused, double *out_8923920068705470393);
void pose_h_10(double *state, double *unused, double *out_8200446056116706374);
void pose_H_10(double *state, double *unused, double *out_8156688557227160880);
void pose_h_13(double *state, double *unused, double *out_9145870174400750931);
void pose_H_13(double *state, double *unused, double *out_5711646243373137592);
void pose_h_14(double *state, double *unused, double *out_5989511771500844071);
void pose_H_14(double *state, double *unused, double *out_6440035572708708927);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}