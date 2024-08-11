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
void live_H(double *in_vec, double *out_922110052455500416);
void live_err_fun(double *nom_x, double *delta_x, double *out_1372731217466422364);
void live_inv_err_fun(double *nom_x, double *true_x, double *out_4171867721208288129);
void live_H_mod_fun(double *state, double *out_1944348177732805919);
void live_f_fun(double *state, double dt, double *out_3839394864859173225);
void live_F_fun(double *state, double dt, double *out_4768353371645606994);
void live_h_4(double *state, double *unused, double *out_8276252422667808505);
void live_H_4(double *state, double *unused, double *out_2151060490846400574);
void live_h_9(double *state, double *unused, double *out_3482698696669977861);
void live_H_9(double *state, double *unused, double *out_5136158444418046896);
void live_h_10(double *state, double *unused, double *out_8916443391754176073);
void live_H_10(double *state, double *unused, double *out_6625552554847898130);
void live_h_12(double *state, double *unused, double *out_328328103410682851);
void live_H_12(double *state, double *unused, double *out_8532318867889133570);
void live_h_35(double *state, double *unused, double *out_1739372950156366948);
void live_H_35(double *state, double *unused, double *out_1215601566526206802);
void live_h_32(double *state, double *unused, double *out_4124213804255924078);
void live_H_32(double *state, double *unused, double *out_3003097671145702268);
void live_h_13(double *state, double *unused, double *out_8912042338290709278);
void live_H_13(double *state, double *unused, double *out_3533011528714349284);
void live_h_14(double *state, double *unused, double *out_3482698696669977861);
void live_H_14(double *state, double *unused, double *out_5136158444418046896);
void live_h_33(double *state, double *unused, double *out_7920736334064917353);
void live_H_33(double *state, double *unused, double *out_7034556213909630385);
void live_predict(double *in_x, double *in_P, double *in_Q, double dt);
}