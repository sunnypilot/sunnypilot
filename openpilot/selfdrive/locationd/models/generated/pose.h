#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_8299703332077589328);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_4608058237383429265);
void pose_H_mod_fun(double *state, double *out_7885453398379249088);
void pose_f_fun(double *state, double dt, double *out_1688144950946873165);
void pose_F_fun(double *state, double dt, double *out_4851283621730691038);
void pose_h_4(double *state, double *unused, double *out_2329133011647763937);
void pose_H_4(double *state, double *unused, double *out_8639614400433961695);
void pose_h_10(double *state, double *unused, double *out_3294648635274985008);
void pose_H_10(double *state, double *unused, double *out_3780608178453222524);
void pose_h_13(double *state, double *unused, double *out_8905113933939181200);
void pose_H_13(double *state, double *unused, double *out_6594855847943257120);
void pose_h_14(double *state, double *unused, double *out_8324071568749841126);
void pose_H_14(double *state, double *unused, double *out_5843888816936105392);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}