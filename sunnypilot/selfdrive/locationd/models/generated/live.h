#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void live_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_9(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_12(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_35(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_32(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_update_33(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void live_H(double *in_vec, double *out_4323635268615141267);
void live_err_fun(double *nom_x, double *delta_x, double *out_6197074480032553231);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_2989387618240936660);
void live_H_mod_fun(double *state, double *out_6613539539070352198);
void live_f_fun(double *state, double dt, double *out_8933377197583675948);
void live_F_fun(double *state, double dt, double *out_3718350443949690231);
void live_h_4(double *state, double *unused, double *out_6331268052836927497);
void live_H_4(double *state, double *unused, double *out_1163708809003022022);
void live_h_9(double *state, double *unused, double *out_2390193527998915912);
void live_H_9(double *state, double *unused, double *out_8450927744267469492);
void live_h_10(double *state, double *unused, double *out_4949516915644995188);
void live_H_10(double *state, double *unused, double *out_2720952721708703855);
void live_h_12(double *state, double *unused, double *out_6417586108362548470);
void live_H_12(double *state, double *unused, double *out_8830837122685472514);
void live_h_35(double *state, double *unused, double *out_4000387409650514689);
void live_H_35(double *state, double *unused, double *out_4530370866375629398);
void live_h_32(double *state, double *unused, double *out_5137988937425953647);
void live_H_32(double *state, double *unused, double *out_4661535651316369867);
void live_h_13(double *state, double *unused, double *out_433309107792795920);
void live_H_13(double *state, double *unused, double *out_4947836704050735313);
void live_h_14(double *state, double *unused, double *out_2390193527998915912);
void live_H_14(double *state, double *unused, double *out_8450927744267469492);
void live_h_33(double *state, double *unused, double *out_183207223102128485);
void live_H_33(double *state, double *unused, double *out_7680927871014487002);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}