#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_7849211930432319310);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_4938013129047494051);
void pose_H_mod_fun(double *state, double *out_4310619498118974873);
void pose_f_fun(double *state, double dt, double *out_1974982568906725041);
void pose_F_fun(double *state, double dt, double *out_6575454721087425774);
void pose_h_4(double *state, double *unused, double *out_1876366542928782564);
void pose_H_4(double *state, double *unused, double *out_3790922340853437677);
void pose_h_10(double *state, double *unused, double *out_3919183550661363398);
void pose_H_10(double *state, double *unused, double *out_2325412850660363779);
void pose_h_13(double *state, double *unused, double *out_5236404584387533616);
void pose_H_13(double *state, double *unused, double *out_578648515521104876);
void pose_h_14(double *state, double *unused, double *out_3604078571385785794);
void pose_H_14(double *state, double *unused, double *out_172318515486046852);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}