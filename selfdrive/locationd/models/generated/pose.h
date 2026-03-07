#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_8941250306396925607);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_7188163769114424214);
void pose_H_mod_fun(double *state, double *out_3126609761481196981);
void pose_f_fun(double *state, double dt, double *out_7800799004538587322);
void pose_F_fun(double *state, double dt, double *out_834843542473115764);
void pose_h_4(double *state, double *unused, double *out_999525771239372771);
void pose_H_4(double *state, double *unused, double *out_645197448362710591);
void pose_h_10(double *state, double *unused, double *out_7654704647972063368);
void pose_H_10(double *state, double *unused, double *out_3722851181056312265);
void pose_h_13(double *state, double *unused, double *out_4337727964590481795);
void pose_H_13(double *state, double *unused, double *out_3188558014939813433);
void pose_h_14(double *state, double *unused, double *out_4948904525269361383);
void pose_H_14(double *state, double *unused, double *out_2437590983932661705);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}