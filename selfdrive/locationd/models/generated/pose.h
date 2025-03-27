#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_4675916976957672131);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_8932320044125663978);
void pose_H_mod_fun(double *state, double *out_8547583619141688255);
void pose_f_fun(double *state, double dt, double *out_5173460647487908586);
void pose_F_fun(double *state, double dt, double *out_7570643880185265565);
void pose_h_4(double *state, double *unused, double *out_680141703095616266);
void pose_H_4(double *state, double *unused, double *out_318144395399465431);
void pose_h_10(double *state, double *unused, double *out_8746364681564070660);
void pose_H_10(double *state, double *unused, double *out_4156082973223883983);
void pose_h_13(double *state, double *unused, double *out_5669417444424150126);
void pose_H_13(double *state, double *unused, double *out_7292486812917235498);
void pose_h_14(double *state, double *unused, double *out_4745054529679966551);
void pose_H_14(double *state, double *unused, double *out_3645096460940019098);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}