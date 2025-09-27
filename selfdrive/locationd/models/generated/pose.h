#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_8904005694201781505);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_319882326801197501);
void pose_H_mod_fun(double *state, double *out_2755842367827800629);
void pose_f_fun(double *state, double dt, double *out_2465907068804727132);
void pose_F_fun(double *state, double dt, double *out_8858355740763119346);
void pose_h_4(double *state, double *unused, double *out_5314299562689028081);
void pose_H_4(double *state, double *unused, double *out_8603924174579759350);
void pose_h_10(double *state, double *unused, double *out_1117176031280540036);
void pose_H_10(double *state, double *unused, double *out_8788488427206403946);
void pose_h_13(double *state, double *unused, double *out_4742713455498518035);
void pose_H_13(double *state, double *unused, double *out_5391650349247426549);
void pose_h_14(double *state, double *unused, double *out_9173159729852422823);
void pose_H_14(double *state, double *unused, double *out_4640683318240274821);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}