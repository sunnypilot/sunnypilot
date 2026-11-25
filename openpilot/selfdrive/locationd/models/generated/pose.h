#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_8239082397058567475);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_7476243289318583052);
void pose_H_mod_fun(double *state, double *out_6682901757221528583);
void pose_f_fun(double *state, double dt, double *out_8926187974092623704);
void pose_F_fun(double *state, double dt, double *out_7762434416297877994);
void pose_h_4(double *state, double *unused, double *out_4305306830373346392);
void pose_H_4(double *state, double *unused, double *out_1517403126751696184);
void pose_h_10(double *state, double *unused, double *out_6976768425782679545);
void pose_H_10(double *state, double *unused, double *out_3773372038423704930);
void pose_h_13(double *state, double *unused, double *out_6361379321214522320);
void pose_H_13(double *state, double *unused, double *out_9128034335068397113);
void pose_h_14(double *state, double *unused, double *out_4542222400622544050);
void pose_H_14(double *state, double *unused, double *out_5480643983091180713);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}